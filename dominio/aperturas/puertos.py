"""Puertos secundarios (driven) del módulo de Aperturas."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .entidades import (
    AperturaRepertorio,
    ColorApertura,
    EfectividadApertura,
    EstadisticaApertura,
    EstadisticaAperturaPorTorneo,
)


class RepositorioAperturas(ABC):
    @abstractmethod
    def guardar(self, apertura: AperturaRepertorio) -> AperturaRepertorio:
        """Persiste una apertura del repertorio."""

    @abstractmethod
    def actualizar_estado(
        self, id_apertura: str, estado: str
    ) -> AperturaRepertorio:
        """Actualiza el estado de una apertura."""

    @abstractmethod
    def buscar_por_atleta_y_color(
        self, id_atleta: str, color: ColorApertura
    ) -> List[AperturaRepertorio]:
        """Devuelve el repertorio del atleta filtrado por color."""

    @abstractmethod
    def listar_por_efectividad(
        self, id_atleta: str, efectividad: EfectividadApertura
    ) -> List[AperturaRepertorio]:
        """Devuelve aperturas según su nivel de efectividad."""

    @abstractmethod
    def buscar_por_id(self, id_apertura: str) -> Optional[AperturaRepertorio]:
        """Devuelve una apertura del repertorio por id."""

    @abstractmethod
    def guardar_estadistica(
        self, estadistica: EstadisticaApertura
    ) -> EstadisticaApertura:
        """Persiste las estadísticas generales de una apertura."""

    @abstractmethod
    def guardar_estadistica_torneo(
        self, estadistica: EstadisticaAperturaPorTorneo
    ) -> EstadisticaAperturaPorTorneo:
        """Persiste las estadísticas por torneo de una apertura."""

    @abstractmethod
    def buscar_estadistica(
        self, id_apertura: str
    ) -> Optional[EstadisticaApertura]:
        """Devuelve las estadísticas generales de una apertura."""


class ProveedorEvaluacionMotor(ABC):
    """Interfaz para obtener evaluación numérica de posiciones (ej: Stockfish)."""

    @abstractmethod
    def evaluar(self, posicion_fen: str) -> float:
        """Devuelve la evaluación centípoda de una posición."""
