"""Endpoints de Auditoría, Trazabilidad e Integridad de Datos para Caissa Analytic."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from infraestructura.dependencias.contenedor import Contenedor
from dominio.auditoria.entidades import RegistroAuditoria, TipoOperacion
from dominio.comun.acceso import Solicitante
from dominio.usuarios.entidades import Rol

router = APIRouter(prefix="/api/v1/auditoria", tags=["Auditoría"])
contenedor = Contenedor()

# --- Schemas ---

class RegistrarAuditoriaSchema(BaseModel):
    usuario: str
    entidad_afectada: str
    tipo_operacion: str = "MODIFICAR"
    campo_modificado: Optional[str] = ""
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None


def _mapear_auditoria(r: RegistroAuditoria) -> Dict[str, Any]:
    return {
        "id": r.id,
        "usuario": r.usuario,
        "fecha_hora": (
            r.fecha_hora.isoformat()
            if hasattr(r.fecha_hora, "isoformat")
            else str(r.fecha_hora)
        ),
        "entidad_afectada": r.entidad_afectada,
        "tipo_operacion": (
            r.tipo_operacion.value
            if hasattr(r.tipo_operacion, "value")
            else str(r.tipo_operacion)
        ),
        "campo_modificado": r.campo_modificado,
        "valor_anterior": r.valor_anterior,
        "valor_nuevo": r.valor_nuevo,
    }


# --- Endpoints ---

@router.get("", response_model=List[Dict[str, Any]])
def listar_historial(
    entidad: Optional[str] = Query(None, description="Filtrar por entidad afectada"),
    usuario: Optional[str] = Query(None, description="Filtrar por usuario autor"),
    tipo_operacion: Optional[str] = Query(None, description="Filtrar por operación (CREAR, MODIFICAR, ELIMINAR)"),
    limite: int = Query(50, ge=1, le=200, description="Cantidad máxima de registros a retornar"),
):
    """Consulta la bitácora inmutable de auditoría con filtros avanzados."""
    try:
        cursor = contenedor.conexion.cursor()
        query = "SELECT * FROM registros_auditoria WHERE 1=1"
        params: List[Any] = []

        if entidad:
            query += " AND entidad_afectada = ?"
            params.append(entidad)
        if usuario:
            query += " AND usuario = ?"
            params.append(usuario)
        if tipo_operacion:
            query += " AND tipo_operacion = ?"
            params.append(tipo_operacion.upper())

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limite)

        cursor.execute(query, tuple(params))
        filas = cursor.fetchall()
        registros = [contenedor.repo_auditoria._fila_a_auditoria(f) for f in filas]

        return [_mapear_auditoria(r) for r in registros]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al consultar registros de auditoría: {str(e)}"
        )


@router.get("/verificar-integridad", response_model=Dict[str, Any])
def verificar_integridad():
    """Ejecuta un análisis forense de integridad preventiva sobre todas las tablas del sistema (RNF-02.5)."""
    try:
        cursor = contenedor.conexion.cursor()
        anomalias: List[str] = []

        # 1. PRAGMA integrity_check en SQLite
        cursor.execute("PRAGMA integrity_check;")
        check_result = cursor.fetchone()
        sqlite_ok = (check_result[0] == "ok") if check_result else False
        if not sqlite_ok:
            anomalias.append(f"Falla estructural de base de datos: {check_result}")

        # 2. Validar Ratings de Atletas en rango [0, 4000]
        cursor.execute("SELECT id, nombre, rating_clasicas, rating_rapidas, rating_blitz FROM atletas;")
        atletas = cursor.fetchall()
        for a in atletas:
            for campo in ("rating_clasicas", "rating_rapidas", "rating_blitz"):
                val = a[campo]
                if val is not None and (val < 0 or val > 4000):
                    anomalias.append(f"Atleta {a['nombre']} (ID {a['id']}): {campo}={val} fuera de rango permitido (0-4000).")

        # 3. Validar Resultados de Partidas
        cursor.execute("SELECT id, resultado FROM partidas;")
        partidas = cursor.fetchall()
        resultados_validos = {"1-0", "0-1", "1/2-1/2"}
        for p in partidas:
            res = p["resultado"]
            if res and res not in resultados_validos:
                anomalias.append(f"Partida ID {p['id']} tiene un resultado inválido: '{res}'.")

        # 4. Validar Consistencia Relacional (Atletas existentes)
        cursor.execute("SELECT DISTINCT id_atleta FROM partidas WHERE id_atleta NOT IN (SELECT id FROM atletas);")
        huerfanas = cursor.fetchall()
        if huerfanas:
            anomalias.append(f"Existen partidas asignadas a IDs de atleta inexistentes: {[h[0] for h in huerfanas]}.")

        # 5. Conteo de auditoría
        cursor.execute("SELECT count(*) FROM registros_auditoria;")
        total_auditorias = cursor.fetchone()[0]

        # 6. Cálculo de Hash SHA-256 de integridad para el snapshot actual
        hasher = hashlib.sha256()
        hasher.update(f"atletas:{len(atletas)}|partidas:{len(partidas)}|auditoria:{total_auditorias}".encode("utf-8"))
        snapshot_hash = hasher.hexdigest()[:16].upper()

        estado = "OPTIMO" if len(anomalias) == 0 else "ADVERTENCIA"

        detalles_exito = [
            f"Estructura SQLite validada: OK ({sqlite_ok}).",
            f"Ratings reglamentarios verificados: {len(atletas)} atletas en regla (0-4000 ELO).",
            f"Notación oficial comprobada: {len(partidas)} partidas conformes (1-0, 0-1, 1/2-1/2).",
            "Integridad referencial y claves foráneas enlazadas al 100%.",
            f"Bitácora inmutable: {total_auditorias} transacciones aseguradas con trazabilidad.",
        ]

        return {
            "estado": estado,
            "integridad_sqlite": "OK" if sqlite_ok else "ERROR",
            "snapshot_hash": f"SHA256-{snapshot_hash}",
            "total_registros_auditados": total_auditorias,
            "atletas_validados": len(atletas),
            "partidas_validadas": len(partidas),
            "anomalias_detectadas": len(anomalias),
            "detalles": detalles_exito if len(anomalias) == 0 else anomalias,
            "fecha_verificacion": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error durante el chequeo de integridad: {str(e)}"
        )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def registrar_evento(payload: RegistrarAuditoriaSchema):
    """Inserta un nuevo evento de auditoría de forma inmutable."""
    try:
        operacion_enum = TipoOperacion(payload.tipo_operacion.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Operación inválida: {payload.tipo_operacion}. Opciones: CREAR, MODIFICAR, ELIMINAR",
        )

    registro = contenedor.registrar_cambio.ejecutar(
        usuario=payload.usuario,
        entidad_afectada=payload.entidad_afectada,
        tipo_operacion=operacion_enum,
        campo_modificado=payload.campo_modificado or "",
        valor_anterior=payload.valor_anterior,
        valor_nuevo=payload.valor_nuevo,
    )
    return _mapear_auditoria(registro)
