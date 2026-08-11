"""Casos de uso (puertos primarios / driving) del módulo de Entrenamientos."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorValidacion,
)
from ..usuarios.entidades import Rol
from .entidades import (
    Asistencia,
    EjecucionEntrenamiento,
    EstadoAsistencia,
    EstadoSesion,
    PlanEntrenamientoSemanal,
    SesionEntrenamiento,
)
from .puertos import RepositorioAsistencia, RepositorioEntrenamientos


@dataclass
class PlanificarEntrenamientoSemanal:
    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_atleta: str,
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
        for sesion in sesiones:
            if sesion.horas_planificadas <= 0:
                raise ErrorValidacion(
                    "Las horas planificadas de cada sesión deben ser mayores a cero."
                )
        plan = PlanEntrenamientoSemanal(
            id=generar_id_plan(id_atleta, semana, anio),
            id_atleta=id_atleta,
            semana=semana,
            anio=anio,
            sesiones=sesiones,
        )
        return self.repositorio.guardar_plan(plan)


@dataclass
class ReprogramarSesion:
    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_sesion: str,
        nuevo_dia: str,
        rol_usuario: Rol,
    ) -> SesionEntrenamiento:
        if rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el entrenador puede reprogramar sesiones."
            )
        sesion = self._buscar_sesion(id_sesion)
        sesion.dia_semana = nuevo_dia
        sesion.estado = EstadoSesion.REPROGRAMADA
        return self.repositorio.actualizar_sesion(sesion)

    def _buscar_sesion(self, id_sesion: str) -> SesionEntrenamiento:
        raise NotImplementedError(
            "Requiere un mecanismo de búsqueda de sesión por id."
        )


@dataclass
class RegistrarEjecucionEntrenamiento:
    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_sesion: str,
        horas_ejecutadas: float,
        fecha_registro: date,
        rol_usuario: Rol,
    ) -> EjecucionEntrenamiento:
        if rol_usuario != Rol.ATLETA and rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el atleta o el entrenador pueden registrar ejecución."
            )
        if horas_ejecutadas < 0:
            raise ErrorValidacion("Las horas ejecutadas no pueden ser negativas.")
        ejecucion = EjecucionEntrenamiento(
            id=generar_id_ejecucion(),
            id_sesion=id_sesion,
            horas_ejecutadas=horas_ejecutadas,
            fecha_registro=fecha_registro,
            registrado_por_atleta=rol_usuario == Rol.ATLETA,
        )
        return self.repositorio.registrar_ejecucion(ejecucion)


@dataclass
class AprobarHorasEjecutadas:
    repositorio: RepositorioEntrenamientos

    def ejecutar(self, id_ejecucion: str, rol_usuario: Rol) -> EjecucionEntrenamiento:
        if rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el entrenador puede aprobar las horas ejecutadas."
            )
        return self.repositorio.aprobar_ejecucion(id_ejecucion)


@dataclass
class ConsultarCumplimientoSemanal:
    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self, id_atleta: str, semana: int, anio: int
    ) -> dict:
        plan = self.repositorio.listar_por_semana(id_atleta, semana, anio)
        if plan is None:
            raise EntidadNoEncontrada("No existe plan para esa semana.")
        return {
            "planificado": plan.total_horas_planificadas,
            "ejecutado_aprobado": plan.total_horas_ejecutadas_aprobadas,
            "porcentaje_cumplimiento": plan.porcentaje_cumplimiento,
        }


@dataclass
class RegistrarAsistencia:
    repositorio_asistencia: RepositorioAsistencia

    def ejecutar(
        self,
        id_atleta: str,
        id_sesion: str,
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
            id=generar_id_asistencia(),
            id_atleta=id_atleta,
            id_sesion=id_sesion,
            fecha=fecha,
            estado=estado,
        )
        return self.repositorio_asistencia.registrar(asistencia)


@dataclass
class ConsultarHistorialEntrenamientos:
    repositorio: RepositorioEntrenamientos

    def ejecutar(self, id_atleta: str) -> List[PlanEntrenamientoSemanal]:
        return self.repositorio.obtener_historial(id_atleta)


def generar_id_plan(id_atleta: str, semana: int, anio: int) -> str:
    return f"plan_{id_atleta}_{anio}_{semana}"


def generar_id_ejecucion() -> str:
    import uuid

    return str(uuid.uuid4())


def generar_id_asistencia() -> str:
    import uuid

    return str(uuid.uuid4())
