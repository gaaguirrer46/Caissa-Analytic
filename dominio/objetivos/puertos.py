"""Puertos secundarios (driven) del módulo de Objetivos SMART."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from .entidades import EstadoObjetivo, ObjetivoSmart, TipoIndicadorAvance

class RepositorioObjetivos(ABC):
    @abstractmethod
    def guardar(self, objetivo: ObjetivoSmart) -> ObjetivoSmart:
        """Persiste un objetivo nuevo o actualizado."""

    @abstractmethod
    def actualizar(self, objetivo: ObjetivoSmart) -> ObjetivoSmart:
        """Actualiza un objetivo existente."""

    @abstractmethod
    def buscar_por_atleta(self, id_atleta: int) -> List[ObjetivoSmart]:
        """Devuelve los objetivos de un atleta."""

    @abstractmethod
    def buscar_por_id(self, id_objetivo: int) -> Optional[ObjetivoSmart]:
        """Devuelve un objetivo por id, o None."""

    @abstractmethod
    def listar_por_estado(self, estado: EstadoObjetivo) -> List[ObjetivoSmart]:
        """Devuelve los objetivos en un estado dado."""

    @abstractmethod
    def eliminar(self, id_objetivo: int) -> None:
        """Elimina un objetivo."""

class ProveedorDatosAvance(ABC):
    """Interfaz para obtener datos actuales sin acoplarse a otros módulos."""

    @abstractmethod
    def horas_entrenadas(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """Horas de entrenamiento ejecutadas y aprobadas en el periodo."""

    @abstractmethod
    def rating_actual(self, id_atleta: int, tipo: str) -> Optional[int]:
        """Rating actual del atleta (ej: 'clasicas', 'rapidas', 'blitz')."""

    @abstractmethod
    def tareas_completadas(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """Número de tareas completadas en el periodo."""

    @abstractmethod
    def torneos_jugados(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """Número de torneos jugados en el periodo."""

    @abstractmethod
    def medallas_obtenidas(
        self, id_atleta: int, desde: date, hasta: date
    ) -> float:
        """Número de medallas obtenidas en el periodo."""
