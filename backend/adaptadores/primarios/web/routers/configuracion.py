"""Endpoints de Configuración del Sistema y Parámetros del Club para Caissa Analytic."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from infraestructura.dependencias.contenedor import Contenedor
from dominio.configuracion.entidades import ConfiguracionSistema
from dominio.usuarios.entidades import Rol
from dominio.comun.acceso import Solicitante

router = APIRouter(prefix="/api/v1/configuracion", tags=["Configuración"])
contenedor = Contenedor()

# --- Schemas ---

class ConfiguracionActualizarSchema(BaseModel):
    maximo_atletas_por_entrenador: int = Field(default=40, ge=1, le=1000)
    minimo_entrenadores_por_atleta: int = Field(default=1, ge=1, le=10)
    maximo_entrenadores_por_atleta: int = Field(default=3, ge=1, le=20)
    permitir_autoevaluacion: bool = True
    rangos_evaluacion: Dict[str, List[float]] = Field(default_factory=dict)
    secciones_autorizadas_invitado: List[str] = Field(default_factory=list)
    actualizado_por: str = "entrenador.magnus@caissa.org"


class AccesoInvitadoSchema(BaseModel):
    secciones: List[str]
    id_usuario: int = 1


def _mapear_configuracion(c: ConfiguracionSistema) -> Dict[str, Any]:
    rangos = {k: list(v) for k, v in c.rangos_evaluacion.items()}
    return {
        "maximo_atletas_por_entrenador": c.maximo_atletas_por_entrenador,
        "minimo_entrenadores_por_atleta": c.minimo_entrenadores_por_atleta,
        "maximo_entrenadores_por_atleta": c.maximo_entrenadores_por_atleta,
        "permitir_autoevaluacion": c.permitir_autoevaluacion,
        "rangos_evaluacion": rangos,
        "secciones_autorizadas_invitado": list(c.secciones_autorizadas_invitado),
        "actualizado_por": c.actualizado_por,
        "fecha_actualizacion": (
            c.fecha_actualizacion.isoformat()
            if hasattr(c.fecha_actualizacion, "isoformat")
            else str(c.fecha_actualizacion)
        ),
        # Metadatos del club e infraestructura
        "nombre_club": "Caissa Analytic Club & Performance Center",
        "federacion": "FIDE (Federación Internacional de Ajedrez)",
        "temporada_activa": "Ciclo Federativo 2026-I",
        "motor_stockfish": {
            "version": "Stockfish 16.1 NNUE",
            "profundidad_defecto": 18,
            "hilos_cpu": 4,
            "hash_mb": 256,
        },
    }


# --- Endpoints ---

@router.get("", response_model=Dict[str, Any])
def consultar_configuracion():
    """Consulta los parámetros operativos, límites y rangos de evaluación vigentes."""
    try:
        conf = contenedor.consultar_configuracion.ejecutar(Rol.ENTRENADOR)
        return _mapear_configuracion(conf)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al consultar configuración: {str(e)}"
        )


@router.put("", response_model=Dict[str, Any])
def actualizar_configuracion(payload: ConfiguracionActualizarSchema):
    """Actualiza los límites operativos, semáforos de evaluación y parámetros del sistema."""
    try:
        # Convertir rangos a tuplas (excelente, bueno, aceptable)
        rangos_tuplas: Dict[str, tuple] = {}
        for clave, vals in payload.rangos_evaluacion.items():
            if len(vals) == 3:
                rangos_tuplas[clave] = tuple(float(x) for x in vals)

        nueva_entidad = ConfiguracionSistema(
            maximo_atletas_por_entrenador=payload.maximo_atletas_por_entrenador,
            minimo_entrenadores_por_atleta=payload.minimo_entrenadores_por_atleta,
            maximo_entrenadores_por_atleta=payload.maximo_entrenadores_por_atleta,
            permitir_autoevaluacion=payload.permitir_autoevaluacion,
            rangos_evaluacion=rangos_tuplas,
            secciones_autorizadas_invitado=tuple(payload.secciones_autorizadas_invitado),
            actualizado_por=payload.actualizado_por,
        )

        guardada = contenedor.actualizar_configuracion.ejecutar(
            nueva_entidad, rol_usuario=Rol.ENTRENADOR
        )

        # Registrar evento de auditoría
        contenedor.registrar_cambio.ejecutar(
            usuario=payload.actualizado_por,
            entidad_afectada="ConfiguracionSistema",
            tipo_operacion="MODIFICAR",
            campo_modificado="parametros_generales",
            valor_anterior="Configuración previa",
            valor_nuevo="Límites y rangos actualizados",
        )

        return _mapear_configuracion(guardada)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar configuración: {str(e)}",
        )


@router.put("/acceso-invitado", response_model=Dict[str, Any])
def configurar_acceso_invitado(payload: AccesoInvitadoSchema):
    """Configura las secciones públicas visibles para el rol Invitado."""
    try:
        solicitante = Solicitante(id_usuario=payload.id_usuario, rol=Rol.ENTRENADOR)
        guardada = contenedor.configurar_acceso_invitado.ejecutar(
            payload.secciones, solicitante=solicitante
        )
        return _mapear_configuracion(guardada)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al configurar acceso de invitado: {str(e)}",
        )
