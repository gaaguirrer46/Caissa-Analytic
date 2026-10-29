"""Puertos secundarios del módulo de Configuración del Sistema."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .entidades import ConfiguracionSistema

class RepositorioConfiguracion(ABC):
    @abstractmethod
    def obtener(self) -> ConfiguracionSistema:
        """Devuelve la configuración vigente (o los valores por defecto)."""

    @abstractmethod
    def guardar(self, configuracion: ConfiguracionSistema) -> ConfiguracionSistema:
        """Persiste la configuración y devuelve la versión guardada."""
