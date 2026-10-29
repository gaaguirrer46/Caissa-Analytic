"""Módulo de Configuración del Sistema.

Permite al entrenador administrar límites operativos y rangos de evaluación sin
modificar el código fuente (RNF-07.1 / RNF-07.2)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Tuple

@dataclass(frozen=True)
class ConfiguracionSistema:
    """Parámetros operativos configurables por el administrador."""

    maximo_atletas_por_entrenador: int = 40
    minimo_entrenadores_por_atleta: int = 1
    maximo_entrenadores_por_atleta: int = 3
    permitir_autoevaluacion: bool = True
    rangos_evaluacion: Dict[str, Tuple[float, float, float]] = field(
        default_factory=dict
    )
    secciones_autorizadas_invitado: Tuple[str, ...] = ()
    actualizado_por: str = "sistema"
    fecha_actualizacion: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
