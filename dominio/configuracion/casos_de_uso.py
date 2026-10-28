"""Casos de uso del módulo de Configuración del Sistema."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Dict, Optional, Sequence, Tuple

from ..auditoria.casos_de_uso import RegistrarCambio
from ..auditoria.entidades import TipoOperacion
from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.errores import ErrorAutenticacion, ErrorValidacion
from ..comun.validaciones import (
    convertir_enum,
    exigir_booleano,
    exigir_decimal,
    exigir_entero,
    exigir_texto,
)
from ..usuarios.entidades import SECCIONES_INVITADO, Rol
from .entidades import ConfiguracionSistema
from .puertos import RepositorioConfiguracion

def _exigir_entrenador(rol_usuario: Rol | str, accion: str) -> Rol:
    rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
    if rol != Rol.ENTRENADOR:
        raise ErrorAutenticacion(
            f"Acceso denegado: sólo el entrenador puede {accion}."
        )
    return rol

def _normalizar_secciones(secciones: Sequence[str] | None) -> Tuple[str, ...]:
    """Valida el catálogo de secciones que puede ver el invitado."""
    if secciones is None:
        return ()
    if isinstance(secciones, str) or not isinstance(secciones, (list, tuple)):
        raise ErrorValidacion(
            "Las secciones autorizadas deben ser una lista de textos."
        )
    resultado = []
    for seccion in secciones:
        nombre = exigir_texto(
            seccion, "sección autorizada", max_longitud=50
        )
        if nombre not in SECCIONES_INVITADO:
            raise ErrorValidacion(
                f"La sección '{nombre}' no está permitida. Válidas: "
                + ", ".join(SECCIONES_INVITADO)
                + "."
            )
        if nombre in resultado:
            raise ErrorValidacion(f"La sección '{nombre}' está duplicada.")
        resultado.append(nombre)
    return tuple(resultado)

@dataclass
class ConsultarConfiguracion:
    """el entrenador consulta la configuración vigente."""

    repositorio: RepositorioConfiguracion

    def ejecutar(
        self, rol_usuario: Rol | str
    ) -> ConfiguracionSistema:
        _exigir_entrenador(rol_usuario, "consultar la configuración")
        return self.repositorio.obtener()

@dataclass
class ActualizarConfiguracion:
    """ / RNF-07.1 / RNF-07.2: actualiza límites y rangos con validación."""

    repositorio: RepositorioConfiguracion

    def ejecutar(
        self,
        configuracion: ConfiguracionSistema,
        rol_usuario: Rol | str,
    ) -> ConfiguracionSistema:
        _exigir_entrenador(rol_usuario, "modificar la configuración")
        if not isinstance(configuracion, ConfiguracionSistema):
            raise ErrorValidacion("La configuración es inválida.")

        maximo_atletas = exigir_entero(
            configuracion.maximo_atletas_por_entrenador,
            "maximo_atletas_por_entrenador",
            minimo=1,
            maximo=10_000,
        )
        minimo_entrenadores = exigir_entero(
            configuracion.minimo_entrenadores_por_atleta,
            "minimo_entrenadores_por_atleta",
            minimo=1,
            maximo=100,
        )
        maximo_entrenadores = exigir_entero(
            configuracion.maximo_entrenadores_por_atleta,
            "maximo_entrenadores_por_atleta",
            minimo=1,
            maximo=100,
        )
        if maximo_entrenadores < minimo_entrenadores:
            raise ErrorValidacion(
                "El máximo de entrenadores no puede ser menor que el mínimo."
            )
        permitir = exigir_booleano(
            configuracion.permitir_autoevaluacion, "permitir_autoevaluacion"
        )

        rangos: Dict[str, Tuple[float, float, float]] = {}
        if not isinstance(configuracion.rangos_evaluacion, dict):
            raise ErrorValidacion("Los rangos de evaluación deben ser un diccionario.")
        for clave, valores in configuracion.rangos_evaluacion.items():
            nombre = exigir_texto(clave, "rango de evaluación", max_longitud=50)
            if not isinstance(valores, (tuple, list)) or len(valores) != 3:
                raise ErrorValidacion(
                    f"El rango '{nombre}' debe tener exactamente 3 valores "
                    "(excelente, bueno, aceptable)."
                )
            valores_numericos = tuple(
                exigir_decimal(valor, f"rango {nombre}") for valor in valores
            )
            rangos[nombre] = valores_numericos

        actualizado_por = exigir_texto(
            configuracion.actualizado_por, "actualizado_por", max_longitud=100
        )
        secciones = _normalizar_secciones(
            configuracion.secciones_autorizadas_invitado
        )
        nueva = ConfiguracionSistema(
            maximo_atletas_por_entrenador=maximo_atletas,
            minimo_entrenadores_por_atleta=minimo_entrenadores,
            maximo_entrenadores_por_atleta=maximo_entrenadores,
            permitir_autoevaluacion=permitir,
            rangos_evaluacion=rangos,
            secciones_autorizadas_invitado=secciones,
            actualizado_por=actualizado_por,
            fecha_actualizacion=datetime.now(timezone.utc),
        )
        return self.repositorio.guardar(nueva)

@dataclass
class ConfigurarAccesoInvitado:
    """el entrenador decide qué secciones ve el usuario invitado.

el cambio de la configuración de acceso queda registrado en
 el historial de auditoría.
 """

    repositorio: RepositorioConfiguracion

    auditor: Optional[RegistrarCambio] = None

    def ejecutar(
        self,
        secciones: Sequence[str],
        *,
        solicitante: Solicitante,
    ) -> ConfiguracionSistema:
        exigir_entrenador(solicitante, "configurar el acceso del invitado")
        validadas = _normalizar_secciones(secciones)
        actual = self.repositorio.obtener()
        nueva = replace(
            actual,
            secciones_autorizadas_invitado=validadas,
            actualizado_por=f"usuario:{solicitante.id_usuario}",
            fecha_actualizacion=datetime.now(timezone.utc),
        )
        guardada = self.repositorio.guardar(nueva)
        if self.auditor is not None:
            previas = tuple(actual.secciones_autorizadas_invitado or ())
            if previas != validadas:
                self.auditor.ejecutar(
                    str(solicitante.id_usuario),
                    "ConfiguracionSistema",
                    TipoOperacion.MODIFICAR,
                    "secciones_autorizadas_invitado",
                    ", ".join(previas),
                    ", ".join(validadas),
                )
        return guardada

__all__ = [
    "ActualizarConfiguracion",
    "ConfigurarAccesoInvitado",
    "ConsultarConfiguracion",
]
