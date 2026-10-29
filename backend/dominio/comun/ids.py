"""Generación centralizada de identificadores del dominio."""
from __future__ import annotations

import random
import time
import uuid

def nuevo_id_entero() -> int:
    """Genera un ID entero único basado en marca de tiempo numérico."""
    return int(time.time_ns() % 1_000_000_000) + random.randint(1, 999)

def nuevo_id(prefijo: str = "") -> str:
    """Genera un identificador UUID (opcionalmente prefijado) para entidades de dominio.

 Se usa en los módulos cuyas tablas no dependen de un autonumérico (por ejemplo
 alertas y reportes generados en memoria).
 """
    base = uuid.uuid4().hex
    return f"{prefijo}_{base}" if prefijo else base
