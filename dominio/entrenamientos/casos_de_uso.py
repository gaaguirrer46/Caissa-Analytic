"""Casos de uso (puertos primarios / driving) del módulo de Entrenamientos."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..atletas.puertos import ResolutorAtletaUsuario
from ..auditoria.casos_de_uso import RegistrarCambio
from ..auditoria.entidades import TipoOperacion
from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorAutenticacion,
    ErrorValidacion,
)
from ..comun.ids import nuevo_id_entero
from ..comun.validaciones import (
    convertir_enum,
    exigir_decimal,
    exigir_entero,
    exigir_fecha,
    exigir_texto,
)
from ..usuarios.entidades import Rol
from .entidades import (
    Asistencia,
    EjecucionEntrenamiento,
    EstadoAsistencia,
    EstadoSesion,
    PlanEntrenamientoSemanal,
    ResumenCumplimientoSemanal,
    SesionEntrenamiento,
    TipoEntrenamiento,
)
from .puertos import RepositorioAsistencia, RepositorioEntrenamientos

DIAS_SEMANA = (
    "LUNES",
    "MARTES",
    "MIERCOLES",
    "JUEVES",
    "VIERNES",
    "SABADO",
    "DOMINGO",
)

_ESTADOS_REPROGRAMABLES = (EstadoSesion.PROGRAMADA, EstadoSesion.REPROGRAMADA)
_HORAS_MAXIMAS_SESION = 24.0

def _exigir_entrenador(rol_usuario: Rol, accion: str) -> None:
    if rol_usuario != Rol.ENTRENADOR:
        raise ErrorAutenticacion(
            f"Acceso denegado: sólo el entrenador puede {accion}."
        )

def _exigir_atleta(rol_usuario: Rol, accion: str) -> None:
    if rol_usuario != Rol.ATLETA:
        raise ErrorAutenticacion(f"Acceso denegado: sólo el atleta puede {accion}.")

def _inicio_de_semana(semana: int, anio: int) -> date:
    try:
        return date.fromisocalendar(anio, semana, 1)
    except ValueError:
        raise ErrorValidacion(
            f"La semana {semana} del año {anio} no existe en el calendario ISO."
        )

def _normalizar_dia(dia: object) -> str:
    if not isinstance(dia, str):
        raise ErrorValidacion("El día de la semana es obligatorio.")
    limpio = dia.strip().upper().replace("É", "E").replace("Á", "A")
    if limpio not in DIAS_SEMANA:
        raise ErrorValidacion(
            f"El día '{dia}' es inválido. Valores permitidos: {', '.join(DIAS_SEMANA)}."
        )
    return limpio

@dataclass
class PlanificarEntrenamientoSemanal:
    """el entrenador define las horas antes del inicio de la semana."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_atleta: int,
        semana: int,
        anio: int,
        sesiones: List[SesionEntrenamiento],
        rol_usuario: Rol | str,
        fecha_actual: Optional[date] = None,
    ) -> PlanEntrenamientoSemanal:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "planificar entrenamientos")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        exigir_entero(semana, "semana", minimo=1, maximo=53)
        exigir_entero(anio, "anio", minimo=2000, maximo=2100)
        hoy = exigir_fecha(fecha_actual or date.today(), "fecha_actual")

        inicio_semana = _inicio_de_semana(semana, anio)
        if hoy >= inicio_semana:
            raise ErrorValidacion(
                "Las horas planificadas deben definirse antes del inicio de la "
                f"semana ({inicio_semana.isoformat()})."
            )

        if not isinstance(sesiones, list) or not sesiones:
            raise ErrorValidacion("El plan semanal debe contener al menos una sesión.")

        if self.repositorio.listar_por_semana(id_atleta, semana, anio) is not None:
            raise ErrorValidacion(
                "Ya existe un plan de entrenamiento para esa semana."
            )

        for sesion in sesiones:
            if not isinstance(sesion, SesionEntrenamiento):
                raise ErrorValidacion("Cada sesión del plan es inválida.")
            sesion.tipo = convertir_enum(TipoEntrenamiento, sesion.tipo, "tipo")
            sesion.dia_semana = _normalizar_dia(sesion.dia_semana)
            sesion.horas_planificadas = exigir_decimal(
                sesion.horas_planificadas,
                "horas_planificadas",
                minimo=0.01,
                maximo=_HORAS_MAXIMAS_SESION,
            )
            estado = convertir_enum(EstadoSesion, sesion.estado, "estado")
            if estado != EstadoSesion.PROGRAMADA:
                raise ErrorValidacion(
                    "Una sesión nueva debe planificarse en estado PROGRAMADA."
                )
            sesion.estado = estado
            if sesion.observaciones:
                sesion.observaciones = exigir_texto(
                    sesion.observaciones, "observaciones", max_longitud=500
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
    """cambia el día de una sesión y la marca como REPROGRAMADA."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_sesion: int,
        nuevo_dia: str,
        rol_usuario: Rol | str,
    ) -> SesionEntrenamiento:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "reprogramar sesiones")
        exigir_entero(id_sesion, "id_sesion", minimo=1)
        dia = _normalizar_dia(nuevo_dia)
        sesion = self.repositorio.buscar_sesion(id_sesion)
        if sesion is None:
            raise EntidadNoEncontrada("Sesión no encontrada.")
        if sesion.estado not in _ESTADOS_REPROGRAMABLES:
            raise ErrorValidacion(
                f"No se puede reprogramar una sesión en estado {sesion.estado.value}."
            )
        sesion.dia_semana = dia
        sesion.estado = EstadoSesion.REPROGRAMADA
        return self.repositorio.actualizar_sesion(sesion)

@dataclass
class CancelarSesion:
    """el entrenador cancela una sesión aún no ejecutada."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_sesion: int,
        rol_usuario: Rol | str,
        motivo: str = "",
    ) -> SesionEntrenamiento:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "cancelar sesiones")
        exigir_entero(id_sesion, "id_sesion", minimo=1)
        sesion = self.repositorio.buscar_sesion(id_sesion)
        if sesion is None:
            raise EntidadNoEncontrada("Sesión no encontrada.")
        if sesion.estado not in _ESTADOS_REPROGRAMABLES:
            raise ErrorValidacion(
                f"No se puede cancelar una sesión en estado {sesion.estado.value}."
            )

        observaciones = (
            exigir_texto(motivo, "motivo", max_longitud=500)
            if motivo
            else sesion.observaciones
        )
        sesion.estado = EstadoSesion.CANCELADA
        sesion.observaciones = observaciones
        return self.repositorio.actualizar_sesion(sesion)

