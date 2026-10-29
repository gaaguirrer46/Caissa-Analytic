"""Módulo de Atletas.

Entidades del expediente deportivo integral del ajedrecista."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional

from ..comun.errores import ErrorValidacion
from ..entrenamientos.entidades import PlanEntrenamientoSemanal, SesionEntrenamiento
from ..objetivos.entidades import ObjetivoSmart
from ..partidas.entidades import EstadisticasFaseJuego, Partida

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
    """Snapshot inmutable del atleta por año y por torneo.

 ``id_atleta`` es obligatorio: es la clave que asocia el snapshot con su
 expediente (antes el adaptador confundía ``id`` con ``id_atleta``).
 """

    id: int
    id_atleta: int
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
    institucion: Optional[str] = None
    carrera: Optional[str] = None
    categorias: List[int] = field(default_factory=list)
    clubs: List[str] = field(default_factory=list)
    entrenadores_asignados: List[int] = field(default_factory=list)
    rating_actual: Rating = field(default_factory=Rating)
    historial: List[PerfilHistorico] = field(default_factory=list)
    activo: bool = True

    def edad(self, hoy: Optional[date] = None) -> int:
        """Calcula la edad automáticamente a partir de la fecha de nacimiento.

la edad es una propiedad derivada, nunca almacenada. La
 guarda defensiva asegura que una entidad construida
 a mano con fecha futura no devuelva una edad negativa silenciosa.
 """
        hoy = hoy or date.today()
        if hoy < self.fecha_nacimiento:
            raise ErrorValidacion("La fecha de nacimiento no puede ser futura.")
        anios = hoy.year - self.fecha_nacimiento.year
        if (hoy.month, hoy.day) < (
            self.fecha_nacimiento.month,
            self.fecha_nacimiento.day,
        ):
            anios -= 1
        return anios

@dataclass(frozen=True)
class MiInformacion:
    """vista consolidada de la información propia del atleta."""

    atleta: Atleta
    calendario: List[SesionEntrenamiento]
    entrenamientos: List[PlanEntrenamientoSemanal]
    objetivos: List[ObjetivoSmart]
    estadisticas: EstadisticasFaseJuego
    partidas: List[Partida]
    reportes: List[str]
