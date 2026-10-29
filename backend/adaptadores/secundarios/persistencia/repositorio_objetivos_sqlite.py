"""Adaptador secundario de persistencia para Objetivos SMART en SQLite."""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import List, Optional

from dominio.comun.errores import ErrorValidacion
from dominio.objetivos.entidades import (
    EstadoObjetivo,
    IndicadorAvance,
    ObjetivoSmart,
    TipoIndicadorAvance,
)
from dominio.objetivos.puertos import ProveedorDatosAvance, RepositorioObjetivos

class RepositorioObjetivosSqlite(RepositorioObjetivos):
    """Implementación de RepositorioObjetivos sobre SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def guardar(self, objetivo: ObjetivoSmart) -> ObjetivoSmart:
        cursor = self._conexion.cursor()
        self._ejecutar_guardado(
            cursor,
            objetivo,
            """
            INSERT INTO objetivos_smart (
                id_atleta, descripcion, indicador_meta, valor_meta,
                rating_actual, rating_meta, fecha_inicio, fecha_limite,
                porcentaje_avance, estado, aprobado_por_entrenador, cumplido_por_entrenador
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                objetivo.id_atleta,
                objetivo.descripcion,
                objetivo.indicador_meta.value,
                objetivo.valor_meta,
                objetivo.rating_actual,
                objetivo.rating_meta,
                objetivo.fecha_inicio.isoformat() if objetivo.fecha_inicio else None,
                objetivo.fecha_limite.isoformat() if objetivo.fecha_limite else None,
                objetivo.porcentaje_avance,
                objetivo.estado.value,
                objetivo.aprobado_por_entrenador,
                objetivo.cumplido_por_entrenador,
            ),
            es_insercion=True,
        )
        return objetivo

    def _ejecutar_guardado(
        self,
        cursor: sqlite3.Cursor,
        objetivo: ObjetivoSmart,
        sentencia: str,
        parametros: tuple,
        es_insercion: bool,
    ) -> None:
        """traduce el fallo de FK a error de dominio.

 La FK de ``objetivos_smart`` apunta a ``atletas(id)``; crear o actualizar
 un objetivo para un atleta inexistente levantaba
 ``sqlite3.IntegrityError`` genérico. Ahora el fallo se traduce a
 ``ErrorValidacion`` y se hace rollback de la transacción.
 """
        try:
            cursor.execute(sentencia, parametros)
            if es_insercion:
                objetivo.id = cursor.lastrowid
            self._sincronizar_indicadores(cursor, objetivo)
            self._conexion.commit()
        except sqlite3.IntegrityError as error:
            self._conexion.rollback()
            raise ErrorValidacion(
                "El atleta indicado no existe como expediente del sistema."
            ) from error

    def actualizar(self, objetivo: ObjetivoSmart) -> ObjetivoSmart:
        cursor = self._conexion.cursor()
        self._ejecutar_guardado(
            cursor,
            objetivo,
            """
            UPDATE objetivos_smart SET
                id_atleta = ?, descripcion = ?, indicador_meta = ?, valor_meta = ?,
                rating_actual = ?, rating_meta = ?, fecha_inicio = ?, fecha_limite = ?,
                porcentaje_avance = ?, estado = ?, aprobado_por_entrenador = ?, cumplido_por_entrenador = ?
            WHERE id = ?;
            """,
            (
                objetivo.id_atleta,
                objetivo.descripcion,
                objetivo.indicador_meta.value,
                objetivo.valor_meta,
                objetivo.rating_actual,
                objetivo.rating_meta,
                objetivo.fecha_inicio.isoformat() if objetivo.fecha_inicio else None,
                objetivo.fecha_limite.isoformat() if objetivo.fecha_limite else None,
                objetivo.porcentaje_avance,
                objetivo.estado.value,
                objetivo.aprobado_por_entrenador,
                objetivo.cumplido_por_entrenador,
                objetivo.id,
            ),
            es_insercion=False,
        )
        return objetivo

    def buscar_por_id(self, id_objetivo: int) -> Optional[ObjetivoSmart]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM objetivos_smart WHERE id = ?;", (id_objetivo,))
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._fila_a_objetivo(cursor, fila)

    def buscar_por_atleta(self, id_atleta: int) -> List[ObjetivoSmart]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM objetivos_smart WHERE id_atleta = ?;", (id_atleta,))
        filas = cursor.fetchall()
        return [self._fila_a_objetivo(cursor, f) for f in filas]

    def listar_por_estado(self, estado: EstadoObjetivo) -> List[ObjetivoSmart]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM objetivos_smart WHERE estado = ?;", (estado.value,))
        filas = cursor.fetchall()
        return [self._fila_a_objetivo(cursor, f) for f in filas]

    def eliminar(self, id_objetivo: int) -> None:
        cursor = self._conexion.cursor()
        cursor.execute("DELETE FROM objetivos_smart WHERE id = ?;", (id_objetivo,))
        self._conexion.commit()

    def _sincronizar_indicadores(self, cursor: sqlite3.Cursor, objetivo: ObjetivoSmart) -> None:
        if not objetivo.avances:
            return
        cursor.execute("DELETE FROM indicadores_avance_objetivo WHERE id_objetivo = ?;", (objetivo.id,))
        for av in objetivo.avances:
            cursor.execute(
                """
                INSERT INTO indicadores_avance_objetivo (id_objetivo, tipo, valor_actual, valor_esperado)
                VALUES (?, ?, ?, ?);
                """,
                (objetivo.id, av.tipo.value, av.valor_actual, av.valor_esperado),
            )

    @staticmethod
    def _fila_a_objetivo(cursor: sqlite3.Cursor, fila: sqlite3.Row) -> ObjetivoSmart:
        id_obj = fila["id"]
        cursor.execute("SELECT tipo, valor_actual, valor_esperado FROM indicadores_avance_objetivo WHERE id_objetivo = ?;", (id_obj,))
        avances = [
            IndicadorAvance(
                tipo=TipoIndicadorAvance(r["tipo"]),
                valor_actual=float(r["valor_actual"]),
                valor_esperado=float(r["valor_esperado"]),
            )
            for r in cursor.fetchall()
        ]

        f_ini = date.fromisoformat(fila["fecha_inicio"]) if isinstance(fila["fecha_inicio"], str) else fila["fecha_inicio"]
        f_lim = date.fromisoformat(fila["fecha_limite"]) if isinstance(fila["fecha_limite"], str) else fila["fecha_limite"]

        return ObjetivoSmart(
            id=id_obj,
            id_atleta=fila["id_atleta"],
            descripcion=fila["descripcion"],
            indicador_meta=TipoIndicadorAvance(fila["indicador_meta"]),
            valor_meta=float(fila["valor_meta"]),
            rating_actual=int(fila["rating_actual"]),
            rating_meta=int(fila["rating_meta"]),
            fecha_inicio=f_ini,
            fecha_limite=f_lim,
            porcentaje_avance=float(fila["porcentaje_avance"]),
            estado=EstadoObjetivo(fila["estado"]),
            aprobado_por_entrenador=bool(fila["aprobado_por_entrenador"]),
            cumplido_por_entrenador=bool(fila["cumplido_por_entrenador"]),
            avances=avances,
        )