@dataclass
class RegistrarEjecucionEntrenamiento:
    """el atleta reporta las horas ejecutadas de una sesión.

 Frecuencia: el registro es por sesión —diario, no en bloque— y
 nunca con fecha futura; el plan semanal se define antes del inicio de la
 semana.
 """

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_sesion: int,
        horas_ejecutadas: float,
        fecha_registro: date,
        rol_usuario: Rol | str = Rol.ATLETA,
    ) -> EjecucionEntrenamiento:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_atleta(rol, "registrar la ejecución de sus horas")
        exigir_entero(id_sesion, "id_sesion", minimo=1)
        horas = exigir_decimal(
            horas_ejecutadas,
            "horas_ejecutadas",
            minimo=0.0,
            maximo=_HORAS_MAXIMAS_SESION,
        )
        fecha = exigir_fecha(fecha_registro, "fecha_registro")
        if fecha > date.today():
            raise ErrorValidacion("La fecha de registro no puede ser futura.")

        sesion = self.repositorio.buscar_sesion(id_sesion)
        if sesion is None:
            raise EntidadNoEncontrada("La sesión no existe.")
        if sesion.estado == EstadoSesion.CANCELADA:
            raise ErrorValidacion(
                "No se puede registrar ejecución de una sesión cancelada."
            )
        if sesion.ejecucion_aprobada:
            raise ErrorValidacion(
                "La ejecución de esta sesión ya fue aprobada por el entrenador."
            )

        ejecucion = EjecucionEntrenamiento(
            id=nuevo_id_entero(),
            id_sesion=id_sesion,
            horas_ejecutadas=horas,
            fecha_registro=fecha,
            registrado_por_atleta=True,
        )
        return self.repositorio.registrar_ejecucion(ejecucion)

