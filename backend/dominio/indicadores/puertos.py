"""Puertos secundarios (driven) del módulo de Indicadores."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional, Tuple

from .entidades import (
    Alerta,
    DashboardAtleta,
    DashboardEntrenador,
    IndicadorRendimiento,
    Reporte,
    TipoIndicador,
)

class RepositorioIndicadores(ABC):
    @abstractmethod
    def guardar(self, indicador: IndicadorRendimiento) -> IndicadorRendimiento:
        """Persiste un indicador calculado."""

    @abstractmethod
    def listar_por_atleta(self, id_atleta: int) -> List[IndicadorRendimiento]:
        """Devuelve los indicadores de un atleta."""

    @abstractmethod
    def listar_por_periodo(
        self, id_atleta: int, desde: date, hasta: date
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
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """Horas de entrenamiento aprobadas en el periodo."""

    @abstractmethod
    def horas_planificadas(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """Horas planificadas en el periodo."""

    @abstractmethod
    def accuracy_promedio(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """Accuracy promedio de las partidas del periodo."""

    @abstractmethod
    def blunders_totales(
        self, id_atleta: int, desde: date, hasta: date
    ) -> int:
        """Blunders cometidos en el periodo."""

    @abstractmethod
    def acpl_promedio(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """ACPL promedio en el periodo."""

    @abstractmethod
    def resultados(
        self, id_atleta: int, desde: date, hasta: date
    ) -> tuple[int, int, int]:
        """(victorias, tablas, derrotas) en el periodo."""

    @abstractmethod
    def partidas_analizadas(
        self, id_atleta: int, desde: date, hasta: date
    ) -> int:
        """Partidas analizadas en el periodo."""

    @abstractmethod
    def partidas_jugadas(
        self, id_atleta: int, desde: date, hasta: date
    ) -> int:
        """Partidas jugadas en el periodo."""

    @abstractmethod
    def torneos_jugados(
        self, id_atleta: int, desde: date, hasta: date
    ) -> int:
        """Torneos disputados en el periodo."""

    @abstractmethod
    def porcentaje_asistencia(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """Porcentaje de asistencia en el periodo."""

    @abstractmethod
    def ejercicios_tacticos_resueltos(
        self, id_atleta: int, desde: date, hasta: date
    ) -> int:
        """Ejercicios tácticos resueltos en el periodo."""

    @abstractmethod
    def cumplimiento_objetivos(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """Porcentaje de objetivos cumplidos en el periodo."""

    @abstractmethod
    def rating_fide(self, id_atleta: int, tipo: str) -> int:
        """Rating FIDE actual (clasicas, rapidas, blitz)."""

    @abstractmethod
    def variacion_rating(self, id_atleta: int, desde: date, hasta: date) -> float:
        """Variación del rating FIDE clásicas en el periodo.

 Calculada desde los snapshots históricos del atleta; sin datos
 suficientes devuelve 0.0 (no se inventa variación).
 """

    @abstractmethod
    def atletas_por_entrenador(self, id_entrenador: int) -> list:
        """Lista de atletas asignados al entrenador."""

    @abstractmethod
    def ids_atletas(self) -> list:
        """Todos los atletas del sistema (comparación por pares)."""

    @abstractmethod
    def torneos_del_atleta(self, id_atleta: int) -> list:
        """Torneos (eventos) del atleta con su rango de fechas, ordenados
 cronológicamente.

 Cada elemento es la tupla ``(evento, desde, hasta)``.
 """

    def objetivos_no_cumplidos(self, id_atleta: int) -> int:
        """Objetivos SMART aún no cumplidos del atleta.

 Implementación por defecto para no obligar a los adaptadores que no
 dispongan de la consulta; el adaptador SQLite la sobrescribe.
 """
        return 0

    def rendimiento_por_color(
        self, id_atleta: int, color: str, desde: date, hasta: date
    ) -> Tuple[int, int, int]:
        """(victorias, tablas, derrotas) jugando con BLANCAS o NEGRAS.

 Implementación por defecto; el adaptador SQLite la sobrescribe.
 """
        return (0, 0, 0)

    def rendimiento_por_apertura(
        self, id_atleta: int, desde: date, hasta: date
    ) -> List[Tuple[str, str, float]]:
        """(codigo_eco, nombre, porcentaje) por apertura usada.

 Implementación por defecto; el adaptador SQLite la sobrescribe.
 """
        return []

    def medallas_obtenidas(self, id_atleta: int, desde: date, hasta: date) -> int:
        """Medallas del periodo.

 El modelo oficial no tiene tabla de medallas, así que la
 implementación por defecto devuelve 0 (no se inventan datos); si el
 modelo crece, cada adaptador la sobrescribe.
 """
        return 0

class ProveedorRangosEvaluacion(ABC):
    """RNF-07.2: configuración de los rangos de evaluación de indicadores.

 Si un adaptador no configura un tipo, el dominio usa los valores
 por defecto definidos en RANGOS_POR_DEFECTO.
 """

    @abstractmethod
    def rangos(
        self, tipo: TipoIndicador
    ) -> Optional[Tuple[float, float, float]]:
        """Devuelve (excelente, bueno, aceptable) para el tipo, o None."""

class ServicioGeneracionReportes(ABC):
    """Interfaz para exportar a PDF/Excel. El dominio define el contenido."""

    @abstractmethod
    def generar(self, reporte: Reporte, ruta_destino: str) -> str:
        """Genera el archivo en el formato del reporte y devuelve la ruta."""
