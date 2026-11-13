"""Validaciones compartidas de límites de atletas y entrenadores."""
from .constantes import (
    MAXIMO_ATLETAS_POR_ENTRENADOR,
    MAXIMO_ENTRENADORES_POR_ATLETA,
    MINIMO_ENTRENADORES_POR_ATLETA,
)
from .errores import ErrorValidacion

def validar_capacidad_entrenador(
    cantidad_actual: int,
    maximo: int = MAXIMO_ATLETAS_POR_ENTRENADOR,
) -> None:
    """Un entrenador no puede superar el máximo configurado de atletas."""
    if cantidad_actual >= maximo:
        raise ErrorValidacion(
            f"El entrenador ya alcanzó el máximo de {maximo} atletas asignados."
        )

def validar_entrenadores_por_atleta(cantidad: int) -> None:
    """Un atleta debe tener entre 1 y 3 entrenadores asignados."""
    if cantidad < MINIMO_ENTRENADORES_POR_ATLETA:
        raise ErrorValidacion("El atleta debe tener al menos 1 entrenador asignado.")
    if cantidad > MAXIMO_ENTRENADORES_POR_ATLETA:
        raise ErrorValidacion("El atleta no puede tener más de 3 entrenadores asignados.")
