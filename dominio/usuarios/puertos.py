"""Puertos secundarios (driven) del módulo de Usuarios.

Interfaces abstractas que los adaptadores de infraestructura implementarán.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .entidades import Permiso, Rol, Usuario


class RepositorioUsuarios(ABC):
    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario:
        """Persiste un usuario nuevo o actualizado."""

    @abstractmethod
    def buscar_por_correo(self, correo: str) -> Optional[Usuario]:
        """Devuelve el usuario asociado al correo, o None."""

    @abstractmethod
    def buscar_por_id(self, id_usuario: str) -> Optional[Usuario]:
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


class PermisosPorRol:
    """Catálogo de permisos concedidos a cada rol (regla del dominio)."""

    _MATRIZ: dict[Rol, set[Permiso]] = {
        Rol.ENTRENADOR: {
            Permiso.GESTIONAR_USUARIOS,
            Permiso.GESTIONAR_ATLETAS,
            Permiso.GESTIONAR_OBJETIVOS,
            Permiso.GESTIONAR_ENTRENAMIENTOS,
            Permiso.GESTIONAR_PARTIDAS,
            Permiso.GESTIONAR_EVALUACIONES,
            Permiso.CONFIGURAR_SISTEMA,
        },
        Rol.ATLETA: {
            Permiso.CONSULTAR_INFO_PROPIA,
            Permiso.PROYECTAR_REGISTROS,
        },
        Rol.INVITADO: {
            Permiso.VER_INFORMACION_AUTORIZADA,
        },
    }

    @classmethod
    def tiene_permiso(cls, rol: Rol, permiso: Permiso) -> bool:
        return permiso in cls._MATRIZ.get(rol, set())
