"""Módulo de Objetivos SMART (RF-03).

Entidades para definir, seguir y validar objetivos cuantificables.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class EstadoObjetivo(str, Enum):
    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"
    EN_PROCESO = "EN_PROCESO"
    RETRASADO = "RETRASADO"
    FINALIZADO = "FINALIZADO"


class TipoIndicadorAvance(str, Enum):
    HORAS_ENTRENADAS = "HORAS_ENTRENADAS"
    RATING = "RATING"
    TAREAS = "TAREAS"
    TORNEOS = "TORNEOS"
    MEDALLAS = "MEDALLAS"


@dataclass(frozen=True)
class IndicadorAvance:
    tipo: TipoIndicadorAvance
    valor_actual: float
    valor_esperado: float

    def porcentaje(self) -> float:
        if self.valor_esperado <= 0:
            return 0.0
        return min(100.0, (self.valor_actual / self.valor_esperado) * 100)


@dataclass
class ObjetivoSmart:
    id: str
    id_atleta: str
    descripcion: str
    indicador_meta: TipoIndicadorAvance
    valor_meta: float
    rating_actual: int
    rating_meta: int
    fecha_inicio: date
    fecha_limite: date
    porcentaje_avance: float = 0.0
    estado: EstadoObjetivo = EstadoObjetivo.PENDIENTE_APROBACION
    aprobado_por_entrenador: bool = False
    cumplido_por_entrenador: bool = False
    avances: list[IndicadorAvance] = field(default_factory=list)
