"""Proveedor SQLite de la información propia del atleta.

Resuelve el vínculo usuario↔atleta mediante la tabla de extensión
``usuario_atleta`` y delega cada sección en su repositorio de módulo."""
from __future__ import annotations

import sqlite3
from typing import List, Optional

from dominio.atletas.puertos import ProveedorInformacionAtleta
from dominio.comun.errores import ErrorValidacion
from dominio.entrenamientos.entidades import (
    PlanEntrenamientoSemanal,
    SesionEntrenamiento,
)
from dominio.entrenamientos.puertos import RepositorioEntrenamientos
from dominio.objetivos.entidades import ObjetivoSmart
from dominio.objetivos.puertos import RepositorioObjetivos
from dominio.partidas.casos_de_uso import ConsultarEstadisticasPorFase
from dominio.partidas.entidades import EstadisticasFaseJuego, Partida
from dominio.partidas.puertos import (
    RepositorioAnalisisTecnico,
    RepositorioPartidas,
)

class ProveedorInformacionAtletaSqlite(ProveedorInformacionAtleta):
    """Consulta cruzada de las siete secciones """

    def __init__(
        self,
        conexion: sqlite3.Connection,
        repo_entrenamientos: RepositorioEntrenamientos,
        repo_objetivos: RepositorioObjetivos,
        repo_partidas: RepositorioPartidas,
        repo_analisis: RepositorioAnalisisTecnico,
    ) -> None:
        self._conexion = conexion
        self._entrenamientos = repo_entrenamientos
        self._objetivos = repo_objetivos
        self._partidas = repo_partidas
        self._estadisticas = ConsultarEstadisticasPorFase(
            repo_partidas, repo_analisis
        )
        self._asegurar_tabla()

    def _asegurar_tabla(self) -> None:
        self._conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS usuario_atleta (
                id_usuario INTEGER PRIMARY KEY,
                id_atleta INTEGER NOT NULL UNIQUE,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (id_atleta) REFERENCES atletas(id) ON DELETE CASCADE
            );
            """
        )
        self._conexion.commit()

    def vincular_usuario(self, id_usuario: int, id_atleta: int) -> None:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT rol FROM usuarios WHERE id = ?;", (id_usuario,))
        fila = cursor.fetchone()
        if fila is None:
            raise ErrorValidacion("El usuario indicado no existe.")
        if fila["rol"] != "ATLETA":
            raise ErrorValidacion(
                "Solo las cuentas con rol ATLETA pueden vincularse a un expediente."
            )
        try:
            self._conexion.execute(
                """
                INSERT INTO usuario_atleta (id_usuario, id_atleta)
                VALUES (?, ?)
                ON CONFLICT(id_usuario) DO UPDATE SET id_atleta = excluded.id_atleta;
                """,
                (id_usuario, id_atleta),
            )
            self._conexion.commit()
        except sqlite3.IntegrityError as error:
            self._conexion.rollback()
            raise ErrorValidacion(
                "No se pudo vincular la cuenta: el atleta no existe "
                "o ya está vinculado a otra cuenta."
            ) from error

    def atleta_de_usuario(self, id_usuario: int) -> Optional[int]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT id_atleta FROM usuario_atleta WHERE id_usuario = ?;",
            (id_usuario,),
        )
        fila = cursor.fetchone()
        return int(fila[0]) if fila else None

    def calendario(self, id_atleta: int) -> List[SesionEntrenamiento]:
        return [
            sesion
            for plan in self._entrenamientos.listar_por_atleta(id_atleta)
            for sesion in plan.sesiones
        ]

    def entrenamientos(self, id_atleta: int) -> List[PlanEntrenamientoSemanal]:
        return self._entrenamientos.listar_por_atleta(id_atleta)

    def objetivos(self, id_atleta: int) -> List[ObjetivoSmart]:
        return self._objetivos.buscar_por_atleta(id_atleta)

    def estadisticas(self, id_atleta: int) -> EstadisticasFaseJuego:
        return self._estadisticas.calcular(id_atleta)

    def partidas(self, id_atleta: int) -> List[Partida]:
        return self._partidas.listar_por_atleta(id_atleta)

    def reportes_disponibles(self, id_atleta: int) -> List[str]:
        return [
            "Informe Integral del Atleta (PDF/Excel)",
            "Reporte de entrenamientos",
            "Reporte de partidas",
            "Reporte de objetivos SMART",
        ]
