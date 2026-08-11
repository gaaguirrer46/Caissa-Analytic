"""Generación centralizada de identificadores del dominio."""
import uuid


def nuevo_id(prefijo: str = "") -> str:
    """Genera un id único, opcionalmente prefijado por entidad."""
    id_unico = str(uuid.uuid4())
    if prefijo:
        return f"{prefijo}_{id_unico}"
    return id_unico
