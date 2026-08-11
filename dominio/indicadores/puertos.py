"""Puertos secundarios (driven) del módulo de Indicadores."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from .entidades import (
    Alerta,
    DashboardAtleta,
    DashboardEntrenador,
    IndicadorRendimiento,
    Reporte,
)


class RepositorioIndicadores(ABC):
    @abstractmethod
    def guardar(self, indicador: IndicadorRendimiento) -> IndicadorRendimiento:
        """Persiste un indicador calculado."""

    @abstractmethod
    def listar_por_atleta(self, id_atleta: str) -> List[IndicadorRendimiento]:
        """Devuelve los indicadores de un atleta."""

    @abstractmethod
    def listar_por_periodo(
        self, id_atleta: str, desde: date, hasta: date
    ) -> List[IndicadorRendimiento]:
        """Devuelve los indicadores de un atleta en un periodo."""

    @abstractmethod
    def guardar_dashboard_entrenador(
        self, dashboard: DashboardEntrenador
    ) -> DashboardEntrenador:
        """Persiste el dashboard consolidado del entrenador."""

    @abstractmethod
    def guardar_dashboard_atleta(
        self, dashboard: DashboardAtleta
    ) -> DashboardAtleta:
        """Persiste el dashboard del atleta."""


class ProveedorDatosRendimiento(ABC):
    """Interfaz unificada para agregar datos de otros módulos sin acoplarse."""

    @abstractmethod
    def horas_entrenadas_aprobadas(
        self, id_atleta: str, desde: date, hasta: date
    ) -> float:
        """Horas de entrenamiento aprobadas en el periodo."""

    @abstractmethod
    def horas_planificadas(
        self, id_atleta: str, desde: date, hasta: date
    ) -> float:
        """Horas planificadas en el periodo."""

    @abstractmethod
    def accuracy_promedio(
        self, id_atleta: str, desde: date, hasta: date
    ) -> float:
        """Accuracy promedio de las partidas del periodo."""

    @abstractmethod
    def blunders_totales(
        self, id_atleta: str, desde: date, hasta: date
    ) -> int:
        """Blunders cometidos en el periodo."""

    @abstractmethod
    def acpl_promedio(
        self, id_atleta: str, desde: date, hasta: date
    ) -> float:
        """ACPL promedio en el periodo."""

    @abstractmethod
    def resultados(
        self, id_atleta: str, desde: date, hasta: date
    ) -> tuple[int, int, int]:
        """(victorias, tablas, derrotas) en el periodo."""

    @abstractmethod
    def partidas_analizadas(
        self, id_atleta: str, desde: date, hasta: date
    ) -> int:
        """Partidas analizadas en el periodo."""

    @abstractmethod
    def partidas_jugadas(
        self, id_atleta: str, desde: date, hasta: date
    ) -> int:
        """Partidas jugadas en el periodo."""

    @abstractmethod
    def porcentaje_asistencia(
        self, id_atleta: str, desde: date, hasta: date
    ) -> float:
        """Porcentaje de asistencia en el periodo."""

    @abstractmethod
    def ejercicios_tacticos_resueltos(
        self, id_atleta: str, desde: date, hasta: date
    ) -> int:
        """Ejercicios tácticos resueltos en el periodo."""

    @abstractmethod
    def cumplimiento_objetivos(
        self, id_atleta: str, desde: date, hasta: date
    ) -> float:
        """Porcentaje de objetivos cumplidos en el periodo."""

    @abstractmethod
    def rating_fide(self, id_atleta: str, tipo: str) -> int:
        """Rating FIDE actual (clasicas, rapidas, blitz)."""

    @abstractmethod
    def atletas_por_entrenador(self, id_entrenador: str) -> list:
        """Lista de atletas asignados al entrenador."""


class ServicioGeneracionReportes(ABC):
    """Interfaz para exportar a PDF/Excel. El dominio define el contenido."""

    @abstractmethod
    def generar(self, reporte: Reporte, ruta_destino: str) -> str:
        """Genera el archivo en el formato del reporte y devuelve la ruta."""
