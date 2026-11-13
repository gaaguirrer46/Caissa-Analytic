"""Endpoints de Planes y Sesiones de Entrenamiento para Caissa Analytic."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from infraestructura.dependencias.contenedor import Contenedor
from dominio.entrenamientos.entidades import (
    PlanEntrenamientoSemanal,
    SesionEntrenamiento,
    TipoEntrenamiento,
    EstadoSesion,
)

router = APIRouter(prefix="/api/v1/entrenamientos", tags=["Entrenamientos"])
contenedor = Contenedor()

# --- Schemas ---

class SesionCrearSchema(BaseModel):
    id_plan: int
    tipo: str = "TACTICA"
    dia_semana: str = "LUNES"
    horas_planificadas: float = 2.0
    observaciones: Optional[str] = ""

class PlanCrearSchema(BaseModel):
    id_atleta: int
    semana: int
    anio: int = 2026


def _mapear_sesion(s: SesionEntrenamiento) -> Dict[str, Any]:
    return {
        "id": s.id,
        "tipo": s.tipo.value if hasattr(s.tipo, "value") else str(s.tipo),
        "dia_semana": s.dia_semana,
        "horas_planificadas": s.horas_planificadas,
        "horas_ejecutadas": s.horas_ejecutadas or 0.0,
        "estado": s.estado.value if hasattr(s.estado, "value") else str(s.estado),
        "ejecucion_aprobada": s.ejecucion_aprobada,
        "observaciones": s.observaciones,
    }


def _mapear_plan(p: PlanEntrenamientoSemanal) -> Dict[str, Any]:
    atleta = contenedor.repo_atletas.buscar_por_id(p.id_atleta)
    nombre_atleta = atleta.nombre if atleta else f"Atleta #{p.id_atleta}"

    total_plan = sum(s.horas_planificadas for s in p.sesiones)
    total_ejec = sum((s.horas_ejecutadas or 0.0) for s in p.sesiones if s.ejecucion_aprobada)
    pct = round((total_ejec / total_plan * 100), 1) if total_plan > 0 else 0.0

    return {
        "id": p.id,
        "id_atleta": p.id_atleta,
        "nombre_atleta": nombre_atleta,
        "semana": p.semana,
        "anio": p.anio,
        "total_horas_planificadas": total_plan,
        "total_horas_ejecutadas": total_ejec,
        "cumplimiento_pct": pct,
        "sesiones": [_mapear_sesion(s) for s in p.sesiones],
    }


# --- Endpoints ---

@router.get("", response_model=List[Dict[str, Any]])
def listar_planes(
    id_atleta: Optional[int] = Query(None, description="Filtrar por ID del atleta"),
    semana: Optional[int] = Query(None, description="Filtrar por número de semana"),
):
    """Retorna los planes semanales de entrenamiento con sus sesiones registradas."""
    planes_lista = []
    if id_atleta:
        planes_lista = contenedor.repo_entrenamientos.listar_por_atleta(id_atleta)
    elif semana:
        planes_lista = contenedor.repo_entrenamientos.listar_por_semana(semana, 2026)
    else:
        # Obtener para todos los atletas activos
        atletas = contenedor.repo_atletas.listar_activos()
        for at in atletas:
            planes_lista.extend(contenedor.repo_entrenamientos.listar_por_atleta(at.id))

    return [_mapear_plan(p) for p in planes_lista]


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_plan(datos: PlanCrearSchema):
    """Crea una nueva semana de entrenamiento para un atleta."""
    cursor = contenedor.conexion.cursor()
    cursor.execute(
        "INSERT INTO planes_entrenamiento (id_atleta, semana, anio) VALUES (?, ?, ?)",
        (datos.id_atleta, datos.semana, datos.anio),
    )
    contenedor.conexion.commit()
    nuevo_id = cursor.lastrowid
    plan_obj = contenedor.repo_entrenamientos.buscar_por_id(nuevo_id)
    return _mapear_plan(plan_obj) if plan_obj else {"id": nuevo_id}


@router.post("/sesion", status_code=status.HTTP_201_CREATED)
def agregar_sesion(datos: SesionCrearSchema):
    """Añade una sesión a un plan semanal."""
    cursor = contenedor.conexion.cursor()
    cursor.execute(
        """
        INSERT INTO sesiones_entrenamiento (id_plan, tipo, dia_semana, horas_planificadas, horas_ejecutadas, estado, ejecucion_aprobada, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datos.id_plan,
            datos.tipo.upper(),
            datos.dia_semana.upper(),
            datos.horas_planificadas,
            0.0,
            "PROGRAMADA",
            0,
            datos.observaciones or "",
        ),
    )
    contenedor.conexion.commit()
    return {"status": "ok", "id_sesion": cursor.lastrowid}
