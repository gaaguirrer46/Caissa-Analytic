"""Adaptador secundario de persistencia para Entrenamientos y Asistencias en SQLite."""
from __future__ import annotations

import sqlite3
from datetime import date
from typing import List, Optional

from dominio.entrenamientos.entidades import (
    Asistencia,
    EjecucionEntrenamiento,
    EstadoAsistencia,
    EstadoSesion,
    PlanEntrenamientoSemanal,
    SesionEntrenamiento,
    TipoEntrenamiento,
)
from dominio.entrenamientos.puertos import RepositorioAsistencia, RepositorioEntrenamientos
from dominio.comun.errores import EntidadNoEncontrada, ErrorValidacion

class RepositorioEntrenamientosSqlite(RepositorioEntrenamientos):
    """Implementación de RepositorioEntrenamientos sobre SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def guardar_plan(self, plan: PlanEntrenamientoSemanal) -> PlanEntrenamientoSemanal:
        cursor = self._conexion.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO planes_entrenamiento (id_atleta, semana, anio)
                VALUES (?, ?, ?);
                """,
                (plan.id_atleta, plan.semana, plan.anio),
            )
        except sqlite3.IntegrityError as error:
            self._conexion.rollback()

            if "UNIQUE constraint failed" in str(error):
                raise ErrorValidacion(
                    "Ya existe un plan de entrenamiento para esa semana."
                ) from error
            raise ErrorValidacion(
                "El atleta indicado no existe como expediente del sistema."
            ) from error
        id_plan = cursor.lastrowid
        plan.id = id_plan

        for sesion in plan.sesiones:
            cursor.execute(
                """
                INSERT INTO sesiones_entrenamiento (
                    id_plan, tipo, dia_semana, horas_planificadas,
                    horas_ejecutadas, estado, ejecucion_aprobada, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    id_plan,
                    sesion.tipo.value,
                    sesion.dia_semana,
                    sesion.horas_planificadas,
                    sesion.horas_ejecutadas,
                    sesion.estado.value,
                    sesion.ejecucion_aprobada,
                    sesion.observaciones,
                ),
            )
            sesion.id = cursor.lastrowid

        self._conexion.commit()
        return plan

    def actualizar_sesion(self, sesion: SesionEntrenamiento) -> SesionEntrenamiento:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            UPDATE sesiones_entrenamiento SET
                tipo = ?, dia_semana = ?, horas_planificadas = ?,
                horas_ejecutadas = ?, estado = ?, ejecucion_aprobada = ?, observaciones = ?
            WHERE id = ?;
            """,
            (
                sesion.tipo.value,
                sesion.dia_semana,
                sesion.horas_planificadas,
                sesion.horas_ejecutadas,
                sesion.estado.value,
                sesion.ejecucion_aprobada,
                sesion.observaciones,
                sesion.id,
            ),
        )
        self._conexion.commit()
        return sesion

    def registrar_ejecucion(
        self, ejecucion: EjecucionEntrenamiento
    ) -> EjecucionEntrenamiento:
        cursor = self._conexion.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO ejecuciones_entrenamiento (
                    id_sesion, horas_ejecutadas, fecha_registro,
                    registrado_por_atleta, aprobado_por_entrenador
                ) VALUES (?, ?, ?, ?, ?);
                """,
                (
                    ejecucion.id_sesion,
                    ejecucion.horas_ejecutadas,
                    ejecucion.fecha_registro.isoformat() if ejecucion.fecha_registro else None,
                    ejecucion.registrado_por_atleta,
                    ejecucion.aprobado_por_entrenador,
                ),
            )
        except sqlite3.IntegrityError as error:
            self._conexion.rollback()
            raise ErrorValidacion(
                "La sesión indicada no existe en el sistema."
            ) from error
        ejecucion.id = cursor.lastrowid

        cursor.execute(
            "UPDATE sesiones_entrenamiento SET horas_ejecutadas = ? WHERE id = ?;",
            (ejecucion.horas_ejecutadas, ejecucion.id_sesion),
        )
        self._conexion.commit()
        return ejecucion

    def aprobar_ejecucion(self, id_ejecucion: int) -> EjecucionEntrenamiento:
        cursor = self._conexion.cursor()
        cursor.execute(
            "UPDATE ejecuciones_entrenamiento SET aprobado_por_entrenador = 1 WHERE id = ?;",
            (id_ejecucion,),
        )
        cursor.execute("SELECT * FROM ejecuciones_entrenamiento WHERE id = ?;", (id_ejecucion,))
        fila = cursor.fetchone()
        if fila is None:
            raise EntidadNoEncontrada("Ejecución de entrenamiento no encontrada.")
        cursor.execute(
            """
            UPDATE sesiones_entrenamiento
            SET ejecucion_aprobada = 1, estado = 'EJECUTADA'
            WHERE id = ?;
            """,
            (fila["id_sesion"],),
        )
        self._conexion.commit()
        return self._fila_a_ejecucion(fila)

    def buscar_ejecucion(
        self, id_ejecucion: int
    ) -> Optional[EjecucionEntrenamiento]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM ejecuciones_entrenamiento WHERE id = ?;",
            (id_ejecucion,),
        )
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._fila_a_ejecucion(fila)

    @staticmethod
    def _fila_a_ejecucion(fila: sqlite3.Row) -> EjecucionEntrenamiento:
        return EjecucionEntrenamiento(
            id=fila["id"],
            id_sesion=fila["id_sesion"],
            horas_ejecutadas=float(fila["horas_ejecutadas"]),
            fecha_registro=(
                date.fromisoformat(fila["fecha_registro"])
                if isinstance(fila["fecha_registro"], str)
                else fila["fecha_registro"]
            ),
            registrado_por_atleta=bool(fila["registrado_por_atleta"]),
            aprobado_por_entrenador=bool(fila["aprobado_por_entrenador"]),
        )

    def buscar_sesion(self, id_sesion: int) -> Optional[SesionEntrenamiento]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM sesiones_entrenamiento WHERE id = ?;", (id_sesion,))
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._fila_a_sesion(fila)

    def buscar_plan_de_sesion(
        self, id_sesion: int
    ) -> Optional[PlanEntrenamientoSemanal]:
        cursor = self._conexion.cursor()
        cursor.execute(
            """
            SELECT p.* FROM planes_entrenamiento p
            INNER JOIN sesiones_entrenamiento s ON s.id_plan = p.id
            WHERE s.id = ?;
            """,
            (id_sesion,),
        )
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._cargar_plan_con_sesiones(cursor, fila)

    def listar_por_semana(
        self, id_atleta: int, semana: int, anio: int
    ) -> Optional[PlanEntrenamientoSemanal]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM planes_entrenamiento WHERE id_atleta = ? AND semana = ? AND anio = ?;",
            (id_atleta, semana, anio),
        )
        fila = cursor.fetchone()
        if fila is None:
            return None
        return self._cargar_plan_con_sesiones(cursor, fila)

    def listar_por_atleta(self, id_atleta: int) -> List[PlanEntrenamientoSemanal]:
        cursor = self._conexion.cursor()
        cursor.execute(
            "SELECT * FROM planes_entrenamiento WHERE id_atleta = ? ORDER BY anio DESC, semana DESC;",
            (id_atleta,),
        )
        return [self._cargar_plan_con_sesiones(cursor, f) for f in cursor.fetchall()]

    def obtener_historial(self, id_atleta: int) -> List[PlanEntrenamientoSemanal]:
        return self.listar_por_atleta(id_atleta)

    def _cargar_plan_con_sesiones(self, cursor: sqlite3.Cursor, fila_plan: sqlite3.Row) -> PlanEntrenamientoSemanal:
        id_plan = fila_plan["id"]
        cursor.execute("SELECT * FROM sesiones_entrenamiento WHERE id_plan = ? ORDER BY id;", (id_plan,))
        sesiones = [self._fila_a_sesion(f) for f in cursor.fetchall()]
        return PlanEntrenamientoSemanal(
            id=id_plan,
            id_atleta=fila_plan["id_atleta"],
            semana=fila_plan["semana"],
            anio=fila_plan["anio"],
            sesiones=sesiones,
        )

    @staticmethod
    def _fila_a_sesion(fila: sqlite3.Row) -> SesionEntrenamiento:
        return SesionEntrenamiento(
            id=fila["id"],
            tipo=TipoEntrenamiento(fila["tipo"]),
            dia_semana=fila["dia_semana"],
            horas_planificadas=float(fila["horas_planificadas"]),
            estado=EstadoSesion(fila["estado"]),
            observaciones=fila["observaciones"] or "",
            horas_ejecutadas=float(fila["horas_ejecutadas"]) if fila["horas_ejecutadas"] is not None else None,
            ejecucion_aprobada=bool(fila["ejecucion_aprobada"]),
        )

class RepositorioAsistenciaSqlite(RepositorioAsistencia):
    """Implementación de RepositorioAsistencia sobre SQLite."""

    def __init__(self, conexion: sqlite3.Connection) -> None:
        self._conexion = conexion

    def registrar(self, asistencia: Asistencia) -> Asistencia:
        cursor = self._conexion.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO asistencias (id_atleta, id_sesion, fecha, estado)
                VALUES (?, ?, ?, ?);
                """,
                (
                    asistencia.id_atleta,
                    asistencia.id_sesion,
                    asistencia.fecha.isoformat() if asistencia.fecha else None,
                    asistencia.estado.value,
                ),
            )
        except sqlite3.IntegrityError as error:
            self._conexion.rollback()

            if "UNIQUE constraint failed" in str(error):
                raise ErrorValidacion(
                    "Ya existe un registro de asistencia para ese atleta en esta sesión."
                ) from error
            raise ErrorValidacion(
                "El atleta o la sesión indicada no existe en el sistema."
            ) from error
        asistencia.id = cursor.lastrowid
        self._conexion.commit()
        return asistencia

    def listar_por_sesion(self, id_sesion: int) -> List[Asistencia]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM asistencias WHERE id_sesion = ?;", (id_sesion,))
        return [self._fila_a_asistencia(f) for f in cursor.fetchall()]

    def listar_por_atleta(self, id_atleta: int) -> List[Asistencia]:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT * FROM asistencias WHERE id_atleta = ? ORDER BY fecha DESC;", (id_atleta,))
        return [self._fila_a_asistencia(f) for f in cursor.fetchall()]

    def calcular_porcentaje(self, id_atleta: int) -> float:
        cursor = self._conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM asistencias WHERE id_atleta = ?;", (id_atleta,))
        total = cursor.fetchone()[0]
        if total == 0:
            return 100.0
        cursor.execute(
            "SELECT COUNT(*) FROM asistencias WHERE id_atleta = ? AND estado = 'PRESENTE';",
            (id_atleta,),
        )
        presentes = cursor.fetchone()[0]
        return (presentes / total) * 100.0

    @staticmethod
    def _fila_a_asistencia(fila: sqlite3.Row) -> Asistencia:
        f = date.fromisoformat(fila["fecha"]) if isinstance(fila["fecha"], str) else fila["fecha"]
        return Asistencia(
            id=fila["id"],
            id_atleta=fila["id_atleta"],
            id_sesion=fila["id_sesion"],
            fecha=f,
            estado=EstadoAsistencia(fila["estado"]),
        )
