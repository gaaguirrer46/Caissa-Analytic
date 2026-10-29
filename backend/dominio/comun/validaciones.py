"""Validaciones y coerciones compartidas por los casos de uso del dominio.

El objetivo es que toda entrada externa (formularios web, JSON, importaciones)
llegue al dominio con tipos y rangos verificados, lanzando siempre excepciones
de dominio (``ErrorValidacion``) y nunca ``TypeError`` / ``ValueError`` /
``KeyError`` genéricos."""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from math import isfinite
from typing import Optional, Type, TypeVar

from .errores import ErrorValidacion

E = TypeVar("E", bound=Enum)

def convertir_enum(clase_enum: Type[E], valor: object, campo: str) -> E:
    """Convierte ``valor`` al Enum ``clase_enum`` tolerando mayúsculas y espacios."""
    if isinstance(valor, clase_enum):
        return valor
    if not isinstance(valor, str) or not valor.strip():
        opciones = ", ".join(m.value for m in clase_enum)
        raise ErrorValidacion(
            f"El campo '{campo}' es obligatorio. Valores permitidos: {opciones}."
        )
    limpio = valor.strip().upper()
    try:
        return clase_enum(limpio)
    except ValueError:
        opciones = ", ".join(m.value for m in clase_enum)
        raise ErrorValidacion(
            f"El valor '{valor}' del campo '{campo}' es inválido. "
            f"Valores permitidos: {opciones}."
        )

def exigir_texto(
    valor: object,
    campo: str,
    *,
    max_longitud: Optional[int] = None,
    permitir_vacio: bool = False,
) -> str:
    """Valida y normaliza un texto obligatorio (recorta espacios)."""
    if valor is None:
        raise ErrorValidacion(f"El campo '{campo}' es obligatorio.")
    if not isinstance(valor, str):
        raise ErrorValidacion(f"El campo '{campo}' debe ser texto.")
    limpio = valor.strip()
    if not limpio and not permitir_vacio:
        raise ErrorValidacion(f"El campo '{campo}' no puede estar vacío.")
    if max_longitud is not None and len(limpio) > max_longitud:
        raise ErrorValidacion(
            f"El campo '{campo}' excede la longitud máxima de {max_longitud} caracteres."
        )
    return limpio

def exigir_entero(
    valor: object,
    campo: str,
    *,
    minimo: Optional[int] = None,
    maximo: Optional[int] = None,
) -> int:
    """Valida un entero (rechaza ``bool``, ``str`` numéricos y ``None``)."""
    if not isinstance(valor, int) or isinstance(valor, bool):
        raise ErrorValidacion(f"El campo '{campo}' debe ser un número entero.")
    if minimo is not None and valor < minimo:
        raise ErrorValidacion(f"El campo '{campo}' no puede ser menor que {minimo}.")
    if maximo is not None and valor > maximo:
        raise ErrorValidacion(f"El campo '{campo}' no puede ser mayor que {maximo}.")
    return valor

def exigir_decimal(
    valor: object,
    campo: str,
    *,
    minimo: Optional[float] = None,
    maximo: Optional[float] = None,
) -> float:
    """Valida un número real (acepta ``int`` y ``float``, rechaza ``bool``)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ErrorValidacion(f"El campo '{campo}' debe ser un número.")
    numero = float(valor)
    if numero != numero or not isfinite(numero):
        raise ErrorValidacion(f"El campo '{campo}' debe ser un número finito.")
    if minimo is not None and numero < minimo:
        raise ErrorValidacion(f"El campo '{campo}' no puede ser menor que {minimo}.")
    if maximo is not None and numero > maximo:
        raise ErrorValidacion(f"El campo '{campo}' no puede ser mayor que {maximo}.")
    return numero

def exigir_fecha(valor: object, campo: str) -> date:
    """Valida una fecha de tipo ``date`` (rechaza ``datetime`` y cadenas)."""
    if isinstance(valor, datetime) or not isinstance(valor, date):
        raise ErrorValidacion(f"El campo '{campo}' debe ser una fecha válida.")
    return valor

def exigir_fecha_texto(valor: object, campo: str) -> date:
    """Acepta ``date`` o una cadena ISO ``AAAA-MM-DD`` y devuelve ``date``."""
    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor
    if isinstance(valor, str) and valor.strip():
        try:
            return date.fromisoformat(valor.strip())
        except ValueError:
            pass
    raise ErrorValidacion(f"El campo '{campo}' debe ser una fecha válida (AAAA-MM-DD).")

def exigir_booleano(valor: object, campo: str) -> bool:
    """Valida un booleano estricto."""
    if not isinstance(valor, bool):
        raise ErrorValidacion(f"El campo '{campo}' debe ser verdadero o falso.")
    return valor
