"""Módulo de Indicadores, Dashboard e Informes.

Entidades para calcular métricas de rendimiento, vistas consolidadas y reportes."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

class TipoIndicador(str, Enum):
    RATING_FIDE = "RATING_FIDE"
    RATING_FIDE_RAPIDAS = "RATING_FIDE_RAPIDAS"
    RATING_FIDE_BLITZ = "RATING_FIDE_BLITZ"
    VARIACION_RATING = "VARIACION_RATING"
    PORCENTAJE_RESULTADOS = "PORCENTAJE_RESULTADOS"
    ACCURACY = "ACCURACY"
    ACPL = "ACPL"
    BLUNDERS = "BLUNDERS"
    CUMPLIMIENTO_ENTRENAMIENTO = "CUMPLIMIENTO_ENTRENAMIENTO"
    CUMPLIMIENTO_OBJETIVOS = "CUMPLIMIENTO_OBJETIVOS"
    RENDIMIENTO_POR_APERTURA = "RENDIMIENTO_POR_APERTURA"
    RENDIMIENTO_EN_FINALES = "RENDIMIENTO_EN_FINALES"
    GESTION_DEL_TIEMPO = "GESTION_DEL_TIEMPO"
    EJERCICIOS_TACTICOS_RESUELTOS = "EJERCICIOS_TACTICOS_RESUELTOS"
    PARTIDAS_ANALIZADAS = "PARTIDAS_ANALIZADAS"
    ASISTENCIA = "ASISTENCIA"
    PARTICIPACION_TORNEOS = "PARTICIPACION_TORNEOS"

INDICADORES_MENOR_ES_MEJOR = frozenset(
    {TipoIndicador.ACPL, TipoIndicador.BLUNDERS}
)

class RangoEvaluacion(str, Enum):
    EXCELENTE = "EXCELENTE"
    BUENO = "BUENO"
    ACEPTABLE = "ACEPTABLE"
    REQUIERE_INTERVENCION = "REQUIERE_INTERVENCION"

    @property
    def color(self) -> str:
        """RNF-03.3: color del semáforo asociado al rango."""
        return _COLOR_POR_RANGO[self]

_COLOR_POR_RANGO: dict[RangoEvaluacion, str] = {
    RangoEvaluacion.EXCELENTE: "VERDE",
    RangoEvaluacion.BUENO: "VERDE",
    RangoEvaluacion.ACEPTABLE: "AMARILLO",
    RangoEvaluacion.REQUIERE_INTERVENCION: "ROJO",
}

class TipoAlerta(str, Enum):
    BAJA_ASISTENCIA = "BAJA_ASISTENCIA"
    OBJETIVO_VENCIDO = "OBJETIVO_VENCIDO"
    DISMINUCION_RENDIMIENTO = "DISMINUCION_RENDIMIENTO"

class EstadoAlerta(str, Enum):
    ACTIVA = "ACTIVA"
    ATENDIDA = "ATENDIDA"
    EXPIRADA = "EXPIRADA"

class TipoReporte(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    GRUPAL = "GRUPAL"
    INSTITUCIONAL = "INSTITUCIONAL"

class FormatoReporte(str, Enum):
    PDF = "PDF"
    EXCEL = "EXCEL"

    JSON = "JSON"
    HTML = "HTML"

class TipoGraficoRendimiento(str, Enum):
    """Catálogo de gráficos de rendimiento."""

    EVOLUCION_RATING = "EVOLUCION_RATING"
    EVOLUCION_ACCURACY = "EVOLUCION_ACCURACY"
    HORAS_ENTRENAMIENTO = "HORAS_ENTRENAMIENTO"
    RENDIMIENTO_POR_TORNEO = "RENDIMIENTO_POR_TORNEO"
    DISTRIBUCION_RESULTADOS = "DISTRIBUCION_RESULTADOS"
    COMPARACION_ENTRE_ATLETAS = "COMPARACION_ENTRE_ATLETAS"
    EVOLUCION_INDICE_GLOBAL = "EVOLUCION_INDICE_GLOBAL"

class TipoTablaDetallada(str, Enum):
    """Catálogo de tablas detalladas exportables."""

    HISTORIAL_PARTIDAS = "HISTORIAL_PARTIDAS"
    REGISTRO_ENTRENAMIENTOS = "REGISTRO_ENTRENAMIENTOS"
    OBJETIVOS_SMART = "OBJETIVOS_SMART"
    ESTADISTICAS_POR_APERTURA = "ESTADISTICAS_POR_APERTURA"
    ESTADISTICAS_POR_TORNEO = "ESTADISTICAS_POR_TORNEO"
    RANKING_EQUIPO = "RANKING_EQUIPO"
    REPORTES_ASISTENCIA = "REPORTES_ASISTENCIA"

class PeriodoInstitucional(str, Enum):
    """Periodos de los informes institucionales."""

    MENSUAL = "MENSUAL"
    TRIMESTRAL = "TRIMESTRAL"
    ANUAL = "ANUAL"

class PeriodicidadGrafico(str, Enum):
    """Granularidad de la serie de un gráfico de tendencias.

 La periodicidad "torneo" se cubre con ``CompararTendenciasPeriodicas``