class ProveedorDatosAvanceSqlite(ProveedorDatosAvance):
    """Proveedor que consulta métricas reales desde SQLite para avance de objetivos."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def horas_entrenadas(self, id_atleta: int, desde: date, hasta: date) -> float:
        cursor = self._conexion.cursor()

        d_anio, d_semana, _ = desde.isocalendar()
        h_anio, h_semana, _ = hasta.isocalendar()
        cursor.execute(
            """
            SELECT COALESCE(SUM(s.horas_ejecutadas), 0.0)
            FROM sesiones_entrenamiento s
            INNER JOIN planes_entrenamiento p ON s.id_plan = p.id
            WHERE p.id_atleta = ? AND s.ejecucion_aprobada = 1
              AND (p.anio > ? OR (p.anio = ? AND p.semana >= ?))
              AND (p.anio < ? OR (p.anio = ? AND p.semana <= ?));
            """,
            (id_atleta, d_anio, d_anio, d_semana, h_anio, h_anio, h_semana),
        )
        fila = cursor.fetchone()
        return float(fila[0]) if fila else 0.0

    def rating_actual(self, id_atleta: int, tipo: str) -> Optional[int]:
        cursor = self._conexion.cursor()
        col = "rating_clasicas"
        if tipo == "rapidas":
            col = "rating_rapidas"
        elif tipo == "blitz":
            col = "rating_blitz"
        elif tipo == "chess_com":
            col = "rating_chess_com"
        elif tipo == "lichess":
            col = "rating_lichess"

        cursor.execute(f"SELECT {col} FROM atletas WHERE id = ?;", (id_atleta,))
        fila = cursor.fetchone()
        return fila[0] if fila and fila[0] is not None else None

    def tareas_completadas(self, id_atleta: int, desde: date, hasta: date) -> float:
        return 0.0

    def torneos_jugados(self, id_atleta: int, desde: date, hasta: date) -> float:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(DISTINCT evento)
            FROM partidas
            WHERE id_atleta = ? AND fecha BETWEEN ? AND ?;
            """,
            (id_atleta, desde.isoformat(), hasta.isoformat()),
        )
        fila = cursor.fetchone()
        return float(fila[0]) if fila else 0.0

    def medallas_obtenidas(self, id_atleta: int, desde: date, hasta: date) -> float:
        return 0.0
