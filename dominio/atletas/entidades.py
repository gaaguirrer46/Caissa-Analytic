"""Módulo de Atletas (RF-02).

Entidades del expediente deportivo integral del ajedrecista.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class TipoCategoria(str, Enum):
    EDAD = "EDAD"
    NIVEL = "NIVEL"
    ELO = "ELO"


@dataclass(frozen=True)
class Categoria:
    id: int
    nombre: str
    tipo: TipoCategoria
    rango: str
    editable_por_admin: bool = True


@dataclass(frozen=True)
class Rating:
    clasicas: Optional[int] = None
    rapidas: Optional[int] = None
    blitz: Optional[int] = None
    chess_com: Optional[int] = None
    lichess: Optional[int] = None
    fecha_actualizacion: Optional[date] = None


@dataclass(frozen=True)
class PerfilHistorico:
    """Snapshot inmutable del atleta por año y por torneo."""

    id: int
    anio: int
    torneo: Optional[str]
    rating: Rating
    observaciones: str = ""


@dataclass
class Atleta:
    id: int
    nombre: str
    fecha_nacimiento: date
    sexo: str
    identidad_opcional: Optional[str] = None
    fotografia_opcional: Optional[str] = None
    federacion: Optional[str] = None
    universidad: Optional[str] = None
    carrera: Optional[str] = None
    categorias: List[int] = field(default_factory=list)
    clubs: List[str] = field(default_factory=list)
    entrenadores_asignados: List[int] = field(default_factory=list)
    rating_actual: Rating = field(default_factory=Rating)
    historial: List[PerfilHistorico] = field(default_factory=list)
    activo: bool = True

    def edad(self, hoy: Optional[date] = None) -> int:
        """Calcula la edad automáticamente a partir de la fecha de nacimiento."""
        hoy = hoy or date.today()
        anios = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (
            self.fecha_nacimiento.month,
            self.fecha_nacimiento.day,
        ):
            anios -= 1
        return anios
