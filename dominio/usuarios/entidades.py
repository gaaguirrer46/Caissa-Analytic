"""Módulo de Usuarios y Permisos (RF-01).

Entidades que encapsulan identidad, roles y permisos del sistema.
El dominio no conoce autenticación concreta (JWT, OAuth, sesiones).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Rol(str, Enum):
    ENTRENADOR = "ENTRENADOR"
    ATLETA = "ATLETA"
    INVITADO = "INVITADO"


class Permiso(str, Enum):
    GESTIONAR_USUARIOS = "GESTIONAR_USUARIOS"
    GESTIONAR_ATLETAS = "GESTIONAR_ATLETAS"
    GESTIONAR_OBJETIVOS = "GESTIONAR_OBJETIVOS"
    GESTIONAR_ENTRENAMIENTOS = "GESTIONAR_ENTRENAMIENTOS"
    GESTIONAR_PARTIDAS = "GESTIONAR_PARTIDAS"
    GESTIONAR_EVALUACIONES = "GESTIONAR_EVALUACIONES"
    CONFIGURAR_SISTEMA = "CONFIGURAR_SISTEMA"
    CONSULTAR_INFO_PROPIA = "CONSULTAR_INFO_PROPIA"
    PROYECTAR_REGISTROS = "PROYECTAR_REGISTROS"
    VER_INFORMACION_AUTORIZADA = "VER_INFORMACION_AUTORIZADA"


@dataclass(frozen=True)
class Usuario:
    """Identidad de un usuario del sistema."""

    id: str
    correo: str
    hash_contrasena: str
    rol: Rol
    fecha_creacion: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
