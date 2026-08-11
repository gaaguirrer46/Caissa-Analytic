"""Puertos secundarios (driven) del módulo de Patrones de Error."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..partidas.entidades import AnalisisTecnico, Partida


class ProveedorDatosPartidas(ABC):
    """Interfaz para obtener partidas y análisis sin acoplarse a otros módulos."""

    @abstractmethod
    def partidas_con_analisis(
        self, id_atleta: str, periodo_inicio=None, periodo_fin=None
    ) -> List[tuple[Partida, AnalisisTecnico]]:
        """Devuelve pares (partida, análisis) en el periodo dado."""
