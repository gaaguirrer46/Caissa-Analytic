"""Puertos secundarios (driven) del módulo de Partidas."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from .entidades import (
    AnalisisTecnico,
    Partida,
)


class RepositorioPartidas(ABC):
    @abstractmethod
    def guardar(self, partida: Partida) -> Partida:
        """Persiste una partida."""

    @abstractmethod
    def buscar_por_id(self, id_partida: int) -> Optional[Partida]:
        """Devuelve una partida por id, o None."""

    @abstractmethod
    def listar_por_atleta(self, id_atleta: int) -> List[Partida]:
        """Devuelve las partidas de un atleta."""

    @abstractmethod
    def listar_por_torneo(self, evento: str) -> List[Partida]:
        """Devuelve las partidas de un torneo/evento."""

    @abstractmethod
    def listar_por_periodo(
        self, id_atleta: int, desde: date, hasta: date
    ) -> List[Partida]:
        """Devuelve las partidas de un atleta en un periodo."""


class RepositorioAnalisisTecnico(ABC):
    @abstractmethod
    def guardar_resumen(self, analisis: AnalisisTecnico) -> AnalisisTecnico:
        """Persiste el resumen técnico de una partida."""

    @abstractmethod
    def buscar_por_partida(self, id_partida: int) -> Optional[AnalisisTecnico]:
        """Devuelve el análisis de una partida, o None."""

    @abstractmethod
    def listar_por_atleta(self, id_atleta: int) -> List[AnalisisTecnico]:
        """Devuelve los análisis de las partidas de un atleta."""


class ProveedorPGN(ABC):
    """Interfaz para importar partidas desde archivos PGN.

    El dominio no parsea PGN; solicita la partida ya estructurada.
    """

    @abstractmethod
    def parsear(self, contenido_pgn: str) -> List[Partida]:
        """Devuelve las partidas estructuradas a partir del contenido PGN."""
