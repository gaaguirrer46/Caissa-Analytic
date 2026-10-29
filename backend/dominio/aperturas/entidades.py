"""Módulo de Repertorio de Aperturas.

Entidades del repertorio de aperturas del atleta y sus estadísticas."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional

class ColorApertura(str, Enum):
    BLANCAS = "BLANCAS"
    NEGRAS = "NEGRAS"

class EstadoApertura(str, Enum):
    EN_ESTUDIO = "EN_ESTUDIO"
    ACTIVA = "ACTIVA"
    EN_REVISION = "EN_REVISION"
    DESCARTADA = "DESCARTADA"

class NivelDominio(str, Enum):
    INICIAL = "INICIAL"
    INTERMEDIO = "INTERMEDIO"
    AVANZADO = "AVANZADO"

class ClasificacionUso(str, Enum):
    PRINCIPAL = "PRINCIPAL"
    SECUNDARIA = "SECUNDARIA"

class EfectividadApertura(str, Enum):
    MUY_EFECTIVA = "MUY_EFECTIVA"
    EFECTIVA = "EFECTIVA"
    EN_DESARROLLO = "EN_DESARROLLO"
    REQUIERE_REVISION = "REQUIERE_REVISION"

@dataclass
class AperturaRepertorio:
    id: int
    id_atleta: int
    codigo_eco: str
    nombre: str
    variante: str = ""
    color: ColorApertura = ColorApertura.BLANCAS
    estado: EstadoApertura = EstadoApertura.EN_ESTUDIO
    nivel_dominio: NivelDominio = NivelDominio.INICIAL
    fuente_estudio: str = ""
    observaciones: str = ""
    clasificacion_uso: ClasificacionUso = ClasificacionUso.SECUNDARIA

@dataclass
class EstadisticaApertura:
    id_apertura: int
    partidas_jugadas: int = 0
    victorias: int = 0
    empates: int = 0
    derrotas: int = 0
    accuracy_promedio: Optional[float] = None
    acpl_promedio: Optional[float] = None
    errores_frecuentes: int = 0
    evaluacion_motor_promedio: Optional[float] = None
    tiempo_promedio: Optional[float] = None

    @property
    def rendimiento(self) -> float:
        """Porcentaje de puntos obtenidos (0-100)."""
        if self.partidas_jugadas == 0:
            return 0.0
        puntos = self.victorias + self.empates * 0.5
        return (puntos / self.partidas_jugadas) * 100

    def efectividad(self) -> EfectividadApertura:
        rend = self.rendimiento
        if self.partidas_jugadas >= 10 and rend >= 70:
            return EfectividadApertura.MUY_EFECTIVA
        if self.partidas_jugadas >= 5 and rend >= 50:
            return EfectividadApertura.EFECTIVA
        if self.partidas_jugadas >= 5:
            return EfectividadApertura.EN_DESARROLLO
        return EfectividadApertura.REQUIERE_REVISION

@dataclass
class EstadisticaAperturaPorTorneo:
    id_apertura: int
    torneo: str
    anio: int
    control_tiempo: Optional[str] = None
    color: Optional[ColorApertura] = None
    nivel_rival: Optional[str] = None
    rival: Optional[str] = None
    partidas_jugadas: int = 0
    victorias: int = 0
    empates: int = 0
    derrotas: int = 0
