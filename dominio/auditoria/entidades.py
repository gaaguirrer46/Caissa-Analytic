"""Módulo de Auditoría y Control de Cambios (RF-12).

Entidades para garantizar trazabilidad de todos los cambios críticos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TipoOperacion(str, Enum):
    CREAR = "CREAR"
    MODIFICAR = "MODIFICAR"
    ELIMINAR = "ELIMINAR"


@dataclass(frozen=True)
class RegistroAuditoria:
    """Registro inmutable de una modificación."""

    id: str
    usuario: str
    fecha_hora: datetime
    entidad_afectada: str
    tipo_operacion: TipoOperacion
    campo_modificado: str = ""
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
