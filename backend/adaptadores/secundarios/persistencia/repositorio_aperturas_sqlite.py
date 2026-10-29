"""Adaptadores SQLite del módulo de Repertorio de Aperturas.

Implementa ``RepositorioAperturas`` y ``ProveedorDatosApertura`` sobre la
base de datos oficial y los cablea en el contenedor de dependencias.

Nota de modelo: el DDL oficial sólo incluye ``estadisticas_aperturas``; la
tabla ``estadisticas_apertura_torneo`` se crea aquí de forma idempotente
como tabla de extensión."""
from __future__ import annotations

import sqlite3
from typing import List, Optional, Tuple

from dominio.aperturas.entidades import (
    AperturaRepertorio,
    ClasificacionUso,
    ColorApertura,
    EfectividadApertura,
    EstadoApertura,
    EstadisticaApertura,
    EstadisticaAperturaPorTorneo,
    NivelDominio,
)
from dominio.aperturas.puertos import (
    ProveedorDatosApertura,
    RepositorioAperturas,
)
from dominio.comun.errores import ErrorValidacion
from dominio.partidas.entidades import AnalisisTecnico, Partida
from .repositorio_partidas_sqlite import (
    RepositorioAnalisisTecnicoSqlite,
    RepositorioPartidasSqlite,
)

_TABLA_TORNEO = "estadisticas_apertura_torneo"

