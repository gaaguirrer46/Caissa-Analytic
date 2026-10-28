"""Casos de uso (puertos primarios / driving) del módulo de Aperturas."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from ..auditoria.casos_de_uso import RegistrarCambio
from ..auditoria.entidades import TipoOperacion
from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorValidacion,
)
from ..comun.validaciones import convertir_enum, exigir_entero, exigir_texto
from .entidades import (
    AperturaRepertorio,
    ClasificacionUso,
    ColorApertura,
    EfectividadApertura,
    EstadoApertura,
    EstadisticaApertura,
    EstadisticaAperturaPorTorneo,
    NivelDominio,
)
from .puertos import ProveedorDatosApertura, RepositorioAperturas

_PATRON_ECO = re.compile(r"^[A-E][0-9]{2}$")

UMBRAL_FRECUENCIA_PRINCIPAL = 0.25
TOP_PRINCIPALES = 3

@dataclass
class RegistrarAperturaRepertorio:
    """registra una apertura del repertorio con datos validados."""

    repositorio: RepositorioAperturas

    def ejecutar(
        self, apertura: AperturaRepertorio, *, solicitante: Solicitante
    ) -> AperturaRepertorio:
        exigir_entrenador(solicitante, "registrar aperturas del repertorio")
        if not isinstance(apertura, AperturaRepertorio):
            raise ErrorValidacion("La apertura del repertorio es inválida.")
        exigir_entero(apertura.id_atleta, "id_atleta", minimo=1)
        eco = exigir_texto(apertura.codigo_eco, "codigo_eco", max_longitud=5).upper()
        if not _PATRON_ECO.match(eco):
            raise ErrorValidacion(
                "El código ECO es inválido; debe tener una letra A-E y dos dígitos."
            )
        apertura.codigo_eco = eco
        apertura.nombre = exigir_texto(
            apertura.nombre, "nombre", max_longitud=100
        )
        if apertura.variante:
            apertura.variante = exigir_texto(
                apertura.variante, "variante", max_longitud=100
            )
        apertura.color = convertir_enum(ColorApertura, apertura.color, "color")
        apertura.estado = convertir_enum(EstadoApertura, apertura.estado, "estado")
        apertura.nivel_dominio = convertir_enum(
            NivelDominio, apertura.nivel_dominio, "nivel_dominio"
        )
        apertura.clasificacion_uso = convertir_enum(
            ClasificacionUso, apertura.clasificacion_uso, "clasificacion_uso"
        )
        if apertura.fuente_estudio:
            apertura.fuente_estudio = exigir_texto(
                apertura.fuente_estudio, "fuente_estudio", max_longitud=255
            )
        if apertura.observaciones:
            apertura.observaciones = exigir_texto(
                apertura.observaciones, "observaciones", max_longitud=300
            )

        for existente in self.repositorio.listar_por_atleta(apertura.id_atleta):
            if (
                existente.codigo_eco == eco
                and existente.color == apertura.color
                and existente.variante == apertura.variante
            ):
                raise ErrorValidacion(
                    "La apertura ya está registrada para ese color y variante."
                )
        return self.repositorio.guardar(apertura)

@dataclass
class ActualizarEstadoApertura:
    """cambia el estado de estudio de una apertura.

