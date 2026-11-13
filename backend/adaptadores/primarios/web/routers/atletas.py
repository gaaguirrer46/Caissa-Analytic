"""Endpoints de Atletas para Caissa Analytic."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from infraestructura.dependencias.contenedor import Contenedor
from dominio.atletas.entidades import Atleta, Rating, PerfilHistorico

router = APIRouter(prefix="/api/v1/atletas", tags=["Atletas"])
contenedor = Contenedor()

# --- Schemas ---

class RatingSchema(BaseModel):
    clasicas: Optional[int] = None
    rapidas: Optional[int] = None
    blitz: Optional[int] = None
    chess_com: Optional[int] = None
    lichess: Optional[int] = None
    fecha_actualizacion: Optional[str] = None

class PerfilHistoricoSchema(BaseModel):
    id: int
    id_atleta: int
    anio: int
    torneo: Optional[str] = None
    rating: RatingSchema
    observaciones: str = ""

class AtletaResumenSchema(BaseModel):
    id: int
    nombre: string = Field(..., alias="nombre")
    fecha_nacimiento: str
    edad: int
    sexo: str
    identidad_opcional: Optional[str] = None
    federacion: Optional[str] = None
    universidad: Optional[str] = None
    institucion: Optional[str] = None
    carrera: Optional[str] = None
    categorias: List[int] = []
    clubs: List[str] = []
    rating_actual: RatingSchema
    activo: bool

class AtletaDetalleSchema(AtletaResumenSchema):
    historial: List[PerfilHistoricoSchema] = []

class AtletaCrearSchema(BaseModel):
    nombre: str
    fecha_nacimiento: date
    sexo: str
    identidad_opcional: Optional[str] = None
    federacion: Optional[str] = "Federación Nacional de Ajedrez"
    universidad: Optional[str] = None
    carrera: Optional[str] = None
    clubs: List[str] = []
    rating_clasicas: Optional[int] = 1500
    rating_rapidas: Optional[int] = 1500
    rating_blitz: Optional[int] = 1500

class ActualizarRatingSchema(BaseModel):
    clasicas: Optional[int] = None
    rapidas: Optional[int] = None
    blitz: Optional[int] = None
    chess_com: Optional[int] = None
    lichess: Optional[int] = None


def _mapear_atleta(atleta: Atleta) -> Dict[str, Any]:
    hoy = date.today()
    edad = atleta.edad(hoy) if hasattr(atleta, "edad") else 20
    return {
        "id": atleta.id,
        "nombre": atleta.nombre,
        "fecha_nacimiento": atleta.fecha_nacimiento.isoformat() if isinstance(atleta.fecha_nacimiento, date) else str(atleta.fecha_nacimiento),
        "edad": edad,
        "sexo": atleta.sexo,
        "identidad_opcional": atleta.identidad_opcional,
        "federacion": atleta.federacion,
        "universidad": atleta.universidad,
        "institucion": atleta.institucion,
        "carrera": atleta.carrera,
        "categorias": atleta.categorias,
        "clubs": atleta.clubs,
        "rating_actual": {
            "clasicas": atleta.rating_actual.clasicas,
            "rapidas": atleta.rating_actual.rapidas,
            "blitz": atleta.rating_actual.blitz,
            "chess_com": atleta.rating_actual.chess_com,
            "lichess": atleta.rating_actual.lichess,
            "fecha_actualizacion": atleta.rating_actual.fecha_actualizacion.isoformat() if atleta.rating_actual.fecha_actualizacion else None,
        },
        "historial": [
            {
                "id": h.id,
                "id_atleta": h.id_atleta,
                "anio": h.anio,
                "torneo": h.torneo,
                "rating": {
                    "clasicas": h.rating.clasicas,
                    "rapidas": h.rating.rapidas,
                    "blitz": h.rating.blitz,
                },
                "observaciones": h.observaciones,
            }
            for h in getattr(atleta, "historial", [])
        ],
        "activo": atleta.activo,
    }


# --- Endpoints ---

@router.get("", response_model=List[Dict[str, Any]])
def listar_atletas(
    q: Optional[str] = Query(None, description="Término de búsqueda por nombre, club o universidad"),
    sexo: Optional[str] = Query(None, description="Filtrar por sexo: M o F"),
):
    """Retorna la lista de atletas activos con filtros opcionales."""
    atletas = contenedor.repo_atletas.listar_activos()
    resultado = [_mapear_atleta(a) for a in atletas]

    if q:
        q_lower = q.lower()
        resultado = [
            a for a in resultado
            if q_lower in a["nombre"].lower()
            or (a["universidad"] and q_lower in a["universidad"].lower())
            or any(q_lower in c.lower() for c in a["clubs"])
        ]

    if sexo and sexo.upper() != "TODOS":
        sexo_norm = "MASCULINO" if sexo.upper() in ["M", "MASCULINO"] else "FEMENINO"
        resultado = [
            a for a in resultado
            if a["sexo"].upper() in [sexo.upper(), sexo_norm]
        ]

    return resultado


@router.get("/{id_atleta}", response_model=Dict[str, Any])
def obtener_atleta(id_atleta: int):
    """Retorna el expediente completo de un atleta por su ID."""
    atleta = contenedor.repo_atletas.buscar_por_id(id_atleta)
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta con ID {id_atleta} no encontrado",
        )
    return _mapear_atleta(atleta)


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_atleta(datos: AtletaCrearSchema):
    """Registra un nuevo atleta en la base de datos."""
    nuevo_atleta = Atleta(
        id=0,
        nombre=datos.nombre,
        fecha_nacimiento=datos.fecha_nacimiento,
        sexo=datos.sexo.upper(),
        identidad_opcional=datos.identidad_opcional,
        federacion=datos.federacion,
        universidad=datos.universidad,
        carrera=datos.carrera,
        clubs=datos.clubs,
        rating_actual=Rating(
            clasicas=datos.rating_clasicas,
            rapidas=datos.rating_rapidas,
            blitz=datos.rating_blitz,
            fecha_actualizacion=date.today(),
        ),
        activo=True,
    )
    atleta_guardado = contenedor.repo_atletas.guardar(nuevo_atleta)
    return _mapear_atleta(atleta_guardado)