@dataclass
class AprobarHorasEjecutadas:
    """el entrenador aprueba las horas reportadas por el atleta.

la aprobación queda registrada en el historial de auditoría.
 """

    repositorio: RepositorioEntrenamientos

    auditor: Optional[RegistrarCambio] = None

    def ejecutar(
        self,
        id_ejecucion: int,
        rol_usuario: Rol | str,
        *,
        solicitante: Optional[Solicitante] = None,
    ) -> EjecucionEntrenamiento:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "aprobar las horas ejecutadas")
        exigir_entero(id_ejecucion, "id_ejecucion", minimo=1)
        ejecucion = self.repositorio.buscar_ejecucion(id_ejecucion)
        if ejecucion is None:
            raise EntidadNoEncontrada("Ejecución de entrenamiento no encontrada.")

        sesion = self.repositorio.buscar_sesion(ejecucion.id_sesion)
        if sesion is not None and sesion.estado == EstadoSesion.CANCELADA:
            raise ErrorValidacion(
                "No se puede aprobar horas de una sesión cancelada."
            )
        if ejecucion.aprobado_por_entrenador:
            return ejecucion
        aprobada = self.repositorio.aprobar_ejecucion(id_ejecucion)
        if self.auditor is not None:
            self.auditor.ejecutar(
                (
                    str(solicitante.id_usuario)
                    if solicitante is not None
                    else f"rol:{rol.value}"
                ),
                "EjecucionEntrenamiento",
                TipoOperacion.MODIFICAR,
                "aprobado_por_entrenador",
                str(False),
                str(True),
            )
        return aprobada

@dataclass
class ConsultarCumplimientoSemanal:
    """compara horas planificadas versus ejecutadas y aprobadas."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_atleta: int,
        semana: int,
        anio: int,
        *,
        solicitante: Solicitante,
    ) -> ResumenCumplimientoSemanal:
        exigir_entrenador(solicitante, "consultar el cumplimiento de un atleta")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        exigir_entero(semana, "semana", minimo=1, maximo=53)
        exigir_entero(anio, "anio", minimo=2000, maximo=2100)
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
class ConsultarDetalleSemanal:
    """el detalle del entrenamiento se consulta únicamente por semana."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self,
        id_atleta: int,
        semana: int,
        anio: int,
        *,
        solicitante: Solicitante,
    ) -> PlanEntrenamientoSemanal:
        exigir_entrenador(solicitante, "consultar el detalle de una semana")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        exigir_entero(semana, "semana", minimo=1, maximo=53)
        exigir_entero(anio, "anio", minimo=2000, maximo=2100)
        plan = self.repositorio.listar_por_semana(id_atleta, semana, anio)
        if plan is None:
            raise EntidadNoEncontrada("No existe plan para esa semana.")
        return plan

