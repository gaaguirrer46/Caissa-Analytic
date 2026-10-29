"""Puertos secundarios (driven) del módulo de Usuarios.

Interfaces abstractas que los adaptadores de infraestructura implementarán."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .entidades import PermisosPorRol, Rol, Usuario

__all__ = [
    "PermisosPorRol",
    "ProveedorInformacionAutorizada",
    "RepositorioUsuarios",
    "ServicioHashContrasenas",
]

class RepositorioUsuarios(ABC):
    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario:
        """Persiste un usuario nuevo o actualizado."""

    @abstractmethod
    def buscar_por_correo(self, correo: str) -> Optional[Usuario]:
        """Devuelve el usuario asociado al correo, o None."""

    @abstractmethod
    def buscar_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """Devuelve el usuario por id, o None."""

    @abstractmethod
    def listar_todos(self) -> List[Usuario]:
        """Devuelve todos los usuarios del sistema."""

    @abstractmethod
    def existe(self, correo: str) -> bool:
        """Indica si ya existe un usuario con ese correo."""

class ServicioHashContrasenas(ABC):
    @abstractmethod
    def hashear(self, contrasena_plana: str) -> str:
        """Genera el hash seguro de una contraseña."""

    @abstractmethod
    def verificar(self, contrasena_plana: str, hash_almacenado: str) -> bool:
        """Verifica una contraseña contra su hash almacenado."""

    @abstractmethod
    def hash_dummy(self) -> str:
        """Devuelve un hash ficticio para mitigar ataques de temporización (timing attacks)."""

class ProveedorInformacionAutorizada(ABC):
    """entrega únicamente las secciones habilitadas al invitado."""

    @abstractmethod
    def obtener(self, seccion: str) -> object:
        """Devuelve los datos de una sección autorizada."""
