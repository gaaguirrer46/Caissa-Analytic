"""Control de acceso compartido.

``Solicitante`` representa la identidad ya autenticada que el adaptador primario
entrega al dominio. Las operaciones administrativas exigen rol Entrenador; el
atleta sólo utiliza los casos de uso de autoservicio."""
from __future__ import annotations

from dataclasses import dataclass

from ..comun.errores import ErrorAutenticacion, ErrorValidacion
from ..usuarios.entidades import Rol

@dataclass(frozen=True)
class Solicitante:
    """Identidad autenticada de quien ejecuta una operación."""

    id_usuario: int
    rol: Rol

    def __post_init__(self) -> None:
        if not isinstance(self.id_usuario, int) or isinstance(self.id_usuario, bool) or self.id_usuario <= 0:
            raise ErrorValidacion("El id del solicitante debe ser un entero positivo.")
        if not isinstance(self.rol, Rol):
            raise ErrorValidacion("El rol del solicitante es inválido.")

def exigir_entrenador(solicitante: Solicitante, accion: str) -> None:
    """niega la operación a cualquier rol distinto de Entrenador."""
    if solicitante is None or solicitante.rol != Rol.ENTRENADOR:
        rol = getattr(solicitante, "rol", None)
        nombre = rol.value if isinstance(rol, Rol) else "ANÓNIMO"
        raise ErrorAutenticacion(
            f"Acceso denegado: el rol {nombre} no puede {accion}."
        )
