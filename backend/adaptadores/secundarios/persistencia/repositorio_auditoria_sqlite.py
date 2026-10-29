"""Adaptador secundario de persistencia para Auditoría en SQLite."""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone
from typing import List

from dominio.auditoria.entidades import RegistroAuditoria, TipoOperacion
from dominio.auditoria.puertos import RepositorioAuditoria

class RepositorioAuditoriaSqlite(RepositorioAuditoria):
    """Implementación inmutable de RepositorioAuditoria sobre SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def guardar(self, registro: RegistroAuditoria) -> RegistroAuditoria:
        cursor = self._conexion.cursor()
        fh = registro.fecha_hora.isoformat() if registro.fecha_hora else datetime.now(timezone.utc).isoformat()
        cursor.execute(
            """
            INSERT INTO registros_auditoria (
                usuario, fecha_hora, entidad_afectada, tipo_operacion,
                campo_modificado, valor_anterior, valor_nuevo
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                registro.usuario,
                fh,
                registro.entidad_afectada,
                registro.tipo_operacion.value,
                registro.campo_modificado,
                registro.valor_anterior,
                registro.valor_nuevo,
            ),
        )
        self._conexion.commit()
        return RegistroAuditoria(
            id=cursor.lastrowid,
            usuario=registro.usuario,
            fecha_hora=registro.fecha_hora,
            entidad_afectada=registro.entidad_afectada,
            tipo_operacion=registro.tipo_operacion,
            campo_modificado=registro.campo_modificado,
            valor_anterior=registro.valor_anterior,
            valor_nuevo=registro.valor_nuevo,
        )

    def listar_por_entidad(self, entidad: str) -> List[RegistroAuditoria]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM registros_auditoria WHERE entidad_afectada = ? ORDER BY id DESC;",
            (entidad,),
        )
        return [self._fila_a_auditoria(f) for f in cursor.fetchall()]

    def listar_por_usuario(self, usuario: str) -> List[RegistroAuditoria]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM registros_auditoria WHERE usuario = ? ORDER BY id DESC;",
            (usuario,),
        )
        return [self._fila_a_auditoria(f) for f in cursor.fetchall()]

    def listar_por_fecha(self, dia: date) -> List[RegistroAuditoria]:
        cursor = self._conexion.cursor()
        dia_str = dia.isoformat()
        cursor.execute(
            "SELECT * FROM registros_auditoria WHERE date(fecha_hora, 'localtime') = ? ORDER BY id DESC;",
            (dia_str,),
        )
        return [self._fila_a_auditoria(f) for f in cursor.fetchall()]

    @staticmethod
    def _fila_a_auditoria(fila: sqlite3.Row) -> RegistroAuditoria:
        raw_fh = fila["fecha_hora"]
        try:
            fh = datetime.fromisoformat(raw_fh)
        except (ValueError, TypeError):
            fh = datetime.now(timezone.utc)

        return RegistroAuditoria(
            id=fila["id"],
            usuario=fila["usuario"],
            fecha_hora=fh,
            entidad_afectada=fila["entidad_afectada"],
            tipo_operacion=TipoOperacion(fila["tipo_operacion"]),
            campo_modificado=fila["campo_modificado"] or "",
            valor_anterior=fila["valor_anterior"],
            valor_nuevo=fila["valor_nuevo"],
        )
