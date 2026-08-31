"""Generación centralizada de identificadores numéricos del dominio."""
import random
import time


def nuevo_id_entero() -> int:
    """Genera un ID entero único basado en marca de tiempo numérico."""
    return int(time.time_ns() % 1_000_000_000) + random.randint(1, 999)
