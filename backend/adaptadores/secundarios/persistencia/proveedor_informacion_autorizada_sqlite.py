"""Proveedor SQLite de la información autorizada al usuario invitado."""
from __future__ import annotations

import sqlite3
from typing import Dict, List

from dominio.comun.errores import ErrorValidacion
from dominio.usuarios.puertos import ProveedorInformacionAutorizada

class ProveedorInformacionAutorizadaSqlite(ProveedorInformacionAutorizada):
    """Expone sólo datos públicos; nunca fechas de nacimiento, identidad ni hashes."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def obtener(self, seccion: str) -> object:
        if seccion == "perfil_publico":
            return self._perfil_publico()
        if seccion == "ranking":
            return self._ranking()
        if seccion == "resumen_equipo":
            return self._resumen_equipo()
        raise ErrorValidacion(f"La sección '{seccion}' no está autorizada.")

    def _perfil_publico(self) -> List[Dict[str, object]]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT id, nombre, sexo, federacion,
                   rating_clasicas, rating_rapidas, rating_blitz,
                   rating_chess_com, rating_lichess
            FROM atletas WHERE activo = 1 ORDER BY nombre;
            """
        )
        resultado: List[Dict[str, object]] = []
        for fila in cursor.fetchall():
            cursor.execute(
                "SELECT club FROM atleta_clubs WHERE id_atleta = ? ORDER BY club;",
                (fila["id"],),
            )
            clubs = [r["club"] for r in cursor.fetchall()]
            resultado.append(
                {
                    "id": fila["id"],
                    "nombre": fila["nombre"],
                    "sexo": fila["sexo"],
                    "federacion": fila["federacion"],
                    "clubes": clubs,
                    "rating_clasicas": fila["rating_clasicas"],
                    "rating_rapidas": fila["rating_rapidas"],
                    "rating_blitz": fila["rating_blitz"],
                    "rating_chess_com": fila["rating_chess_com"],
                    "rating_lichess": fila["rating_lichess"],
                }
            )
        return resultado

    def _ranking(self) -> List[Dict[str, object]]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT id, nombre, rating_clasicas
            FROM atletas WHERE activo = 1
            ORDER BY rating_clasicas DESC, nombre;
            """
        )
        return [
            {
                "posicion": posicion,
                "id": fila["id"],
                "nombre": fila["nombre"],
                "rating": fila["rating_clasicas"],
            }
            for posicion, fila in enumerate(cursor.fetchall(), start=1)
        ]

    def _resumen_equipo(self) -> Dict[str, object]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT COUNT(*),
                   COALESCE(SUM(CASE WHEN activo = 1 THEN 1 ELSE 0 END), 0),
                   COALESCE(AVG(rating_clasicas), 0),
                   COALESCE(MAX(rating_clasicas), 0)
            FROM atletas;
            """
        )
        total, activos, promedio, mejor = cursor.fetchone()
        return {
            "total_atletas": int(total or 0),
            "atletas_activos": int(activos or 0),
            "rating_promedio": float(promedio or 0),
            "mejor_rating": int(mejor or 0),
        }
