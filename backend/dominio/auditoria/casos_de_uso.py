"""Casos de uso (puertos primarios / driving) del módulo de Auditoría."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import List, Optional

from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.errores import ErrorValidacion
from ..comun.ids import nuevo_id_entero
from ..comun.validaciones import convertir_enum, exigir_entero, exigir_texto
from .entidades import RegistroAuditoria, TipoOperacion
from .puertos import RepositorioAuditoria

_RESULTADOS_VALIDOS = ("1-0", "0-1", "1/2-1/2")

@dataclass
class RegistrarCambio:
    """registra usuario, fecha/hora, campo y valores anterior/nuevo."""

    repositorio: RepositorioAuditoria

    def ejecutar(
        self,
        usuario: str,
        entidad_afectada: str,
        tipo_operacion: TipoOperacion | str,
        campo_modificado: str = "",
        valor_anterior: Optional[str] = None,
        valor_nuevo: Optional[str] = None,
    ) -> RegistroAuditoria:
        usuario_limpio = exigir_texto(usuario, "usuario", max_longitud=100)
        entidad = exigir_texto(entidad_afectada, "entidad_afectada", max_longitud=50)
        operacion = convertir_enum(TipoOperacion, tipo_operacion, "tipo_operacion")
        campo = ""
        if campo_modificado:
            campo = exigir_texto(
                campo_modificado, "campo_modificado", max_longitud=50
            )
        anterior = self._texto_opcional(valor_anterior, "valor_anterior")
        nuevo = self._texto_opcional(valor_nuevo, "valor_nuevo")

        registro = RegistroAuditoria(
            id=nuevo_id_entero(),
            usuario=usuario_limpio,
            fecha_hora=datetime.now(timezone.utc),
            entidad_afectada=entidad,
            tipo_operacion=operacion,
            campo_modificado=campo,
            valor_anterior=anterior,
            valor_nuevo=nuevo,
        )
        return self.repositorio.guardar(registro)

    @staticmethod
    def _texto_opcional(valor: Optional[object], campo: str) -> Optional[str]:
        if valor is None:
            return None
        if not isinstance(valor, str):
            valor = str(valor)
        if len(valor) > 500:
            raise ErrorValidacion(
                f"El campo '{campo}' excede la longitud máxima de 500 caracteres."
            )
        return valor

@dataclass
class ConsultarHistorialCambios:
    """consulta el trail de auditoría con filtros combinables."""

    repositorio: RepositorioAuditoria

    def ejecutar(
        self,
        entidad: Optional[str] = None,
        usuario: Optional[str] = None,
        dia: Optional[date] = None,
        *,
        solicitante: Solicitante,
    ) -> List[RegistroAuditoria]:
        exigir_entrenador(solicitante, "consultar el historial de auditoría")
        if not entidad and not usuario and not dia:
            raise ErrorValidacion(
                "Debe indicar al menos un filtro (entidad, usuario o fecha)."
            )
        if entidad:
            registros = self.repositorio.listar_por_entidad(entidad)
        elif usuario:
            registros = self.repositorio.listar_por_usuario(usuario)
        else:
            registros = self.repositorio.listar_por_fecha(dia)

        if usuario:
            registros = [r for r in registros if r.usuario == usuario]
        if dia:

            registros = [
                r for r in registros if r.fecha_hora.astimezone().date() == dia
            ]
        if entidad:
            registros = [r for r in registros if r.entidad_afectada == entidad]
        return registros

@dataclass
class ValidarIntegridadDatos:
    """ / RNF-02.5: validaciones preventivas de errores críticos.

 Casos cubiertos: rating fuera de rango, resultado inválido, eliminación no
 autorizada de históricos, modificación de estadísticas automáticas sin
 permiso, partida asignada a un atleta equivocado y reapertura de una
 competencia finalizada.
 """

    RATING_MINIMO = 0
    RATING_MAXIMO = 4000

    def ejecutar(self, **datos) -> None:
        rating = datos.get("rating")
        if rating is not None:
            exigir_entero(
                rating,
                "rating",
                minimo=self.RATING_MINIMO,
                maximo=self.RATING_MAXIMO,
            )

        resultado = datos.get("resultado")
        if resultado is not None and resultado not in _RESULTADOS_VALIDOS:
            raise ErrorValidacion("El resultado registrado es inválido.")

        if self._bandera(datos, "eliminacion_no_autorizada"):
            raise ErrorValidacion(
                "No está permitido eliminar información histórica sin autorización."
            )

        if self._bandera(datos, "modificacion_estadistica_automatica") and not (
            self._bandera(datos, "permiso_estadisticas")
        ):
            raise ErrorValidacion(
                "No se pueden modificar estadísticas automáticas sin permisos."
            )

        if self._bandera(datos, "competencia_finalizada") and self._bandera(
            datos, "reabrir_competencia"
        ):
            raise ErrorValidacion(
                "No se puede reabrir una competencia que ya fue finalizada."
            )

        id_esperado = datos.get("id_atleta_esperado")
        id_recibido = datos.get("id_atleta_partida")
        if id_esperado is not None and id_recibido is not None:
            exigir_entero(id_esperado, "id_atleta_esperado", minimo=1)
            exigir_entero(id_recibido, "id_atleta_partida", minimo=1)
            if id_esperado != id_recibido:
                raise ErrorValidacion(
                    "La partida se está asignando a un atleta equivocado."
                )

    @staticmethod
    def _bandera(datos: dict, clave: str) -> bool:
        valor = datos.get(clave, False)
        if not isinstance(valor, bool):
            raise ErrorValidacion(f"El indicador '{clave}' debe ser booleano.")
        return valor

__all__ = [
    "ConsultarHistorialCambios",
    "RegistrarCambio",
    "ValidarIntegridadDatos",
]
