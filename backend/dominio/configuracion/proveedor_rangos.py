"""Proveedor de rangos de evaluación respaldado por la configuración del sistema."""
from __future__ import annotations

from typing import Optional, Tuple

from ..indicadores.entidades import TipoIndicador
from ..indicadores.puertos import ProveedorRangosEvaluacion
from .puertos import RepositorioConfiguracion

class ProveedorRangosConfiguracion(ProveedorRangosEvaluacion):
    """RNF-07.2: lee los rangos configurados por el administrador."""

    def __init__(self, repositorio: RepositorioConfiguracion) -> None:
        self._repositorio = repositorio

    def rangos(
        self, tipo: TipoIndicador
    ) -> Optional[Tuple[float, float, float]]:
        configuracion = self._repositorio.obtener()
        valores = configuracion.rangos_evaluacion.get(tipo.value)
        if valores is None:
            return None
        return tuple(float(v) for v in valores)
