"""Casos de uso (puertos primarios / driving) del módulo de Indicadores."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List

from ..comun.errores import EntidadNoEncontrada
from ..usuarios.entidades import Rol
from .entidades import (
    Alerta,
    DashboardAtleta,
    DashboardEntrenador,
    EstadoAlerta,
    FormatoReporte,
    IndicadorRendimiento,
    RangoEvaluacion,
    Reporte,
    TipoAlerta,
    TipoIndicador,
    TipoReporte,
)
from .puertos import (
    ProveedorDatosRendimiento,
    RepositorioIndicadores,
    ServicioGeneracionReportes,
)

# Rangos de evaluación por defecto (configurables, con valores en el dominio).
# Cada valor límite representa el piso del rango "verde" / "excelente".
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


def _evaluar(
    tipo: TipoIndicador, valor: float
) -> RangoEvaluacion:
    """Aplica los rangos por defecto; si el valor no tiene rango definido,
    se asigna ACEPTABLE por defecto (configuración futura lo sobreescribe)."""
    rangos = RANGOS_POR_DEFECTO.get(tipo)
    if rangos is None:
        return RangoEvaluacion.ACEPTABLE
    excelente, bueno, aceptable = rangos
    if tipo in (TipoIndicador.ACPL, TipoIndicador.BLUNDERS):
        # En estos indicadores un valor menor es mejor.
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


@dataclass
class CalcularIndicadoresPrincipales:
    repositorio: RepositorioIndicadores
    proveedor: ProveedorDatosRendimiento

    def ejecutar(
        self, id_atleta: str, desde: date, hasta: date
    ) -> List[IndicadorRendimiento]:
        indicadores: List[IndicadorRendimiento] = []

        accuracy = self.proveedor.accuracy_promedio(id_atleta, desde, hasta)
        indicadores.append(
            self._crear(id_atleta, TipoIndicador.ACCURACY, accuracy, desde, hasta)
        )

        cumplimiento = self._calcular_cumplimiento(id_atleta, desde, hasta)
        indicadores.append(
            self._crear(
                id_atleta,
                TipoIndicador.CUMPLIMIENTO_ENTRENAMIENTO,
                cumplimiento,
                desde,
                hasta,
            )
        )

        objetivos = self.proveedor.cumplimiento_objetivos(id_atleta, desde, hasta)
        indicadores.append(
            self._crear(
                id_atleta,
                TipoIndicador.CUMPLIMIENTO_OBJETIVOS,
                objetivos,
                desde,
                hasta,
            )
        )

        victorias, tablas, derrotas = self.proveedor.resultados(
            id_atleta, desde, hasta
        )
        total = victorias + tablas + derrotas
        porcentaje_resultados = (
            ((victorias + 0.5 * tablas) / total * 100) if total else 0.0
        )
        indicadores.append(
            self._crear(
                id_atleta,
                TipoIndicador.PORCENTAJE_RESULTADOS,
                porcentaje_resultados,
                desde,
                hasta,
            )
        )

        blunders = self.proveedor.blunders_totales(id_atleta, desde, hasta)
        indicadores.append(
            self._crear(
                id_atleta, TipoIndicador.BLUNDERS, float(blunders), desde, hasta
            )
        )

        rating = self.proveedor.rating_fide(id_atleta, "clasicas")
        indicadores.append(
            self._crear(id_atleta, TipoIndicador.RATING_FIDE, float(rating), desde, hasta)
        )

        for indicador in indicadores:
            self.repositorio.guardar(indicador)
        return indicadores

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

    def _crear(
        self,
        id_atleta: str,
        tipo: TipoIndicador,
        valor: float,
        desde: date,
        hasta: date,
    ) -> IndicadorRendimiento:
        return IndicadorRendimiento(
            id=generar_id_indicador(),
            id_atleta=id_atleta,
            tipo=tipo,
            valor=valor,
            rango_evaluacion=_evaluar(tipo, valor),
            periodo_inicio=desde,
            periodo_fin=hasta,
        )


@dataclass
class CalcularIndicadoresSecundarios:
    repositorio: RepositorioIndicadores
    proveedor: ProveedorDatosRendimiento

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
                float(self.proveedor.partidas_jugadas(id_atleta, desde, hasta)),
                desde,
                hasta,
            ),
        ]
        for indicador in indicadores:
            self.repositorio.guardar(indicador)
        return indicadores

    def _crear(
        self,
        id_atleta: str,
        tipo: TipoIndicador,
        valor: float,
        desde: date,
        hasta: date,
    ) -> IndicadorRendimiento:
        return IndicadorRendimiento(
            id=generar_id_indicador(),
            id_atleta=id_atleta,
            tipo=tipo,
            valor=valor,
            rango_evaluacion=_evaluar(tipo, valor),
            periodo_inicio=desde,
            periodo_fin=hasta,
        )


@dataclass
class GenerarDashboardEntrenador:
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
        """RF-09: las alertas se generan automáticamente cuando un indicador
        cae en 'Requiere Intervención'."""
        alertas: List[Alerta] = []
        for atleta in atletas:
            id_atleta = getattr(atleta, "id", "")
            indicadores = self.repositorio.listar_por_atleta(id_atleta)
            for indicador in indicadores:
                if indicador.rango_evaluacion == RangoEvaluacion.REQUIERE_INTERVENCION:
                    alertas.append(
                        Alerta(
                            id=generar_id_alerta(),
                            tipo=self._tipo_alerta(indicador.tipo),
                            id_atleta=id_atleta,
                            fecha_generacion=datetime.now(),
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
class GenerarReporte:
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
            id=generar_id_reporte(),
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
            id=generar_id_reporte(),
            tipo=TipoReporte.INDIVIDUAL,
            formato=formato,
            titulo="Informe Integral del Atleta",
            secciones=list(self.SECCIONES_OBLIGATORIAS),
            contenido=contenido,
        )
        return self.servicio_reporte.generar(reporte, ruta_destino)


def generar_id_indicador() -> str:
    import uuid

    return str(uuid.uuid4())


def generar_id_alerta() -> str:
    import uuid

    return str(uuid.uuid4())


def generar_id_reporte() -> str:
    import uuid

    return str(uuid.uuid4())
