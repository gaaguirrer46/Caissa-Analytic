"""Adaptador secundario de persistencia para Atletas y Categorías en SQLite."""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import List, Optional

from dominio.atletas.entidades import (
    Atleta,
    Categoria,
    PerfilHistorico,
    Rating,
    TipoCategoria,
)
from dominio.atletas.puertos import RepositorioAtletas, RepositorioCategorias
from dominio.comun.errores import ErrorValidacion

class RepositorioAtletasSqlite(RepositorioAtletas):
    """Implementación de RepositorioAtletas sobre SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

        columnas = {
            fila["name"]
            for fila in self._conexion.execute("PRAGMA table_info(atletas);").fetchall()
        }
        if columnas and "institucion" not in columnas:
            self._conexion.execute(
                "ALTER TABLE atletas ADD COLUMN institucion VARCHAR(80);"
            )
            self._conexion.commit()

    def sincronizar_relaciones_controlado(
        self, cursor: sqlite3.Cursor, atleta: Atleta
    ) -> None:
        """traduce el fallo de FK a excepción de dominio.

 La FK de ``atleta_entrenadores`` apunta a ``usuarios(id)``; asignar un
 entrenador inexistente hacía fallar la sincronización con
 ``sqlite3.IntegrityError`` genérico. Ahora el fallo se traduce a
 ``ErrorValidacion`` y se hace rollback de la transacción.
 """
        try:
            self._sincronizar_relaciones(cursor, atleta)
        except sqlite3.IntegrityError as error:
            self._conexion.rollback()
            raise ErrorValidacion(
                "El entrenador indicado no existe como usuario del sistema."
            ) from error

    def guardar(self, atleta: Atleta) -> Atleta:
        cursor = self._conexion.cursor()
        r = atleta.rating_actual or Rating()
        cursor.execute(
            """
            INSERT INTO atletas (
                nombre, fecha_nacimiento, sexo, identidad_opcional,
                fotografia_opcional, federacion, universidad, institucion,
                carrera, rating_clasicas, rating_rapidas, rating_blitz,
                rating_chess_com, rating_lichess, fecha_actualizacion_rating, activo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                atleta.nombre,
                atleta.fecha_nacimiento.isoformat() if atleta.fecha_nacimiento else None,
                atleta.sexo,
                atleta.identidad_opcional,
                atleta.fotografia_opcional,
                atleta.federacion,
                atleta.universidad,
                atleta.institucion,
                atleta.carrera,
                r.clasicas,
                r.rapidas,
                r.blitz,
                r.chess_com,
                r.lichess,
                r.fecha_actualizacion.isoformat() if r.fecha_actualizacion else None,
                atleta.activo,
            ),
        )
        id_atleta = cursor.lastrowid
        atleta.id = id_atleta
        self.sincronizar_relaciones_controlado(cursor, atleta)
        self._conexion.commit()
        return atleta

    def actualizar(self, atleta: Atleta) -> Atleta:
        cursor = self._conexion.cursor()
        r = atleta.rating_actual or Rating()
        cursor.execute(
            """
            UPDATE atletas SET
                nombre = ?, fecha_nacimiento = ?, sexo = ?, identidad_opcional = ?,
                fotografia_opcional = ?, federacion = ?, universidad = ?,
                institucion = ?, carrera = ?,
                rating_clasicas = ?, rating_rapidas = ?, rating_blitz = ?,
                rating_chess_com = ?, rating_lichess = ?, fecha_actualizacion_rating = ?, activo = ?
            WHERE id = ?;
            """,
            (
                atleta.nombre,
                atleta.fecha_nacimiento.isoformat() if atleta.fecha_nacimiento else None,
                atleta.sexo,
                atleta.identidad_opcional,
                atleta.fotografia_opcional,
                atleta.federacion,
                atleta.universidad,
                atleta.institucion,
                atleta.carrera,
                r.clasicas,
                r.rapidas,
                r.blitz,
                r.chess_com,
                r.lichess,
                r.fecha_actualizacion.isoformat() if r.fecha_actualizacion else None,
                atleta.activo,
                atleta.id,
            ),
        )
        self.sincronizar_relaciones_controlado(cursor, atleta)
        self._conexion.commit()
        return atleta

    def buscar_por_id(self, id_atleta: int) -> Optional[Atleta]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM atletas WHERE id = ?;", (id_atleta,))
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._cargar_atleta_completo(cursor, fila)

    def listar_por_entrenador(self, id_entrenador: int) -> List[Atleta]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT a.* FROM atletas a
            INNER JOIN atleta_entrenadores ae ON a.id = ae.id_atleta
            WHERE ae.id_entrenador = ?;
            """,
            (id_entrenador,),
        )
        filas = cursor.fetchall()
        return [self._cargar_atleta_completo(cursor, f) for f in filas]

    def listar_activos(self) -> List[Atleta]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM atletas WHERE activo = 1;")
        filas = cursor.fetchall()
        return [self._cargar_atleta_completo(cursor, f) for f in filas]

    def buscar_por_categoria(self, id_categoria: int) -> List[Atleta]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT a.* FROM atletas a
            INNER JOIN atleta_categorias ac ON a.id = ac.id_atleta
            WHERE ac.id_categoria = ?;
            """,
            (id_categoria,),
        )
        filas = cursor.fetchall()
        return [self._cargar_atleta_completo(cursor, f) for f in filas]

    def existe(self, id_atleta: int) -> bool:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT 1 FROM atletas WHERE id = ? LIMIT 1;", (id_atleta,))
        return cursor.fetchone() is not None

    def guardar_snapshot(self, historico: PerfilHistorico) -> PerfilHistorico:
        cursor = self._conexion.cursor()
        r = historico.rating
        cursor.execute(
            """
            INSERT INTO perfiles_historicos_atleta (
                id_atleta, anio, torneo, rating_clasicas, rating_rapidas,
                rating_blitz, rating_chess_com, rating_lichess,
                fecha_actualizacion_rating, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                historico.id_atleta,
                historico.anio,
                historico.torneo,
                r.clasicas,
                r.rapidas,
                r.blitz,
                r.chess_com,
                r.lichess,
                r.fecha_actualizacion.isoformat() if r.fecha_actualizacion else None,
                historico.observaciones,
            ),
        )
        id_historico = cursor.lastrowid
        self._conexion.commit()
        return PerfilHistorico(
            id=id_historico,
            id_atleta=historico.id_atleta,
            anio=historico.anio,
            torneo=historico.torneo,
            rating=historico.rating,
            observaciones=historico.observaciones,
        )

    def _sincronizar_relaciones(self, cursor: sqlite3.Cursor, atleta: Atleta) -> None:
        id_atleta = atleta.id

        cursor.execute("DELETE FROM atleta_categorias WHERE id_atleta = ?;", (id_atleta,))
        for cat_id in atleta.categorias:
            cursor.execute(
                "INSERT OR IGNORE INTO atleta_categorias (id_atleta, id_categoria) VALUES (?, ?);",
                (id_atleta, cat_id),
            )

        cursor.execute("DELETE FROM atleta_clubs WHERE id_atleta = ?;", (id_atleta,))
        for club in atleta.clubs:
            cursor.execute(
                "INSERT OR IGNORE INTO atleta_clubs (id_atleta, club) VALUES (?, ?);",
                (id_atleta, club),
            )

        cursor.execute("DELETE FROM atleta_entrenadores WHERE id_atleta = ?;", (id_atleta,))
        for ent_id in atleta.entrenadores_asignados:
            cursor.execute(
                "INSERT OR IGNORE INTO atleta_entrenadores (id_atleta, id_entrenador) VALUES (?, ?);",
                (id_atleta, ent_id),
            )

    def _cargar_atleta_completo(self, cursor: sqlite3.Cursor, fila: sqlite3.Row) -> Atleta:
        id_atleta = fila["id"]

        cursor.execute("SELECT id_categoria FROM atleta_categorias WHERE id_atleta = ?;", (id_atleta,))
        categorias = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT club FROM atleta_clubs WHERE id_atleta = ?;", (id_atleta,))
        clubs = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT id_entrenador FROM atleta_entrenadores WHERE id_atleta = ?;", (id_atleta,))
        entrenadores = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM perfiles_historicos_atleta WHERE id_atleta = ? ORDER BY anio, id;", (id_atleta,))
        historial = []
        for h in cursor.fetchall():
            f_act = date.fromisoformat(h["fecha_actualizacion_rating"]) if h["fecha_actualizacion_rating"] else None
            historial.append(
                PerfilHistorico(
                    id=h["id"],
                    id_atleta=id_atleta,
                    anio=h["anio"],
                    torneo=h["torneo"],
                    rating=Rating(
                        clasicas=h["rating_clasicas"],
                        rapidas=h["rating_rapidas"],
                        blitz=h["rating_blitz"],
                        chess_com=h["rating_chess_com"],
                        lichess=h["rating_lichess"],
                        fecha_actualizacion=f_act,
                    ),
                    observaciones=h["observaciones"] or "",
                )
            )

        f_nac = date.fromisoformat(fila["fecha_nacimiento"]) if isinstance(fila["fecha_nacimiento"], str) else fila["fecha_nacimiento"]
        f_act_r = date.fromisoformat(fila["fecha_actualizacion_rating"]) if fila["fecha_actualizacion_rating"] else None

        rating_actual = Rating(
            clasicas=fila["rating_clasicas"],
            rapidas=fila["rating_rapidas"],
            blitz=fila["rating_blitz"],
            chess_com=fila["rating_chess_com"],
            lichess=fila["rating_lichess"],
            fecha_actualizacion=f_act_r,
        )

        return Atleta(
            id=id_atleta,
            nombre=fila["nombre"],
            fecha_nacimiento=f_nac,
            sexo=fila["sexo"],
            identidad_opcional=fila["identidad_opcional"],
            fotografia_opcional=fila["fotografia_opcional"],
            federacion=fila["federacion"],
            universidad=fila["universidad"],
            institucion=fila["institucion"],
            carrera=fila["carrera"],
            categorias=categorias,
            clubs=clubs,
            entrenadores_asignados=entrenadores,
            rating_actual=rating_actual,
            historial=historial,
            activo=bool(fila["activo"]),
        )

class RepositorioCategoriasSqlite(RepositorioCategorias):
    """Implementación de RepositorioCategorias sobre SQLite."""

    _REFERENCIAS_PREDEFINIDAS = (
        ("Sub-8", "EDAD", "hasta 8 años"),
        ("Sub-10", "EDAD", "9-10 años"),
        ("Sub-12", "EDAD", "11-12 años"),
        ("Sub-14", "EDAD", "13-14 años"),
        ("Sub-16", "EDAD", "15-16 años"),
        ("Sub-18", "EDAD", "16-18 años"),
        ("Sub-20", "EDAD", "19-20 años"),
        ("Principiante", "NIVEL", "0-1200 ELO"),
        ("Intermedio", "NIVEL", "1201-1600 ELO"),
        ("Avanzado", "NIVEL", "1601-2000 ELO"),
        ("Alto Rendimiento", "NIVEL", "2001+ ELO"),
    )

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion
        self._asegurar_referencias_predefinidas()

    def _asegurar_referencias_predefinidas(self) -> None:
        """siembra las referencias predefinidas

 Idempotente: no duplica las categorías que ya existan con el mismo
 nombre y tipo (p. ej., ``Sub-18`` y ``Elite FIDE`` del seed oficial).
 """
        cursor = self._conexion.cursor()
        cursor.execute("SELECT nombre, tipo FROM categorias;")
        existentes = {(f["nombre"], f["tipo"]) for f in cursor.fetchall()}
        nuevas = [
            (nombre, tipo, rango)
            for nombre, tipo, rango in self._REFERENCIAS_PREDEFINIDAS
            if (nombre, tipo) not in existentes
        ]
        if nuevas:
            cursor.executemany(
                """
                INSERT INTO categorias (nombre, tipo, rango, editable_por_admin)
                VALUES (?, ?, ?, TRUE);
                """,
                nuevas,
            )
            self._conexion.commit()

    def listar_predefinidas(self) -> List[Categoria]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT id, nombre, tipo, rango, editable_por_admin FROM categorias;")
        return [
            Categoria(
                id=f["id"],
                nombre=f["nombre"],
                tipo=TipoCategoria(f["tipo"]),
                rango=f["rango"],
                editable_por_admin=bool(f["editable_por_admin"]),
            )
            for f in cursor.fetchall()
        ]

    def crear_personalizada(self, categoria: Categoria) -> Categoria:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            INSERT INTO categorias (nombre, tipo, rango, editable_por_admin)
            VALUES (?, ?, ?, ?);
            """,
            (categoria.nombre, categoria.tipo.value, categoria.rango, categoria.editable_por_admin),
        )
        self._conexion.commit()
        return Categoria(
            id=cursor.lastrowid,
            nombre=categoria.nombre,
            tipo=categoria.tipo,
            rango=categoria.rango,
            editable_por_admin=categoria.editable_por_admin,
        )

    def editar(self, categoria: Categoria) -> Categoria:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            UPDATE categorias SET nombre = ?, tipo = ?, rango = ?, editable_por_admin = ?
            WHERE id = ?;
            """,
            (categoria.nombre, categoria.tipo.value, categoria.rango, categoria.editable_por_admin, categoria.id),
        )
        self._conexion.commit()
        return categoria

    def eliminar(self, id_categoria: int) -> None:
        cursor = self._conexion.cursor()
        cursor.execute("DELETE FROM categorias WHERE id = ?;", (id_categoria,))
        self._conexion.commit()
