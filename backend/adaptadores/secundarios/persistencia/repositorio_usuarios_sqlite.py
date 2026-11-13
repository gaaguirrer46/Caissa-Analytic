"""Adaptador secundario de persistencia para Usuarios en SQLite."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from dominio.comun.errores import ErrorValidacion
from dominio.usuarios.entidades import Rol, Usuario
from dominio.usuarios.puertos import RepositorioUsuarios

class RepositorioUsuariosSqlite(RepositorioUsuarios):
    """Implementación de RepositorioUsuarios sobre SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion
        try:
            self._conexion.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS ux_usuarios_unico_entrenador "
                "ON usuarios(rol) WHERE rol = 'ENTRENADOR';"
            )
            self._conexion.commit()
        except sqlite3.IntegrityError as error:
            raise ErrorValidacion(
                "La base de datos contiene más de un usuario ENTRENADOR; "
                "corrija los datos antes de continuar."
            ) from error

    def guardar(self, usuario: Usuario) -> Usuario:
        cursor = self._conexion.cursor()

        if usuario.id is not None:
            cursor.execute("SELECT id FROM usuarios WHERE id = ?;", (usuario.id,))
            existe = cursor.fetchone() is not None
        else:
            existe = False

        if existe:
            cursor.execute(
                """
                UPDATE usuarios
                SET correo = ?, hash_contrasena = ?, rol = ?
                WHERE id = ?;
                """,
                (usuario.correo, usuario.hash_contrasena, usuario.rol.value, usuario.id),
            )
            id_guardado = usuario.id
        else:
            cursor.execute(
                """
                INSERT INTO usuarios (correo, hash_contrasena, rol, fecha_creacion)
                VALUES (?, ?, ?, ?);
                """,
                (
                    usuario.correo,
                    usuario.hash_contrasena,
                    usuario.rol.value,
                    usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else datetime.now(timezone.utc).isoformat(),
                ),
            )
            id_guardado = cursor.lastrowid

        self._conexion.commit()
        return Usuario(
            id=id_guardado,
            correo=usuario.correo,
            hash_contrasena=usuario.hash_contrasena,
            rol=usuario.rol,
            fecha_creacion=usuario.fecha_creacion,
        )

    def buscar_por_correo(self, correo: str) -> Optional[Usuario]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT id, correo, hash_contrasena, rol, fecha_creacion FROM usuarios WHERE lower(correo) = lower(?);",
            (correo.strip(),),
        )
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._fila_a_usuario(fila)

    def buscar_por_id(self, id_usuario: int) -> Optional[Usuario]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT id, correo, hash_contrasena, rol, fecha_creacion FROM usuarios WHERE id = ?;",
            (id_usuario,),
        )
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._fila_a_usuario(fila)

    def listar_todos(self) -> List[Usuario]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT id, correo, hash_contrasena, rol, fecha_creacion FROM usuarios ORDER BY id;")
        return [self._fila_a_usuario(f) for f in cursor.fetchall()]

    def existe(self, correo: str) -> bool:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE lower(correo) = lower(?) LIMIT 1;", (correo.strip(),))
        return cursor.fetchone() is not None

    @staticmethod
    def _fila_a_usuario(fila: sqlite3.Row) -> Usuario:
        fecha_raw = fila["fecha_creacion"]
        if isinstance(fecha_raw, str):
            try:
                fecha = datetime.fromisoformat(fecha_raw)
            except ValueError:
                fecha = datetime.now(timezone.utc)
        elif isinstance(fecha_raw, datetime):
            fecha = fecha_raw
        else:
            fecha = datetime.now(timezone.utc)

        return Usuario(
            id=fila["id"],
            correo=fila["correo"],
            hash_contrasena=fila["hash_contrasena"],
            rol=Rol(fila["rol"]),
            fecha_creacion=fecha,
        )
