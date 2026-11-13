"""Módulo de Usuarios y Permisos.

Entidades que encapsulan identidad, roles y permisos del sistema.
El dominio no conoce autenticación concreta (JWT, OAuth, sesiones)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Dict, Mapping, Optional, Tuple

from ..comun.errores import ErrorValidacion

class Rol(str, Enum):
    ENTRENADOR = "ENTRENADOR"
    ATLETA = "ATLETA"
    INVITADO = "INVITADO"

    @classmethod
    def desde_str(cls, valor: str | Rol) -> Rol:
        """Convierte y valida un rol a partir de string o Enum, tolerando mayúsculas/minúsculas."""
        if isinstance(valor, Rol):
            return valor
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ErrorValidacion("El rol es obligatorio y no puede ser nulo o vacío.")
        limpio = valor.strip().upper()
        try:
            return cls(limpio)
        except ValueError:
            roles_validos = ", ".join(r.value for r in cls)
            raise ErrorValidacion(
                f"El rol '{valor}' es inválido. Los roles permitidos son: {roles_validos}."
            )

class Permiso(str, Enum):

    GESTIONAR_USUARIOS = "GESTIONAR_USUARIOS"
    CONFIGURAR_SISTEMA = "CONFIGURAR_SISTEMA"
    GESTIONAR_ATLETAS = "GESTIONAR_ATLETAS"
    GESTIONAR_OBJETIVOS = "GESTIONAR_OBJETIVOS"
    GESTIONAR_ENTRENAMIENTOS = "GESTIONAR_ENTRENAMIENTOS"
    GESTIONAR_PARTIDAS = "GESTIONAR_PARTIDAS"
    GESTIONAR_EVALUACIONES = "GESTIONAR_EVALUACIONES"
    GESTIONAR_REPORTES = "GESTIONAR_REPORTES"
    CONSULTAR_ESTADISTICAS = "CONSULTAR_ESTADISTICAS"

    CONSULTAR_INFO_PROPIA = "CONSULTAR_INFO_PROPIA"
    PROYECTAR_REGISTROS = "PROYECTAR_REGISTROS"

    VER_INFORMACION_AUTORIZADA = "VER_INFORMACION_AUTORIZADA"

SECCIONES_INVITADO = ("perfil_publico", "ranking", "resumen_equipo")

class PermisosPorRol:
    """Catálogo inmutable de permisos concedidos a cada rol.

 La matriz se expone como ``MappingProxyType`` de ``frozenset`` para que
 ninguna capa pueda conceder permisos mutando el catálogo en tiempo de
 ejecución.
 """

    _MATRIZ: Mapping[Rol, frozenset[Permiso]] = MappingProxyType(
        {
            Rol.ENTRENADOR: frozenset(
                {

                    Permiso.GESTIONAR_USUARIOS,
                    Permiso.CONFIGURAR_SISTEMA,
                    Permiso.GESTIONAR_ATLETAS,
                    Permiso.GESTIONAR_OBJETIVOS,
                    Permiso.GESTIONAR_ENTRENAMIENTOS,
                    Permiso.GESTIONAR_PARTIDAS,
                    Permiso.GESTIONAR_EVALUACIONES,
                    Permiso.GESTIONAR_REPORTES,
                    Permiso.CONSULTAR_ESTADISTICAS,
                }
            ),
            Rol.ATLETA: frozenset(
                {
                    Permiso.CONSULTAR_INFO_PROPIA,
                    Permiso.PROYECTAR_REGISTROS,
                }
            ),
            Rol.INVITADO: frozenset({Permiso.VER_INFORMACION_AUTORIZADA}),
        }
    )

    @classmethod
    def tiene_permiso(cls, rol: Rol, permiso: Permiso) -> bool:
        return permiso in cls._MATRIZ.get(rol, frozenset())

    @classmethod
    def permisos_del_rol(cls, rol: Rol) -> set[Permiso]:
        """Devuelve una copia mutable de los permisos otorgados a un rol."""
        return set(cls._MATRIZ.get(rol, frozenset()))

@dataclass(frozen=True)
class Usuario:
    """Identidad de un usuario del sistema."""

    id: Optional[int]
    correo: str
    hash_contrasena: str
    rol: Rol
    fecha_creacion: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

@dataclass(frozen=True)
class UsuarioResumen:
    """Vista de usuario sin material sensible.

 Se usa en consultas de listado para no exponer ``hash_contrasena`` a la capa
 de presentación.
 """

    id: Optional[int]
    correo: str
    rol: Rol
    fecha_creacion: datetime

@dataclass(frozen=True)
class InformacionAutorizada:
    """vista de solo lectura con las secciones habilitadas al invitado."""

    secciones: Tuple[str, ...]
    datos: Dict[str, object]
