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
        self, id_apertura: str, clasificacion: ClasificacionUso
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

    def ejecutar(self, id_apertura: str) -> EfectividadApertura:
        estadistica = self.repositorio.buscar_estadistica(id_apertura)
        if estadistica is None:
            raise EntidadNoEncontrada(
                "No existen estadísticas para la apertura indicada."
            )
        return estadistica.efectividad()


@dataclass
class ConsultarEstadisticasGeneralesApertura:
    repositorio: RepositorioAperturas

    def ejecutar(self, id_apertura: str) -> EstadisticaApertura:
        estadistica = self.repositorio.buscar_estadistica(id_apertura)
        if estadistica is None:
            raise EntidadNoEncontrada(
                "No existen estadísticas para la apertura indicada."
            )
        return estadistica
