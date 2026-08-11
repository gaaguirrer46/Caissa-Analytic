"""Módulo de Partidas y Análisis Técnico (RF-05, RF-07).

Entidades para registrar competencias, almacenar resúmenes de análisis
técnico y clasificar la calidad del juego.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class ResultadoPartida(str, Enum):
    VICTORIA_BLANCAS = "1-0"
    VICTORIA_NEGRAS = "0-1"
    TABLAS = "1/2-1/2"


class ColorPartida(str, Enum):
    """Color con el que jugó el atleta registrado en la partida."""

    BLANCAS = "BLANCAS"
    NEGRAS = "NEGRAS"


class FuentePartida(str, Enum):
    PGN = "PGN"
    CHESS_COM = "CHESS_COM"
    LICHESS = "LICHESS"
    MANUAL = "MANUAL"
    CHESSBASE = "CHESSBASE"


class ClasificacionPartida(str, Enum):
    PARTIDA_BOTADA = "PARTIDA_BOTADA"
    EXCELENTE = "EXCELENTE"
    BUENA = "BUENA"
    LIBRO = "LIBRO"


@dataclass
class Partida:
    id: str
    id_atleta: str
    evento: str
    fecha: date
    jugador_blancas: str
    jugador_negras: str
    rating_blancas: int
    rating_negras: int
    resultado: ResultadoPartida
    apertura_eco: str
    control_tiempo: Optional[str] = None
    fuente: FuentePartida = FuentePartida.MANUAL
    color_atleta: Optional[ColorPartida] = None

    def puntos_obtenidos(self) -> float:
        """Puntos que obtuvo el atleta en esta partida según su color."""
        if self.resultado == ResultadoPartida.TABLAS:
            return 0.5
        if self.color_atleta == ColorPartida.NEGRAS:
            return 1.0 if self.resultado == ResultadoPartida.VICTORIA_NEGRAS else 0.0
        return 1.0 if self.resultado == ResultadoPartida.VICTORIA_BLANCAS else 0.0


@dataclass
class AnalisisTecnico:
    id_partida: str
    accuracy: Optional[float] = None
    acpl: Optional[float] = None
    blunders: int = 0
    errores: int = 0
    imprecisiones: int = 0
    brilliant_moves: int = 0
    excelente: int = 0
    buena: int = 0
    libro: int = 0
    tiempo_promedio_jugada: Optional[float] = None
    perdidas_por_tiempo: int = 0


@dataclass
class EstadisticasApertura:
    porcentaje_exito: float = 0.0
    errores_cometidos: int = 0
    tiempo_utilizado: Optional[float] = None


@dataclass
class EstadisticasMedioJuego:
    precision: Optional[float] = None
    errores_tacticos: int = 0
    errores_estrategicos: int = 0


@dataclass
class EstadisticasFinales:
    conversion_posiciones_ganadas: float = 0.0
    tablas_salvadas: int = 0
    errores_tecnicos: int = 0
    partidas_botadas: int = 0


@dataclass
class EstadisticasFaseJuego:
    id_atleta: str
    apertura: EstadisticasApertura = field(default_factory=EstadisticasApertura)
    medio_juego: EstadisticasMedioJuego = field(default_factory=EstadisticasMedioJuego)
    finales: EstadisticasFinales = field(default_factory=EstadisticasFinales)
