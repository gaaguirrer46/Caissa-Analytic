"""Adaptador SQLite de la configuración del sistema.

La tabla ``configuracion_sistema`` es una **extensión** del esquema oficial
(``BD profesor.txt``) para soportar RNF-07.1/RNF-07.2 sin modificar el script
del curso. Se crea de forma idempotente al instanciar el repositorio."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Tuple

from dominio.configuracion.entidades import ConfiguracionSistema
from dominio.configuracion.puertos import RepositorioConfiguracion

class RepositorioConfiguracionSqlite(RepositorioConfiguracion):
    """Persiste una única fila (id=1) con los parámetros del sistema."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion
        self._asegurar_tabla()

    def _asegurar_tabla(self) -> None:
        self._conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS configuracion_sistema (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                maximo_atletas_por_entrenador INTEGER NOT NULL,
                minimo_entrenadores_por_atleta INTEGER NOT NULL,
                maximo_entrenadores_por_atleta INTEGER NOT NULL,
                permitir_autoevaluacion BOOLEAN NOT NULL,
                rangos_json TEXT NOT NULL DEFAULT '{}',
                secciones_invitado_json TEXT NOT NULL DEFAULT '[]',
                actualizado_por VARCHAR(100) NOT NULL,
                fecha_actualizacion TIMESTAMP NOT NULL
            );
            """
        )

        columnas = {
            fila["name"]
            for fila in self._conexion.execute(
                "PRAGMA table_info(configuracion_sistema);"
            ).fetchall()
        }
        if "secciones_invitado_json" not in columnas:
            self._conexion.execute(
                "ALTER TABLE configuracion_sistema ADD COLUMN "
                "secciones_invitado_json TEXT NOT NULL DEFAULT '[]';"
            )
        self._conexion.commit()

    def obtener(self) -> ConfiguracionSistema:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM configuracion_sistema WHERE id = 1;")
        fila = cursor.fetchone()
        if fila is None:
            return self.guardar(ConfiguracionSistema())
        return self._fila_a_configuracion(fila)

    def guardar(self, configuracion: ConfiguracionSistema) -> ConfiguracionSistema:
        cursor = self._conexion.cursor()
        rangos_json = json.dumps(
            {clave: list(valores) for clave, valores in configuracion.rangos_evaluacion.items()},
            ensure_ascii=False,
        )
        secciones_json = json.dumps(
            list(configuracion.secciones_autorizadas_invitado),
            ensure_ascii=False,
        )
        cursor.execute(
            """
            INSERT INTO configuracion_sistema (
                id, maximo_atletas_por_entrenador, minimo_entrenadores_por_atleta,
                maximo_entrenadores_por_atleta, permitir_autoevaluacion,
                rangos_json, secciones_invitado_json, actualizado_por,
                fecha_actualizacion
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                maximo_atletas_por_entrenador = excluded.maximo_atletas_por_entrenador,
                minimo_entrenadores_por_atleta = excluded.minimo_entrenadores_por_atleta,
                maximo_entrenadores_por_atleta = excluded.maximo_entrenadores_por_atleta,
                permitir_autoevaluacion = excluded.permitir_autoevaluacion,
                rangos_json = excluded.rangos_json,
                secciones_invitado_json = excluded.secciones_invitado_json,
                actualizado_por = excluded.actualizado_por,
                fecha_actualizacion = excluded.fecha_actualizacion;
            """,
            (
                configuracion.maximo_atletas_por_entrenador,
                configuracion.minimo_entrenadores_por_atleta,
                configuracion.maximo_entrenadores_por_atleta,
                int(configuracion.permitir_autoevaluacion),
                rangos_json,
                secciones_json,
                configuracion.actualizado_por,
                configuracion.fecha_actualizacion.isoformat(),
            ),
        )
        self._conexion.commit()
        return self.obtener()

    @staticmethod
    def _fila_a_configuracion(fila: sqlite3.Row) -> ConfiguracionSistema:
        crudos: Dict[str, list] = json.loads(fila["rangos_json"] or "{}")
        rangos: Dict[str, Tuple[float, float, float]] = {
            clave: tuple(float(v) for v in valores)
            for clave, valores in crudos.items()
        }
        fecha = fila["fecha_actualizacion"]
        if isinstance(fecha, str):
            fecha = datetime.fromisoformat(fecha)
        secciones = tuple(json.loads(fila["secciones_invitado_json"] or "[]"))
        return ConfiguracionSistema(
            maximo_atletas_por_entrenador=int(fila["maximo_atletas_por_entrenador"]),
            minimo_entrenadores_por_atleta=int(fila["minimo_entrenadores_por_atleta"]),
            maximo_entrenadores_por_atleta=int(fila["maximo_entrenadores_por_atleta"]),
            permitir_autoevaluacion=bool(fila["permitir_autoevaluacion"]),
            rangos_evaluacion=rangos,
            secciones_autorizadas_invitado=secciones,
            actualizado_por=fila["actualizado_por"],
            fecha_actualizacion=fecha,
        )
