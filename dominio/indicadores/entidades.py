"""Módulo de Indicadores, Dashboard e Informes (RF-09, RF-11).

Entidades para calcular métricas de rendimiento, vistas consolidadas y reportes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional


class TipoIndicador(str, Enum):
    RATING_FIDE = "RATING_FIDE"
    VARIACION_RATING = "VARIACION_RATING"
    PORCENTAJE_RESULTADOS = "PORCENTAJE_RESULTADOS"
    ACCURACY = "ACCURACY"
    ACPL = "ACPL"
    BLUNDERS = "BLUNDERS"
    CUMPLIMIENTO_ENTRENAMIENTO = "CUMPLIMIENTO_ENTRENAMIENTO"
    CUMPLIMIENTO_OBJETIVOS = "CUMPLIMIENTO_OBJETIVOS"
    RENDIMIENTO_POR_APERTURA = "RENDIMIENTO_POR_APERTURA"
    RENDIMIENTO_EN_FINALES = "RENDIMIENTO_EN_FINALES"
    GESTION_DEL_TIEMPO = "GESTION_DEL_TIEMPO"
    EJERCICIOS_TACTICOS_RESUELTOS = "EJERCICIOS_TACTICOS_RESUELTOS"
    PARTIDAS_ANALIZADAS = "PARTIDAS_ANALIZADAS"
    ASISTENCIA = "ASISTENCIA"
    PARTICIPACION_TORNEOS = "PARTICIPACION_TORNEOS"


class RangoEvaluacion(str, Enum):
    EXCELENTE = "EXCELENTE"
    BUENO = "BUENO"
    ACEPTABLE = "ACEPTABLE"
    REQUIERE_INTERVENCION = "REQUIERE_INTERVENCION"


class TipoAlerta(str, Enum):
    BAJA_ASISTENCIA = "BAJA_ASISTENCIA"
    OBJETIVO_VENCIDO = "OBJETIVO_VENCIDO"
    DISMINUCION_RENDIMIENTO = "DISMINUCION_RENDIMIENTO"


class EstadoAlerta(str, Enum):
    ACTIVA = "ACTIVA"
    ATENDIDA = "ATENDIDA"
    EXPIRADA = "EXPIRADA"


class TipoReporte(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    GRUPAL = "GRUPAL"
    INSTITUCIONAL = "INSTITUCIONAL"


class FormatoReporte(str, Enum):
    PDF = "PDF"
    EXCEL = "EXCEL"


@dataclass
class IndicadorRendimiento:
    id: str
    id_atleta: str
    tipo: TipoIndicador
    valor: float
    rango_evaluacion: RangoEvaluacion
    periodo_inicio: date
    periodo_fin: date


@dataclass
class Alerta:
    id: str
    tipo: TipoAlerta
    id_atleta: str
    fecha_generacion: datetime
    estado: EstadoAlerta = EstadoAlerta.ACTIVA


@dataclass
class DashboardEntrenador:
    resumen_equipo: dict
    atletas_activos: int
    alertas: List[Alerta] = field(default_factory=list)
    cumplimiento_plan: dict = field(default_factory=dict)
    evolucion_rating_grupal: dict = field(default_factory=dict)
    objetivos_pendientes: List[str] = field(default_factory=list)


@dataclass
class DashboardAtleta:
    id_atleta: str
    kpi_personales: Dict[TipoIndicador, float] = field(default_factory=dict)
    semaforos: Dict[TipoIndicador, RangoEvaluacion] = field(default_factory=dict)
    comparacion_mes_actual_vs_anterior: dict = field(default_factory=dict)


@dataclass
class Reporte:
    id: str
    tipo: TipoReporte
    formato: FormatoReporte
    titulo: str
    secciones: List[str] = field(default_factory=list)
    contenido: dict = field(default_factory=dict)
    generado_en: datetime = field(default_factory=datetime.utcnow)
