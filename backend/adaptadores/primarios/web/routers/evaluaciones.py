"""Endpoints de Evaluaciones Técnicas del DT para Caissa Analytic."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from infraestructura.dependencias.contenedor import Contenedor
from dominio.evaluaciones.entidades import (
    EvaluacionAtleta,
    PeriodoEvaluacion,
    TipoIndicadorEvaluacion,
)
from dominio.comun.acceso import Solicitante
from dominio.usuarios.entidades import Rol

router = APIRouter(prefix="/api/v1/evaluaciones", tags=["Evaluaciones"])
contenedor = Contenedor()

# --- Schemas ---

class EvaluacionCrearSchema(BaseModel):
    id_atleta: int
    id_entrenador: int = 1
    periodo: str = "MES"
    referencia_periodo: str
    fecha_realizacion: Optional[str] = None
    calificaciones: Dict[str, int]
    fortalezas: Optional[str] = ""
    aspectos_por_mejorar: Optional[str] = ""
    recomendaciones: Optional[str] = ""
    es_autoevaluacion: bool = False


def _obtener_nombre_atleta(id_atleta: int) -> str:
    try:
        atleta = contenedor.repo_atletas.buscar_por_id(id_atleta)
        return atleta.nombre if atleta else f"Atleta #{id_atleta}"
    except Exception:
        return f"Atleta #{id_atleta}"


def _mapear_evaluacion(e: EvaluacionAtleta) -> Dict[str, Any]:
    califs = {
        (k.value if hasattr(k, "value") else str(k)): v
        for k, v in e.calificaciones.items()
    }
    prom = e.promedio_calificaciones
    return {
        "id": e.id,
        "id_atleta": e.id_atleta,
        "nombre_atleta": _obtener_nombre_atleta(e.id_atleta),
        "id_entrenador": e.id_entrenador,
        "periodo": e.periodo.value if hasattr(e.periodo, "value") else str(e.periodo),
        "referencia_periodo": e.referencia_periodo,
        "fecha_realizacion": (
            e.fecha_realizacion.isoformat()
            if isinstance(e.fecha_realizacion, (date,))
            else str(e.fecha_realizacion)
        ),
        "promedio": round(prom, 2),
        "calificaciones": califs,
        "fortalezas": e.fortalezas,
        "aspectos_por_mejorar": e.aspectos_por_mejorar,
        "recomendaciones": e.recomendaciones,
        "es_autoevaluacion": e.es_autoevaluacion,
    }


# --- Endpoints ---

@router.get("", response_model=List[Dict[str, Any]])
def listar_evaluaciones(
    id_atleta: Optional[int] = Query(None, description="Filtrar por ID de atleta"),
    periodo: Optional[str] = Query(None, description="Filtrar por período (TORNEO, MES, MESOCICLO, ANIO)"),
):
    """Lista las evaluaciones técnicas registradas con filtros opcionales."""
    try:
        if id_atleta is not None:
            if periodo:
                periodo_enum = PeriodoEvaluacion(periodo.upper())
                evals = contenedor.repo_evaluaciones.listar_por_periodo(id_atleta, periodo_enum)
            else:
                evals = contenedor.repo_evaluaciones.listar_por_atleta(id_atleta)
        else:
            # Traer todas las evaluaciones de todos los atletas registrados
            cursor = contenedor.conexion.cursor()
            cursor.execute("SELECT id FROM evaluaciones_atleta ORDER BY fecha_realizacion DESC, id DESC")
            filas = cursor.fetchall()
            evals = [contenedor.repo_evaluaciones.buscar_por_id(f[0]) for f in filas if f[0]]
            evals = [e for e in evals if e is not None]

        return [_mapear_evaluacion(e) for e in evals]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar evaluaciones: {str(e)}")


@router.get("/resumen/{id_atleta}", response_model=Dict[str, Any])
def obtener_resumen_atleta(id_atleta: int):
    """Calcula y devuelve la síntesis ejecutiva y analítica de evaluaciones del atleta."""
    try:
        solicitante_dt = Solicitante(id_usuario=1, rol=Rol.ENTRENADOR)
        resumen = contenedor.resumir_evaluaciones.ejecutar(id_atleta, solicitante=solicitante_dt)

        prom_por_ind = {
            (k.value if hasattr(k, "value") else str(k)): round(v, 2)
            for k, v in resumen.promedio_por_indicador.items()
        }
        var_por_ind = {
            (k.value if hasattr(k, "value") else str(k)): round(v, 2)
            for k, v in resumen.variaciones_por_indicador.items()
        }
        areas_mejora = [
            (i.value if hasattr(i, "value") else str(i))
            for i in resumen.areas_de_mejora
        ]

        return {
            "id_atleta": id_atleta,
            "nombre_atleta": _obtener_nombre_atleta(id_atleta),
            "cantidad_evaluaciones": resumen.cantidad_evaluaciones,
            "ultima_evaluacion": (
                resumen.ultima_evaluacion.isoformat()
                if resumen.ultima_evaluacion
                else None
            ),
            "promedio_general": round(resumen.promedio_general, 2),
            "promedio_por_indicador": prom_por_ind,
            "areas_de_mejora": areas_mejora,
            "variacion_ultimo_ciclo": round(resumen.variacion_ultimo_ciclo, 2),
            "variaciones_por_indicador": var_por_ind,
            "recomendaciones_consolidadas": resumen.recomendaciones_consolidadas,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular resumen: {str(e)}")


@router.get("/{id_evaluacion}", response_model=Dict[str, Any])
def obtener_evaluacion_detalle(id_evaluacion: int):
    """Consulta el detalle completo de una evaluación individual."""
    evaluacion = contenedor.repo_evaluaciones.buscar_por_id(id_evaluacion)
    if not evaluacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluación con ID {id_evaluacion} no encontrada.",
        )
    return _mapear_evaluacion(evaluacion)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def crear_nueva_evaluacion(payload: EvaluacionCrearSchema):
    """Crea y registra una nueva evaluación técnica del DT."""
    try:
        periodo_enum = PeriodoEvaluacion(payload.periodo.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Período inválido: {payload.periodo}. Opciones: TORNEO, MES, MESOCICLO, ANIO",
        )

    calificaciones_enum: Dict[TipoIndicadorEvaluacion, int] = {}
    for ind_str, nota in payload.calificaciones.items():
        try:
            ind_enum = TipoIndicadorEvaluacion(ind_str.upper())
            calificaciones_enum[ind_enum] = max(1, min(10, int(nota)))
        except ValueError:
            pass

    # Asegurar que los 8 indicadores estén presentes
    for ind in TipoIndicadorEvaluacion:
        if ind not in calificaciones_enum:
            calificaciones_enum[ind] = 8

    fecha_real = date.fromisoformat(payload.fecha_realizacion) if payload.fecha_realizacion else date.today()

    eval_entidad = EvaluacionAtleta(
        id=0,
        id_atleta=payload.id_atleta,
        id_entrenador=payload.id_entrenador,
        periodo=periodo_enum,
        referencia_periodo=payload.referencia_periodo,
        fecha_realizacion=fecha_real,
        calificaciones=calificaciones_enum,
        fortalezas=payload.fortalezas or "",
        aspectos_por_mejorar=payload.aspectos_por_mejorar or "",
        recomendaciones=payload.recomendaciones or "",
        es_autoevaluacion=payload.es_autoevaluacion,
    )

    try:
        guardada = contenedor.repo_evaluaciones.guardar(eval_entidad)
        return _mapear_evaluacion(guardada)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar la evaluación: {str(e)}",
        )
