"""Módulo de Evaluación del Entrenador (RF-10).

Entidades para evaluar el rendimiento del atleta después de cada torneo,
al finalizar un mes, un mesociclo o el año.
"""
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
    """Indicadores evaluados en cada evaluación (RF-10.2)."""

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
    """RF-10.4: calificación cuantitativa (1-10) y comentarios cualitativos."""

    id: str
    id_atleta: str
    id_entrenador: str
    periodo: PeriodoEvaluacion
    referencia_periodo: str
    fecha_realizacion: date
    calificaciones: Dict[TipoIndicadorEvaluacion, int] = field(default_factory=dict)
    fortalezas: str = ""
    aspectos_por_mejorar: str = ""
    recomendaciones: str = ""
    # RF-10.3: la evaluación del entrenador es obligatoria; la autoevaluación
    # del atleta es opcional.
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
