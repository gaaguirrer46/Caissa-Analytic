"""Casos de uso (puertos primarios / driving) del módulo de Aperturas."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorValidacion,
)
from .entidades import (
    AperturaRepertorio,
    ClasificacionUso,
    ColorApertura,
    EfectividadApertura,
    EstadoApertura,
    EstadisticaApertura,
    EstadisticaAperturaPorTorneo,
)
from .puertos import RepositorioAperturas


@dataclass
class RegistrarAperturaRepertorio:
    repositorio: RepositorioAperturas

    def ejecutar(self, apertura: AperturaRepertorio) -> AperturaRepertorio:
        if not apertura.codigo_eco:
            raise ErrorValidacion("El código ECO es obligatorio.")
        if not apertura.nombre:
            raise ErrorValidacion("El nombre de la apertura es obligatorio.")
        if apertura.estado not in EstadoApertura:
            raise ErrorValidacion("El estado de la apertura es inválido.")
        return self.repositorio.guardar(apertura)


@dataclass
class ClasificarAperturaPrincipalSecundaria:
    repositorio: RepositorioAperturas

    def ejecutar(
        self, id_apertura: int, clasificacion: ClasificacionUso
    ) -> AperturaRepertorio:
        apertura = self.repositorio.buscar_por_id(id_apertura)
        if apertura is None:
            raise EntidadNoEncontrada("Apertura no encontrada.")
        if clasificacion not in ClasificacionUso:
            raise ErrorValidacion("Clasificación de uso inválida.")
        apertura.clasificacion_uso = clasificacion
        return self.repositorio.guardar(apertura)


@dataclass
class EvaluarEfectividadApertura:
    """La efectividad se mide por desempeño del atleta, no por valoración teórica."""

    repositorio: RepositorioAperturas

    def ejecutar(self, id_apertura: int) -> EfectividadApertura:
        estadistica = self.repositorio.buscar_estadistica(id_apertura)
        if estadistica is None:
            raise EntidadNoEncontrada(
                "No existen estadísticas para la apertura indicada."
            )
        return estadistica.efectividad()


@dataclass
class ConsultarEstadisticasGeneralesApertura:
    repositorio: RepositorioAperturas

    def ejecutar(self, id_apertura: int) -> EstadisticaApertura:
        estadistica = self.repositorio.buscar_estadistica(id_apertura)
        if estadistica is None:
            raise EntidadNoEncontrada(
                "No existen estadísticas para la apertura indicada."
            )
        return estadistica


@dataclass
class ConsultarEstadisticasPorTorneo:
    """RF-08.5: estadísticas de una apertura filtradas por contexto competitivo."""

    repositorio: RepositorioAperturas

    def ejecutar(
        self,
        id_apertura: int,
        torneo: Optional[str] = None,
        anio: Optional[int] = None,
        control_tiempo: Optional[str] = None,
        color: Optional[ColorApertura] = None,
        nivel_rival: Optional[str] = None,
        rival: Optional[str] = None,
    ) -> List[EstadisticaAperturaPorTorneo]:
        if self.repositorio.buscar_por_id(id_apertura) is None:
            raise EntidadNoEncontrada("Apertura no encontrada.")
        estadisticas = self.repositorio.listar_estadisticas_por_apertura(
            id_apertura
        )
        return [
            e
            for e in estadisticas
            if (torneo is None or e.torneo == torneo)
            and (anio is None or e.anio == anio)
            and (control_tiempo is None or e.control_tiempo == control_tiempo)
            and (color is None or e.color == color)
            and (nivel_rival is None or e.nivel_rival == nivel_rival)
            and (rival is None or e.rival == rival)
        ]
