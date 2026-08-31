"""Casos de uso (puertos primarios / driving) del módulo de Indicadores."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Dict, List, Optional

from ..comun.errores import EntidadNoEncontrada, ErrorValidacion
from ..comun.ids import nuevo_id_entero
from ..usuarios.entidades import Rol
from .entidades import (
    Alerta,
    DashboardAtleta,
    DashboardEntrenador,
    EstadoAlerta,
    FormatoReporte,
    IndicadorRendimiento,
    PeriodoInstitucional,
    RangoEvaluacion,
    Reporte,
    TendenciaComparada,
    TipoAlerta,
    TipoIndicador,
    TipoReporte,
)
from .puertos import (
    ProveedorDatosRendimiento,
    ProveedorRangosEvaluacion,
    RepositorioIndicadores,
    ServicioGeneracionReportes,
)

# Rangos de evaluación por defecto (RNF-07.2: configurables, con valores en el
# dominio). Cada valor límite representa el piso del rango.
RANGOS_POR_DEFECTO: dict[TipoIndicador, tuple[float, float, float]] = {
    TipoIndicador.ACCURACY: (85, 75, 60),
    TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO: (90, 75, 50),
    TipoIndicador.CUMPLIMIENTO_OBJETIVOS: (90, 75, 50),
    TipoIndicador.ASISTENCIA: (90, 75, 50),
    TipoIndicador.RENDIMIENTO_EN_FINALES: (70, 55, 40),
    TipoIndicador.RENDIMIENTO_POR_APERTURA: (70, 55, 40),
    TipoIndicador.RATING_FIDE: (2000, 1800, 1600),
    TipoIndicador.VARIACION_RATING: (20, 0, -20),
    TipoIndicador.PORCENTAJE_RESULTADOS: (70, 50, 30),
    TipoIndicador.ACPL: (30, 50, 70),
    TipoIndicador.BLUNDERS: (1, 3, 5),
}

# Indicadores "menor es mejor": el valor del rango se interpreta como tope.
_INDICADORES_MENOR_ES_MEJOR = frozenset(
    {TipoIndicador.ACPL, TipoIndicador.BLUNDERS}
)

# Tipos comparables con los datos disponibles del proveedor (RF-09.6/RF-11.4).
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
]


@dataclass
class EvaluadorRangos:
    """RNF-07.2: aplica la configuración de rangos o los valores por defecto."""

    proveedor_configuracion: Optional[ProveedorRangosEvaluacion] = None

    def evaluar(self, tipo: TipoIndicador, valor: float) -> RangoEvaluacion:
        rangos = self._obtener_rangos(tipo)
        if rangos is None:
            return RangoEvaluacion.ACEPTABLE
        excelente, bueno, aceptable = rangos
        if tipo in _INDICADORES_MENOR_ES_MEJOR:
            if valor <= excelente:
                return RangoEvaluacion.EXCELENTE
            if valor <= bueno:
                return RangoEvaluacion.BUENO
            if valor <= aceptable:
                return RangoEvaluacion.ACEPTABLE
            return RangoEvaluacion.REQUIERE_INTERVENCION
        if valor >= excelente:
            return RangoEvaluacion.EXCELENTE
        if valor >= bueno:
            return RangoEvaluacion.BUENO
        if valor >= aceptable:
            return RangoEvaluacion.ACEPTABLE
        return RangoEvaluacion.REQUIERE_INTERVENCION

    def _obtener_rangos(
        self, tipo: TipoIndicador
    ) -> Optional[tuple[float, float, float]]:
        if self.proveedor_configuracion is not None:
            configurados = self.proveedor_configuracion.rangos(tipo)
            if configurados is not None:
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
        return IndicadorRendimiento(
            id=nuevo_id_entero(),
            id_atleta=id_atleta,
            tipo=tipo,
            valor=valor,
            rango_evaluacion=self.evaluador.evaluar(tipo, valor),
            periodo_inicio=desde,
            periodo_fin=hasta,
        )

    def _persistir(
        self, indicadores: List[IndicadorRendimiento]
    ) -> List[IndicadorRendimiento]:
        for indicador in indicadores:
            self.repositorio.guardar(indicador)
        return indicadores


@dataclass
class CalcularIndicadoresPrincipales(_BaseCalculoIndicadores):
    """RF-09.1: métricas principales de rendimiento."""

    def ejecutar(
        self, id_atleta: str, desde: date, hasta: date
    ) -> List[IndicadorRendimiento]:
        indicadores: List[IndicadorRendimiento] = [
            self._crear(
                id_atleta,
                TipoIndicador.ACCURACY,
                self.proveedor.accuracy_promedio(id_atleta, desde, hasta),
                desde,
                hasta,
            ),
            self._crear(
                id_atleta,
                TipoIndicador.ACPL,
                self.proveedor.acpl_promedio(id_atleta, desde, hasta),
                desde,
                hasta,
            ),
            self._crear(
                id_atleta,
                TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
                self._calcular_cumplimiento(id_atleta, desde, hasta),
                desde,
                hasta,
            ),
            self._crear(
                id_atleta,
                TipoIndicador.CUMPLIMIENTO_OBJETIVOS,
                self.proveedor.cumplimiento_objetivos(id_atleta, desde, hasta),
                desde,
                hasta,
            ),
            self._crear(
                id_atleta,
                TipoIndicador.PORCENTAJE_RESULTADOS,
                self._porcentaje_resultados(id_atleta, desde, hasta),
                desde,
                hasta,
            ),
            self._crear(
                id_atleta,
                TipoIndicador.BLUNDERS,
                float(self.proveedor.blunders_totales(id_atleta, desde, hasta)),
                desde,
                hasta,
            ),
            self._crear(
                id_atleta,
                TipoIndicador.RATING_FIDE,
                float(self.proveedor.rating_fide(id_atleta, "clasicas")),
                desde,
                hasta,
            ),
        ]
        return self._persistir(indicadores)

    def _calcular_cumplimiento(
        self, id_atleta: str, desde: date, hasta: date
    ) -> float:
        planificadas = self.proveedor.horas_planificadas(id_atleta, desde, hasta)
        if planificadas <= 0:
            return 0.0
        ejecutadas = self.proveedor.horas_entrenadas_aprobadas(
            id_atleta, desde, hasta
        )
        return (ejecutadas / planificadas) * 100

    def _porcentaje_resultados(
        self, id_atleta: str, desde: date, hasta: date
    ) -> float:
        victorias, tablas, derrotas = self.proveedor.resultados(
            id_atleta, desde, hasta
        )
        total = victorias + tablas + derrotas
        if total == 0:
            return 0.0
        return ((victorias + 0.5 * tablas) / total) * 100


@dataclass
class CalcularIndicadoresSecundarios(_BaseCalculoIndicadores):
    """RF-09.2: métricas secundarias de actividad."""

    def ejecutar(
        self, id_atleta: str, desde: date, hasta: date
    ) -> List[IndicadorRendimiento]:
        indicadores: List[IndicadorRendimiento] = [
            self._crear(
                id_atleta,
                TipoIndicador.EJERCICIOS_TACTICOS_RESUELTOS,
                float(
                    self.proveedor.ejercicios_tacticos_resueltos(
                        id_atleta, desde, hasta
                    )
                ),
                desde,
                hasta,
            ),
            self._crear(
                id_atleta,
                TipoIndicador.PARTIDAS_ANALIZADAS,
                float(self.proveedor.partidas_analizadas(id_atleta, desde, hasta)),
                desde,
                hasta,
            ),
            self._crear(
                id_atleta,
                TipoIndicador.ASISTENCIA,
                self.proveedor.porcentaje_asistencia(id_atleta, desde, hasta),
                desde,
                hasta,
            ),
            self._crear(
                id_atleta,
                TipoIndicador.PARTICIPACION_TORNEOS,
                float(self.proveedor.torneos_jugados(id_atleta, desde, hasta)),
                desde,
                hasta,
            ),
        ]
        return self._persistir(indicadores)


@dataclass
class GenerarDashboardEntrenador:
    """RF-11.1: vista consolidada del equipo con alertas automáticas."""

    repositorio: RepositorioIndicadores
    proveedor: ProveedorDatosRendimiento

    def ejecutar(self, id_entrenador: str) -> DashboardEntrenador:
        atletas = self.proveedor.atletas_por_entrenador(id_entrenador)
        alertas = self._detectar_alertas(atletas)
        dashboard = DashboardEntrenador(
            resumen_equipo={"total_atletas": len(atletas)},
            atletas_activos=len([a for a in atletas if getattr(a, "activo", True)]),
            alertas=alertas,
        )
        return self.repositorio.guardar_dashboard_entrenador(dashboard)

    def _detectar_alertas(self, atletas: list) -> List[Alerta]:
        """RF-09.3: alertas automáticas cuando un indicador cae en
        'Requiere Intervención'."""
        alertas: List[Alerta] = []
        for atleta in atletas:
            id_atleta = getattr(atleta, "id", "")
            indicadores = self.repositorio.listar_por_atleta(id_atleta)
            for indicador in indicadores:
                if indicador.rango_evaluacion == RangoEvaluacion.REQUIERE_INTERVENCION:
                    alertas.append(
                        Alerta(
                            id=nuevo_id("alerta"),
                            tipo=self._tipo_alerta(indicador.tipo),
                            id_atleta=id_atleta,
                            fecha_generacion=datetime.now(timezone.utc),
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


@dataclass
class GenerarDashboardAtleta:
    """RF-11.2: vista personal con KPIs tipo semáforo."""

    repositorio: RepositorioIndicadores
    proveedor: ProveedorDatosRendimiento

    def ejecutar(self, id_atleta: str, desde: date, hasta: date) -> DashboardAtleta:
        indicadores = self.repositorio.listar_por_periodo(id_atleta, desde, hasta)
        kpi: Dict[TipoIndicador, float] = {}
        semaforos: Dict[TipoIndicador, RangoEvaluacion] = {}
        for indicador in indicadores:
            kpi[indicador.tipo] = indicador.valor
            semaforos[indicador.tipo] = indicador.rango_evaluacion

        dashboard = DashboardAtleta(
            id_atleta=id_atleta,
            kpi_personales=kpi,
            semaforos=semaforos,
            comparacion_mes_actual_vs_anterior={},
        )
        return self.repositorio.guardar_dashboard_atleta(dashboard)


@dataclass
class CompararTendencias:
    """RF-09.6 / RF-11.4: compara indicadores entre dos periodos."""

    proveedor: ProveedorDatosRendimiento

    def ejecutar(
        self,
        id_atleta: str,
        desde_anterior: date,
        hasta_anterior: date,
        desde_actual: date,
        hasta_actual: date,
        tipos: Optional[List[TipoIndicador]] = None,
    ) -> List[TendenciaComparada]:
        if desde_anterior > hasta_anterior or desde_actual > hasta_actual:
            raise ErrorValidacion(
                "Los periodos a comparar son inválidos (fecha inicial mayor que final)."
            )
        if desde_actual < desde_anterior:
            raise ErrorValidacion(
                "El periodo actual no puede iniciar antes que el periodo anterior."
            )
        tipos = tipos or self._tipos_comparables()
        if not tipos:
            raise ErrorValidacion("Debe indicar al menos un indicador a comparar.")
        return [
            TendenciaComparada(
                tipo=tipo,
                valor_anterior=self._valor(
                    tipo, id_atleta, desde_anterior, hasta_anterior
                ),
                valor_actual=self._valor(tipo, id_atleta, desde_actual, hasta_actual),
            )
            for tipo in tipos
        ]

    def _tipos_comparables(self) -> List[TipoIndicador]:
        return list(TIPOS_COMPARABLES)

    def _valor(
        self, tipo: TipoIndicador, id_atleta: str, desde: date, hasta: date
    ) -> float:
        p = self.proveedor
        if tipo == TipoIndicador.ACCURACY:
            return p.accuracy_promedio(id_atleta, desde, hasta)
        if tipo == TipoIndicador.ACPL:
            return p.acpl_promedio(id_atleta, desde, hasta)
        if tipo == TipoIndicador.BLUNDERS:
            return float(p.blunders_totales(id_atleta, desde, hasta))
        if tipo == TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO:
            return self._cumplimiento(id_atleta, desde, hasta)
        if tipo == TipoIndicador.CUMPLIMIENTO_OBJETIVOS:
            return p.cumplimiento_objetivos(id_atleta, desde, hasta)
        if tipo == TipoIndicador.PORCENTAJE_RESULTADOS:
            return self._porcentaje_resultados(id_atleta, desde, hasta)
        if tipo == TipoIndicador.ASISTENCIA:
            return p.porcentaje_asistencia(id_atleta, desde, hasta)
        if tipo == TipoIndicador.PARTIDAS_ANALIZADAS:
            return float(p.partidas_analizadas(id_atleta, desde, hasta))
        if tipo == TipoIndicador.PARTICIPACION_TORNEOS:
            return float(p.torneos_jugados(id_atleta, desde, hasta))
        if tipo == TipoIndicador.EJERCICIOS_TACTICOS_RESUELTOS:
            return float(p.ejercicios_tacticos_resueltos(id_atleta, desde, hasta))
        if tipo == TipoIndicador.RATING_FIDE:
            return float(p.rating_fide(id_atleta, "clasicas"))
        raise ErrorValidacion(
            f"El indicador {tipo.value} no es comparable con los datos disponibles."
        )

    def _cumplimiento(self, id_atleta: str, desde: date, hasta: date) -> float:
        planificadas = self.proveedor.horas_planificadas(id_atleta, desde, hasta)
        if planificadas <= 0:
            return 0.0
        ejecutadas = self.proveedor.horas_entrenadas_aprobadas(
            id_atleta, desde, hasta
        )
        return (ejecutadas / planificadas) * 100

    def _porcentaje_resultados(
        self, id_atleta: str, desde: date, hasta: date
    ) -> float:
        victorias, tablas, derrotas = self.proveedor.resultados(
            id_atleta, desde, hasta
        )
        total = victorias + tablas + derrotas
        if total == 0:
            return 0.0
        return ((victorias + 0.5 * tablas) / total) * 100


@dataclass
class GenerarReporte:
    """RF-11.5: genera un reporte a partir de contenido definido por el llamador."""

    servicio_reporte: ServicioGeneracionReportes

    def ejecutar(
        self,
        tipo: TipoReporte,
        formato: FormatoReporte,
        titulo: str,
        secciones: List[str],
        contenido: dict,
        ruta_destino: str,
    ) -> str:
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=tipo,
            formato=formato,
            titulo=titulo,
            secciones=secciones,
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta_destino)


@dataclass
class GenerarReporteIntegralAtleta:
    """RF-11.10: composición estricta de secciones definidas en el dominio."""

    servicio_reporte: ServicioGeneracionReportes
    proveedor: ProveedorDatosRendimiento

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
        id_atleta: str,
        formato: FormatoReporte,
        ruta_destino: str,
    ) -> str:
        contenido = {
            "id_atleta": id_atleta,
            "rating_fide": self.proveedor.rating_fide(id_atleta, "clasicas"),
        }
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.INDIVIDUAL,
            formato=formato,
            titulo="Informe Integral del Atleta",
            secciones=list(self.SECCIONES_OBLIGATORIAS),
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta_destino)


@dataclass
class GenerarReporteGrupal:
    """RF-11.6: reporte comparativo entre atletas, asistencia y cumplimiento."""

    servicio_reporte: ServicioGeneracionReportes
    proveedor: ProveedorDatosRendimiento

    SECCIONES_OBLIGATORIAS = [
        "Comparativo entre atletas",
        "Asistencia",
        "Cumplimiento del entrenamiento",
    ]

    def ejecutar(
        self,
        id_entrenador: str,
        formato: FormatoReporte,
        ruta_destino: str,
    ) -> str:
        atletas = self.proveedor.atletas_por_entrenador(id_entrenador)
        contenido = {
            "id_entrenador": id_entrenador,
            "cantidad_atletas": len(atletas),
            "atletas": [getattr(a, "id", "") for a in atletas],
        }
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.GRUPAL,
            formato=formato,
            titulo="Reporte Grupal del Equipo",
            secciones=list(self.SECCIONES_OBLIGATORIAS),
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta_destino)


@dataclass
class GenerarReporteInstitucional:
    """RF-11.7: informes mensual, trimestral y anual."""

    servicio_reporte: ServicioGeneracionReportes

    SECCIONES_OBLIGATORIAS = [
        "Resumen del periodo",
        "Rendimiento del equipo",
        "Asistencia y cumplimiento",
        "Objetivos SMART",
    ]

    def ejecutar(
        self,
        periodo: PeriodoInstitucional,
        formato: FormatoReporte,
        ruta_destino: str,
    ) -> str:
        if periodo not in PeriodoInstitucional:
            raise ErrorValidacion("El periodo institucional es inválido.")
        reporte = Reporte(
            id=nuevo_id("reporte"),
            tipo=TipoReporte.INSTITUCIONAL,
            formato=formato,
            titulo=f"Informe {periodo.value}",
            secciones=list(self.SECCIONES_OBLIGATORIAS),
            contenido={"periodo": periodo.value},
        )
        return self.servicio_reporte.generar(reporte, ruta_destino)
