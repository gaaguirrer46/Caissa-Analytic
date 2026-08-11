"""Casos de uso (puertos primarios / driving) del módulo de Usuarios.

Orquestan el flujo, inyectan dependencias por constructor y nunca
instancian adaptadores.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorAutenticacion,
    ErrorValidacion,
)
from .entidades import Permiso, Rol, Usuario
from .puertos import (
    PermisosPorRol,
    RepositorioUsuarios,
    ServicioHashContrasenas,
)

MAXIMO_ATLETAS_POR_ENTRENADOR = 40
MINIMO_ENTRENADORES_POR_ATLETA = 1
MAXIMO_ENTRENADORES_POR_ATLETA = 3


@dataclass
class AutenticarUsuario:
    repositorio: RepositorioUsuarios
    servicio_hash: ServicioHashContrasenas

    def ejecutar(self, correo: str, contrasena: str) -> Usuario:
        usuario = self.repositorio.buscar_por_correo(correo)
        if usuario is None or not self.servicio_hash.verificar(
            contrasena, usuario.hash_contrasena
        ):
            raise ErrorAutenticacion("Credenciales inválidas.")
        return usuario


@dataclass
class CrearUsuario:
    repositorio: RepositorioUsuarios
    servicio_hash: ServicioHashContrasenas

    def ejecutar(self, correo: str, contrasena: str, rol: Rol) -> Usuario:
        if not correo or "@" not in correo:
            raise ErrorValidacion("El correo es inválido.")
        if not contrasena or len(contrasena) < 8:
            raise ErrorValidacion("La contraseña debe tener al menos 8 caracteres.")
        if self.repositorio.existe(correo):
            raise ErrorValidacion(f"Ya existe un usuario con el correo {correo}.")
        if rol == Rol.ENTRENADOR and any(
            u.rol == Rol.ENTRENADOR for u in self.repositorio.listar_todos()
        ):
            raise ErrorValidacion(
                "Solo puede existir un usuario con rol ENTRENADOR como administrador."
            )
        hash_cont = self.servicio_hash.hashear(contrasena)
        usuario = Usuario(
            id=generar_id_usuario(),
            correo=correo,
            hash_contrasena=hash_cont,
            rol=rol,
        )
        return self.repositorio.guardar(usuario)


@dataclass
class VerificarPermiso:
    def ejecutar(self, usuario: Usuario, permiso: Permiso) -> bool:
        return PermisosPorRol.tiene_permiso(usuario.rol, permiso)


@dataclass
class ObtenerUsuarioActual:
    repositorio: RepositorioUsuarios

    def ejecutar(self, id_usuario: str) -> Usuario:
        usuario = self.repositorio.buscar_por_id(id_usuario)
        if usuario is None:
            raise EntidadNoEncontrada("Usuario no encontrado.")
        return usuario


def generar_id_usuario() -> str:
    import uuid

    return str(uuid.uuid4())


@dataclass(frozen=True)
class ValidacionLimiteEntrenador:
    """Regla de negocio: máximo de atletas por entrenador."""

    def validar_capacidad(self, cantidad_actual: int) -> None:
        if cantidad_actual >= MAXIMO_ATLETAS_POR_ENTRENADOR:
            raise ErrorValidacion(
                "El entrenador ya alcanzó el máximo de 40 atletas asignados."
            )


@dataclass(frozen=True)
class ValidacionLimiteEntrenadores:
    """Regla de negocio: un atleta tiene entre 1 y 3 entrenadores."""

    def validar(self, cantidad: int) -> None:
        if cantidad < MINIMO_ENTRENADORES_POR_ATLETA:
            raise ErrorValidacion(
                "El atleta debe tener al menos 1 entrenador asignado."
            )
        if cantidad > MAXIMO_ENTRENADORES_POR_ATLETA:
            raise ErrorValidacion(
                "El atleta no puede tener más de 3 entrenadores asignados."
            )
