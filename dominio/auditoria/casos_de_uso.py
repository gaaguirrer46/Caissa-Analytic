"""Casos de uso (puertos primarios / driving) del módulo de Auditoría."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import List, Optional

from ..comun.errores import ErrorValidacion
from ..comun.ids import nuevo_id_entero
from .entidades import RegistroAuditoria, TipoOperacion
from .puertos import RepositorioAuditoria


@dataclass
class RegistrarCambio:
    repositorio: RepositorioAuditoria

    def ejecutar(
        self,
        usuario: str,
        entidad_afectada: str,
        tipo_operacion: TipoOperacion,
        campo_modificado: str = "",
        valor_anterior: Optional[str] = None,
        valor_nuevo: Optional[str] = None,
    ) -> RegistroAuditoria:
        if not usuario:
            raise ErrorValidacion("El usuario es obligatorio.")
        if not entidad_afectada:
            raise ErrorValidacion("La entidad afectada es obligatoria.")
        if tipo_operacion not in TipoOperacion:
            raise ErrorValidacion("El tipo de operación es inválido.")
        registro = RegistroAuditoria(
            id=nuevo_id_entero(),
            usuario=usuario,
            fecha_hora=datetime.now(timezone.utc),
            entidad_afectada=entidad_afectada,
            tipo_operacion=tipo_operacion,
            campo_modificado=campo_modificado,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
        )
        return self.repositorio.guardar(registro)


@dataclass
class ConsultarHistorialCambios:
    repositorio: RepositorioAuditoria

    def ejecutar(
        self,
        entidad: Optional[str] = None,
        usuario: Optional[str] = None,
        dia: Optional[date] = None,
    ) -> List[RegistroAuditoria]:
        if entidad:
            return self.repositorio.listar_por_entidad(entidad)
        if usuario:
            return self.repositorio.listar_por_usuario(usuario)
        if dia:
            return self.repositorio.listar_por_fecha(dia)
        raise ErrorValidacion(
            "Debe indicar al menos un filtro (entidad, usuario o fecha)."
        )


@dataclass
class ValidarIntegridadDatos:
    """Previene errores críticos: rating incorrecto, resultado inválido,
    eliminación no autorizada de históricos."""

    def ejecutar(self, **datos) -> None:
        rating = datos.get("rating")
        if rating is not None and (not isinstance(rating, int) or rating < 0):
            raise ErrorValidacion("El rating registrado es inválido.")

        resultado = datos.get("resultado")
        if resultado is not None and resultado not in ("1-0", "0-1", "1/2-1/2"):
            raise ErrorValidacion("El resultado registrado es inválido.")

        if datos.get("eliminacion_no_autorizada"):
            raise ErrorValidacion(
                "No está permitido eliminar información histórica sin autorización."
            )
