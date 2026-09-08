"""Módulo de Objetivos SMART (RF-03).

Define las entidades y enumeraciones esenciales para modelar metas de entrenamiento
cuantificables y temporalizadas para los atletas de ajedrez en Caissa Analytics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional, Union

from .validador import ObjetivoSMARTValidator


class EstadoObjetivo(str, Enum):
    """Estados del ciclo de vida de un Objetivo SMART."""
    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"
    EN_PROCESO = "EN_PROCESO"
    RETRASADO = "RETRASADO"
    FINALIZADO = "FINALIZADO"


class TipoIndicadorAvance(str, Enum):
    """Métricas cuantitativas utilizadas para evaluar el cumplimiento del objetivo."""
    HORAS_ENTRENADAS = "HORAS_ENTRENADAS"
    RATING = "RATING"
    TAREAS = "TAREAS"
    TORNEOS = "TORNEOS"
    MEDALLAS = "MEDALLAS"


@dataclass(frozen=True)
class IndicadorAvance:
    """Representa una medición concreta de avance hacia la meta."""
    tipo: TipoIndicadorAvance
    valor_actual: float
    valor_esperado: float

    def porcentaje(self) -> float:
        """Calcula el porcentaje de progreso de 0 a 100%."""
        if self.valor_esperado <= 0:
            return 0.0
        return min(100.0, (self.valor_actual / self.valor_esperado) * 100)


@dataclass
class ObjetivoSMART:
    """Entidad de Dominio para Objetivos SMART (RF-03).
    
    Aplica en __post_init__ la obligatoriedad estricta de fecha_inicio y fecha_limite (RF-03.3).
    """
    # Atributos esenciales
    id_atleta: Union[int, str]
    descripcion: str
    fecha_inicio: date             # Fecha obligatoria de inicio (RF-03.3)
    fecha_limite: date             # Fecha obligatoria de finalización (RF-03.3)

    # Atributos del modelo con valores por defecto
    rating_actual: int = 0         # Puntuación Elo inicial (RF-03.1)
    rating_meta: int = 0           # Puntuación Elo meta (RF-03.1)
    id: Optional[Union[int, str]] = None
    id_objetivo: Optional[int] = None
    titulo: str = ""
    indicador_meta: TipoIndicadorAvance = TipoIndicadorAvance.RATING
    valor_meta: float = 0.0
    porcentaje_avance: float = 0.0
    estado: EstadoObjetivo = EstadoObjetivo.PENDIENTE_APROBACION
    aprobado_por_entrenador: bool = False
    cumplido_por_entrenador: bool = False
    creado_por: Optional[str] = None
    fecha_registro: Optional[Union[date, datetime]] = None
    avances: list[IndicadorAvance] = field(default_factory=list)

    def __post_init__(self):
        """Invariante de dominio: valida obligatoriedad y coherencia de fechas (RF-03.3).
        
        Garantiza que ningún objeto ObjetivoSMART pueda existir en memoria
        con fechas nulas, vacías o cronológicamente invertidas.
        """
        # Sincronizar identificadores para compatibilidad entre esquemas
        if self.id is not None and self.id_objetivo is None and isinstance(self.id, int):
            self.id_objetivo = self.id
        elif self.id_objetivo is not None and self.id is None:
            self.id = self.id_objetivo

        # Validación estricta y exclusiva de fechas según el requerimiento RF-03.3
        self.fecha_inicio, self.fecha_limite = ObjetivoSMARTValidator.validar_fechas(
            self.fecha_inicio, self.fecha_limite
        )


# Alias para retrocompatibilidad
ObjetivoSmart = ObjetivoSMART
