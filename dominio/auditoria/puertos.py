"""Puertos secundarios (driven) del módulo de Auditoría."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from .entidades import RegistroAuditoria


class RepositorioAuditoria(ABC):
    @abstractmethod
    def guardar(self, registro: RegistroAuditoria) -> RegistroAuditoria:
        """Persiste un registro inmutable de auditoría."""

    @abstractmethod
    def listar_por_entidad(self, entidad: str) -> List[RegistroAuditoria]:
        """Devuelve el trail de cambios de una entidad."""

    @abstractmethod
    def listar_por_usuario(self, usuario: str) -> List[RegistroAuditoria]:
        """Devuelve los cambios realizados por un usuario."""

    @abstractmethod
    def listar_por_fecha(self, dia: date) -> List[RegistroAuditoria]:
        """Devuelve los cambios registrados en una fecha."""
