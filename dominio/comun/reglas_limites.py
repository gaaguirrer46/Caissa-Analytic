"""Validaciones compartidas de límites de atletas y entrenadores (RF-01.8, RF-02.6)."""
from .constantes import (
    MAXIMO_ATLETAS_POR_ENTRENADOR,
    MAXIMO_ENTRENADORES_POR_ATLETA,
    MINIMO_ENTRENADORES_POR_ATLETA,
)
from .errores import ErrorValidacion


def validar_capacidad_entrenador(cantidad_actual: int) -> None:
    """Un entrenador puede tener como máximo 40 atletas asignados."""
    if cantidad_actual >= MAXIMO_ATLETAS_POR_ENTRENADOR:
        raise ErrorValidacion(
            "El entrenador ya alcanzó el máximo de 40 atletas asignados."
        )


def validar_entrenadores_por_atleta(cantidad: int) -> None:
    """Un atleta debe tener entre 1 y 3 entrenadores asignados."""
    if cantidad < MINIMO_ENTRENADORES_POR_ATLETA:
        raise ErrorValidacion("El atleta debe tener al menos 1 entrenador asignado.")
    if cantidad > MAXIMO_ENTRENADORES_POR_ATLETA:
        raise ErrorValidacion("El atleta no puede tener más de 3 entrenadores asignados.")
