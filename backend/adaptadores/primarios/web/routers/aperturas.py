"""Endpoints de Repertorio de Aperturas para Caissa Analytic."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query, status, HTTPException
from pydantic import BaseModel, Field

from infraestructura.dependencias.contenedor import Contenedor
from dominio.aperturas.entidades import AperturaRepertorio, ColorApertura, EstadoApertura, ClasificacionUso, NivelDominio

router = APIRouter(prefix="/api/v1/aperturas", tags=["Aperturas"])
contenedor = Contenedor()

# --- Schemas ---

class AperturaCrearSchema(BaseModel):
    id_atleta: int
    codigo_eco: str
    nombre: str
    variante: Optional[str] = ""
    color: str = "BLANCAS"
    estado: str = "EN_ESTUDIO"
    nivel_dominio: str = "INTERMEDIO"
    fuente_estudio: Optional[str] = ""
    observaciones: Optional[str] = ""
    clasificacion_uso: str = "PRINCIPAL"


def _mapear_apertura(a: AperturaRepertorio) -> Dict[str, Any]:
    stats = contenedor.repo_aperturas.buscar_estadistica(a.id)
    partidas = stats.partidas_jugadas if stats else 0
    victorias = stats.victorias if stats else 0
    empates = stats.empates if stats else 0
    derrotas = stats.derrotas if stats else 0
    accuracy = stats.accuracy_promedio if stats else 90.0
    acpl = stats.acpl_promedio if stats else 20.0
    errores = stats.errores_frecuentes if stats else 0
    eval_motor = stats.evaluacion_motor_promedio if stats else 0.3

    puntos = victorias + (empates * 0.5)
    rendimiento = round((puntos / partidas * 100), 1) if partidas > 0 else 0.0

    efectividad_str = "MUY_EFECTIVA" if rendimiento >= 70 else "EFECTIVA" if rendimiento >= 50 else "REQUIERE_REVISION"

    return {
        "id": a.id,
        "id_atleta": a.id_atleta,
        "codigo_eco": a.codigo_eco,
        "nombre": a.nombre,
        "variante": a.variante,
        "color": a.color.value if hasattr(a.color, "value") else str(a.color),
        "estado": a.estado.value if hasattr(a.estado, "value") else str(a.estado),
        "nivel_dominio": a.nivel_dominio.value if hasattr(a.nivel_dominio, "value") else str(a.nivel_dominio),
        "clasificacion_uso": a.clasificacion_uso.value if hasattr(a.clasificacion_uso, "value") else str(a.clasificacion_uso),
        "fuente_estudio": a.fuente_estudio,
        "observaciones": a.observaciones,
        "partidas_jugadas": partidas,
        "victorias": victorias,
        "empates": empates,
        "derrotas": derrotas,
        "rendimiento_pct": rendimiento,
        "accuracy_promedio": accuracy,
        "acpl_promedio": acpl,
        "errores_frecuentes": errores,
        "evaluacion_motor": eval_motor,
        "efectividad": efectividad_str,
    }


# --- Endpoints ---

@router.get("", response_model=List[Dict[str, Any]])
def listar_aperturas(
    id_atleta: Optional[int] = Query(None, description="Filtrar por atleta"),
    color: Optional[str] = Query(None, description="Filtrar por color: BLANCAS o NEGRAS"),
    eco: Optional[str] = Query(None, description="Filtrar por código ECO"),
):
    """Retorna las aperturas del repertorio registradas en SQLite."""
    aperturas_lista = []
    if id_atleta:
        aperturas_lista = contenedor.repo_aperturas.listar_por_atleta(id_atleta)
    else:
        # Listar de todos los atletas activos
        atletas = contenedor.repo_atletas.listar_activos()
        for at in atletas:
            aperturas_lista.extend(contenedor.repo_aperturas.listar_por_atleta(at.id))

    resultado = [_mapear_apertura(a) for a in aperturas_lista]

    if color and color.upper() != "TODOS":
        resultado = [a for a in resultado if a["color"].upper() == color.upper()]

    if eco:
        resultado = [a for a in resultado if eco.upper() in a["codigo_eco"].upper()]

    return resultado


@router.post("", status_code=status.HTTP_201_CREATED)
def agregar_apertura_repertorio(datos: AperturaCrearSchema):
    """Añade una nueva apertura al repertorio del atleta."""
    col_enum = ColorApertura.BLANCAS if datos.color.upper() == "BLANCAS" else ColorApertura.NEGRAS
    nueva = AperturaRepertorio(
        id=0,
        id_atleta=datos.id_atleta,
        codigo_eco=datos.codigo_eco.upper(),
        nombre=datos.nombre,
        variante=datos.variante or "",
        color=col_enum,
        estado=EstadoApertura(datos.estado) if hasattr(EstadoApertura, datos.estado) else EstadoApertura.EN_ESTUDIO,
        nivel_dominio=NivelDominio(datos.nivel_dominio) if hasattr(NivelDominio, datos.nivel_dominio) else NivelDominio.INTERMEDIO,
        fuente_estudio=datos.fuente_estudio or "",
        observaciones=datos.observaciones or "",
        clasificacion_uso=ClasificacionUso(datos.clasificacion_uso) if hasattr(ClasificacionUso, datos.clasificacion_uso) else ClasificacionUso.PRINCIPAL,
    )
    guardada = contenedor.repo_aperturas.guardar(nueva)
    return _mapear_apertura(guardada)
