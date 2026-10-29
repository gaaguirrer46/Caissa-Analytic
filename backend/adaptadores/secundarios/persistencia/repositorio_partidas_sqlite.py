"""Adaptador secundario de persistencia para Partidas y Análisis Técnico en SQLite."""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import List, Optional

from dominio.comun.errores import ErrorValidacion
from dominio.partidas.entidades import (
    AnalisisTecnico,
    ClasificacionPartida,
    ColorPartida,
    FuentePartida,
    Partida,
    ResultadoPartida,
)
from dominio.partidas.puertos import (
    RepositorioAnalisisTecnico,
    RepositorioPartidas,
)

class RepositorioPartidasSqlite(RepositorioPartidas):
    """Implementación de RepositorioPartidas sobre SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion
        self._asegurar_columnas()

    def _asegurar_columnas(self) -> None:
        """Columnas de extensión idempotentes para /

 El DDL oficial no guarda la clasificación automática ni la ventaja
 alcanzada; se añaden como columnas de extensión (mismo criterio que la
 migración de ``institucion`` en atletas).
 """
        cursor = self._conexion.cursor()
        cursor.execute("PRAGMA table_info(partidas);")
        columnas = {fila[1] for fila in cursor.fetchall()}
        if "ventaja_maxima" not in columnas:
            cursor.execute("ALTER TABLE partidas ADD COLUMN ventaja_maxima REAL;")
        if "clasificacion" not in columnas:
            cursor.execute(
                "ALTER TABLE partidas ADD COLUMN clasificacion VARCHAR(16);"
            )
        self._conexion.commit()

    def guardar(self, partida: Partida) -> Partida:
        cursor = self._conexion.cursor()
        if partida.id and partida.id > 0:

            cursor.execute(
                """
                UPDATE partidas SET
                    id_atleta = ?, evento = ?, fecha = ?, jugador_blancas = ?,
                    jugador_negras = ?, rating_blancas = ?, rating_negras = ?,
                    resultado = ?, apertura_eco = ?, control_tiempo = ?,
                    fuente = ?, color_atleta = ?, ventaja_maxima = ?,
                    clasificacion = ?
                WHERE id = ?;
                """,
                (
                    partida.id_atleta,
                    partida.evento,
                    partida.fecha.isoformat() if partida.fecha else None,
                    partida.jugador_blancas,
                    partida.jugador_negras,
                    partida.rating_blancas,
                    partida.rating_negras,
                    partida.resultado.value,
                    partida.apertura_eco,
                    partida.control_tiempo,
                    partida.fuente.value,
                    partida.color_atleta.value if partida.color_atleta else None,
                    partida.ventaja_maxima,
                    partida.clasificacion.value if partida.clasificacion else None,
                    partida.id,
                ),
            )
            self._conexion.commit()
            return partida
        try:
            cursor.execute(
                """
                INSERT INTO partidas (
                    id_atleta, evento, fecha, jugador_blancas, jugador_negras,
                    rating_blancas, rating_negras, resultado, apertura_eco,
                    control_tiempo, fuente, color_atleta, ventaja_maxima,
                    clasificacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    partida.id_atleta,
                    partida.evento,
                    partida.fecha.isoformat() if partida.fecha else None,
                    partida.jugador_blancas,
                    partida.jugador_negras,
                    partida.rating_blancas,
                    partida.rating_negras,
                    partida.resultado.value,
                    partida.apertura_eco,
                    partida.control_tiempo,
                    partida.fuente.value,
                    partida.color_atleta.value if partida.color_atleta else None,
                    partida.ventaja_maxima,
                    partida.clasificacion.value if partida.clasificacion else None,
                ),
            )
        except sqlite3.IntegrityError as error:
            self._conexion.rollback()
            raise ErrorValidacion(
                "El atleta indicado no existe como expediente del sistema."
            ) from error
        partida.id = cursor.lastrowid
        self._conexion.commit()
        return partida

    def buscar_por_id(self, id_partida: int) -> Optional[Partida]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM partidas WHERE id = ?;", (id_partida,))
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._fila_a_partida(fila)

    def listar_por_atleta(self, id_atleta: int) -> List[Partida]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM partidas WHERE id_atleta = ? ORDER BY fecha DESC;", (id_atleta,))
        return [self._fila_a_partida(f) for f in cursor.fetchall()]

    def listar_por_torneo(self, evento: str) -> List[Partida]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM partidas WHERE evento = ? ORDER BY fecha DESC;", (evento,))
        return [self._fila_a_partida(f) for f in cursor.fetchall()]

    def listar_por_periodo(
        self, id_atleta: int, desde: date, hasta: date
    ) -> List[Partida]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT * FROM partidas
            WHERE id_atleta = ? AND fecha BETWEEN ? AND ?
            ORDER BY fecha DESC;
            """,
            (id_atleta, desde.isoformat(), hasta.isoformat()),
        )
        return [self._fila_a_partida(f) for f in cursor.fetchall()]

    @staticmethod
    def _fila_a_partida(fila: sqlite3.Row) -> Partida:
        f = date.fromisoformat(fila["fecha"]) if isinstance(fila["fecha"], str) else fila["fecha"]
        c = ColorPartida(fila["color_atleta"]) if fila["color_atleta"] else None
        return Partida(
            id=fila["id"],
            id_atleta=fila["id_atleta"],
            evento=fila["evento"],
            fecha=f,
            jugador_blancas=fila["jugador_blancas"],
            jugador_negras=fila["jugador_negras"],
            rating_blancas=int(fila["rating_blancas"]),
            rating_negras=int(fila["rating_negras"]),
            resultado=ResultadoPartida(fila["resultado"]),
            apertura_eco=fila["apertura_eco"],
            control_tiempo=fila["control_tiempo"],
            fuente=FuentePartida(fila["fuente"]),
            color_atleta=c,
            ventaja_maxima=
                float(fila["ventaja_maxima"]) if fila["ventaja_maxima"] is not None else None,
            clasificacion=
                ClasificacionPartida(fila["clasificacion"]) if fila["clasificacion"] else None,
        )

class RepositorioAnalisisTecnicoSqlite(RepositorioAnalisisTecnico):
    """Implementación de RepositorioAnalisisTecnico sobre SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def guardar_resumen(self, analisis: AnalisisTecnico) -> AnalisisTecnico:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            INSERT INTO analisis_tecnico_partidas (
                id_partida, accuracy, acpl, blunders, errores, imprecisiones,
                brilliant_moves, excelente, buena, libro,
                tiempo_promedio_jugada, perdidas_por_tiempo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id_partida) DO UPDATE SET
                accuracy = excluded.accuracy,
                acpl = excluded.acpl,
                blunders = excluded.blunders,
                errores = excluded.errores,
                imprecisiones = excluded.imprecisiones,
                brilliant_moves = excluded.brilliant_moves,
                excelente = excluded.excelente,
                buena = excluded.buena,
                libro = excluded.libro,
                tiempo_promedio_jugada = excluded.tiempo_promedio_jugada,
                perdidas_por_tiempo = excluded.perdidas_por_tiempo;
            """,
            (
                analisis.id_partida,
                analisis.accuracy,
                analisis.acpl,
                analisis.blunders,
                analisis.errores,
                analisis.imprecisiones,
                analisis.brilliant_moves,
                analisis.excelente,
                analisis.buena,
                analisis.libro,
                analisis.tiempo_promedio_jugada,
                analisis.perdidas_por_tiempo,
            ),
        )
        self._conexion.commit()
        return analisis

    def buscar_por_partida(self, id_partida: int) -> Optional[AnalisisTecnico]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM analisis_tecnico_partidas WHERE id_partida = ?;", (id_partida,))
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._fila_a_analisis(fila)

    def listar_por_atleta(self, id_atleta: int) -> List[AnalisisTecnico]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT a.* FROM analisis_tecnico_partidas a
            INNER JOIN partidas p ON a.id_partida = p.id
            WHERE p.id_atleta = ?
            ORDER BY p.fecha DESC;
            """,
            (id_atleta,),
        )
        return [self._fila_a_analisis(f) for f in cursor.fetchall()]

    @staticmethod
    def _fila_a_analisis(fila: sqlite3.Row) -> AnalisisTecnico:
        return AnalisisTecnico(
            id_partida=fila["id_partida"],
            accuracy=float(fila["accuracy"]) if fila["accuracy"] is not None else None,
            acpl=float(fila["acpl"]) if fila["acpl"] is not None else None,
            blunders=fila["blunders"] or 0,
            errores=fila["errores"] or 0,
            imprecisiones=fila["imprecisiones"] or 0,
            brilliant_moves=fila["brilliant_moves"] or 0,
            excelente=fila["excelente"] or 0,
            buena=fila["buena"] or 0,
            libro=fila["libro"] or 0,
            tiempo_promedio_jugada=float(fila["tiempo_promedio_jugada"]) if fila["tiempo_promedio_jugada"] is not None else None,
            perdidas_por_tiempo=fila["perdidas_por_tiempo"] or 0,
        )
