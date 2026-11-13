"""Adaptador secundario de persistencia para Evaluaciones del Entrenador en SQLite."""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import List, Optional

from dominio.evaluaciones.entidades import (
    EvaluacionAtleta,
    PeriodoEvaluacion,
    TipoIndicadorEvaluacion,
)
from dominio.evaluaciones.puertos import RepositorioEvaluaciones

class RepositorioEvaluacionesSqlite(RepositorioEvaluaciones):
    """Implementación de RepositorioEvaluaciones sobre las tablas oficiales."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def guardar(self, evaluacion: EvaluacionAtleta) -> EvaluacionAtleta:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            INSERT INTO evaluaciones_atleta (
                id_atleta, id_entrenador, periodo, referencia_periodo,
                fecha_realizacion, fortalezas, aspectos_por_mejorar,
                recomendaciones, es_autoevaluacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                evaluacion.id_atleta,
                evaluacion.id_entrenador,
                evaluacion.periodo.value,
                evaluacion.referencia_periodo,
                evaluacion.fecha_realizacion.isoformat(),
                evaluacion.fortalezas,
                evaluacion.aspectos_por_mejorar,
                evaluacion.recomendaciones,
                evaluacion.es_autoevaluacion,
            ),
        )
        evaluacion.id = cursor.lastrowid
        self._guardar_calificaciones(cursor, evaluacion)
        self._conexion.commit()
        return evaluacion

    def actualizar(self, evaluacion: EvaluacionAtleta) -> EvaluacionAtleta:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            UPDATE evaluaciones_atleta SET
                id_atleta = ?, id_entrenador = ?, periodo = ?,
                referencia_periodo = ?, fecha_realizacion = ?,
                fortalezas = ?, aspectos_por_mejorar = ?, recomendaciones = ?,
                es_autoevaluacion = ?
            WHERE id = ?;
            """,
            (
                evaluacion.id_atleta,
                evaluacion.id_entrenador,
                evaluacion.periodo.value,
                evaluacion.referencia_periodo,
                evaluacion.fecha_realizacion.isoformat(),
                evaluacion.fortalezas,
                evaluacion.aspectos_por_mejorar,
                evaluacion.recomendaciones,
                evaluacion.es_autoevaluacion,
                evaluacion.id,
            ),
        )
        cursor.execute(
            "DELETE FROM evaluacion_calificaciones_indicador WHERE id_evaluacion = ?;",
            (evaluacion.id,),
        )
        self._guardar_calificaciones(cursor, evaluacion)
        self._conexion.commit()
        return evaluacion

    def buscar_por_id(self, id_evaluacion: int) -> Optional[EvaluacionAtleta]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM evaluaciones_atleta WHERE id = ?;", (id_evaluacion,)
        )
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._fila_a_evaluacion(cursor, fila)

    def listar_por_atleta(self, id_atleta: int) -> List[EvaluacionAtleta]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM evaluaciones_atleta WHERE id_atleta = ? ORDER BY fecha_realizacion DESC, id DESC;",
            (id_atleta,),
        )
        return [self._fila_a_evaluacion(cursor, f) for f in cursor.fetchall()]

    def listar_por_entrenador(self, id_entrenador: int) -> List[EvaluacionAtleta]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM evaluaciones_atleta WHERE id_entrenador = ? ORDER BY fecha_realizacion DESC, id DESC;",
            (id_entrenador,),
        )
        return [self._fila_a_evaluacion(cursor, f) for f in cursor.fetchall()]

    def listar_por_periodo(
        self, id_atleta: int, periodo: PeriodoEvaluacion
    ) -> List[EvaluacionAtleta]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT * FROM evaluaciones_atleta
            WHERE id_atleta = ? AND periodo = ?
            ORDER BY fecha_realizacion DESC, id DESC;
            """,
            (id_atleta, periodo.value),
        )
        return [self._fila_a_evaluacion(cursor, f) for f in cursor.fetchall()]

    def _guardar_calificaciones(
        self, cursor: sqlite3.Cursor, evaluacion: EvaluacionAtleta
    ) -> None:
        for indicador, calificacion in evaluacion.calificaciones.items():
            cursor.execute(
                """
                INSERT INTO evaluacion_calificaciones_indicador (
                    id_evaluacion, tipo_indicador, calificacion
                ) VALUES (?, ?, ?);
                """,
                (evaluacion.id, indicador.value, calificacion),
            )

    def _fila_a_evaluacion(
        self, cursor: sqlite3.Cursor, fila: sqlite3.Row
    ) -> EvaluacionAtleta:
        cursor.execute(
            """
            SELECT tipo_indicador, calificacion
            FROM evaluacion_calificaciones_indicador
            WHERE id_evaluacion = ?;
            """,
            (fila["id"],),
        )
        calificaciones = {
            TipoIndicadorEvaluacion(r["tipo_indicador"]): int(r["calificacion"])
            for r in cursor.fetchall()
        }
        fecha = fila["fecha_realizacion"]
        if isinstance(fecha, str):
            fecha = date.fromisoformat(fecha)
        return EvaluacionAtleta(
            id=fila["id"],
            id_atleta=fila["id_atleta"],
            id_entrenador=fila["id_entrenador"],
            periodo=PeriodoEvaluacion(fila["periodo"]),
            referencia_periodo=fila["referencia_periodo"],
            fecha_realizacion=fecha,
            calificaciones=calificaciones,
            fortalezas=fila["fortalezas"] or "",
            aspectos_por_mejorar=fila["aspectos_por_mejorar"] or "",
            recomendaciones=fila["recomendaciones"] or "",
            es_autoevaluacion=bool(fila["es_autoevaluacion"]),
        )
