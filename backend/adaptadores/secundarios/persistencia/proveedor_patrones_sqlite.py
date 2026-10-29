"""Proveedor SQLite de datos para la detección de patrones de error.

Antes el caso de uso ``DetectarPatronesError`` sólo era ejecutable con repos
de prueba en memoria: no existía implementación del puerto
``ProveedorDatosPartidas`` sobre la base de datos oficial."""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import Dict, List, Optional, Tuple

from dominio.partidas.entidades import AnalisisTecnico, Partida
from dominio.patrones.puertos import ProveedorDatosPartidas
from .repositorio_partidas_sqlite import (
    RepositorioAnalisisTecnicoSqlite,
    RepositorioPartidasSqlite,
)

class ProveedorDatosPartidasSqlite(ProveedorDatosPartidas):
    """Agrega partidas+análisis y conteos de disciplina desde SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def partidas_con_analisis(
        self,
        id_atleta: int,
        periodo_inicio: Optional[date] = None,
        periodo_fin: Optional[date] = None,
    ) -> List[Tuple[Partida, AnalisisTecnico]]:
        cursor = self._conexion.cursor()
        sql = (
            "SELECT p.* FROM partidas p "
            "INNER JOIN analisis_tecnico_partidas a ON a.id_partida = p.id "
            "WHERE p.id_atleta = ?"
        )
        parametros: list = [id_atleta]
        if periodo_inicio is not None:
            sql += " AND p.fecha >= ?"
            parametros.append(periodo_inicio.isoformat())
        if periodo_fin is not None:
            sql += " AND p.fecha <= ?"
            parametros.append(periodo_fin.isoformat())
        sql += " ORDER BY p.fecha, p.id;"
        cursor.execute(sql, parametros)
        return [
            (
                RepositorioPartidasSqlite._fila_a_partida(fila),
                self._analisis_de(cursor, fila["id"]),
            )
            for fila in cursor.fetchall()
        ]

    @staticmethod
    def _analisis_de(cursor: sqlite3.Cursor, id_partida: int) -> AnalisisTecnico:
        cursor.execute(
            "SELECT * FROM analisis_tecnico_partidas WHERE id_partida = ?;",
            (id_partida,),
        )
        return RepositorioAnalisisTecnicoSqlite._fila_a_analisis(cursor.fetchone())

    def conteos_disciplina(
        self,
        id_atleta: int,
        periodo_inicio: Optional[date] = None,
        periodo_fin: Optional[date] = None,
    ) -> Dict[str, int]:
        cursor = self._conexion.cursor()
        conteos: Dict[str, int] = {}

        sql = "SELECT COUNT(*) FROM partidas WHERE id_atleta = ?"
        parametros: list = [id_atleta]
        if periodo_inicio is not None:
            sql += " AND fecha >= ?"
            parametros.append(periodo_inicio.isoformat())
        if periodo_fin is not None:
            sql += " AND fecha <= ?"
            parametros.append(periodo_fin.isoformat())
        cursor.execute(sql + ";", parametros)
        total = int(cursor.fetchone()[0])
        conteos["partidas_totales"] = total

        sql_con_analisis = sql.replace(
            "SELECT COUNT(*) FROM partidas",
            "SELECT COUNT(*) FROM partidas p "
            "INNER JOIN analisis_tecnico_partidas a ON a.id_partida = p.id",
        )
        cursor.execute(sql_con_analisis + ";", parametros)
        conteos["partidas_sin_analisis"] = total - int(cursor.fetchone()[0])

        anio_inicio = periodo_inicio.year if periodo_inicio else None
        anio_fin = periodo_fin.year if periodo_fin else None
        sql_planes = (
            "SELECT p.id FROM planes_entrenamiento p WHERE p.id_atleta = ?"
        )
        parametros_planes: list = [id_atleta]
        if anio_inicio is not None:
            sql_planes += " AND p.anio >= ?"
            parametros_planes.append(anio_inicio)
        if anio_fin is not None:
            sql_planes += " AND p.anio <= ?"
            parametros_planes.append(anio_fin)
        cursor.execute(sql_planes + ";", parametros_planes)
        planes = [f["id"] for f in cursor.fetchall()]
        conteos["semanas_evaluadas"] = len(planes)

        incumplidos = 0
        for id_plan in planes:
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(s.horas_planificadas), 0.0),
                    COALESCE(SUM(CASE WHEN s.ejecucion_aprobada = 1
                        THEN s.horas_ejecutadas ELSE 0 END), 0.0)
                FROM sesiones_entrenamiento s WHERE s.id_plan = ?;
                """,
                (id_plan,),
            )
            planificadas, aprobadas = cursor.fetchone()
            if float(aprobadas or 0) < float(planificadas or 0):
                incumplidos += 1
        conteos["incumplimientos_semanales"] = incumplidos

        sql_asis = (
            "SELECT COUNT(*), "
            "SUM(CASE WHEN estado IN ('AUSENTE', 'JUSTIFICADO') THEN 1 ELSE 0 END) "
            "FROM asistencias WHERE id_atleta = ?"
        )
        parametros_asis: list = [id_atleta]
        if periodo_inicio is not None:
            sql_asis += " AND fecha >= ?"
            parametros_asis.append(periodo_inicio.isoformat())
        if periodo_fin is not None:
            sql_asis += " AND fecha <= ?"
            parametros_asis.append(periodo_fin.isoformat())
        cursor.execute(sql_asis + ";", parametros_asis)
        evaluadas, ausencias = cursor.fetchone()
        conteos["sesiones_evaluadas"] = int(evaluadas or 0)
        conteos["inasistencias"] = int(ausencias or 0)
        return conteos