el cambio de estado queda registrado en el historial de
 auditoría con el valor anterior y el nuevo.
 """

    repositorio: RepositorioAperturas

    auditor: Optional[RegistrarCambio] = None

    def ejecutar(
        self,
        id_apertura: int,
        estado: EstadoApertura | str,
        *,
        solicitante: Solicitante,
    ) -> AperturaRepertorio:
        exigir_entrenador(solicitante, "actualizar el estado de una apertura")
        exigir_entero(id_apertura, "id_apertura", minimo=1)
        estado_enum = convertir_enum(EstadoApertura, estado, "estado")
        apertura = self.repositorio.buscar_por_id(id_apertura)
        if apertura is None:
            raise EntidadNoEncontrada("Apertura no encontrada.")

        estado_previo = getattr(apertura.estado, "value", apertura.estado)
        actualizada = self.repositorio.actualizar_estado(
            id_apertura, estado_enum.value
        )
        if self.auditor is not None:
            if estado_previo != estado_enum.value:
                self.auditor.ejecutar(
                    str(solicitante.id_usuario),
                    "AperturaRepertorio",
                    TipoOperacion.MODIFICAR,
                    "estado",
                    str(estado_previo),
                    estado_enum.value,
                )
        return actualizada

@dataclass
class ClasificarAperturaPrincipalSecundaria:
    """ (clasificación manual): marca una apertura como principal o secundaria."""

    repositorio: RepositorioAperturas

    def ejecutar(
        self,
        id_apertura: int,
        clasificacion: ClasificacionUso | str,
        *,
        solicitante: Solicitante,
    ) -> AperturaRepertorio:
        exigir_entrenador(solicitante, "clasificar aperturas del repertorio")
        exigir_entero(id_apertura, "id_apertura", minimo=1)
        clasificacion_enum = convertir_enum(
            ClasificacionUso, clasificacion, "clasificacion_uso"
        )
        apertura = self.repositorio.buscar_por_id(id_apertura)
        if apertura is None:
            raise EntidadNoEncontrada("Apertura no encontrada.")
        apertura.clasificacion_uso = clasificacion_enum
        return self.repositorio.guardar(apertura)

@dataclass
class ClasificarAperturasPorFrecuencia:
    """ (automático): clasifica según la frecuencia real de uso.

 Regla del dominio: es PRINCIPAL la apertura con partidas jugadas que esté en
 el top 3 del repertorio o que concentre al menos el 25 % de las partidas
 totales del atleta; el resto pasa a SECUNDARIA.
 """

    repositorio: RepositorioAperturas

    def ejecutar(
        self, id_atleta: int, *, solicitante: Solicitante
    ) -> List[AperturaRepertorio]:
        exigir_entrenador(solicitante, "clasificar aperturas por frecuencia")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        aperturas = self.repositorio.listar_por_atleta(id_atleta)
        if not aperturas:
            return []

        jugadas_por_apertura = {}
        for apertura in aperturas:
            estadistica = self.repositorio.buscar_estadistica(apertura.id)
            jugadas_por_apertura[apertura.id] = (
                estadistica.partidas_jugadas if estadistica else 0
            )

        total = sum(jugadas_por_apertura.values())
        ordenadas = sorted(
            aperturas, key=lambda a: jugadas_por_apertura[a.id], reverse=True
        )
        principales = set()
        for posicion, apertura in enumerate(ordenadas):
            jugadas = jugadas_por_apertura[apertura.id]
            if jugadas <= 0:
                continue
            proporcion = jugadas / total if total else 0.0
            if posicion < TOP_PRINCIPALES or proporcion >= UMBRAL_FRECUENCIA_PRINCIPAL:
                principales.add(apertura.id)

        actualizadas: List[AperturaRepertorio] = []
        for apertura in aperturas:
            objetivo = (
                ClasificacionUso.PRINCIPAL
                if apertura.id in principales
                else ClasificacionUso.SECUNDARIA
            )
            if apertura.clasificacion_uso != objetivo:
                apertura.clasificacion_uso = objetivo
                apertura = self.repositorio.guardar(apertura)
            actualizadas.append(apertura)
        return actualizadas

@dataclass
class EvaluarEfectividadApertura:
    """la efectividad se mide por desempeño, no por valoración teórica."""

    repositorio: RepositorioAperturas

    def ejecutar(
        self, id_apertura: int, *, solicitante: Solicitante
    ) -> EfectividadApertura:
        exigir_entrenador(solicitante, "evaluar la efectividad de una apertura")
        exigir_entero(id_apertura, "id_apertura", minimo=1)
        estadistica = self.repositorio.buscar_estadistica(id_apertura)
        if estadistica is None:
            raise EntidadNoEncontrada(
                "No existen estadísticas para la apertura indicada."
            )
        return estadistica.efectividad()

@dataclass
class ConsultarEstadisticasGeneralesApertura:
    """estadísticas generales (partidas, resultados, accuracy, ACPL.)."""

    repositorio: RepositorioAperturas

    def ejecutar(
        self, id_apertura: int, *, solicitante: Solicitante
    ) -> EstadisticaApertura:
        exigir_entrenador(solicitante, "consultar estadísticas de una apertura")
        exigir_entero(id_apertura, "id_apertura", minimo=1)
        estadistica = self.repositorio.buscar_estadistica(id_apertura)
        if estadistica is None:
            raise EntidadNoEncontrada(
                "No existen estadísticas para la apertura indicada."
            )
        return estadistica

@dataclass
class CalcularEstadisticasApertura:
    """calcula las estadísticas generales desde partidas reales.

 La evaluación media del motor queda en ``None`` mientras no exista un
 adaptador de motor (Stockfish); el resto de métricas se calculan aquí.
 """

    repositorio: RepositorioAperturas
    proveedor_datos: ProveedorDatosApertura

    def ejecutar(
        self,
        id_apertura: int,
        color: Optional[ColorApertura | str] = None,
        *,
        solicitante: Solicitante,
    ) -> EstadisticaApertura:
        exigir_entrenador(solicitante, "calcular estadísticas de una apertura")
        exigir_entero(id_apertura, "id_apertura", minimo=1)
        apertura = self.repositorio.buscar_por_id(id_apertura)
        if apertura is None:
            raise EntidadNoEncontrada("Apertura no encontrada.")
        color_enum = apertura.color
        if color is not None:
            color_enum = convertir_enum(ColorApertura, color, "color")

        datos = self.proveedor_datos.partidas_con_apertura(
            apertura.id_atleta, apertura.codigo_eco, color_enum
        )
        victorias = empates = derrotas = 0
        accuracies: List[float] = []
        acpls: List[float] = []
        tiempos: List[float] = []
        errores = 0
        for partida, analisis in datos:
            puntos = partida.puntos_obtenidos()
            if puntos == 1.0:
                victorias += 1
            elif puntos == 0.5:
                empates += 1
            else:
                derrotas += 1
            if analisis is None:
                continue
            if analisis.accuracy is not None:
                accuracies.append(analisis.accuracy)
            if analisis.acpl is not None:
                acpls.append(analisis.acpl)
            if analisis.tiempo_promedio_jugada is not None:
                tiempos.append(analisis.tiempo_promedio_jugada)
            errores += analisis.blunders + analisis.errores

        estadistica = EstadisticaApertura(
            id_apertura=apertura.id,
            partidas_jugadas=len(datos),
            victorias=victorias,
            empates=empates,
            derrotas=derrotas,
            accuracy_promedio=(sum(accuracies) / len(accuracies)) if accuracies else None,
            acpl_promedio=(sum(acpls) / len(acpls)) if acpls else None,
            errores_frecuentes=errores,
            evaluacion_motor_promedio=None,
            tiempo_promedio=(sum(tiempos) / len(tiempos)) if tiempos else None,
        )
        return self.repositorio.guardar_estadistica(estadistica)

@dataclass
class ConsultarEstadisticasPorTorneo:
    """estadísticas de una apertura filtradas por contexto competitivo."""

    repositorio: RepositorioAperturas

    def ejecutar(
        self,
        id_apertura: int,
        torneo: Optional[str] = None,
        anio: Optional[int] = None,
        control_tiempo: Optional[str] = None,
        color: Optional[ColorApertura | str] = None,
        nivel_rival: Optional[str] = None,
        rival: Optional[str] = None,
        *,
        solicitante: Solicitante,
    ) -> List[EstadisticaAperturaPorTorneo]:
        exigir_entrenador(solicitante, "consultar estadísticas por torneo")
        exigir_entero(id_apertura, "id_apertura", minimo=1)
        if self.repositorio.buscar_por_id(id_apertura) is None:
            raise EntidadNoEncontrada("Apertura no encontrada.")
        color_enum = None
        if color is not None:
            color_enum = convertir_enum(ColorApertura, color, "color")
        estadisticas = self.repositorio.listar_estadisticas_por_apertura(
            id_apertura
        )
        return [
            e
            for e in estadisticas
            if (torneo is None or e.torneo == torneo)
            and (anio is None or e.anio == anio)
            and (control_tiempo is None or e.control_tiempo == control_tiempo)
            and (color_enum is None or e.color == color_enum)
            and (nivel_rival is None or e.nivel_rival == nivel_rival)
            and (rival is None or e.rival == rival)
        ]

__all__ = [
    "ActualizarEstadoApertura",
    "CalcularEstadisticasApertura",
    "ClasificarAperturaPrincipalSecundaria",
    "ClasificarAperturasPorFrecuencia",
    "ConsultarEstadisticasGeneralesApertura",
    "ConsultarEstadisticasPorTorneo",
    "EvaluarEfectividadApertura",
    "RegistrarAperturaRepertorio",
    "TOP_PRINCIPALES",
    "UMBRAL_FRECUENCIA_PRINCIPAL",
]
