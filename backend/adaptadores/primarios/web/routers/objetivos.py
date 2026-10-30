"""Endpoints de Objetivos SMART (RF-03.5 / RF-03.6) para Caissa Analytic."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from infraestructura.dependencias.contenedor import Contenedor
from dominio.objetivos.entidades import ObjetivoSmart, TipoIndicadorAvance, EstadoObjetivo

router = APIRouter(prefix="/api/v1/objetivos", tags=["Objetivos SMART"])
contenedor = Contenedor()

# --- Schemas ---

class ObjetivoSmartSchema(BaseModel):
    id: int
    id_atleta: int
    descripcion: str
    indicador_meta: str
    valor_meta: float
    rating_actual: int
    rating_meta: int
    fecha_inicio: str
    fecha_limite: str
    porcentaje_avance: float
    estado: str
    color_semaforo: str
    supera_umbral_temporal: bool

class ObjetivoCrearSchema(BaseModel):
    id_atleta: int
    descripcion: str
    indicador_meta: str = "RATING"
    valor_meta: float = 2100.0
    rating_actual: int = 2000
    rating_meta: int = 2100
    fecha_inicio: date = Field(default_factory=date.today)
    fecha_limite: date


def _mapear_objetivo(obj: ObjetivoSmart) -> Dict[str, Any]:
    return {
        "id": obj.id,
        "id_atleta": obj.id_atleta,
        "descripcion": obj.descripcion,
        "indicador_meta": obj.indicador_meta.value if hasattr(obj.indicador_meta, "value") else str(obj.indicador_meta),
        "valor_meta": obj.valor_meta,
        "rating_actual": obj.rating_actual,
        "rating_meta": obj.rating_meta,
        "fecha_inicio": obj.fecha_inicio.isoformat() if isinstance(obj.fecha_inicio, date) else str(obj.fecha_inicio),
        "fecha_limite": obj.fecha_limite.isoformat() if isinstance(obj.fecha_limite, date) else str(obj.fecha_limite),
        "porcentaje_avance": round(obj.porcentaje_avance, 1),
        "estado": obj.estado.value if hasattr(obj.estado, "value") else str(obj.estado),
        "color_semaforo": obj.color_semaforo if hasattr(obj, "color_semaforo") else "VERDE",
        "supera_umbral_temporal": obj.supera_umbral_temporal() if hasattr(obj, "supera_umbral_temporal") else True,
    }


# --- Endpoints ---

@router.get("", response_model=List[Dict[str, Any]])
def listar_objetivos(
    id_atleta: Optional[int] = Query(None, description="Filtrar por atleta"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
):
    """Retorna los objetivos SMART registrados con su cálculo de avance."""
    if id_atleta:
        objetivos = contenedor.repo_objetivos.buscar_por_atleta(id_atleta)
    elif estado:
        try:
            est_enum = EstadoObjetivo(estado.upper())
            objetivos = contenedor.repo_objetivos.listar_por_estado(est_enum)
        except ValueError:
            objetivos = contenedor.repo_objetivos.buscar_por_atleta(1)
    else:
        # Por defecto listar los del atleta activo principal
        objetivos = contenedor.repo_objetivos.buscar_por_atleta(1)

    return [_mapear_objetivo(o) for o in objetivos]


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_objetivo(datos: ObjetivoCrearSchema):
    """Crea un nuevo objetivo SMART (RF-03.5 / RF-03.6)."""
    try:
        ind_enum = TipoIndicadorAvance(datos.indicador_meta.upper())
    except ValueError:
        ind_enum = TipoIndicadorAvance.RATING

    nuevo = ObjetivoSmart(
        id=0,
        id_atleta=datos.id_atleta,
        descripcion=datos.descripcion,
        indicador_meta=ind_enum,
        valor_meta=datos.valor_meta,
        rating_actual=datos.rating_actual,
        rating_meta=datos.rating_meta,
        fecha_inicio=datos.fecha_inicio,
        fecha_limite=datos.fecha_limite,
        porcentaje_avance=0.0,
        estado=EstadoObjetivo.EN_PROCESO,
        aprobado_por_entrenador=True,
    )
    guardado = contenedor.repo_objetivos.guardar(nuevo)
    return _mapear_objetivo(guardado)

