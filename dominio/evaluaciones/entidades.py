"""Módulo de Evaluación del Entrenador.

Entidades para evaluar el rendimiento del atleta después de cada torneo,
al finalizar un mes, un mesociclo o el año."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional

class PeriodoEvaluacion(str, Enum):
    TORNEO = "TORNEO"
    MES = "MES"
    MESOCICLO = "MESOCICLO"
    ANIO = "ANIO"

class TipoIndicadorEvaluacion(str, Enum):
    """Indicadores evaluados en cada evaluación."""

    CUMPLIMIENTO_PLAN = "CUMPLIMIENTO_PLAN"
    DESARROLLO_TECNICO_TACTICO = "DESARROLLO_TECNICO_TACTICO"
    PROGRESO_RATING = "PROGRESO_RATING"
    CUMPLIMIENTO_OBJETIVOS_SMART = "CUMPLIMIENTO_OBJETIVOS_SMART"
    ORGANIZACION = "ORGANIZACION"
    GESTION_COMPETENCIAS = "GESTION_COMPETENCIAS"
    DESARROLLO_APERTURAS = "DESARROLLO_APERTURAS"
    SEGUIMIENTO_INDIVIDUAL = "SEGUIMIENTO_INDIVIDUAL"

CALIFICACION_MINIMA = 1
CALIFICACION_MAXIMA = 10

@dataclass
class EvaluacionAtleta:
    """calificación cuantitativa (1-10) y comentarios cualitativos."""

    id: int
    id_atleta: int
    id_entrenador: int
    periodo: PeriodoEvaluacion
    referencia_periodo: str
    fecha_realizacion: date
    calificaciones: Dict[TipoIndicadorEvaluacion, int] = field(default_factory=dict)
    fortalezas: str = ""
    aspectos_por_mejorar: str = ""
    recomendaciones: str = ""

    es_autoevaluacion: bool = False

    @property
    def promedio_calificaciones(self) -> float:
        if not self.calificaciones:
            return 0.0
        return sum(self.calificaciones.values()) / len(self.calificaciones)

    def calificacion_por_indicador(
        self, indicador: TipoIndicadorEvaluacion
    ) -> Optional[int]:
        return self.calificaciones.get(indicador)

@dataclass(frozen=True)
class ResumenEvaluaciones:
    """síntesis de las evaluaciones oficiales de un atleta.

 Emplea las evaluaciones registradas (sólo las del entrenador; la
 autoevaluación opcional se consulta aparte) para cuatro fines:

 - **Informes periódicos:** :meth:`a_contenido` produce el dict que
 alimenta el motor genérico ``GenerarReporte`` para
 exportar el informe en PDF/Excel.
 - **Seguimiento entre ciclos:** variación de la última evaluación
 frente a la anterior (promedio general y por indicador).
 - **Áreas de mejora:** los tres indicadores con menor promedio
 histórico (sólo los que tienen datos).
 - **Planificación deportiva:** recomendaciones consolidadas de los
 tres ciclos más recientes.
 """

    id_atleta: int
    cantidad_evaluaciones: int
    ultima_evaluacion: Optional[date]
    promedio_general: float
    promedio_por_indicador: Dict[TipoIndicadorEvaluacion, float]
    areas_de_mejora: List[TipoIndicadorEvaluacion]
    variacion_ultimo_ciclo: float
    variaciones_por_indicador: Dict[TipoIndicadorEvaluacion, float]
    recomendaciones_consolidadas: List[str]

    def a_contenido(self) -> Dict[str, object]:
        """Contenido listo para el motor genérico de reportes."""
        return {
            "id_atleta": self.id_atleta,
            "cantidad_evaluaciones": self.cantidad_evaluaciones,
            "ultima_evaluacion": (
                self.ultima_evaluacion.isoformat()
                if self.ultima_evaluacion
                else None
            ),
            "promedio_general": self.promedio_general,
            "promedio_por_indicador": {
                indicador.value: valor
                for indicador, valor in self.promedio_por_indicador.items()
            },
            "areas_de_mejora": [
                indicador.value for indicador in self.areas_de_mejora
            ],
            "variacion_ultimo_ciclo": self.variacion_ultimo_ciclo,
            "variaciones_por_indicador": {
                indicador.value: valor
                for indicador, valor in self.variaciones_por_indicador.items()
            },
            "recomendaciones_consolidadas": list(
                self.recomendaciones_consolidadas
            ),
        }