@dataclass
class RegistrarAsistencia:
    """asistencia registrada por el entrenador tras la sesión.

 Frecuencia: la sesión no tiene fecha-hora concreta en el modelo
 oficial (``dia_semana`` + semana ISO), por lo que "después de cada sesión"
 se garantiza como registro no futuro (fecha <= hoy) y exactamente una
 asistencia por sesión — limitación de modelo documentada.
 """

    repositorio_asistencia: RepositorioAsistencia
    repositorio_entrenamientos: Optional[RepositorioEntrenamientos] = None

    def ejecutar(
        self,
        id_atleta: int,
        id_sesion: int,
        fecha: date,
        estado: EstadoAsistencia | str,
        rol_usuario: Rol | str,
    ) -> Asistencia:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "registrar la asistencia")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        exigir_entero(id_sesion, "id_sesion", minimo=1)
        fecha_registro = exigir_fecha(fecha, "fecha")
        if fecha_registro > date.today():
            raise ErrorValidacion("La asistencia no puede registrarse con fecha futura.")
        estado_enum = convertir_enum(EstadoAsistencia, estado, "estado")
        if (
            self.repositorio_entrenamientos is not None
            and self.repositorio_entrenamientos.buscar_sesion(id_sesion) is None
        ):
            raise EntidadNoEncontrada("La sesión no existe.")

        if self.repositorio_entrenamientos is not None:
            plan = self.repositorio_entrenamientos.buscar_plan_de_sesion(id_sesion)
            if plan is not None and plan.id_atleta != id_atleta:
                raise ErrorValidacion(
                    "La sesión indicada no pertenece al plan de ese atleta."
                )

        if any(
            registro.id_atleta == id_atleta
            for registro in self.repositorio_asistencia.listar_por_sesion(id_sesion)
        ):
            raise ErrorValidacion(
                "Ya existe un registro de asistencia para ese atleta en esta sesión."
            )

        asistencia = Asistencia(
            id=nuevo_id_entero(),
            id_atleta=id_atleta,
            id_sesion=id_sesion,
            fecha=fecha_registro,
            estado=estado_enum,
        )
        return self.repositorio_asistencia.registrar(asistencia)

@dataclass
class ConsultarHistorialEntrenamientos:
    """historial completo de sesiones conservando todos los estados."""

    repositorio: RepositorioEntrenamientos

    def ejecutar(
        self, id_atleta: int, *, solicitante: Solicitante
    ) -> List[PlanEntrenamientoSemanal]:
        exigir_entrenador(solicitante, "consultar el historial de entrenamientos")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        return self.repositorio.obtener_historial(id_atleta)

@dataclass
class RegistrarMiEjecucionEntrenamiento:
    """el atleta registra la ejecución de una sesión de su propio plan.

 Resuelve la identidad desde el ``Solicitante`` autenticado y verifica que
 el plan de la sesión pertenezca al atleta vinculado. La aprobación sigue
 siendo del entrenador.
 """

    repositorio: RepositorioEntrenamientos
    resolutor: ResolutorAtletaUsuario

    def ejecutar(
        self,
        solicitante: Solicitante,
        id_sesion: int,
        horas_ejecutadas: float,
        fecha_registro: date,
    ) -> EjecucionEntrenamiento:
        exigir_entero(id_sesion, "id_sesion", minimo=1)
        id_atleta = self.resolutor.atleta_de_usuario(solicitante.id_usuario)
        if id_atleta is None:
            raise EntidadNoEncontrada(
                "No existe un atleta vinculado a este usuario."
            )
        plan = self.repositorio.buscar_plan_de_sesion(id_sesion)
        if plan is None:
            raise EntidadNoEncontrada("La sesión no existe.")
        if plan.id_atleta != id_atleta:
            raise ErrorAutenticacion(
                "Acceso denegado: la sesión no pertenece a su plan de entrenamiento."
            )
        return RegistrarEjecucionEntrenamiento(self.repositorio).ejecutar(
            id_sesion=id_sesion,
            horas_ejecutadas=horas_ejecutadas,
            fecha_registro=fecha_registro,
            rol_usuario=Rol.ATLETA,
        )

__all__ = [
    "AprobarHorasEjecutadas",
    "CancelarSesion",
    "ConsultarCumplimientoSemanal",
    "ConsultarDetalleSemanal",
    "ConsultarHistorialEntrenamientos",
    "DIAS_SEMANA",
    "PlanificarEntrenamientoSemanal",
    "RegistrarAsistencia",
    "RegistrarEjecucionEntrenamiento",
    "RegistrarMiEjecucionEntrenamiento",
    "ReprogramarSesion",
]