class RepositorioAperturasSqlite(RepositorioAperturas):
    """Implementación de RepositorioAperturas sobre SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion
        self._asegurar_tabla_torneo()

    def _asegurar_tabla_torneo(self) -> None:
        """Tabla de extensión idempotente para las estadísticas por torneo."""
        cursor = self._conexion.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_TABLA_TORNEO} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_apertura INTEGER NOT NULL,
                torneo VARCHAR(100) NOT NULL,
                anio SMALLINT NOT NULL,
                control_tiempo VARCHAR(20),
                color VARCHAR(7),
                nivel_rival VARCHAR(20),
                rival VARCHAR(100),
                partidas_jugadas SMALLINT NOT NULL DEFAULT 0,
                victorias SMALLINT NOT NULL DEFAULT 0,
                empates SMALLINT NOT NULL DEFAULT 0,
                derrotas SMALLINT NOT NULL DEFAULT 0,
                FOREIGN KEY (id_apertura)
                    REFERENCES aperturas_repertorio(id) ON DELETE CASCADE
            );
            """
        )
        self._conexion.commit()

    def guardar(self, apertura: AperturaRepertorio) -> AperturaRepertorio:
        cursor = self._conexion.cursor()
        try:
            if apertura.id and apertura.id > 0:
                cursor.execute(
                    """
                    UPDATE aperturas_repertorio SET
                        id_atleta = ?, codigo_eco = ?, nombre = ?, variante = ?,
                        color = ?, estado = ?, nivel_dominio = ?,
                        fuente_estudio = ?, observaciones = ?, clasificacion_uso = ?
                    WHERE id = ?;
                    """,
                    (
                        apertura.id_atleta,
                        apertura.codigo_eco,
                        apertura.nombre,
                        apertura.variante,
                        apertura.color.value,
                        apertura.estado.value,
                        apertura.nivel_dominio.value,
                        apertura.fuente_estudio,
                        apertura.observaciones,
                        apertura.clasificacion_uso.value,
                        apertura.id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO aperturas_repertorio (
                        id_atleta, codigo_eco, nombre, variante, color, estado,
                        nivel_dominio, fuente_estudio, observaciones,
                        clasificacion_uso
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        apertura.id_atleta,
                        apertura.codigo_eco,
                        apertura.nombre,
                        apertura.variante,
                        apertura.color.value,
                        apertura.estado.value,
                        apertura.nivel_dominio.value,
                        apertura.fuente_estudio,
                        apertura.observaciones,
                        apertura.clasificacion_uso.value,
                    ),
                )
                apertura.id = cursor.lastrowid
        except sqlite3.IntegrityError as error:
            self._conexion.rollback()
            raise ErrorValidacion(
                "El atleta indicado no existe como expediente del sistema."
            ) from error
        self._conexion.commit()
        return apertura

    def actualizar_estado(
        self, id_apertura: int, estado: str
    ) -> AperturaRepertorio:
        cursor = self._conexion.cursor()
        cursor.execute(
            "UPDATE aperturas_repertorio SET estado = ? WHERE id = ?;",
            (estado, id_apertura),
        )
        self._conexion.commit()
        return self.buscar_por_id(id_apertura)

    def listar_por_atleta(self, id_atleta: int) -> List[AperturaRepertorio]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM aperturas_repertorio WHERE id_atleta = ? ORDER BY id;",
            (id_atleta,),
        )
        return [self._fila_a_apertura(f) for f in cursor.fetchall()]

    def buscar_por_atleta_y_color(
        self, id_atleta: int, color: ColorApertura
    ) -> List[AperturaRepertorio]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT * FROM aperturas_repertorio
            WHERE id_atleta = ? AND color = ? ORDER BY id;
            """,
            (id_atleta, color.value),
        )
        return [self._fila_a_apertura(f) for f in cursor.fetchall()]

    def listar_por_efectividad(
        self, id_atleta: int, efectividad: EfectividadApertura
    ) -> List[AperturaRepertorio]:
        return [
            apertura
            for apertura in self.listar_por_atleta(id_atleta)
            if _efectividad_de(self, apertura.id) == efectividad
        ]

    def buscar_por_id(self, id_apertura: int) -> Optional[AperturaRepertorio]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM aperturas_repertorio WHERE id = ?;", (id_apertura,)
        )
        fila = cursor.fetchone()
        return self._fila_a_apertura(fila) if fila else None

    def guardar_estadistica(
        self, estadistica: EstadisticaApertura
    ) -> EstadisticaApertura:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            INSERT INTO estadisticas_aperturas (
                id_apertura, partidas_jugadas, victorias, empates, derrotas,
                accuracy_promedio, acpl_promedio, errores_frecuentes,
                evaluacion_motor_promedio, tiempo_promedio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id_apertura) DO UPDATE SET
                partidas_jugadas = excluded.partidas_jugadas,
                victorias = excluded.victorias,
                empates = excluded.empates,
                derrotas = excluded.derrotas,
                accuracy_promedio = excluded.accuracy_promedio,
                acpl_promedio = excluded.acpl_promedio,
                errores_frecuentes = excluded.errores_frecuentes,
                evaluacion_motor_promedio = excluded.evaluacion_motor_promedio,
                tiempo_promedio = excluded.tiempo_promedio;
            """,
            (
                estadistica.id_apertura,
                estadistica.partidas_jugadas,
                estadistica.victorias,
                estadistica.empates,
                estadistica.derrotas,
                estadistica.accuracy_promedio,
                estadistica.acpl_promedio,
                estadistica.errores_frecuentes,
                estadistica.evaluacion_motor_promedio,
                estadistica.tiempo_promedio,
            ),
        )
        self._conexion.commit()
        return estadistica

    def guardar_estadistica_torneo(
        self, estadistica: EstadisticaAperturaPorTorneo
    ) -> EstadisticaAperturaPorTorneo:
        cursor = self._conexion.cursor()
        cursor.execute(
            f"""
            INSERT INTO {_TABLA_TORNEO} (
                id_apertura, torneo, anio, control_tiempo, color, nivel_rival,
                rival, partidas_jugadas, victorias, empates, derrotas
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                estadistica.id_apertura,
                estadistica.torneo,
                estadistica.anio,
                estadistica.control_tiempo,
                estadistica.color.value if estadistica.color else None,
                estadistica.nivel_rival,
                estadistica.rival,
                estadistica.partidas_jugadas,
                estadistica.victorias,
                estadistica.empates,
                estadistica.derrotas,
            ),
        )
        self._conexion.commit()
        return estadistica

    def buscar_estadistica(
        self, id_apertura: int
    ) -> Optional[EstadisticaApertura]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM estadisticas_aperturas WHERE id_apertura = ?;",
            (id_apertura,),
        )
        fila = cursor.fetchone()
        return self._fila_a_estadistica(fila) if fila else None

    def listar_estadisticas_por_apertura(
        self, id_apertura: int
    ) -> List[EstadisticaAperturaPorTorneo]:
        cursor = self._conexion.cursor()
        cursor.execute(
            f"SELECT * FROM {_TABLA_TORNEO} WHERE id_apertura = ? ORDER BY anio DESC;",
            (id_apertura,),
        )
        return [
            EstadisticaAperturaPorTorneo(
                id_apertura=f["id_apertura"],
                torneo=f["torneo"],
                anio=int(f["anio"]),
                control_tiempo=f["control_tiempo"],
                color=ColorApertura(f["color"]) if f["color"] else None,
                nivel_rival=f["nivel_rival"],
                rival=f["rival"],
                partidas_jugadas=f["partidas_jugadas"] or 0,
                victorias=f["victorias"] or 0,
                empates=f["empates"] or 0,
                derrotas=f["derrotas"] or 0,
            )
            for f in cursor.fetchall()
        ]

    @staticmethod
    def _fila_a_apertura(fila: sqlite3.Row) -> AperturaRepertorio:
        return AperturaRepertorio(
            id=fila["id"],
            id_atleta=fila["id_atleta"],
            codigo_eco=fila["codigo_eco"],
            nombre=fila["nombre"],
            variante=fila["variante"] or "",
            color=ColorApertura(fila["color"]),
            estado=EstadoApertura(fila["estado"]),
            nivel_dominio=NivelDominio(fila["nivel_dominio"]),
            fuente_estudio=fila["fuente_estudio"] or "",
            observaciones=fila["observaciones"] or "",
            clasificacion_uso=ClasificacionUso(fila["clasificacion_uso"]),
        )

    @staticmethod
    def _fila_a_estadistica(fila: sqlite3.Row) -> EstadisticaApertura:
        return EstadisticaApertura(
            id_apertura=fila["id_apertura"],
            partidas_jugadas=fila["partidas_jugadas"] or 0,
            victorias=fila["victorias"] or 0,
            empates=fila["empates"] or 0,
            derrotas=fila["derrotas"] or 0,
            accuracy_promedio=(
                float(fila["accuracy_promedio"])
                if fila["accuracy_promedio"] is not None
                else None
            ),
            acpl_promedio=(
                float(fila["acpl_promedio"])
                if fila["acpl_promedio"] is not None
                else None
            ),
            errores_frecuentes=fila["errores_frecuentes"] or 0,
            evaluacion_motor_promedio=(
                float(fila["evaluacion_motor_promedio"])
                if fila["evaluacion_motor_promedio"] is not None
                else None
            ),
            tiempo_promedio=(
                float(fila["tiempo_promedio"])
                if fila["tiempo_promedio"] is not None
                else None
            ),
        )

def _efectividad_de(
    repositorio: RepositorioAperturasSqlite, id_apertura: int
) -> EfectividadApertura:
    estadistica = repositorio.buscar_estadistica(id_apertura)
    return (
        estadistica.efectividad()
        if estadistica is not None
        else EfectividadApertura.REQUIERE_REVISION
    )

class ProveedorDatosAperturaSqlite(ProveedorDatosApertura):
    """Consulta cruzada partidas + análisis por apertura (ECO y color).

 Criterio documentado: el filtro por color compara con ``color_atleta``
 registrado en la partida; las partidas sin color explícito no se asignan a
 ningún color del repertorio (el color se infiere sólo para el resultado).
 """

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def partidas_con_apertura(
        self,
        id_atleta: int,
        codigo_eco: str,
        color: Optional[ColorApertura] = None,
    ) -> List[Tuple[Partida, Optional[AnalisisTecnico]]]:
        cursor = self._conexion.cursor()
        sql = (
            "SELECT * FROM partidas "
            "WHERE id_atleta = ? AND apertura_eco = ?"
        )
        parametros: list = [id_atleta, codigo_eco]
        if color is not None:
            sql += " AND color_atleta = ?"
            parametros.append(color.value)
        sql += " ORDER BY fecha, id;"
        cursor.execute(sql, parametros)
        resultado: List[Tuple[Partida, Optional[AnalisisTecnico]]] = []
        for fila in cursor.fetchall():
            partida = RepositorioPartidasSqlite._fila_a_partida(fila)
            cursor.execute(
                "SELECT * FROM analisis_tecnico_partidas WHERE id_partida = ?;",
                (partida.id,),
            )
            fila_analisis = cursor.fetchone()
            analisis = (
                RepositorioAnalisisTecnicoSqlite._fila_a_analisis(fila_analisis)
                if fila_analisis is not None
                else None
            )
            resultado.append((partida, analisis))
        return resultado
