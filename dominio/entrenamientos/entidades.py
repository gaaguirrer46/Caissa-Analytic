"""Módulo de Entrenamientos (RF-04).

Entidades para planificar semanalmente, registrar ejecución y controlar asistencia.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class TipoEntrenamiento(str, Enum):
    APERTURAS = "APERTURAS"
    MEDIO_JUEGO = "MEDIO_JUEGO"
    FINALES = "FINALES"
    TACTICA = "TACTICA"
    ESTRATEGIA = "ESTRATEGIA"
    CALCULO = "CALCULO"
    VISUALIZACION = "VISUALIZACION"
    ANALISIS_PARTIDAS = "ANALISIS_PARTIDAS"
    CLASES_TEORICAS = "CLASES_TEORICAS"
    PREPARACION_FISICA = "PREPARACION_FISICA"
    PSICOLOGICA_DEPORTIVA = "PSICOLOGICA_DEPORTIVA"
    PREPARACION_COMPETITIVA = "PREPARACION_COMPETITIVA"


class EstadoSesion(str, Enum):
    PROGRAMADA = "PROGRAMADA"
    REPROGRAMADA = "REPROGRAMADA"
    CANCELADA = "CANCELADA"
    EJECUTADA = "EJECUTADA"


class EstadoAsistencia(str, Enum):
    PRESENTE = "PRESENTE"
    AUSENTE = "AUSENTE"
    JUSTIFICADO = "JUSTIFICADO"


@dataclass
class SesionEntrenamiento:
    id: str
    tipo: TipoEntrenamiento
    dia_semana: str
    horas_planificadas: float
    estado: EstadoSesion = EstadoSesion.PROGRAMADA
    observaciones: str = ""
    horas_ejecutadas: Optional[float] = None
    ejecucion_aprobada: bool = False


@dataclass
class PlanEntrenamientoSemanal:
    id: str
    id_atleta: str
    semana: int
    anio: int
    sesiones: List[SesionEntrenamiento] = field(default_factory=list)

    @property
    def total_horas_planificadas(self) -> float:
        return sum(s.horas_planificadas for s in self.sesiones)

    @property
    def total_horas_ejecutadas_aprobadas(self) -> float:
        return sum(
            s.horas_ejecutadas or 0.0
            for s in self.sesiones
            if s.ejecucion_aprobada
        )

    @property
    def porcentaje_cumplimiento(self) -> float:
        total = self.total_horas_planificadas
        if total <= 0:
            return 0.0
        return (self.total_horas_ejecutadas_aprobadas / total) * 100


@dataclass
class EjecucionEntrenamiento:
    id: str
    id_sesion: str
    horas_ejecutadas: float
    fecha_registro: date
    registrado_por_atleta: bool = True
    aprobado_por_entrenador: bool = False


@dataclass
class Asistencia:
    id: str
    id_atleta: str
    id_sesion: str
    fecha: date
    estado: EstadoAsistencia
