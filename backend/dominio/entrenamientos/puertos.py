"""Puertos secundarios (driven) del módulo de Entrenamientos."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .entidades import (
    Asistencia,
    EjecucionEntrenamiento,
    PlanEntrenamientoSemanal,
    SesionEntrenamiento,
)

class RepositorioEntrenamientos(ABC):
    @abstractmethod
    def guardar_plan(self, plan: PlanEntrenamientoSemanal) -> PlanEntrenamientoSemanal:
        """Persiste el plan semanal de un atleta."""

    @abstractmethod
    def actualizar_sesion(self, sesion: SesionEntrenamiento) -> SesionEntrenamiento:
        """Actualiza una sesión (estado, reprogramación, etc.)."""

    @abstractmethod
    def registrar_ejecucion(
        self, ejecucion: EjecucionEntrenamiento
    ) -> EjecucionEntrenamiento:
        """Registra la ejecución reportada por el atleta."""

    @abstractmethod
    def aprobar_ejecucion(
        self, id_ejecucion: int
    ) -> EjecucionEntrenamiento:
        """Aprueba la ejecución reportada."""

    @abstractmethod
    def buscar_ejecucion(
        self, id_ejecucion: int
    ) -> Optional[EjecucionEntrenamiento]:
        """Devuelve una ejecución por id, o None."""

    @abstractmethod
    def buscar_sesion(self, id_sesion: int) -> Optional[SesionEntrenamiento]:
        """Devuelve una sesión por id, o None."""

    @abstractmethod
    def buscar_plan_de_sesion(
        self, id_sesion: int
    ) -> Optional[PlanEntrenamientoSemanal]:
        """Devuelve el plan al que pertenece una sesión, o None."""

    @abstractmethod
    def listar_por_semana(self, id_atleta: int, semana: int, anio: int) -> Optional[PlanEntrenamientoSemanal]:
        """Devuelve el plan de la semana del atleta."""

    @abstractmethod
    def listar_por_atleta(self, id_atleta: int) -> List[PlanEntrenamientoSemanal]:
        """Devuelve el historial completo de planes del atleta."""

    @abstractmethod
    def obtener_historial(self, id_atleta: int) -> List[PlanEntrenamientoSemanal]:
        """Devuelve las semanas anteriores conservando todos los estados."""

class RepositorioAsistencia(ABC):
    @abstractmethod
    def registrar(self, asistencia: Asistencia) -> Asistencia:
        """Registra la asistencia después de una sesión."""

    @abstractmethod
    def listar_por_sesion(self, id_sesion: int) -> List[Asistencia]:
        """Devuelve las asistencias de una sesión."""

    @abstractmethod
    def listar_por_atleta(self, id_atleta: int) -> List[Asistencia]:
        """Devuelve las asistencias de un atleta."""

    @abstractmethod
    def calcular_porcentaje(self, id_atleta: int) -> float:
        """Devuelve el porcentaje de asistencia del atleta."""
