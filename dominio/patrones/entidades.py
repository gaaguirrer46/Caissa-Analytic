"""Módulo de Detección de Patrones de Error (RF-06).

Detecta patrones recurrentes a partir de partidas y métricas analizadas.
El dominio solo presenta estadísticas de patrones; no genera sugerencias.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class TipoPatron(str, Enum):
    TACTICO = "TACTICO"
    ESTRATEGICO = "ESTRATEGICO"
    APERTURA = "APERTURA"
    FINALES = "FINALES"
    GESTION_TIEMPO = "GESTION_TIEMPO"
    COMPETITIVO = "COMPETITIVO"
    DISCIPLINA = "DISCIPLINA"


class NivelMinimoPartidas(str, Enum):
    """Mínimos de partidas para mostrar tendencias según el tipo de análisis."""

    BASICO = "BASICO"      # 5
    INICIAL = "INICIAL"    # 10
    APERTURA = "APERTURA"  # 15
    FINALES = "FINALES"    # 15
    COLOR = "COLOR"        # 20
    RIVAL = "RIVAL"        # 20
    AVANZADO = "AVANZADO"  # 30


MINIMOS_PARTIDAS: dict[NivelMinimoPartidas, int] = {
    NivelMinimoPartidas.BASICO: 5,
    NivelMinimoPartidas.INICIAL: 10,
    NivelMinimoPartidas.APERTURA: 15,
    NivelMinimoPartidas.FINALES: 15,
    NivelMinimoPartidas.COLOR: 20,
    NivelMinimoPartidas.RIVAL: 20,
    NivelMinimoPartidas.AVANZADO: 30,
}

MINIMO_PARTIDAS_PATRON = 5
PORCENTAJE_MINIMO_PATRON = 40.0


@dataclass
class PatronDetectado:
    tipo: TipoPatron
    descripcion: str
    frecuencia_absoluta: int
    frecuencia_relativa: Optional[float] = None
    periodo_inicio: Optional[date] = None
    periodo_fin: Optional[date] = None


@dataclass
class AnalisisPatrones:
    id_atleta: str
    patrones: List[PatronDetectado] = field(default_factory=list)
    minimo_requerido: int = MINIMO_PARTIDAS_PATRON
