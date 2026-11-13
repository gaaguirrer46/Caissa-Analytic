"""Casos de uso (puertos primarios / driving) del módulo de Indicadores."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from statistics import fmean
from typing import Dict, List, Optional

from ..atletas.puertos import (
    ProveedorInformacionAtleta,
    RepositorioAtletas,
    ResolutorAtletaUsuario,
)
from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorAutenticacion,
    ErrorValidacion,
)
from ..comun.ids import nuevo_id
from ..comun.validaciones import (
    convertir_enum,
    exigir_decimal,
    exigir_entero,
    exigir_fecha,
    exigir_texto,
)
from ..entrenamientos.puertos import RepositorioEntrenamientos
from ..objetivos.puertos import RepositorioObjetivos
from ..partidas.puertos import RepositorioPartidas
from .entidades import (
    INDICADORES_MENOR_ES_MEJOR,
    Alerta,
    ComparacionGrupal,
    DashboardAtleta,
    DashboardEntrenador,
    EstadoAlerta,
    FormatoReporte,
    IndicadorRendimiento,
    IndicadoresPermanentes,
    PeriodicidadGrafico,
    PeriodicidadTendencia,
    PeriodoInstitucional,
    PuntoSerie,
    RangoEvaluacion,
    Reporte,
    TendenciaComparada,
    TipoAlerta,
    TipoGraficoRendimiento,
    TipoIndicador,
    TipoReporte,
    TipoTablaDetallada,
)
from ..usuarios.entidades import Rol
from .puertos import (
    ProveedorDatosRendimiento,
    ProveedorRangosEvaluacion,
    RepositorioIndicadores,
    ServicioGeneracionReportes,
)

RANGOS_POR_DEFECTO: dict[TipoIndicador, tuple[float, float, float]] = {
    TipoIndicador.ACCURACY: (85, 75, 60),
    TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO: (90, 75, 50),
    TipoIndicador.CUMPLIMIENTO_OBJETIVOS: (90, 75, 50),
    TipoIndicador.ASISTENCIA: (90, 75, 50),
    TipoIndicador.RENDIMIENTO_EN_FINALES: (70, 55, 40),
    TipoIndicador.RENDIMIENTO_POR_APERTURA: (70, 55, 40),
    TipoIndicador.RATING_FIDE: (2000, 1800, 1600),
    TipoIndicador.RATING_FIDE_RAPIDAS: (2000, 1800, 1600),
    TipoIndicador.RATING_FIDE_BLITZ: (2000, 1800, 1600),
    TipoIndicador.VARIACION_RATING: (20, 0, -20),
    TipoIndicador.PORCENTAJE_RESULTADOS: (70, 50, 30),
    TipoIndicador.ACPL: (30, 50, 70),
    TipoIndicador.BLUNDERS: (1, 3, 5),
}

_INDICADORES_MENOR_ES_MEJOR = INDICADORES_MENOR_ES_MEJOR

TIPOS_COMPARABLES = [
    TipoIndicador.ACCURACY,
    TipoIndicador.ACPL,
    TipoIndicador.BLUNDERS,
    TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
    TipoIndicador.CUMPLIMIENTO_OBJETIVOS,
    TipoIndicador.PORCENTAJE_RESULTADOS,
    TipoIndicador.ASISTENCIA,
    TipoIndicador.PARTIDAS_ANALIZADAS,
    TipoIndicador.PARTICIPACION_TORNEOS,
    TipoIndicador.EJERCICIOS_TACTICOS_RESUELTOS,
    TipoIndicador.RATING_FIDE,
    TipoIndicador.RATING_FIDE_RAPIDAS,
    TipoIndicador.RATING_FIDE_BLITZ,
    TipoIndicador.VARIACION_RATING,
]

TIPOS_COMPARACION_GRUPO = [
    TipoIndicador.RATING_FIDE,
    TipoIndicador.ACCURACY,
    TipoIndicador.ACPL,
    TipoIndicador.BLUNDERS,
    TipoIndicador.PORCENTAJE_RESULTADOS,
    TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
]

def _validar_periodo(desde: object, hasta: object) -> tuple[date, date]:
    inicio = exigir_fecha(desde, "desde")
    fin = exigir_fecha(hasta, "hasta")
    if fin < inicio:
        raise ErrorValidacion("El periodo es inválido: la fecha final precede a la inicial.")
    return inicio, fin

def _id_de(atleta: object) -> int:
    """Extrae el id de un atleta representado por entidad o por id."""
    valor = getattr(atleta, "id", atleta)
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ErrorValidacion("El proveedor devolvió un atleta sin id válido.")
    return valor

def _resolver_tipos(
    tipos: Optional[List[TipoIndicador | str]],
    por_defecto: List[TipoIndicador],
) -> List[TipoIndicador]:
    """Convierte los tipos indicados o aplica los por defecto.

 Una lista explícita pero vacía es un error del llamador: se prefiere
 fallar con ``ErrorValidacion`` antes que comparar en silencio con un
 conjunto distinto del solicitado.
 """
    if tipos is None:
        return list(por_defecto)
    if not tipos:
        raise ErrorValidacion("Debe indicar al menos un indicador a comparar.")
    return [convertir_enum(TipoIndicador, t, "tipo") for t in tipos]

def _valor_indicador(
    proveedor: ProveedorDatosRendimiento,
    tipo: TipoIndicador,
    id_atleta: int,
    desde: date,
    hasta: date,
) -> float:
    """Calcula un indicador comparable a partir del proveedor de datos."""
    if tipo == TipoIndicador.ACCURACY:
        return proveedor.accuracy_promedio(id_atleta, desde, hasta)
    if tipo == TipoIndicador.ACPL:
        return proveedor.acpl_promedio(id_atleta, desde, hasta)
    if tipo == TipoIndicador.BLUNDERS:
        return float(proveedor.blunders_totales(id_atleta, desde, hasta))
    if tipo == TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO:
        planificadas = proveedor.horas_planificadas(id_atleta, desde, hasta)
        if planificadas <= 0:
            return 0.0
        return (
            proveedor.horas_entrenadas_aprobadas(id_atleta, desde, hasta)
            / planificadas
        ) * 100
    if tipo == TipoIndicador.CUMPLIMIENTO_OBJETIVOS:
        return proveedor.cumplimiento_objetivos(id_atleta, desde, hasta)
    if tipo == TipoIndicador.PORCENTAJE_RESULTADOS:
        victorias, tablas, derrotas = proveedor.resultados(
            id_atleta, desde, hasta
        )
        total = victorias + tablas + derrotas
        if total == 0:
            return 0.0
        return ((victorias + 0.5 * tablas) / total) * 100
    if tipo == TipoIndicador.ASISTENCIA:
        return proveedor.porcentaje_asistencia(id_atleta, desde, hasta)
    if tipo == TipoIndicador.PARTIDAS_ANALIZADAS:
        return float(proveedor.partidas_analizadas(id_atleta, desde, hasta))
    if tipo == TipoIndicador.PARTICIPACION_TORNEOS:
        return float(proveedor.torneos_jugados(id_atleta, desde, hasta))
    if tipo == TipoIndicador.EJERCICIOS_TACTICOS_RESUELTOS:
        return float(proveedor.ejercicios_tacticos_resueltos(id_atleta, desde, hasta))
    if tipo == TipoIndicador.RATING_FIDE:
        return float(proveedor.rating_fide(id_atleta, "clasicas"))
    if tipo == TipoIndicador.RATING_FIDE_RAPIDAS:
        return float(proveedor.rating_fide(id_atleta, "rapidas"))
    if tipo == TipoIndicador.RATING_FIDE_BLITZ:
        return float(proveedor.rating_fide(id_atleta, "blitz"))
    if tipo == TipoIndicador.VARIACION_RATING:
        return proveedor.variacion_rating(id_atleta, desde, hasta)
    raise ErrorValidacion(
        f"El indicador {tipo.value} no es comparable con los datos disponibles."
    )

def _mes_anterior(hoy: date) -> tuple[date, date, date, date]:
    """Devuelve (inicio_actual, fin_actual, inicio_anterior, fin_anterior)."""
    inicio_actual = date(hoy.year, hoy.month, 1)
    if hoy.month == 1:
        inicio_anterior = date(hoy.year - 1, 12, 1)
        fin_anterior = date(hoy.year - 1, 12, 31)
    else:
        inicio_anterior = date(hoy.year, hoy.month - 1, 1)
        fin_anterior = inicio_actual - date.resolution
    return inicio_actual, hoy, inicio_anterior, fin_anterior

def ventanas_de_periodo(
    periodicidad: PeriodicidadTendencia,
    fecha_referencia: date,
    torneo: Optional[str] = None,
    torneos: Optional[List[tuple]] = None,
    semana_plan: Optional[int] = None,
    anio_plan: Optional[int] = None,
) -> tuple[tuple[date, date], tuple[date, date]]:
    """resuelve las ventanas ``(anterior, actual)``.

 - SEMANAL: lunes.fecha de referencia contra la semana natural previa.
 - MENSUAL: mes en curso contra el mes anterior completo.
 - ANUAL: en.fecha del año en curso contra el mismo tramo del año previo
 (29 de febrero se ajusta al 28 cuando el año anterior no es bisiesto).
 - TORNEO: rango de fechas del evento contra el torneo inmediatamente
 anterior del atleta; si es su primer torneo, contra la ventana de igual
 duración inmediatamente anterior (sin inventar datos: los valores salen
 del proveedor para el rango que se le indique).
 - PLAN: la semana ISO del plan de entrenamiento contra la
 semana inmediatamente anterior ("antes y después de un plan"); exige
 ``semana_plan`` y ``anio_plan``.
 """
    if periodicidad == PeriodicidadTendencia.PLAN:
        if semana_plan is None or anio_plan is None:
            raise ErrorValidacion(
                "La periodicidad PLAN requiere 'semana_plan' y 'anio_plan' "
                "del plan de entrenamiento a comparar."
            )
        semana = exigir_entero(semana_plan, "semana_plan", minimo=1, maximo=53)
        anio = exigir_entero(anio_plan, "anio_plan", minimo=2000, maximo=2100)
        try:
            lunes = date.fromisocalendar(anio, semana, 1)
        except ValueError:
            raise ErrorValidacion(
                f"La semana {semana} del año {anio} no existe en el calendario ISO."
            )
        return (
            (lunes - timedelta(days=7), lunes - timedelta(days=1)),
            (lunes, lunes + timedelta(days=6)),
        )
    if semana_plan is not None or anio_plan is not None:
        raise ErrorValidacion(
            "Los parámetros 'semana_plan'/'anio_plan' sólo aplican a la "
            "periodicidad PLAN."
        )
    if periodicidad == PeriodicidadTendencia.SEMANAL:
        lunes = fecha_referencia - timedelta(days=fecha_referencia.weekday())
        anterior = (lunes - timedelta(days=7), lunes - timedelta(days=1))
        return anterior, (lunes, fecha_referencia)

    if periodicidad == PeriodicidadTendencia.MENSUAL:
        inicio, fin, inicio_previo, fin_previo = _mes_anterior(fecha_referencia)
        return (inicio_previo, fin_previo), (inicio, fin)

    if periodicidad == PeriodicidadTendencia.ANUAL:
        try:
            previo = fecha_referencia.replace(year=fecha_referencia.year - 1)
        except ValueError:
            previo = date(fecha_referencia.year - 1, 2, 28)
        anterior = (date(fecha_referencia.year - 1, 1, 1), previo)
        return anterior, (date(fecha_referencia.year, 1, 1), fecha_referencia)

    nombre = (torneo or "").strip().lower()
    propio: Optional[tuple[date, date]] = None
    previos: List[tuple[date, date]] = []
    for evento, desde, hasta in torneos or []:
        rango = (desde, hasta)
        if evento.strip().lower() == nombre:
            propio = rango
        else:
            previos.append(rango)
    if propio is None:
        raise EntidadNoEncontrada(f"No hay partidas registradas del torneo '{torneo}'.")

    inicio_propio, fin_propio = propio
    candidatos = [r for r in previos if r[1] < inicio_propio]
    if candidatos:
        anterior = max(candidatos, key=lambda r: (r[1], r[0]))
    else:

        duracion = (fin_propio - inicio_propio).days
        fin = inicio_propio - timedelta(days=1)
        anterior = (fin - timedelta(days=duracion), fin)
    return anterior, propio

@dataclass
class EvaluadorRangos:
    """RNF-07.2: aplica la configuración de rangos o los valores por defecto."""

    proveedor_configuracion: Optional[ProveedorRangosEvaluacion] = None

    def evaluar(self, tipo: TipoIndicador, valor: float) -> RangoEvaluacion:
        tipo_enum = convertir_enum(TipoIndicador, tipo, "tipo")
        numero = exigir_decimal(valor, "valor")
        rangos = self._obtener_rangos(tipo_enum)
        if rangos is None:
            return RangoEvaluacion.ACEPTABLE
        excelente, bueno, aceptable = rangos
        if tipo_enum in _INDICADORES_MENOR_ES_MEJOR:
            if numero <= excelente:
                return RangoEvaluacion.EXCELENTE
            if numero <= bueno:
                return RangoEvaluacion.BUENO
            if numero <= aceptable:
                return RangoEvaluacion.ACEPTABLE
            return RangoEvaluacion.REQUIERE_INTERVENCION
        if numero >= excelente:
            return RangoEvaluacion.EXCELENTE
        if numero >= bueno:
            return RangoEvaluacion.BUENO
        if numero >= aceptable:
            return RangoEvaluacion.ACEPTABLE
        return RangoEvaluacion.REQUIERE_INTERVENCION

    def _obtener_rangos(
        self, tipo: TipoIndicador
    ) -> Optional[tuple[float, float, float]]:
        if self.proveedor_configuracion is not None:
            configurados = self.proveedor_configuracion.rangos(tipo)
            if configurados is not None:
                if (
                    not isinstance(configurados, tuple)
                    or len(configurados) != 3
                    or any(
                        isinstance(v, bool) or not isinstance(v, (int, float))
                        for v in configurados
                    )
                ):
                    raise ErrorValidacion(
                        "La configuración de rangos debe ser una tupla de 3 números."
                    )
                return configurados
        return RANGOS_POR_DEFECTO.get(tipo)

@dataclass
class _BaseCalculoIndicadores:
    """Base común para la creación y persistencia de indicadores."""

    repositorio: RepositorioIndicadores
    proveedor: ProveedorDatosRendimiento
    evaluador: EvaluadorRangos = field(default_factory=EvaluadorRangos)

    def _crear(
        self,
        id_atleta: int,
        tipo: TipoIndicador,
        valor: float,
        desde: date,
        hasta: date,
    ) -> IndicadorRendimiento:
        inicio, fin = _validar_periodo(desde, hasta)
        numero = exigir_decimal(valor, f"valor de {tipo.value}")
        return IndicadorRendimiento(
            id=0,
            id_atleta=exigir_entero(id_atleta, "id_atleta", minimo=1),
            tipo=convertir_enum(TipoIndicador, tipo, "tipo"),
            valor=numero,
            rango_evaluacion=self.evaluador.evaluar(tipo, numero),
            periodo_inicio=inicio,
            periodo_fin=fin,
        )

    def _persistir(
        self, indicadores: List[IndicadorRendimiento]
    ) -> List[IndicadorRendimiento]:
        for indicador in indicadores:
            self.repositorio.guardar(indicador)
        return indicadores

@dataclass
class CalcularIndicadoresPrincipales(_BaseCalculoIndicadores):
    """métricas principales de rendimiento.

 Cobertura: rating FIDE (clásicas, rápidas y blitz), variación del rating
 en el periodo (desde snapshots históricos), porcentaje de resultados,
 accuracy, ACPL, blunders, cumplimiento de entrenamiento y de objetivos.
 ``RENDIMIENTO_POR_APERTURA``, ``RENDIMIENTO_EN_FINALES`` y
 ``GESTION_DEL_TIEMPO`` requieren datos que el modelo actual no expone y
 quedan documentados como pendientes.
 """

    def ejecutar(
        self, id_atleta: int, desde: date, hasta: date, *, solicitante: Solicitante
    ) -> List[IndicadorRendimiento]:
        exigir_entrenador(solicitante, "calcular indicadores principales")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        inicio, fin = _validar_periodo(desde, hasta)
        valores = {
            TipoIndicador.ACCURACY: self.proveedor.accuracy_promedio(
                id_atleta, inicio, fin
            ),
            TipoIndicador.ACPL: self.proveedor.acpl_promedio(id_atleta, inicio, fin),
            TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO: _valor_indicador(
                self.proveedor,
                TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
                id_atleta,
                inicio,
                fin,
            ),
            TipoIndicador.CUMPLIMIENTO_OBJETIVOS: self.proveedor.cumplimiento_objetivos(
                id_atleta, inicio, fin
            ),
            TipoIndicador.PORCENTAJE_RESULTADOS: _valor_indicador(
                self.proveedor,
                TipoIndicador.PORCENTAJE_RESULTADOS,
                id_atleta,
                inicio,
                fin,
            ),
            TipoIndicador.BLUNDERS: float(
                self.proveedor.blunders_totales(id_atleta, inicio, fin)
            ),
            TipoIndicador.RATING_FIDE: float(
                self.proveedor.rating_fide(id_atleta, "clasicas")
            ),
            TipoIndicador.RATING_FIDE_RAPIDAS: float(
                self.proveedor.rating_fide(id_atleta, "rapidas")
            ),
            TipoIndicador.RATING_FIDE_BLITZ: float(
                self.proveedor.rating_fide(id_atleta, "blitz")
            ),
            TipoIndicador.VARIACION_RATING: float(
                self.proveedor.variacion_rating(id_atleta, inicio, fin)
            ),
        }
        indicadores = [
            self._crear(id_atleta, tipo, valor, inicio, fin)
            for tipo, valor in valores.items()
        ]
        return self._persistir(indicadores)

@dataclass
class CalcularIndicadoresSecundarios(_BaseCalculoIndicadores):
    """métricas secundarias de actividad."""

    def ejecutar(
        self, id_atleta: int, desde: date, hasta: date, *, solicitante: Solicitante
    ) -> List[IndicadorRendimiento]:
        exigir_entrenador(solicitante, "calcular indicadores secundarios")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        inicio, fin = _validar_periodo(desde, hasta)
        valores = {
            TipoIndicador.EJERCICIOS_TACTICOS_RESUELTOS: float(
                self.proveedor.ejercicios_tacticos_resueltos(id_atleta, inicio, fin)
            ),
            TipoIndicador.PARTIDAS_ANALIZADAS: float(
                self.proveedor.partidas_analizadas(id_atleta, inicio, fin)
            ),
            TipoIndicador.ASISTENCIA: self.proveedor.porcentaje_asistencia(
                id_atleta, inicio, fin
            ),
            TipoIndicador.PARTICIPACION_TORNEOS: float(
                self.proveedor.torneos_jugados(id_atleta, inicio, fin)
            ),
        }
        indicadores = [
            self._crear(id_atleta, tipo, valor, inicio, fin)
            for tipo, valor in valores.items()
        ]
        return self._persistir(indicadores)

@dataclass
class GenerarDashboardEntrenador:
    """vista consolidada del equipo con alertas automáticas.

 Cubre estado general del equipo, atletas activos, alertas importantes,
 cumplimiento del plan, evolución del rating grupal (nivel actual y
 variación en el periodo), rendimiento promedio (accuracy medio del
 equipo) y estado de objetivos SMART.

 Limitación del modelo: "próximos eventos" requiere un calendario de
 competencias que el esquema no incluye (no hay tabla de eventos
 futuros), por lo que no se inventa esa sección.
 """

    repositorio: RepositorioIndicadores
    proveedor: ProveedorDatosRendimiento

    def ejecutar(
        self,
        id_entrenador: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        *,
        solicitante: Solicitante,
    ) -> DashboardEntrenador:
        exigir_entrenador(solicitante, "generar el dashboard del entrenador")
        exigir_entero(id_entrenador, "id_entrenador", minimo=1)
        hoy = date.today()
        fin = hasta or hoy
        inicio = desde or date(fin.year, 1, 1)
        inicio, fin = _validar_periodo(inicio, fin)

        atletas = self.proveedor.atletas_por_entrenador(id_entrenador)
        ids = [_id_de(a) for a in atletas]

        ratings: List[float] = []
        variaciones: List[float] = []
        rendimientos: List[float] = []
        cumplimientos: List[float] = []
        asistencias: List[float] = []
        pendientes: List[int] = []
        for id_atleta in ids:
            ratings.append(
                float(self.proveedor.rating_fide(id_atleta, "clasicas"))
            )
            variaciones.append(
                self.proveedor.variacion_rating(id_atleta, inicio, fin)
            )
            rendimientos.append(
                self.proveedor.accuracy_promedio(id_atleta, inicio, fin)
            )
            cumplimientos.append(
                _valor_indicador(
                    self.proveedor,
                    TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
                    id_atleta,
                    inicio,
                    fin,
                )
            )
            asistencias.append(
                self.proveedor.porcentaje_asistencia(id_atleta, inicio, fin)
            )
            if self.proveedor.objetivos_no_cumplidos(id_atleta) > 0:
                pendientes.append(id_atleta)

        resumen = {
            "total_atletas": len(ids),
            "rating_promedio": fmean(ratings) if ratings else 0.0,
            "rendimiento_promedio": fmean(rendimientos) if rendimientos else 0.0,
            "cumplimiento_promedio": fmean(cumplimientos) if cumplimientos else 0.0,
            "asistencia_promedio": fmean(asistencias) if asistencias else 0.0,
            "periodo_inicio": inicio.isoformat(),
            "periodo_fin": fin.isoformat(),
        }
        dashboard = DashboardEntrenador(
            resumen_equipo=resumen,
            atletas_activos=len([a for a in atletas if getattr(a, "activo", True)]),
            alertas=self._detectar_alertas(ids),
            cumplimiento_plan={
                "promedio": resumen["cumplimiento_promedio"],
                "por_atleta": dict(zip(ids, cumplimientos)),
            },
            evolucion_rating_grupal={
                "promedio_actual": resumen["rating_promedio"],
                "variacion_promedio": fmean(variaciones) if variaciones else 0.0,
                "por_atleta": dict(zip(ids, ratings)),
                "variacion_por_atleta": dict(zip(ids, variaciones)),
            },
            objetivos_pendientes=pendientes,
        )
        return self.repositorio.guardar_dashboard_entrenador(dashboard)

    def _detectar_alertas(self, ids_atletas: List[int]) -> List[Alerta]:
        """alertas cuando un indicador cae en 'Requiere Intervención'."""
        alertas: List[Alerta] = []
        for id_atleta in ids_atletas:
            for indicador in self.repositorio.listar_por_atleta(id_atleta):
                if indicador.rango_evaluacion == RangoEvaluacion.REQUIERE_INTERVENCION:
                    alertas.append(
                        Alerta(
                            id=nuevo_id("alerta"),
                            tipo=self._tipo_alerta(indicador.tipo),
                            id_atleta=id_atleta,
                            fecha_generacion=datetime.now(timezone.utc),
                            estado=EstadoAlerta.ACTIVA,
                        )
                    )
        return alertas

    @staticmethod
    def _tipo_alerta(tipo: TipoIndicador) -> TipoAlerta:
        if tipo == TipoIndicador.ASISTENCIA:
            return TipoAlerta.BAJA_ASISTENCIA
        if tipo == TipoIndicador.CUMPLIMIENTO_OBJETIVOS:
            return TipoAlerta.OBJETIVO_VENCIDO
        return TipoAlerta.DISMINUCION_RENDIMIENTO

def _exigir_acceso_informacion_atleta(
    resolutor: Optional[ResolutorAtletaUsuario],
    id_atleta: int,
    solicitante: Solicitante,
    accion: str,
) -> None:
    """entrenador (cualquier atleta) o atleta (sólo el propio).

 Sin ``resolutor`` configurado el autoservicio del atleta queda denegado.
 """
    if solicitante.rol == Rol.ENTRENADOR:
        return
    if solicitante.rol != Rol.ATLETA:
        raise ErrorAutenticacion(
            f"Acceso denegado: el rol {solicitante.rol.value} no puede {accion}."
        )
    if resolutor is None:
        raise ErrorAutenticacion(
            f"Acceso denegado: el autoservicio del atleta no puede {accion}."
        )
    vinculado = resolutor.atleta_de_usuario(solicitante.id_usuario)
    if vinculado is None:
        raise EntidadNoEncontrada(
            "No existe un atleta vinculado a este usuario."
        )
    if vinculado != id_atleta:
        raise ErrorAutenticacion(
            "Acceso denegado: la información consultada no pertenece a su "
            "información personal."
        )

@dataclass
class GenerarDashboardAtleta:
    """vista personal con KPIs tipo semáforo.

 El entrenador genera el dashboard de cualquiera de sus atletas; el
 atleta autenticado consulta únicamente el suyo propio mediante el
 ``resolutor`` de identidad (autoservicio). Sin ``resolutor``
 configurado el autoservicio queda denegado.
 """

    repositorio: RepositorioIndicadores
    proveedor: ProveedorDatosRendimiento
    resolutor: Optional[ResolutorAtletaUsuario] = None

    def _exigir_acceso(self, id_atleta: int, solicitante: Solicitante) -> None:
        _exigir_acceso_informacion_atleta(
            self.resolutor,
            id_atleta,
            solicitante,
            "generar el dashboard de un atleta",
        )

    def ejecutar(
        self,
        id_atleta: int,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        hoy: Optional[date] = None,
        *,
        solicitante: Solicitante,
    ) -> DashboardAtleta:
        self._exigir_acceso(id_atleta, solicitante)
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        referencia = exigir_fecha(hoy or date.today(), "hoy")
        inicio_actual, fin_actual, inicio_previo, fin_previo = _mes_anterior(referencia)
        inicio = desde or inicio_actual
        fin = hasta or fin_actual
        inicio, fin = _validar_periodo(inicio, fin)

        indicadores = self.repositorio.listar_por_periodo(id_atleta, inicio, fin)
        kpi: Dict[TipoIndicador, float] = {}
        semaforos: Dict[TipoIndicador, RangoEvaluacion] = {}
        for indicador in indicadores:
            kpi[indicador.tipo] = indicador.valor
            semaforos[indicador.tipo] = indicador.rango_evaluacion

        comparacion: Dict[str, dict] = {}
        for tendencia in _comparar_periodos(
            self.proveedor,
            id_atleta,
            inicio_previo,
            fin_previo,
            inicio_actual,
            fin_actual,
        ):
            comparacion[tendencia.tipo.value] = {
                "anterior": tendencia.valor_anterior,
                "actual": tendencia.valor_actual,
                "variacion": tendencia.variacion,
            }

        dashboard = DashboardAtleta(
            id_atleta=id_atleta,
            kpi_personales=kpi,
            semaforos=semaforos,
            comparacion_mes_actual_vs_anterior=comparacion,

            horas_entrenadas=self.proveedor.horas_entrenadas_aprobadas(
                id_atleta, inicio, fin
            ),
            horas_planificadas=self.proveedor.horas_planificadas(
                id_atleta, inicio, fin
            ),
        )
        return self.repositorio.guardar_dashboard_atleta(dashboard)

def _comparar_periodos(
    proveedor: ProveedorDatosRendimiento,
    id_atleta: int,
    desde_anterior: date,
    hasta_anterior: date,
    desde_actual: date,
    hasta_actual: date,
    tipos: Optional[List[TipoIndicador | str]] = None,
) -> List[TendenciaComparada]:
    """Núcleo de la comparación entre dos periodos, sin control de acceso.

 Lo público (``CompararTendencias``) exige rol entrenador; el dashboard
 del atleta reutiliza este núcleo tras autorizar el acceso a su
 propia información.
 """
    exigir_entero(id_atleta, "id_atleta", minimo=1)
    inicio_previo, fin_previo = _validar_periodo(desde_anterior, hasta_anterior)
    inicio_actual, fin_actual = _validar_periodo(desde_actual, hasta_actual)
    if inicio_actual < inicio_previo:
        raise ErrorValidacion(
            "El periodo actual no puede iniciar antes que el periodo anterior."
        )
    tipos_enum = _resolver_tipos(tipos, TIPOS_COMPARABLES)
    return [
        TendenciaComparada(
            tipo=tipo,
            valor_anterior=_valor_indicador(
                proveedor, tipo, id_atleta, inicio_previo, fin_previo
            ),
            valor_actual=_valor_indicador(
                proveedor, tipo, id_atleta, inicio_actual, fin_actual
            ),
        )
        for tipo in tipos_enum
    ]

_INDICADORES_PERMANENTES = [
    TipoIndicador.RATING_FIDE,
    TipoIndicador.VARIACION_RATING,
    TipoIndicador.ACCURACY,
    TipoIndicador.PORCENTAJE_RESULTADOS,
    TipoIndicador.BLUNDERS,
    TipoIndicador.ASISTENCIA,
    TipoIndicador.CUMPLIMIENTO_OBJETIVOS,
    TipoIndicador.PARTICIPACION_TORNEOS,
    TipoIndicador.ACPL,
    TipoIndicador.EJERCICIOS_TACTICOS_RESUELTOS,
]

@dataclass
class ConsultarIndicadoresPermanentes:
    """vista siempre visible de los indicadores del atleta.

 Reúne en una sola vista los indicadores del sistema: rating promedio,
 variación de rating, accuracy, resultados, blunders, rendimiento por
 color, asistencia, cumplimiento de objetivos, mejores y peores aperturas,
 conversión de finales, rendimiento táctico, torneos, medallas y ranking.

 Limitaciones documentadas del modelo oficial:
 - ``RENDIMIENTO_EN_FINALES`` no tiene fuente por fase: 0.0.
 - Las ``medallas`` no tienen tabla: 0 (mismo criterio que el proveedor
 de avance de objetivos).
 - La táctica usa ACPL como proxy; los ejercicios resueltos valen 0
 porque el modelo no los registra.
 """

    proveedor: ProveedorDatosRendimiento
    resolutor: Optional[ResolutorAtletaUsuario] = None

    def ejecutar(
        self,
        id_atleta: int,
        desde: date,
        hasta: date,
        *,
        solicitante: Solicitante,
    ) -> IndicadoresPermanentes:
        _exigir_acceso_informacion_atleta(
            self.resolutor,
            id_atleta,
            solicitante,
            "consultar los indicadores permanentes de un atleta",
        )
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        inicio, fin = _validar_periodo(desde, hasta)

        indicadores = {
            tipo: _valor_indicador(
                self.proveedor, tipo, id_atleta, inicio, fin
            )
            for tipo in _INDICADORES_PERMANENTES
        }

        indicadores[TipoIndicador.RENDIMIENTO_EN_FINALES] = 0.0

        return IndicadoresPermanentes(
            id_atleta=id_atleta,
            periodo_inicio=inicio,
            periodo_fin=fin,
            indicadores=indicadores,
            rendimiento_por_color={
                color: self._rendimiento_color(id_atleta, color, inicio, fin)
                for color in ("BLANCAS", "NEGRAS")
            },
            aperturas=self._mejores_peores_aperturas(id_atleta, inicio, fin),
            medallas=int(
                self.proveedor.medallas_obtenidas(id_atleta, inicio, fin)
            ),
            ranking=self._ranking(id_atleta),
        )

    def _rendimiento_color(
        self, id_atleta: int, color: str, inicio: date, fin: date
    ) -> dict:
        victorias, tablas, derrotas = self.proveedor.rendimiento_por_color(
            id_atleta, color, inicio, fin
        )
        total = victorias + tablas + derrotas
        porcentaje = ((victorias + 0.5 * tablas) / total) * 100 if total else 0.0
        return {
            "victorias": victorias,
            "tablas": tablas,
            "derrotas": derrotas,
            "porcentaje": porcentaje,
        }

    def _mejores_peores_aperturas(
        self, id_atleta: int, inicio: date, fin: date
    ) -> Dict[str, Optional[dict]]:
        usadas = [
            {"codigo": eco, "nombre": nombre, "rendimiento": porcentaje}
            for eco, nombre, porcentaje in self.proveedor.rendimiento_por_apertura(
                id_atleta, inicio, fin
            )
        ]
        if not usadas:
            return {"mejor": None, "peor": None}
        return {
            "mejor": max(usadas, key=lambda a: a["rendimiento"]),
            "peor": min(usadas, key=lambda a: a["rendimiento"]),
        }

    def _ranking(self, id_atleta: int) -> dict:
        """Posición por rating FIDE clásicas entre los atletas del sistema."""
        ids = [_id_de(a) for a in self.proveedor.ids_atletas()]
        if id_atleta not in ids:
            ids.append(id_atleta)
        propio = float(self.proveedor.rating_fide(id_atleta, "clasicas"))
        posicion = 1 + sum(
            1
            for otro in ids
            if otro != id_atleta
            and float(self.proveedor.rating_fide(otro, "clasicas")) > propio
        )
        return {
            "posicion": posicion,
            "total_atletas": len(ids),
            "criterio": TipoIndicador.RATING_FIDE.value,
        }

@dataclass
class CompararTendencias:
    """compara indicadores entre dos periodos."""

    proveedor: ProveedorDatosRendimiento

    def ejecutar(
        self,
        id_atleta: int,
        desde_anterior: date,
        hasta_anterior: date,
        desde_actual: date,
        hasta_actual: date,
        tipos: Optional[List[TipoIndicador | str]] = None,
        *,
        solicitante: Solicitante,
    ) -> List[TendenciaComparada]:
        exigir_entrenador(solicitante, "comparar tendencias de un atleta")
        return _comparar_periodos(
            self.proveedor,
            id_atleta,
            desde_anterior,
            hasta_anterior,
            desde_actual,
            hasta_actual,
            tipos,
        )

@dataclass
class CompararTendenciasPeriodicas:
    """tendencias en periodos semanal, mensual, anual o por torneo."""

    proveedor: ProveedorDatosRendimiento

    def ejecutar(
        self,
        id_atleta: int,
        periodicidad: PeriodicidadTendencia | str,
        tipos: Optional[List[TipoIndicador | str]] = None,
        *,
        fecha_referencia: Optional[date] = None,
        torneo: Optional[str] = None,
        semana_plan: Optional[int] = None,
        anio_plan: Optional[int] = None,
        solicitante: Solicitante,
    ) -> List[TendenciaComparada]:
        exigir_entrenador(solicitante, "comparar tendencias por periodo")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        periodicidad_enum = convertir_enum(
            PeriodicidadTendencia, periodicidad, "periodicidad"
        )
        referencia = exigir_fecha(
            fecha_referencia if fecha_referencia is not None else date.today(),
            "fecha_referencia",
        )
        nombre_torneo: Optional[str] = None
        torneos: List[tuple] = []
        if periodicidad_enum == PeriodicidadTendencia.TORNEO:
            nombre_torneo = exigir_texto(torneo, "torneo", max_longitud=100)
            torneos = self.proveedor.torneos_del_atleta(id_atleta)
        elif torneo is not None:
            raise ErrorValidacion(
                "El parámetro 'torneo' sólo aplica a la periodicidad TORNEO."
            )

        semana_plan_enum: Optional[int] = None
        anio_plan_enum: Optional[int] = None
        if periodicidad_enum == PeriodicidadTendencia.PLAN:
            if semana_plan is None or anio_plan is None:
                raise ErrorValidacion(
                    "La periodicidad PLAN requiere 'semana_plan' y 'anio_plan' "
                    "del plan de entrenamiento a comparar."
                )
            semana_plan_enum = exigir_entero(
                semana_plan, "semana_plan", minimo=1, maximo=53
            )
            anio_plan_enum = exigir_entero(
                anio_plan, "anio_plan", minimo=2000, maximo=2100
            )
        elif semana_plan is not None or anio_plan is not None:
            raise ErrorValidacion(
                "Los parámetros 'semana_plan'/'anio_plan' sólo aplican a la "
                "periodicidad PLAN."
            )

        (ant_desde, ant_hasta), (act_desde, act_hasta) = ventanas_de_periodo(
            periodicidad_enum,
            referencia,
            nombre_torneo,
            torneos,
            semana_plan_enum,
            anio_plan_enum,
        )
        return CompararTendencias(self.proveedor).ejecutar(
            id_atleta,
            ant_desde,
            ant_hasta,
            act_desde,
            act_hasta,
            tipos,
            solicitante=solicitante,
        )

def _comparar_poblacion(
    proveedor: ProveedorDatosRendimiento,
    poblacion: List[int],
    id_atleta: int,
    inicio: date,
    fin: date,
    tipos_enum: List[TipoIndicador],
) -> List[ComparacionGrupal]:
    """Promedio, ranking y progreso general de un atleta frente a ``poblacion``.

 El progreso general es la variación de rating FIDE clásicas
 de cada atleta dentro del periodo, agregada como valor propio y como
 promedio de la población comparada.
 """
    progresos = {
        id_grupo: proveedor.variacion_rating(id_grupo, inicio, fin)
        for id_grupo in poblacion
    }
    progreso_atleta = progresos[id_atleta]
    progreso_grupo = fmean(progresos.values()) if progresos else 0.0

    comparaciones: List[ComparacionGrupal] = []
    for tipo in tipos_enum:
        valores = {
            id_grupo: _valor_indicador(proveedor, tipo, id_grupo, inicio, fin)
            for id_grupo in poblacion
        }
        valor_atleta = valores[id_atleta]
        promedio = fmean(valores.values()) if valores else 0.0
        menor_es_mejor = tipo in _INDICADORES_MENOR_ES_MEJOR
        ordenados = sorted(
            valores.items(),
            key=lambda par: par[1],
            reverse=not menor_es_mejor,
        )
        posicion = next(
            i for i, (id_grupo, _) in enumerate(ordenados, start=1)
            if id_grupo == id_atleta
        )
        comparaciones.append(
            ComparacionGrupal(
                tipo=tipo,
                valor_atleta=valor_atleta,
                promedio_grupo=promedio,
                posicion=posicion,
                total_atletas=len(poblacion),
                progreso_atleta=progreso_atleta,
                progreso_grupo=progreso_grupo,
            )
        )
    return comparaciones

def _grupo_del_entrenador(
    proveedor: ProveedorDatosRendimiento,
    id_entrenador: int,
    id_atleta: int,
) -> List[int]:
    """Ids del grupo exigiendo que el atleta pertenezca a él."""
    ids = [_id_de(a) for a in proveedor.atletas_por_entrenador(id_entrenador)]
    if id_atleta not in ids:
        raise EntidadNoEncontrada(
            "El atleta no pertenece al grupo del entrenador indicado."
        )
    return ids

@dataclass
class CompararConGrupo:
    """compara al atleta con el promedio del grupo y su ranking."""

    proveedor: ProveedorDatosRendimiento

    def ejecutar(
        self,
        id_entrenador: int,
        id_atleta: int,
        desde: date,
        hasta: date,
        tipos: Optional[List[TipoIndicador | str]] = None,
        *,
        solicitante: Solicitante,
    ) -> List[ComparacionGrupal]:
        exigir_entrenador(solicitante, "comparar a un atleta con su grupo")
        exigir_entero(id_entrenador, "id_entrenador", minimo=1)
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        inicio, fin = _validar_periodo(desde, hasta)
        ids = _grupo_del_entrenador(self.proveedor, id_entrenador, id_atleta)
        tipos_enum = _resolver_tipos(tipos, TIPOS_COMPARACION_GRUPO)
        return _comparar_poblacion(
            self.proveedor, ids, id_atleta, inicio, fin, tipos_enum
        )

@dataclass
class CompararConPares:
    """compara al atleta con los del mismo rango de rating (club)."""

    proveedor: ProveedorDatosRendimiento
    evaluador: EvaluadorRangos = field(default_factory=EvaluadorRangos)

    def ejecutar(
        self,
        id_entrenador: int,
        id_atleta: int,
        desde: date,
        hasta: date,
        tipos: Optional[List[TipoIndicador | str]] = None,
        *,
        solicitante: Solicitante,
    ) -> List[ComparacionGrupal]:
        exigir_entrenador(solicitante, "comparar a un atleta con sus pares")
        exigir_entero(id_entrenador, "id_entrenador", minimo=1)
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        inicio, fin = _validar_periodo(desde, hasta)
        _grupo_del_entrenador(self.proveedor, id_entrenador, id_atleta)

        rango_atleta = self._rango_de(id_atleta)
        pares = [
            id_par
            for id_par in [_id_de(a) for a in self.proveedor.ids_atletas()]
            if self._rango_de(id_par) == rango_atleta
        ]
        if id_atleta not in pares:

            pares.append(id_atleta)
        tipos_enum = _resolver_tipos(tipos, TIPOS_COMPARACION_GRUPO)
        return _comparar_poblacion(
            self.proveedor, pares, id_atleta, inicio, fin, tipos_enum
        )

    def _rango_de(self, id_atleta: int) -> RangoEvaluacion:
        """Rango de evaluación del rating FIDE clásicas."""
        rating = float(self.proveedor.rating_fide(id_atleta, "clasicas"))
        return self.evaluador.evaluar(TipoIndicador.RATING_FIDE, rating)

@dataclass
class GenerarReporte:
    """genera un reporte con el contenido indicado."""

    servicio_reporte: ServicioGeneracionReportes

    def ejecutar(
        self,
        tipo: TipoReporte | str,
        formato: FormatoReporte | str,
        titulo: str,
        secciones: List[str],
        contenido: dict,
        ruta_destino: str,
        *,
        solicitante: Solicitante,
    ) -> str:
        exigir_entrenador(solicitante, "generar reportes")
        tipo_enum = convertir_enum(TipoReporte, tipo, "tipo")
        formato_enum = convertir_enum(FormatoReporte, formato, "formato")
        titulo_limpio = exigir_texto(titulo, "titulo", max_longitud=200)
        if not isinstance(secciones, list) or not secciones:
            raise ErrorValidacion("El reporte debe incluir al menos una sección.")
        secciones_limpias = [
            exigir_texto(s, "sección", max_longitud=120) for s in secciones
        ]
        if not isinstance(contenido, dict):
            raise ErrorValidacion("El contenido del reporte debe ser un diccionario.")
        ruta = exigir_texto(ruta_destino, "ruta_destino", max_longitud=500)
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=tipo_enum,
            formato=formato_enum,
            titulo=titulo_limpio,
            secciones=secciones_limpias,
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta)

def _fecha_de_torneo(valor: object) -> date:
    """Normaliza la fecha de un torneo devuelta por el proveedor."""
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return date.fromisoformat(valor)
        except ValueError as error:
            raise ErrorValidacion(
                "El proveedor devolvió una fecha de torneo inválida."
            ) from error
    raise ErrorValidacion("El proveedor devolvió una fecha de torneo inválida.")

def _promedio(valores) -> float:
    """Promedio de una muestra; 0.0 sin datos (no se inventan valores)."""
    return float(fmean(valores)) if valores else 0.0

def _indice_global(
    proveedor: ProveedorDatosRendimiento,
    id_atleta: int,
    desde: date,
    hasta: date,
) -> float:
    """Índice Global de Rendimiento, escala 0–100.

 Definición: promedio de los cuatro indicadores de porcentaje del
 modelo — accuracy, cumplimiento del entrenamiento, asistencia y
 cumplimiento de objetivos SMART. El modelo oficial no trae una
 fórmula para el IGR.
 """
    return _promedio(
        [
            proveedor.accuracy_promedio(id_atleta, desde, hasta),
            _valor_indicador(
                proveedor,
                TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
                id_atleta,
                desde,
                hasta,
            ),
            proveedor.porcentaje_asistencia(id_atleta, desde, hasta),
            proveedor.cumplimiento_objetivos(id_atleta, desde, hasta),
        ]
    )

@dataclass
class GenerarReporteIndividualAtleta:
    """reporte individual del atleta en PDF o Excel.

 Compone con datos reales los seis contenidos del reporte: perfil del
 atleta, evolución del rating, estadísticas de partidas, historial de
 torneos, rendimiento por aperturas y objetivos SMART.

 Notas de modelo:
 - El historial de torneos se deriva de los eventos de las partidas (el
 modelo oficial no tiene tabla de torneos) y sólo incluye los que se
 solapan con el periodo del reporte.
 - El atleta debe pertenecer al grupo del entrenador: no se
 genera un reporte silencioso de ceros para un atleta inexistente o ajeno.
 """

    servicio_reporte: ServicioGeneracionReportes
    proveedor: ProveedorDatosRendimiento
    repositorio_atletas: RepositorioAtletas

    SECCIONES_OBLIGATORIAS = [
        "Perfil del atleta",
        "Evolución del rating",
        "Estadísticas de partidas",
        "Historial de torneos",
        "Rendimiento por aperturas",
        "Objetivos SMART",
    ]

    def ejecutar(
        self,
        id_atleta: int,
        formato: FormatoReporte | str,
        ruta_destino: str,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        *,
        solicitante: Solicitante,
    ) -> str:
        exigir_entrenador(
            solicitante, "generar el reporte individual de un atleta"
        )
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        formato_enum = convertir_enum(FormatoReporte, formato, "formato")
        ruta = exigir_texto(ruta_destino, "ruta_destino", max_longitud=500)
        hoy = date.today()
        fin = hasta or hoy
        inicio = desde or date(fin.year, 1, 1)
        inicio, fin = _validar_periodo(inicio, fin)

        _grupo_del_entrenador(self.proveedor, solicitante.id_usuario, id_atleta)
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada(
                "No existe el expediente del atleta indicado."
            )

        victorias, tablas, derrotas = self.proveedor.resultados(
            id_atleta, inicio, fin
        )
        torneos = [
            {
                "evento": evento,
                "desde": _fecha_de_torneo(desde_t).isoformat(),
                "hasta": _fecha_de_torneo(hasta_t).isoformat(),
            }
            for evento, desde_t, hasta_t in self.proveedor.torneos_del_atleta(
                id_atleta
            )
            if _fecha_de_torneo(desde_t) <= fin
            and _fecha_de_torneo(hasta_t) >= inicio
        ]
        aperturas = [
            {"codigo": eco, "nombre": nombre, "porcentaje": porcentaje}
            for eco, nombre, porcentaje in self.proveedor.rendimiento_por_apertura(
                id_atleta, inicio, fin
            )
        ]

        contenido = {
            "id_atleta": id_atleta,
            "periodo": {"desde": inicio.isoformat(), "hasta": fin.isoformat()},
            "perfil": {
                "nombre": atleta.nombre,
                "edad": atleta.edad(),
                "sexo": atleta.sexo,
                "federacion": atleta.federacion,
                "categorias": list(atleta.categorias),
                "clubs": list(atleta.clubs),
                "rating_clasicas": atleta.rating_actual.clasicas,
                "rating_rapidas": atleta.rating_actual.rapidas,
                "rating_blitz": atleta.rating_actual.blitz,
            },
            "evolucion_rating": {
                "rating_actual": self.proveedor.rating_fide(id_atleta, "clasicas"),
                "variacion_periodo": self.proveedor.variacion_rating(
                    id_atleta, inicio, fin
                ),
            },
            "estadisticas_partidas": {
                "partidas_jugadas": self.proveedor.partidas_jugadas(
                    id_atleta, inicio, fin
                ),
                "partidas_analizadas": self.proveedor.partidas_analizadas(
                    id_atleta, inicio, fin
                ),
                "accuracy": self.proveedor.accuracy_promedio(
                    id_atleta, inicio, fin
                ),
                "acpl": self.proveedor.acpl_promedio(id_atleta, inicio, fin),
                "blunders": self.proveedor.blunders_totales(
                    id_atleta, inicio, fin
                ),
                "victorias": victorias,
                "tablas": tablas,
                "derrotas": derrotas,
                "asistencia": self.proveedor.porcentaje_asistencia(
                    id_atleta, inicio, fin
                ),
            },
            "historial_torneos": torneos,
            "rendimiento_por_aperturas": aperturas,
            "objetivos_smart": {
                "cumplimiento": self.proveedor.cumplimiento_objetivos(
                    id_atleta, inicio, fin
                ),
                "no_cumplidos": self.proveedor.objetivos_no_cumplidos(id_atleta),
            },
        }
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.INDIVIDUAL,
            formato=formato_enum,
            titulo=f"Reporte Individual de {atleta.nombre}",
            secciones=list(self.SECCIONES_OBLIGATORIAS),
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta)

@dataclass
class GenerarReporteIntegralAtleta:
    """informe integral con las ocho secciones consolidadas.

 Cada sección se compone con datos reales del periodo (por defecto:
 año en curso) y el atleta debe pertenecer al grupo del entrenador.

 Limitación del modelo: "observaciones del entrenador" no tiene campo
 de captura en el esquema; la sección se mantiene en el informe y el
 contenido se expone vacío para que la capa de entrada lo rellene.
 """

    servicio_reporte: ServicioGeneracionReportes
    proveedor: ProveedorDatosRendimiento
    repositorio_atletas: RepositorioAtletas

    SECCIONES_OBLIGATORIAS = [
        "Datos personales",
        "Evolución del rating",
        "Historial de entrenamientos",
        "Resultados competitivos",
        "Estadísticas de partidas",
        "Rendimiento por apertura",
        "Cumplimiento de objetivos SMART",
        "Observaciones del entrenador",
    ]

    def ejecutar(
        self,
        id_atleta: int,
        formato: FormatoReporte | str,
        ruta_destino: str,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        *,
        solicitante: Solicitante,
    ) -> str:
        exigir_entrenador(solicitante, "generar el informe integral de un atleta")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        formato_enum = convertir_enum(FormatoReporte, formato, "formato")
        ruta = exigir_texto(ruta_destino, "ruta_destino", max_longitud=500)
        hoy = date.today()
        fin = hasta or hoy
        inicio = desde or date(fin.year, 1, 1)
        inicio, fin = _validar_periodo(inicio, fin)
        _grupo_del_entrenador(self.proveedor, solicitante.id_usuario, id_atleta)
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada(
                "No existe el expediente del atleta indicado."
            )

        victorias, tablas, derrotas = self.proveedor.resultados(
            id_atleta, inicio, fin
        )
        contenido = {
            "id_atleta": id_atleta,
            "rating_fide": self.proveedor.rating_fide(id_atleta, "clasicas"),
            "periodo": {"desde": inicio.isoformat(), "hasta": fin.isoformat()},
            "datos_personales": {
                "nombre": atleta.nombre,
                "edad": atleta.edad(),
                "sexo": atleta.sexo,
                "federacion": atleta.federacion,
                "categorias": list(atleta.categorias),
                "clubs": list(atleta.clubs),
                "rating_clasicas": atleta.rating_actual.clasicas,
                "rating_rapidas": atleta.rating_actual.rapidas,
                "rating_blitz": atleta.rating_actual.blitz,
            },
            "evolucion_rating": {
                "rating_actual": self.proveedor.rating_fide(
                    id_atleta, "clasicas"
                ),
                "variacion_periodo": self.proveedor.variacion_rating(
                    id_atleta, inicio, fin
                ),
            },
            "historial_entrenamientos": {
                "horas_planificadas": self.proveedor.horas_planificadas(
                    id_atleta, inicio, fin
                ),
                "horas_ejecutadas_aprobadas": self.proveedor.horas_entrenadas_aprobadas(
                    id_atleta, inicio, fin
                ),
                "cumplimiento_pct": _valor_indicador(
                    self.proveedor,
                    TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
                    id_atleta,
                    inicio,
                    fin,
                ),
            },
            "resultados_competitivos": {
                "victorias": victorias,
                "tablas": tablas,
                "derrotas": derrotas,
                "torneos_jugados": self.proveedor.torneos_jugados(
                    id_atleta, inicio, fin
                ),
                "asistencia_pct": self.proveedor.porcentaje_asistencia(
                    id_atleta, inicio, fin
                ),
            },
            "estadisticas_partidas": {
                "partidas_jugadas": self.proveedor.partidas_jugadas(
                    id_atleta, inicio, fin
                ),
                "partidas_analizadas": self.proveedor.partidas_analizadas(
                    id_atleta, inicio, fin
                ),
                "accuracy": self.proveedor.accuracy_promedio(
                    id_atleta, inicio, fin
                ),
                "acpl": self.proveedor.acpl_promedio(id_atleta, inicio, fin),
                "blunders": self.proveedor.blunders_totales(
                    id_atleta, inicio, fin
                ),
            },
            "rendimiento_por_apertura": [
                {"codigo": eco, "nombre": nombre, "porcentaje": porcentaje}
                for eco, nombre, porcentaje in (
                    self.proveedor.rendimiento_por_apertura(
                        id_atleta, inicio, fin
                    )
                )
            ],
            "objetivos_smart": {
                "cumplimiento": self.proveedor.cumplimiento_objetivos(
                    id_atleta, inicio, fin
                ),
                "no_cumplidos": self.proveedor.objetivos_no_cumplidos(
                    id_atleta
                ),
            },
            "observaciones_entrenador": "",
        }
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.INDIVIDUAL,
            formato=formato_enum,
            titulo="Informe Integral del Atleta",
            secciones=list(self.SECCIONES_OBLIGATORIAS),
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta)

@dataclass
class GenerarReporteGrupal:
    """reporte comparativo entre atletas, asistencia y cumplimiento.

 Los tres contenidos del informe se computan con datos reales del
 grupo para el periodo indicado (por defecto: año en curso).
 """

    servicio_reporte: ServicioGeneracionReportes
    proveedor: ProveedorDatosRendimiento

    SECCIONES_OBLIGATORIAS = [
        "Comparativo entre atletas",
        "Asistencia",
        "Cumplimiento del entrenamiento",
    ]

    def ejecutar(
        self,
        id_entrenador: int,
        formato: FormatoReporte | str,
        ruta_destino: str,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        *,
        solicitante: Solicitante,
    ) -> str:
        exigir_entrenador(solicitante, "generar reportes grupales")
        exigir_entero(id_entrenador, "id_entrenador", minimo=1)
        formato_enum = convertir_enum(FormatoReporte, formato, "formato")
        ruta = exigir_texto(ruta_destino, "ruta_destino", max_longitud=500)
        hoy = date.today()
        fin = hasta or hoy
        inicio = desde or date(fin.year, 1, 1)
        inicio, fin = _validar_periodo(inicio, fin)
        ids = [
            _id_de(a)
            for a in self.proveedor.atletas_por_entrenador(id_entrenador)
        ]
        comparativo = [
            {
                "id_atleta": id_atleta,
                "rating_fide": self.proveedor.rating_fide(id_atleta, "clasicas"),
                "accuracy": self.proveedor.accuracy_promedio(
                    id_atleta, inicio, fin
                ),
                "variacion_rating": self.proveedor.variacion_rating(
                    id_atleta, inicio, fin
                ),
            }
            for id_atleta in ids
        ]
        asistencia = {
            id_atleta: self.proveedor.porcentaje_asistencia(
                id_atleta, inicio, fin
            )
            for id_atleta in ids
        }
        cumplimiento = {
            id_atleta: _valor_indicador(
                self.proveedor,
                TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
                id_atleta,
                inicio,
                fin,
            )
            for id_atleta in ids
        }
        contenido = {
            "id_entrenador": id_entrenador,
            "periodo": {"desde": inicio.isoformat(), "hasta": fin.isoformat()},
            "cantidad_atletas": len(ids),
            "atletas": ids,
            "comparativo_entre_atletas": comparativo,
            "asistencia": {
                "por_atleta": asistencia,
                "promedio": _promedio(list(asistencia.values())),
            },
            "cumplimiento_entrenamiento": {
                "por_atleta": cumplimiento,
                "promedio": _promedio(list(cumplimiento.values())),
            },
        }
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.GRUPAL,
            formato=formato_enum,
            titulo="Reporte Grupal del Equipo",
            secciones=list(self.SECCIONES_OBLIGATORIAS),
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta)

@dataclass
class GenerarReporteInstitucional:
    """informes mensual, trimestral y anual.

 El contenido se computa sobre **todos** los atletas del sistema (la
 institución no depende de un entrenador) y la ventana corresponde al
 periodo en curso de la granularidad solicitada.

 Frecuencia: las tres cadencias se cubren así — mensual: este catálogo
 ``PeriodoInstitucional.MENSUAL``; semanal: los reportes
 ``desde``/``hasta`` con la ventana ISO de la semana
 (``GenerarReporte*``); y al finalizar cada torneo: ventana con las
 fechas del evento derivadas de las partidas.
 """

    servicio_reporte: ServicioGeneracionReportes
    proveedor: ProveedorDatosRendimiento

    SECCIONES_OBLIGATORIAS = [
        "Resumen del periodo",
        "Rendimiento del equipo",
        "Asistencia y cumplimiento",
        "Objetivos SMART",
    ]

    @staticmethod
    def _ventana(periodo: PeriodoInstitucional) -> tuple[date, date]:
        """Ventana en curso de la granularidad del informe."""
        hoy = date.today()
        if periodo == PeriodoInstitucional.MENSUAL:
            return date(hoy.year, hoy.month, 1), hoy
        if periodo == PeriodoInstitucional.TRIMESTRAL:
            primer_mes = 3 * ((hoy.month - 1) // 3) + 1
            return date(hoy.year, primer_mes, 1), hoy
        return date(hoy.year, 1, 1), hoy

    def ejecutar(
        self,
        periodo: PeriodoInstitucional | str,
        formato: FormatoReporte | str,
        ruta_destino: str,
        *,
        solicitante: Solicitante,
    ) -> str:
        exigir_entrenador(solicitante, "generar reportes institucionales")
        periodo_enum = convertir_enum(
            PeriodoInstitucional, periodo, "periodo_institucional"
        )
        formato_enum = convertir_enum(FormatoReporte, formato, "formato")
        ruta = exigir_texto(ruta_destino, "ruta_destino", max_longitud=500)
        inicio, fin = self._ventana(periodo_enum)
        ids = [_id_de(a) for a in self.proveedor.ids_atletas()]
        contenido = {
            "periodo": periodo_enum.value,
            "ventana": {"desde": inicio.isoformat(), "hasta": fin.isoformat()},
            "resumen_del_periodo": {
                "cantidad_atletas": len(ids),
                "partidas_jugadas": sum(
                    self.proveedor.partidas_jugadas(i, inicio, fin) for i in ids
                ),
                "torneos_jugados": sum(
                    self.proveedor.torneos_jugados(i, inicio, fin) for i in ids
                ),
            },
            "rendimiento_del_equipo": {
                "rating_promedio": _promedio(
                    [float(self.proveedor.rating_fide(i, "clasicas")) for i in ids]
                ),
                "accuracy_promedio": _promedio(
                    [self.proveedor.accuracy_promedio(i, inicio, fin) for i in ids]
                ),
            },
            "asistencia_y_cumplimiento": {
                "asistencia_promedio": _promedio(
                    [self.proveedor.porcentaje_asistencia(i, inicio, fin) for i in ids]
                ),
                "cumplimiento_promedio": _promedio(
                    [
                        _valor_indicador(
                            self.proveedor,
                            TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
                            i,
                            inicio,
                            fin,
                        )
                        for i in ids
                    ]
                ),
            },
            "objetivos_smart": {
                "cumplimiento_promedio": _promedio(
                    [self.proveedor.cumplimiento_objetivos(i, inicio, fin) for i in ids]
                ),
                "no_cumplidos": sum(
                    self.proveedor.objetivos_no_cumplidos(i) for i in ids
                ),
            },
        }
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.INSTITUCIONAL,
            formato=formato_enum,
            titulo=f"Informe {periodo_enum.value}",
            secciones=list(self.SECCIONES_OBLIGATORIAS),
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta)

MAX_PUNTOS_SERIE = 120

_FORMATOS_GRAFICO = (FormatoReporte.JSON, FormatoReporte.HTML)

def _periodos_de(
    inicio: date, fin: date, periodicidad: PeriodicidadGrafico
) -> List[tuple[str, date, date]]:
    """Divide el periodo en casillas (etiqueta, desde, hasta) de la serie."""
    casillas: List[tuple[str, date, date]] = []
    actual = inicio
    while actual <= fin:
        if periodicidad == PeriodicidadGrafico.SEMANAL:
            cierre = min(actual + timedelta(days=6), fin)
            etiqueta = f"sem {actual.strftime('%d-%m-%y')}"
        elif periodicidad == PeriodicidadGrafico.MENSUAL:
            if actual.month == 12:
                cierre = min(date(actual.year, 12, 31), fin)
            else:
                cierre = min(
                    date(actual.year, actual.month + 1, 1) - timedelta(days=1),
                    fin,
                )
            etiqueta = actual.strftime("%Y-%m")
        else:
            cierre = min(date(actual.year, 12, 31), fin)
            etiqueta = str(actual.year)
        casillas.append((etiqueta, actual, cierre))
        if len(casillas) > MAX_PUNTOS_SERIE:
            raise ErrorValidacion(
                f"El rango produce más de {MAX_PUNTOS_SERIE} puntos para "
                f"periodicidad {periodicidad.value}; use un rango menor o una "
                "periodicidad menos fina."
            )
        actual = cierre + timedelta(days=1)
    return casillas

@dataclass
class GenerarGraficoTendencias:
    """ (medida provisional): gráfico interactivo de tendencias.

 Mientras no exista la capa de frontend, el backend genera el artefacto
 directamente: ``JSON`` con la serie lista para cualquier librería de
 gráficos y ``HTML`` con un gráfico interactivo autocontenido (SVG +
 JavaScript nativo, sin dependencias externas). El frontend real consumirá
 la misma serie cuando se construya.
 """

    proveedor: ProveedorDatosRendimiento
    servicio_reporte: ServicioGeneracionReportes

    def ejecutar(
        self,
        id_atleta: int,
        tipo: TipoIndicador | str,
        periodicidad: PeriodicidadGrafico | str,
        desde: date,
        hasta: date,
        formato: FormatoReporte | str,
        ruta_destino: str,
        *,
        solicitante: Solicitante,
    ) -> str:
        exigir_entrenador(solicitante, "generar gráficos de tendencias")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        tipo_enum = convertir_enum(TipoIndicador, tipo, "tipo")
        periodicidad_enum = convertir_enum(
            PeriodicidadGrafico, periodicidad, "periodicidad"
        )
        formato_enum = convertir_enum(FormatoReporte, formato, "formato")
        if formato_enum not in _FORMATOS_GRAFICO:
            raise ErrorValidacion(
                "El gráfico de tendencias se exporta en JSON o HTML."
            )
        inicio, fin = _validar_periodo(desde, hasta)
        ruta = exigir_texto(ruta_destino, "ruta_destino", max_longitud=500)

        _grupo_del_entrenador(
            self.proveedor, solicitante.id_usuario, id_atleta
        )

        puntos = [
            PuntoSerie(
                etiqueta=etiqueta,
                desde=caso_desde,
                hasta=caso_hasta,
                valor=_valor_indicador(
                    self.proveedor, tipo_enum, id_atleta, caso_desde, caso_hasta
                ),
            )
            for etiqueta, caso_desde, caso_hasta in _periodos_de(
                inicio, fin, periodicidad_enum
            )
        ]
        valores = [p.valor for p in puntos]
        contenido = {
            "id_atleta": id_atleta,
            "indicador": tipo_enum.value,
            "periodicidad": periodicidad_enum.value,
            "desde": inicio.isoformat(),
            "hasta": fin.isoformat(),
            "series": [
                {
                    "etiqueta": p.etiqueta,
                    "desde": p.desde.isoformat(),
                    "hasta": p.hasta.isoformat(),
                    "valor": p.valor,
                }
                for p in puntos
            ],
            "resumen": {
                "puntos": len(puntos),
                "minimo": min(valores),
                "maximo": max(valores),
                "promedio": fmean(valores),
                "variacion": valores[-1] - valores[0],
            },
        }
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.INDIVIDUAL,
            formato=formato_enum,
            titulo=f"Tendencia {tipo_enum.value} ({periodicidad_enum.value})",
            secciones=["Serie de tendencia", "Resumen"],
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta)

@dataclass
class GenerarGraficoRendimiento:
    """catálogo de gráficos de rendimiento y ELO.

 Los siete gráficos comparten un mismo artefacto (``JSON`` con la serie
 lista o ``HTML`` interactivo autocontenido con plantilla):

 - Series temporales (evolución del rating, del accuracy, de las horas
 de entrenamiento y del Índice Global de Rendimiento): una casilla
 por ``periodicidad``.
 - Rendimiento por torneo: un punto por evento solapado con el periodo
 (porcentaje de puntos conseguidos).
 - Distribución de resultados: victorias, tablas y derrotas en
 porcentaje del total.
 - Comparación entre atletas: el IGR de cada atleta del grupo del
 entrenador solicitante (no recibe ``id_atleta``).

 Notas de modelo:
 - El IGR no trae fórmula oficial: se define como promedio de accuracy,
 cumplimiento del entrenamiento, asistencia y cumplimiento de
 objetivos SMART (ver ``_indice_global``).
 - La evolución del rating se reconstruye con los snapshots históricos
 (rating actual menos la variación desde el inicio de cada casilla);
 sin historial la variación es 0.0 y la serie queda en el rating
 actual (no se inventan valores).
 - Sin torneos en el periodo la serie sale vacía con resumen en cero
 (no se inventan eventos).
 """

    proveedor: ProveedorDatosRendimiento
    servicio_reporte: ServicioGeneracionReportes

    SERIE_TEMPORAL = (
        TipoGraficoRendimiento.EVOLUCION_RATING,
        TipoGraficoRendimiento.EVOLUCION_ACCURACY,
        TipoGraficoRendimiento.HORAS_ENTRENAMIENTO,
        TipoGraficoRendimiento.EVOLUCION_INDICE_GLOBAL,
    )

    TITULOS = {
        TipoGraficoRendimiento.EVOLUCION_RATING: "Evolución del rating",
        TipoGraficoRendimiento.EVOLUCION_ACCURACY: "Evolución del accuracy",
        TipoGraficoRendimiento.HORAS_ENTRENAMIENTO: "Horas de entrenamiento",
        TipoGraficoRendimiento.RENDIMIENTO_POR_TORNEO: "Rendimiento por torneo",
        TipoGraficoRendimiento.DISTRIBUCION_RESULTADOS: "Distribución de resultados",
        TipoGraficoRendimiento.COMPARACION_ENTRE_ATLETAS: "Comparación entre atletas",
        TipoGraficoRendimiento.EVOLUCION_INDICE_GLOBAL: (
            "Evolución del Índice Global de Rendimiento"
        ),
    }

    def ejecutar(
        self,
        tipo: TipoGraficoRendimiento | str,
        id_atleta: Optional[int],
        formato: FormatoReporte | str,
        ruta_destino: str,
        desde: date,
        hasta: date,
        *,
        periodicidad: PeriodicidadGrafico | str = PeriodicidadGrafico.MENSUAL,
        solicitante: Solicitante,
    ) -> str:
        exigir_entrenador(solicitante, "generar gráficos de rendimiento")
        tipo_enum = convertir_enum(TipoGraficoRendimiento, tipo, "tipo_grafico")
        formato_enum = convertir_enum(FormatoReporte, formato, "formato")
        if formato_enum not in _FORMATOS_GRAFICO:
            raise ErrorValidacion(
                "Los gráficos de rendimiento se exportan en JSON o HTML."
            )
        inicio, fin = _validar_periodo(desde, hasta)
        ruta = exigir_texto(ruta_destino, "ruta_destino", max_longitud=500)
        comparacion = (
            tipo_enum == TipoGraficoRendimiento.COMPARACION_ENTRE_ATLETAS
        )
        if comparacion:
            if id_atleta is not None:
                raise ErrorValidacion(
                    "La comparación entre atletas trabaja sobre el grupo del "
                    "entrenador y no acepta un atleta concreto."
                )
        else:
            exigir_entero(id_atleta, "id_atleta", minimo=1)

            _grupo_del_entrenador(
                self.proveedor, solicitante.id_usuario, id_atleta
            )
        periodicidad_enum = convertir_enum(
            PeriodicidadGrafico, periodicidad, "periodicidad"
        )

        puntos = self._puntos(
            tipo_enum, id_atleta, inicio, fin, periodicidad_enum, comparacion,
            solicitante,
        )
        valores = [p.valor for p in puntos]
        contenido = {
            "id_atleta": id_atleta,
            "grafico": tipo_enum.value,

            "indicador": tipo_enum.value,
            "periodicidad": periodicidad_enum.value,
            "desde": inicio.isoformat(),
            "hasta": fin.isoformat(),
            "series": [
                {
                    "etiqueta": p.etiqueta,
                    "desde": p.desde.isoformat(),
                    "hasta": p.hasta.isoformat(),
                    "valor": p.valor,
                }
                for p in puntos
            ],
            "resumen": {
                "puntos": len(puntos),
                "minimo": min(valores) if valores else 0.0,
                "maximo": max(valores) if valores else 0.0,
                "promedio": fmean(valores) if valores else 0.0,
                "variacion": (
                    valores[-1] - valores[0] if len(valores) > 1 else 0.0
                ),
            },
        }
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.GRUPAL if comparacion else TipoReporte.INDIVIDUAL,
            formato=formato_enum,
            titulo=self.TITULOS[tipo_enum],
            secciones=["Datos del gráfico", "Resumen"],
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta)

    def _puntos(
        self,
        tipo: TipoGraficoRendimiento,
        id_atleta: Optional[int],
        inicio: date,
        fin: date,
        periodicidad: PeriodicidadGrafico,
        comparacion: bool,
        solicitante: Solicitante,
    ) -> List[PuntoSerie]:
        if comparacion:
            puntos = []
            for atleta in self.proveedor.atletas_por_entrenador(
                solicitante.id_usuario
            ):
                id_a = _id_de(atleta)
                etiqueta = getattr(atleta, "nombre", None) or f"Atleta {id_a}"
                puntos.append(
                    PuntoSerie(
                        etiqueta=etiqueta,
                        desde=inicio,
                        hasta=fin,
                        valor=_indice_global(
                            self.proveedor, id_a, inicio, fin
                        ),
                    )
                )
            return puntos
        if tipo == TipoGraficoRendimiento.RENDIMIENTO_POR_TORNEO:
            puntos = []
            for evento, desde_t, hasta_t in self.proveedor.torneos_del_atleta(
                id_atleta
            ):
                evento_desde = _fecha_de_torneo(desde_t)
                evento_hasta = _fecha_de_torneo(hasta_t)
                if evento_hasta < inicio or evento_desde > fin:
                    continue
                corte_inicio = max(evento_desde, inicio)
                corte_fin = min(evento_hasta, fin)
                victorias, tablas, derrotas = self.proveedor.resultados(
                    id_atleta, corte_inicio, corte_fin
                )
                total = victorias + tablas + derrotas
                puntos.append(
                    PuntoSerie(
                        etiqueta=evento,
                        desde=corte_inicio,
                        hasta=corte_fin,
                        valor=(
                            ((victorias + 0.5 * tablas) / total) * 100
                            if total
                            else 0.0
                        ),
                    )
                )
            return puntos
        if tipo == TipoGraficoRendimiento.DISTRIBUCION_RESULTADOS:
            victorias, tablas, derrotas = self.proveedor.resultados(
                id_atleta, inicio, fin
            )
            total = victorias + tablas + derrotas

            def _pct(cantidad: int) -> float:
                return (cantidad / total) * 100 if total else 0.0

            return [
                PuntoSerie("Victorias", inicio, fin, _pct(victorias)),
                PuntoSerie("Tablas", inicio, fin, _pct(tablas)),
                PuntoSerie("Derrotas", inicio, fin, _pct(derrotas)),
            ]

        hoy = date.today()
        puntos = []
        for etiqueta, caso_desde, caso_hasta in _periodos_de(
            inicio, fin, periodicidad
        ):
            puntos.append(
                PuntoSerie(
                    etiqueta=etiqueta,
                    desde=caso_desde,
                    hasta=caso_hasta,
                    valor=self._valor_de_serie(
                        tipo, id_atleta, caso_desde, caso_hasta, hoy
                    ),
                )
            )
        return puntos

    def _valor_de_serie(
        self,
        tipo: TipoGraficoRendimiento,
        id_atleta: int,
        desde: date,
        hasta: date,
        hoy: date,
    ) -> float:
        if tipo == TipoGraficoRendimiento.EVOLUCION_RATING:

            return float(
                self.proveedor.rating_fide(id_atleta, "clasicas")
                - self.proveedor.variacion_rating(id_atleta, desde, hoy)
            )
        if tipo == TipoGraficoRendimiento.EVOLUCION_ACCURACY:
            return self.proveedor.accuracy_promedio(id_atleta, desde, hasta)
        if tipo == TipoGraficoRendimiento.HORAS_ENTRENAMIENTO:
            return self.proveedor.horas_entrenadas_aprobadas(
                id_atleta, desde, hasta
            )
        return _indice_global(self.proveedor, id_atleta, desde, hasta)

@dataclass
class GenerarTablaDetallada:
    """tablas detalladas exportables (PDF, Excel o JSON).

 Las siete tablas se componen con datos reales del
 periodo y se exportan como ``columnas`` + ``filas`` para que el
 adaptador dibuje la tabla (PDF/Excel) o la entregue estructurada
 (JSON). El HTML queda fuera: la plantilla autocontenida es un gráfico
 de series, no una tabla.

 - Las tablas individuales exigen que el atleta pertenezca al grupo del
 entrenador solicitante; ``RANKING_EQUIPO`` trabaja sobre el
 grupo del entrenador y no recibe ``id_atleta``.
 - Sesiones y objetivos no guardan ventana propia: las sesiones se
 filtran por año del plan y los objetivos por solape con el periodo
 (criterio ya documentado en el proveedor SQLite).
 - La asistencia se reporta mes a mes (mensual); el ranking se ordena
 por IGR descendente y, a igualdad, por id.
 """

    servicio_reporte: ServicioGeneracionReportes
    proveedor: ProveedorDatosRendimiento
    repositorio_partidas: RepositorioPartidas
    repositorio_entrenamientos: RepositorioEntrenamientos
    repositorio_objetivos: RepositorioObjetivos

    FORMATOS = (FormatoReporte.PDF, FormatoReporte.EXCEL, FormatoReporte.JSON)

    TABLAS_INDIVIDUALES = (
        TipoTablaDetallada.HISTORIAL_PARTIDAS,
        TipoTablaDetallada.REGISTRO_ENTRENAMIENTOS,
        TipoTablaDetallada.OBJETIVOS_SMART,
        TipoTablaDetallada.ESTADISTICAS_POR_APERTURA,
        TipoTablaDetallada.ESTADISTICAS_POR_TORNEO,
        TipoTablaDetallada.REPORTES_ASISTENCIA,
    )

    TITULOS = {
        TipoTablaDetallada.HISTORIAL_PARTIDAS: "Historial de partidas",
        TipoTablaDetallada.REGISTRO_ENTRENAMIENTOS: "Registro de entrenamientos",
        TipoTablaDetallada.OBJETIVOS_SMART: "Objetivos SMART",
        TipoTablaDetallada.ESTADISTICAS_POR_APERTURA: "Estadísticas por apertura",
        TipoTablaDetallada.ESTADISTICAS_POR_TORNEO: "Estadísticas por torneo",
        TipoTablaDetallada.RANKING_EQUIPO: "Ranking del equipo",
        TipoTablaDetallada.REPORTES_ASISTENCIA: "Reportes de asistencia",
    }

    def ejecutar(
        self,
        tabla: TipoTablaDetallada | str,
        id_atleta: Optional[int],
        formato: FormatoReporte | str,
        ruta_destino: str,
        desde: date,
        hasta: date,
        *,
        solicitante: Solicitante,
    ) -> str:
        exigir_entrenador(solicitante, "generar tablas detalladas")
        tabla_enum = convertir_enum(TipoTablaDetallada, tabla, "tabla")
        formato_enum = convertir_enum(FormatoReporte, formato, "formato")
        if formato_enum not in self.FORMATOS:
            raise ErrorValidacion(
                "Las tablas detalladas se exportan en PDF, Excel o JSON."
            )
        inicio, fin = _validar_periodo(desde, hasta)
        ruta = exigir_texto(ruta_destino, "ruta_destino", max_longitud=500)
        grupal = tabla_enum == TipoTablaDetallada.RANKING_EQUIPO
        if grupal:
            if id_atleta is not None:
                raise ErrorValidacion(
                    "El ranking del equipo trabaja sobre el grupo del "
                    "entrenador y no acepta un atleta concreto."
                )
        else:
            exigir_entero(id_atleta, "id_atleta", minimo=1)
            _grupo_del_entrenador(
                self.proveedor, solicitante.id_usuario, id_atleta
            )

        columnas, filas = self._tabla(
            tabla_enum, id_atleta, inicio, fin, solicitante
        )
        contenido = {
            "tabla": tabla_enum.value,
            "periodo": {"desde": inicio.isoformat(), "hasta": fin.isoformat()},
            "columnas": columnas,
            "filas": filas,
            "total_filas": len(filas),
        }
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.GRUPAL if grupal else TipoReporte.INDIVIDUAL,
            formato=formato_enum,
            titulo=self.TITULOS[tabla_enum],
            secciones=[self.TITULOS[tabla_enum]],
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta)

    def _tabla(
        self,
        tabla: TipoTablaDetallada,
        id_atleta: Optional[int],
        inicio: date,
        fin: date,
        solicitante: Solicitante,
    ) -> tuple[List[str], List[list]]:
        if tabla == TipoTablaDetallada.HISTORIAL_PARTIDAS:
            columnas = [
                "fecha", "evento", "rivales", "color", "resultado",
                "apertura", "puntos",
            ]
            partidas = sorted(
                self.repositorio_partidas.listar_por_periodo(
                    id_atleta, inicio, fin
                ),
                key=lambda p: p.fecha,
            )
            filas = [
                [
                    p.fecha.isoformat(),
                    p.evento,
                    f"{p.jugador_blancas} vs {p.jugador_negras}",
                    p.color_atleta.value if p.color_atleta else "",
                    p.resultado.value,
                    p.apertura_eco,
                    p.puntos_obtenidos(),
                ]
                for p in partidas
            ]
            return columnas, filas

        if tabla == TipoTablaDetallada.REGISTRO_ENTRENAMIENTOS:
            columnas = [
                "anio", "semana", "dia", "tipo", "horas_planificadas",
                "horas_ejecutadas", "estado", "aprobada",
            ]
            filas: List[list] = []
            planes = sorted(
                self.repositorio_entrenamientos.listar_por_atleta(id_atleta),
                key=lambda p: (p.anio, p.semana),
            )
            for plan in planes:

                if plan.anio < inicio.year or plan.anio > fin.year:
                    continue
                for sesion in plan.sesiones:
                    filas.append(
                        [
                            plan.anio,
                            plan.semana,
                            sesion.dia_semana,
                            sesion.tipo.value,
                            sesion.horas_planificadas,
                            (
                                sesion.horas_ejecutadas
                                if sesion.horas_ejecutadas is not None
                                else ""
                            ),
                            sesion.estado.value,
                            "SI" if sesion.ejecucion_aprobada else "NO",
                        ]
                    )
            return columnas, filas

        if tabla == TipoTablaDetallada.OBJETIVOS_SMART:
            columnas = [
                "descripcion", "indicador_meta", "valor_meta", "fecha_inicio",
                "fecha_limite", "avance_pct", "estado", "cumplido",
            ]
            objetivos = sorted(
                self.repositorio_objetivos.buscar_por_atleta(id_atleta),
                key=lambda o: (o.fecha_inicio, o.id),
            )
            filas = [
                [
                    o.descripcion,
                    o.indicador_meta.value,
                    o.valor_meta,
                    o.fecha_inicio.isoformat(),
                    o.fecha_limite.isoformat(),
                    o.porcentaje_avance,
                    o.estado.value,
                    "SI" if o.cumplido_por_entrenador else "NO",
                ]
                for o in objetivos
                if o.fecha_inicio <= fin and o.fecha_limite >= inicio
            ]
            return columnas, filas

        if tabla == TipoTablaDetallada.ESTADISTICAS_POR_APERTURA:
            return (
                ["codigo", "nombre", "porcentaje"],
                [
                    [eco, nombre, porcentaje]
                    for eco, nombre, porcentaje in (
                        self.proveedor.rendimiento_por_apertura(
                            id_atleta, inicio, fin
                        )
                    )
                ],
            )

        if tabla == TipoTablaDetallada.ESTADISTICAS_POR_TORNEO:
            columnas = [
                "evento", "desde", "hasta", "partidas", "victorias",
                "tablas", "derrotas", "puntos_pct",
            ]
            filas = []
            for evento, desde_t, hasta_t in self.proveedor.torneos_del_atleta(
                id_atleta
            ):
                evento_desde = _fecha_de_torneo(desde_t)
                evento_hasta = _fecha_de_torneo(hasta_t)
                if evento_hasta < inicio or evento_desde > fin:
                    continue
                corte_inicio = max(evento_desde, inicio)
                corte_fin = min(evento_hasta, fin)
                victorias, tablas, derrotas = self.proveedor.resultados(
                    id_atleta, corte_inicio, corte_fin
                )
                total = victorias + tablas + derrotas
                filas.append(
                    [
                        evento,
                        corte_inicio.isoformat(),
                        corte_fin.isoformat(),
                        total,
                        victorias,
                        tablas,
                        derrotas,
                        (
                            ((victorias + 0.5 * tablas) / total) * 100
                            if total
                            else 0.0
                        ),
                    ]
                )
            return columnas, filas

        if tabla == TipoTablaDetallada.REPORTES_ASISTENCIA:
            columnas = ["periodo", "desde", "hasta", "asistencia_pct"]
            filas = [
                [
                    etiqueta,
                    caso_desde.isoformat(),
                    caso_hasta.isoformat(),
                    self.proveedor.porcentaje_asistencia(
                        id_atleta, caso_desde, caso_hasta
                    ),
                ]
                for etiqueta, caso_desde, caso_hasta in _periodos_de(
                    inicio, fin, PeriodicidadGrafico.MENSUAL
                )
            ]
            return columnas, filas

        columnas = [
            "posicion", "id_atleta", "atleta", "rating_fide", "accuracy",
            "asistencia_pct", "indice_global",
        ]
        filas = []
        for atleta in self.proveedor.atletas_por_entrenador(
            solicitante.id_usuario
        ):
            id_a = _id_de(atleta)
            etiqueta = getattr(atleta, "nombre", None) or f"Atleta {id_a}"
            filas.append(
                (
                    _indice_global(self.proveedor, id_a, inicio, fin),
                    id_a,
                    etiqueta,
                    float(self.proveedor.rating_fide(id_a, "clasicas")),
                    self.proveedor.accuracy_promedio(id_a, inicio, fin),
                    self.proveedor.porcentaje_asistencia(id_a, inicio, fin),
                )
            )
        filas.sort(key=lambda f: (-f[0], f[1]))
        return columnas, [
            [posicion, id_a, etiqueta, rating, accuracy, asistencia, igr]
            for posicion, (igr, id_a, etiqueta, rating, accuracy, asistencia) in (
                enumerate(filas, start=1)
            )
        ]

__all__ = [
    "CalcularIndicadoresPrincipales",
    "CalcularIndicadoresSecundarios",
    "ConsultarIndicadoresPermanentes",
    "CompararConGrupo",
    "CompararConPares",
    "CompararTendencias",
    "CompararTendenciasPeriodicas",
    "EvaluadorRangos",
    "GenerarDashboardAtleta",
    "GenerarDashboardEntrenador",
    "GenerarGraficoRendimiento",
    "GenerarGraficoTendencias",
    "GenerarReporte",
    "PeriodicidadGrafico",
    "PeriodicidadTendencia",
    "GenerarReporteGrupal",
    "GenerarReporteIndividualAtleta",
    "GenerarReporteInstitucional",
    "GenerarReporteIntegralAtleta",
    "GenerarTablaDetallada",
    "RANGOS_POR_DEFECTO",
    "TIPOS_COMPARABLES",
    "TIPOS_COMPARACION_GRUPO",
    "TipoGraficoRendimiento",
    "TipoTablaDetallada",
    "ventanas_de_periodo",
]
