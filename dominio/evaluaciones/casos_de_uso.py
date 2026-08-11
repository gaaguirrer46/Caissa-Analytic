"""Casos de uso (puertos primarios / driving) del módulo de Evaluación (RF-10)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..comun.errores import EntidadNoEncontrada, ErrorValidacion
from ..comun.ids import nuevo_id
from ..usuarios.entidades import Rol
from .entidades import (
    CALIFICACION_MAXIMA,
    CALIFICACION_MINIMA,
    EvaluacionAtleta,
    PeriodoEvaluacion,
    TipoIndicadorEvaluacion,
)
from .puertos import RepositorioEvaluaciones


@dataclass
class CrearEvaluacion:
    """RF-10.3: la completa el entrenador (obligatoria) o el atleta (opcional)."""

    repositorio: RepositorioEvaluaciones

    def ejecutar(
        self, evaluacion: EvaluacionAtleta, rol_usuario: Rol
    ) -> EvaluacionAtleta:
        if evaluacion.es_autoevaluacion and rol_usuario != Rol.ATLETA:
            raise ErrorValidacion(
                "Solo el atleta puede completar su autoevaluación."
            )
        if not evaluacion.es_autoevaluacion and rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el entrenador puede completar la evaluación oficial."
            )
        self._validar_contenido(evaluacion)
        return self.repositorio.guardar(evaluacion)

    @staticmethod
    def _validar_contenido(evaluacion: EvaluacionAtleta) -> None:
        if evaluacion.referencia_periodo is None or not evaluacion.referencia_periodo:
            raise ErrorValidacion(
                "La referencia del periodo (torneo, mes, etc.) es obligatoria."
            )
        if evaluacion.periodo not in PeriodoEvaluacion:
            raise ErrorValidacion("El periodo de evaluación es inválido.")
        if not evaluacion.calificaciones:
            raise ErrorValidacion(
                "La evaluación debe incluir al menos una calificación."
            )
        if not evaluacion.es_autoevaluacion:
            faltantes = set(TipoIndicadorEvaluacion) - set(evaluacion.calificaciones)
            if faltantes:
                raise ErrorValidacion(
                    "La evaluación del entrenador debe cubrir todos los "
                    "indicadores. Faltan: "
                    + ", ".join(sorted(i.value for i in faltantes))
                    + "."
                )
        for indicador, nota in evaluacion.calificaciones.items():
            if indicador not in TipoIndicadorEvaluacion:
                raise ErrorValidacion(
                    f"El indicador de evaluación {indicador!r} es inválido."
                )
            if not CALIFICACION_MINIMA <= nota <= CALIFICACION_MAXIMA:
                raise ErrorValidacion(
                    f"La calificación debe estar entre {CALIFICACION_MINIMA} y "
                    f"{CALIFICACION_MAXIMA}."
                )


@dataclass
class ActualizarEvaluacion:
    """RF-10.5: permite dar seguimiento entre ciclos editando la evaluación."""

    repositorio: RepositorioEvaluaciones

    def ejecutar(
        self,
        id_evaluacion: str,
        evaluacion_actualizada: EvaluacionAtleta,
        rol_usuario: Rol,
    ) -> EvaluacionAtleta:
        existente = self.repositorio.buscar_por_id(id_evaluacion)
        if existente is None:
            raise EntidadNoEncontrada("Evaluación no encontrada.")
        rol_esperado = Rol.ATLETA if existente.es_autoevaluacion else Rol.ENTRENADOR
        if rol_usuario != rol_esperado:
            raise ErrorValidacion(
                "No tiene permisos para modificar esta evaluación."
            )
        CrearEvaluacion._validar_contenido(evaluacion_actualizada)
        evaluacion_actualizada.id = id_evaluacion
        return self.repositorio.actualizar(evaluacion_actualizada)


@dataclass
class ConsultarEvaluacionesPorAtleta:
    """RF-10.5: evalucaciones de un atleta, opcionalmente por periodo."""

    repositorio: RepositorioEvaluaciones

    def ejecutar(
        self,
        id_atleta: str,
        periodo: Optional[PeriodoEvaluacion] = None,
    ) -> List[EvaluacionAtleta]:
        if periodo is not None:
            return self.repositorio.listar_por_periodo(id_atleta, periodo)
        return self.repositorio.listar_por_atleta(id_atleta)


def nueva_evaluacion(
    id_atleta: str,
    id_entrenador: str,
    periodo: PeriodoEvaluacion,
    referencia_periodo: str,
    fecha_realizacion: date,
    calificaciones: dict,
    fortalezas: str = "",
    aspectos_por_mejorar: str = "",
    recomendaciones: str = "",
    es_autoevaluacion: bool = False,
) -> EvaluacionAtleta:
    """Factoría de EvaluacionAtleta con id autogenerado."""
    return EvaluacionAtleta(
        id=nuevo_id("evaluacion"),
        id_atleta=id_atleta,
        id_entrenador=id_entrenador,
        periodo=periodo,
        referencia_periodo=referencia_periodo,
        fecha_realizacion=fecha_realizacion,
        calificaciones=calificaciones,
        fortalezas=fortalezas,
        aspectos_por_mejorar=aspectos_por_mejorar,
        recomendaciones=recomendaciones,
        es_autoevaluacion=es_autoevaluacion,
    )
