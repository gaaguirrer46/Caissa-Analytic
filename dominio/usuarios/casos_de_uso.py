"""Casos de uso (puertos primarios / driving) del módulo de Usuarios."""
from __future__ import annotations

from dataclasses import dataclass

from ..comun.constantes import (
    MAXIMO_ATLETAS_POR_ENTRENADOR,
    MAXIMO_ENTRENADORES_POR_ATLETA,
    MINIMO_ENTRENADORES_POR_ATLETA,
)
from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorAutenticacion,
    ErrorValidacion,
)
from ..comun.ids import nuevo_id
from .entidades import Permiso, Rol, Usuario
from .puertos import (
    PermisosPorRol,
    RepositorioUsuarios,
    ServicioHashContrasenas,
)

# Re-export de límites compartidos para compatibilidad con importaciones previas.
__all__ = [
    "AutenticarUsuario",
    "CrearUsuario",
    "ObtenerUsuarioActual",
    "VerificarPermiso",
    "MAXIMO_ATLETAS_POR_ENTRENADOR",
    "MAXIMO_ENTRENADORES_POR_ATLETA",
    "MINIMO_ENTRENADORES_POR_ATLETA",
]


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
        self._validar_datos(correo, contrasena, rol)
        # RF-01.3: solo puede existir un usuario con rol ENTRENADOR.
        if rol == Rol.ENTRENADOR and any(
            u.rol == Rol.ENTRENADOR for u in self.repositorio.listar_todos()
        ):
            raise ErrorValidacion(
                "Solo puede existir un usuario con rol ENTRENADOR como administrador."
            )
        hash_cont = self.servicio_hash.hashear(contrasena)
        usuario = Usuario(
            id=nuevo_id("usuario"),
            correo=correo,
            hash_contrasena=hash_cont,
            rol=rol,
        )
        return self.repositorio.guardar(usuario)

    @staticmethod
    def _validar_datos(correo: str, contrasena: str, rol: Rol) -> None:
        if not correo or "@" not in correo:
            raise ErrorValidacion("El correo es inválido.")
        if not contrasena or len(contrasena) < 8:
            raise ErrorValidacion("La contraseña debe tener al menos 8 caracteres.")
        if rol not in Rol:
            raise ErrorValidacion("El rol es inválido.")


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
