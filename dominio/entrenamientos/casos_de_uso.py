"""Casos de uso (puertos primarios / driving) del módulo de Entrenamientos."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorValidacion,
)
from ..comun.ids import nuevo_id_entero
from ..usuarios.entidades import Rol
from .entidades import (
    Asistencia,
    EjecucionEntrenamiento,
    EstadoAsistencia,
    EstadoSesion,
    PlanEntrenamientoSemanal,
    ResumenCumplimientoSemanal,
    SesionEntrenamiento,
)
from .puertos import RepositorioAsistencia, RepositorioEntrenamientos


@dataclass
class PlanificarEntrenamientoSemanal:
    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_atleta: int,
        semana: int,
        anio: int,
        sesiones: List[SesionEntrenamiento],
    ) -> PlanEntrenamientoSemanal:
        if not 1 <= semana <= 53:
            raise ErrorValidacion("La semana debe estar entre 1 y 53.")
        if not sesiones:
            raise ErrorValidacion(
                "El plan semanal debe contener al menos una sesión."
            )
        # RF-04.2: la planificación se define antes del inicio de la semana;
        # no se permite duplicar el plan de una misma semana.
        if self.repositorio.listar_por_semana(id_atleta, semana, anio) is not None:
            raise ErrorValidacion(
                "Ya existe un plan de entrenamiento para esa semana."
            )
        for sesion in sesiones:
            if sesion.horas_planificadas <= 0:
                raise ErrorValidacion(
                    "Las horas planificadas de cada sesión deben ser mayores a cero."
                )
            if not sesion.dia_semana:
                raise ErrorValidacion(
                    "El día de la semana de cada sesión es obligatorio."
                )
        plan = PlanEntrenamientoSemanal(
            id=nuevo_id_entero(),
            id_atleta=id_atleta,
            semana=semana,
            anio=anio,
            sesiones=sesiones,
        )
        return self.repositorio.guardar_plan(plan)


@dataclass
class ReprogramarSesion:
    """RF-04.7: cambia el día de una sesión y la marca como REPROGRAMADA."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_sesion: int,
        nuevo_dia: str,
        rol_usuario: Rol,
    ) -> SesionEntrenamiento:
        if rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el entrenador puede reprogramar sesiones."
            )
        if not nuevo_dia:
            raise ErrorValidacion("El nuevo día de la sesión es obligatorio.")
        sesion = self.repositorio.buscar_sesion(id_sesion)
        if sesion is None:
            raise EntidadNoEncontrada("Sesión no encontrada.")
        sesion.dia_semana = nuevo_dia
        sesion.estado = EstadoSesion.REPROGRAMADA
        return self.repositorio.actualizar_sesion(sesion)


@dataclass
class RegistrarEjecucionEntrenamiento:
    """RF-04.3: el atleta reporta las horas ejecutadas de una sesión."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_sesion: int,
        horas_ejecutadas: float,
        fecha_registro: date,
        rol_usuario: Rol,
    ) -> EjecucionEntrenamiento:
        if rol_usuario != Rol.ATLETA:
            raise ErrorValidacion(
                "Solo el atleta puede registrar la ejecución de sus horas."
            )
        if horas_ejecutadas < 0:
            raise ErrorValidacion("Las horas ejecutadas no pueden ser negativas.")
        if self.repositorio.buscar_sesion(id_sesion) is None:
            raise EntidadNoEncontrada("La sesión no existe.")
        ejecucion = EjecucionEntrenamiento(
            id=nuevo_id_entero(),
            id_sesion=id_sesion,
            horas_ejecutadas=horas_ejecutadas,
            fecha_registro=fecha_registro,
            registrado_por_atleta=True,
        )
        return self.repositorio.registrar_ejecucion(ejecucion)


@dataclass
class AprobarHorasEjecutadas:
    """RF-04.3: el entrenador aprueba las horas reportadas por el atleta."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(self, id_ejecucion: int, rol_usuario: Rol) -> EjecucionEntrenamiento:
        if rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el entrenador puede aprobar las horas ejecutadas."
            )
        return self.repositorio.aprobar_ejecucion(id_ejecucion)


@dataclass
class ConsultarCumplimientoSemanal:
    """RF-04.4: compara planificado vs ejecutado y devuelve el porcentaje."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self, id_atleta: int, semana: int, anio: int
    ) -> ResumenCumplimientoSemanal:
        plan = self.repositorio.listar_por_semana(id_atleta, semana, anio)
        if plan is None:
            raise EntidadNoEncontrada("No existe plan para esa semana.")
        return ResumenCumplimientoSemanal(
            id_atleta=id_atleta,
            semana=semana,
            anio=anio,
            horas_planificadas=plan.total_horas_planificadas,
            horas_ejecutadas_aprobadas=plan.total_horas_ejecutadas_aprobadas,
        )


@dataclass
class RegistrarAsistencia:
    """RF-04.8: asistencia registrada por el entrenador después de la sesión."""

    repositorio_asistencia: RepositorioAsistencia

    def ejecutar(
        self,
        id_atleta: int,
        id_sesion: int,
        fecha: date,
        estado: EstadoAsistencia,
        rol_usuario: Rol,
    ) -> Asistencia:
        if rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el entrenador puede registrar la asistencia."
            )
        if estado not in EstadoAsistencia:
            raise ErrorValidacion("Estado de asistencia inválido.")
        asistencia = Asistencia(
            id=nuevo_id_entero(),
            id_atleta=id_atleta,
            id_sesion=id_sesion,
            fecha=fecha,
            estado=estado,
        )
        return self.repositorio_asistencia.registrar(asistencia)


@dataclass
class ConsultarHistorialEntrenamientos:
    """RF-04.6: historial completo de sesiones conservando todos los estados."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(self, id_atleta: int) -> List[PlanEntrenamientoSemanal]:
        return self.repositorio.obtener_historial(id_atleta)


def generar_id_plan(id_atleta: str, semana: int, anio: int) -> str:
    return f"plan_{id_atleta}_{anio}_{semana}"
