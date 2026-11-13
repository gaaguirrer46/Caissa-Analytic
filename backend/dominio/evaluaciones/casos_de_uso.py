"""Casos de uso (puertos primarios / driving) del módulo de Evaluación."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import fmean
from typing import Dict, List, Optional

from ..atletas.puertos import ResolutorAtletaUsuario
from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorAutenticacion,
    ErrorValidacion,
)
from ..comun.ids import nuevo_id_entero
from ..comun.validaciones import (
    convertir_enum,
    exigir_booleano,
    exigir_entero,
    exigir_fecha,
    exigir_texto,
)
from ..usuarios.entidades import Rol
from .entidades import (
    CALIFICACION_MAXIMA,
    CALIFICACION_MINIMA,
    EvaluacionAtleta,
    PeriodoEvaluacion,
    ResumenEvaluaciones,
    TipoIndicadorEvaluacion,
)
from .puertos import RepositorioEvaluaciones

def _validar_contenido(evaluacion: EvaluacionAtleta) -> None:
    """valida y normaliza el contenido de la evaluación."""
    if not isinstance(evaluacion, EvaluacionAtleta):
        raise ErrorValidacion("La evaluación es inválida.")
    exigir_entero(evaluacion.id_atleta, "id_atleta", minimo=1)
    exigir_entero(evaluacion.id_entrenador, "id_entrenador", minimo=1)
    exigir_booleano(evaluacion.es_autoevaluacion, "es_autoevaluacion")
    evaluacion.periodo = convertir_enum(
        PeriodoEvaluacion, evaluacion.periodo, "periodo"
    )
    evaluacion.referencia_periodo = exigir_texto(
        evaluacion.referencia_periodo, "referencia_periodo", max_longitud=50
    )
    fecha = exigir_fecha(evaluacion.fecha_realizacion, "fecha_realizacion")
    if fecha > date.today():
        raise ErrorValidacion("La fecha de la evaluación no puede ser futura.")

    for campo in ("fortalezas", "aspectos_por_mejorar", "recomendaciones"):
        setattr(
            evaluacion,
            campo,
            exigir_texto(getattr(evaluacion, campo), campo, max_longitud=500),
        )

    if not isinstance(evaluacion.calificaciones, dict) or not evaluacion.calificaciones:
        raise ErrorValidacion("La evaluación debe incluir al menos una calificación.")

    normalizadas: dict[TipoIndicadorEvaluacion, int] = {}
    for indicador, nota in evaluacion.calificaciones.items():
        indicador_enum = convertir_enum(
            TipoIndicadorEvaluacion, indicador, "indicador de evaluación"
        )
        nota_valida = exigir_entero(
            nota,
            f"calificación de {indicador_enum.value}",
            minimo=CALIFICACION_MINIMA,
            maximo=CALIFICACION_MAXIMA,
        )
        normalizadas[indicador_enum] = nota_valida
    evaluacion.calificaciones = normalizadas

    if not evaluacion.es_autoevaluacion:
        faltantes = set(TipoIndicadorEvaluacion) - set(normalizadas)
        if faltantes:
            raise ErrorValidacion(
                "La evaluación del entrenador debe cubrir todos los indicadores. "
                "Faltan: " + ", ".join(sorted(i.value for i in faltantes)) + "."
            )

@dataclass
class CrearEvaluacion:
    """la completa el entrenador (obligatoria) o el atleta (opcional)."""

    repositorio: RepositorioEvaluaciones

    resolutor: Optional[ResolutorAtletaUsuario] = None

    def ejecutar(
        self,
        evaluacion: EvaluacionAtleta,
        rol_usuario: Rol | str,
        *,
        id_usuario: Optional[int] = None,
    ) -> EvaluacionAtleta:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        if not isinstance(evaluacion, EvaluacionAtleta):
            raise ErrorValidacion("La evaluación es inválida.")
        if evaluacion.es_autoevaluacion and rol != Rol.ATLETA:
            raise ErrorAutenticacion(
                "Acceso denegado: sólo el atleta puede completar su autoevaluación."
            )
        if not evaluacion.es_autoevaluacion and rol != Rol.ENTRENADOR:
            raise ErrorAutenticacion(
                "Acceso denegado: sólo el entrenador puede completar la evaluación oficial."
            )
        _validar_contenido(evaluacion)
        if evaluacion.es_autoevaluacion:

            vinculado = (
                self.resolutor.atleta_de_usuario(id_usuario)
                if self.resolutor is not None and id_usuario is not None
                else None
            )
            if vinculado is None or vinculado != evaluacion.id_atleta:
                raise ErrorAutenticacion(
                    "Acceso denegado: la autoevaluación sólo puede registrarse "
                    "sobre el propio atleta del usuario autenticado."
                )
        return self.repositorio.guardar(evaluacion)

@dataclass
class ActualizarEvaluacion:
    """permite dar seguimiento entre ciclos editando la evaluación."""

    repositorio: RepositorioEvaluaciones

    def ejecutar(
        self,
        id_evaluacion: int,
        evaluacion_actualizada: EvaluacionAtleta,
        rol_usuario: Rol | str,
    ) -> EvaluacionAtleta:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        exigir_entero(id_evaluacion, "id_evaluacion", minimo=1)
        existente = self.repositorio.buscar_por_id(id_evaluacion)
        if existente is None:
            raise EntidadNoEncontrada("Evaluación no encontrada.")
        rol_esperado = Rol.ATLETA if existente.es_autoevaluacion else Rol.ENTRENADOR
        if rol != rol_esperado:
            raise ErrorAutenticacion(
                "Acceso denegado: no tiene permisos para modificar esta evaluación."
            )
        if not isinstance(evaluacion_actualizada, EvaluacionAtleta):
            raise ErrorValidacion("La evaluación es inválida.")

        if evaluacion_actualizada.es_autoevaluacion != existente.es_autoevaluacion:
            raise ErrorValidacion(
                "No se puede cambiar el tipo (autoevaluación/oficial) de una evaluación."
            )
        _validar_contenido(evaluacion_actualizada)
        evaluacion_actualizada.id = id_evaluacion
        return self.repositorio.actualizar(evaluacion_actualizada)

@dataclass
class ConsultarEvaluacionesPorAtleta:
    """consulta administrativa de evaluaciones (sólo entrenador).

 Las evaluaciones oficiales son confidenciales; el atleta usa
 ``ConsultarMisEvaluaciones``, que sólo devuelve sus autoevaluaciones.
 """

    repositorio: RepositorioEvaluaciones

    def ejecutar(
        self,
        id_atleta: int,
        periodo: Optional[PeriodoEvaluacion | str] = None,
        *,
        solicitante: Solicitante,
    ) -> List[EvaluacionAtleta]:
        exigir_entrenador(solicitante, "consultar evaluaciones de un atleta")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        if periodo is None:
            return self.repositorio.listar_por_atleta(id_atleta)
        periodo_enum = convertir_enum(PeriodoEvaluacion, periodo, "periodo")
        return self.repositorio.listar_por_periodo(id_atleta, periodo_enum)

@dataclass
class ConsultarMisEvaluaciones:
    """el atleta consulta únicamente sus propias autoevaluaciones.

 Las evaluaciones oficiales del entrenador no se exponen por esta vía.
 """

    repositorio: RepositorioEvaluaciones
    resolutor: ResolutorAtletaUsuario

    def ejecutar(self, id_usuario: int) -> List[EvaluacionAtleta]:
        exigir_entero(id_usuario, "id_usuario", minimo=1)
        id_atleta = self.resolutor.atleta_de_usuario(id_usuario)
        if id_atleta is None:
            raise EntidadNoEncontrada(
                "No existe un atleta vinculado a este usuario."
            )
        return [
            evaluacion
            for evaluacion in self.repositorio.listar_por_atleta(id_atleta)
            if evaluacion.es_autoevaluacion
        ]

def nueva_evaluacion(
    id_atleta: int,
    id_entrenador: int,
    periodo: PeriodoEvaluacion,
    referencia_periodo: str,
    fecha_realizacion: date,
    calificaciones: dict,
    fortalezas: str = "",
    aspectos_por_mejorar: str = "",
    recomendaciones: str = "",
    es_autoevaluacion: bool = False,
) -> EvaluacionAtleta:
    """Factoría de EvaluacionAtleta con id autogenerado (sin persistencia)."""
    return EvaluacionAtleta(
        id=nuevo_id_entero(),
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

@dataclass
class ResumirEvaluaciones:
    """emplea las evaluaciones del atleta entre ciclos.

 Cuatro fines del resumen (sólo evaluaciones
 **oficiales** del entrenador: la autoevaluación opcional se consulta
 aparte con ``ConsultarMisEvaluaciones`` y no se mezcla):

 - **Informes periódicos:** :meth:`ResumenEvaluaciones.a_contenido`
 alimenta el motor genérico ``GenerarReporte`` para
 exportar el informe en PDF/Excel.
 - **Seguimiento entre ciclos:** variación de la última evaluación
 frente a la anterior (general y por indicador).
 - **Áreas de mejora:** los tres indicadores con menor promedio
 histórico, orden ascendente (a igualdad, por nombre).
 - **Planificación deportiva:** recomendaciones consolidadas de los
 tres ciclos más recientes, del más reciente al más antiguo.

 Sin evaluaciones el resumen sale en cero (no se inventan datos).
 """

    repositorio: RepositorioEvaluaciones

    def ejecutar(
        self,
        id_atleta: int,
        *,
        solicitante: Solicitante,
    ) -> ResumenEvaluaciones:
        exigir_entrenador(solicitante, "resumir las evaluaciones de un atleta")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        evaluaciones = sorted(
            (
                evaluacion
                for evaluacion in self.repositorio.listar_por_atleta(id_atleta)

                if not evaluacion.es_autoevaluacion
            ),
            key=lambda e: (e.fecha_realizacion, e.id),
        )
        if not evaluaciones:
            return ResumenEvaluaciones(
                id_atleta=id_atleta,
                cantidad_evaluaciones=0,
                ultima_evaluacion=None,
                promedio_general=0.0,
                promedio_por_indicador={},
                areas_de_mejora=[],
                variacion_ultimo_ciclo=0.0,
                variaciones_por_indicador={},
                recomendaciones_consolidadas=[],
            )

        notas: List[float] = []
        notas_por_indicador: Dict[TipoIndicadorEvaluacion, List[float]] = {}
        for evaluacion in evaluaciones:
            for indicador, nota in evaluacion.calificaciones.items():
                notas.append(float(nota))
                notas_por_indicador.setdefault(indicador, []).append(float(nota))
        promedios = {
            indicador: fmean(valores)
            for indicador, valores in notas_por_indicador.items()
        }

        areas_de_mejora = sorted(
            promedios, key=lambda i: (promedios[i], i.value)
        )[:3]

        ultima = evaluaciones[-1]
        anterior = evaluaciones[-2] if len(evaluaciones) > 1 else None
        variaciones: Dict[TipoIndicadorEvaluacion, float] = {}
        variacion_general = 0.0
        if anterior is not None:
            variacion_general = (
                float(ultima.promedio_calificaciones)
                - float(anterior.promedio_calificaciones)
            )
            variaciones = {
                indicador: float(ultima.calificaciones[indicador])
                - float(anterior.calificaciones[indicador])
                for indicador in (
                    set(ultima.calificaciones) & set(anterior.calificaciones)
                )
            }
        recomendaciones = [
            evaluacion.recomendaciones
            for evaluacion in reversed(evaluaciones[-3:])
            if evaluacion.recomendaciones
        ]
        return ResumenEvaluaciones(
            id_atleta=id_atleta,
            cantidad_evaluaciones=len(evaluaciones),
            ultima_evaluacion=ultima.fecha_realizacion,
            promedio_general=fmean(notas),
            promedio_por_indicador=promedios,
            areas_de_mejora=areas_de_mejora,
            variacion_ultimo_ciclo=variacion_general,
            variaciones_por_indicador=variaciones,
            recomendaciones_consolidadas=recomendaciones,
        )

__all__ = [
    "ActualizarEvaluacion",
    "ConsultarEvaluacionesPorAtleta",
    "ConsultarMisEvaluaciones",
    "CrearEvaluacion",
    "ResumirEvaluaciones",
    "nueva_evaluacion",
]
