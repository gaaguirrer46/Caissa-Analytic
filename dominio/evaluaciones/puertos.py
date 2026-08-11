"""Puertos secundarios (driven) del módulo de Evaluación del Entrenador."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .entidades import EvaluacionAtleta, PeriodoEvaluacion


class RepositorioEvaluaciones(ABC):
    @abstractmethod
    def guardar(self, evaluacion: EvaluacionAtleta) -> EvaluacionAtleta:
        """Persiste una evaluación nueva o actualizada."""

    @abstractmethod
    def actualizar(self, evaluacion: EvaluacionAtleta) -> EvaluacionAtleta:
        """Actualiza una evaluación existente."""

    @abstractmethod
    def buscar_por_id(self, id_evaluacion: str) -> Optional[EvaluacionAtleta]:
        """Devuelve una evaluación por id, o None."""

    @abstractmethod
    def listar_por_atleta(self, id_atleta: str) -> List[EvaluacionAtleta]:
        """Devuelve las evaluaciones de un atleta."""

    @abstractmethod
    def listar_por_entrenador(self, id_entrenador: str) -> List[EvaluacionAtleta]:
        """Devuelve las evaluaciones realizadas por un entrenador."""

    @abstractmethod
    def listar_por_periodo(
        self, id_atleta: str, periodo: PeriodoEvaluacion
    ) -> List[EvaluacionAtleta]:
        """Devuelve las evaluaciones de un atleta en un periodo dado."""
