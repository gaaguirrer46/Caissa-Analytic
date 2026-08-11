"""Puertos secundarios (driven) del módulo de Patrones de Error."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Dict, List, Optional

from ..partidas.entidades import AnalisisTecnico, Partida


class ProveedorDatosPartidas(ABC):
    """Interfaz para obtener partidas y análisis sin acoplarse a otros módulos."""

    @abstractmethod
    def partidas_con_analisis(
        self,
        id_atleta: str,
        periodo_inicio: Optional[date] = None,
        periodo_fin: Optional[date] = None,
    ) -> List[tuple[Partida, AnalisisTecnico]]:
        """Devuelve pares (partida, análisis) en el periodo dado."""

    @abstractmethod
    def conteos_disciplina(
        self,
        id_atleta: str,
        periodo_inicio: Optional[date] = None,
        periodo_fin: Optional[date] = None,
    ) -> Dict[str, int]:
        """Devuelve conteos de disciplina (RF-06.7).

        Claves esperadas:
        - incumplimientos_semanales: semanas con cumplimiento < 100%%
        - inasistencias: sesiones con asistencia AUSENTE/JUSTIFICADO
        - partidas_sin_analisis: partidas del periodo sin análisis técnico
        """