, que define la ventana con las fechas de las partidas del
 evento y la compara contra el torneo anterior del atleta.
 """

    SEMANAL = "SEMANAL"
    MENSUAL = "MENSUAL"
    ANUAL = "ANUAL"

class PeriodicidadTendencia(str, Enum):
    """Periodos de comparación de tendencias.

 A diferencia de ``PeriodicidadGrafico`` incorpora "torneo":
 la ventana la define el rango de fechas de las partidas del evento.
 "PLAN" compara la semana ISO de un plan de entrenamiento contra la
 semana inmediatamente anterior.
 """

    SEMANAL = "SEMANAL"
    MENSUAL = "MENSUAL"
    ANUAL = "ANUAL"
    TORNEO = "TORNEO"
    PLAN = "PLAN"

@dataclass
class IndicadorRendimiento:
    id: int
    id_atleta: int
    tipo: TipoIndicador
    valor: float
    rango_evaluacion: RangoEvaluacion
    periodo_inicio: date
    periodo_fin: date

@dataclass
class Alerta:
    id: int
    tipo: TipoAlerta
    id_atleta: int
    fecha_generacion: datetime
    estado: EstadoAlerta = EstadoAlerta.ACTIVA

@dataclass
class DashboardEntrenador:
    resumen_equipo: dict
    atletas_activos: int
    alertas: List[Alerta] = field(default_factory=list)
    cumplimiento_plan: dict = field(default_factory=dict)
    evolucion_rating_grupal: dict = field(default_factory=dict)
    objetivos_pendientes: List[int] = field(default_factory=list)

@dataclass
class DashboardAtleta:
    """KPIs personales, semáforos y comparación mensual.

 Las horas (entrenadas aprobadas y planificadas) se exponen como valores
 absolutos junto al porcentaje de cumplimiento del mismo periodo.
 """

    id_atleta: int
    kpi_personales: Dict[TipoIndicador, float] = field(default_factory=dict)
    semaforos: Dict[TipoIndicador, RangoEvaluacion] = field(default_factory=dict)
    comparacion_mes_actual_vs_anterior: dict = field(default_factory=dict)
    horas_entrenadas: float = 0.0
    horas_planificadas: float = 0.0

@dataclass(frozen=True)
class IndicadoresPermanentes:
    """vista consolidada de los indicadores siempre visibles.

 Reúne los indicadores escalares del periodo, el rendimiento por color de
 piezas, las mejores y peores aperturas, las medallas y la posición en el
 ranking de rating del sistema.
 """

    id_atleta: int
    periodo_inicio: date
    periodo_fin: date
    indicadores: Dict[TipoIndicador, float] = field(default_factory=dict)
    rendimiento_por_color: Dict[str, dict] = field(default_factory=dict)
    aperturas: Dict[str, Optional[dict]] = field(default_factory=dict)
    medallas: int = 0
    ranking: dict = field(default_factory=dict)

@dataclass
class Reporte:
    id: int
    tipo: TipoReporte
    formato: FormatoReporte
    titulo: str
    secciones: List[str] = field(default_factory=list)
    contenido: dict = field(default_factory=dict)
    generado_en: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

@dataclass(frozen=True)
class TendenciaComparada:
    """Comparación de un indicador entre dos periodos."""

    tipo: TipoIndicador
    valor_anterior: float
    valor_actual: float

    @property
    def variacion(self) -> float:
        """Diferencia absoluta entre el periodo actual y el anterior."""
        return self.valor_actual - self.valor_anterior

    @property
    def variacion_porcentual(self) -> Optional[float]:
        """Variación relativa; None si el periodo anterior era cero."""
        if self.valor_anterior == 0:
            return None
        return (self.variacion / self.valor_anterior) * 100

@dataclass(frozen=True)
class PuntoSerie:
    """Punto de la serie de un gráfico de tendencias."""

    etiqueta: str
    desde: date
    hasta: date
    valor: float

@dataclass(frozen=True)
class ComparacionGrupal:
    """posición de un atleta frente al promedio de su grupo."""

    tipo: TipoIndicador
    valor_atleta: float
    promedio_grupo: float
    posicion: int
    total_atletas: int

    progreso_atleta: float = 0.0
    progreso_grupo: float = 0.0

    @property
    def diferencia(self) -> float:
        return self.valor_atleta - self.promedio_grupo

    @property
    def sobre_el_promedio(self) -> bool:
        """Indica si el valor numérico supera el promedio del grupo."""
        return self.diferencia >= 0

    @property
    def es_favorable(self) -> bool:
        """Indica si el atleta está mejor que el promedio según la dirección del indicador."""
        if self.tipo in INDICADORES_MENOR_ES_MEJOR:
            return self.valor_atleta <= self.promedio_grupo
        return self.valor_atleta >= self.promedio_grupo
