"""Casos de uso (puertos primarios / driving) del módulo de Usuarios."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

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
from ..comun.ids import nuevo_id_entero
from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.validaciones import exigir_entero
from ..configuracion.puertos import RepositorioConfiguracion
from .entidades import (
    InformacionAutorizada,
    Permiso,
    PermisosPorRol,
    Rol,
    Usuario,
    UsuarioResumen,
)
from .puertos import (
    ProveedorInformacionAutorizada,
    RepositorioUsuarios,
    ServicioHashContrasenas,
)

__all__ = [
    "AutenticarUsuario",
    "CambiarRolUsuario",
    "ConsultarInformacionAutorizada",
    "CrearUsuario",
    "ListarUsuariosPorRol",
    "ObtenerUsuarioActual",
    "VerificarPermiso",
    "MAXIMO_ATLETAS_POR_ENTRENADOR",
    "MAXIMO_ENTRENADORES_POR_ATLETA",
    "MINIMO_ENTRENADORES_POR_ATLETA",
]

_PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@dataclass
class AutenticarUsuario:
    repositorio: RepositorioUsuarios
    servicio_hash: ServicioHashContrasenas

    def ejecutar(self, correo: str, contrasena: str) -> Usuario:

        if not correo or not isinstance(correo, str) or not correo.strip():
            self.servicio_hash.verificar("dummy", self.servicio_hash.hash_dummy())
            raise ErrorAutenticacion("Credenciales inválidas.")

        if not contrasena or not isinstance(contrasena, str):
            self.servicio_hash.verificar("dummy", self.servicio_hash.hash_dummy())
            raise ErrorAutenticacion("Credenciales inválidas.")

        correo_limpio = correo.strip().lower()
        if len(correo_limpio) > 100:
            self.servicio_hash.verificar("dummy", self.servicio_hash.hash_dummy())
            raise ErrorAutenticacion("Credenciales inválidas.")

        usuario = self.repositorio.buscar_por_correo(correo_limpio)

        hash_almacenado = usuario.hash_contrasena if usuario is not None else self.servicio_hash.hash_dummy()
        es_valido = self.servicio_hash.verificar(contrasena, hash_almacenado)

        if usuario is None or not es_valido:
            raise ErrorAutenticacion("Credenciales inválidas.")

        return usuario

@dataclass
class CrearUsuario:
    repositorio: RepositorioUsuarios
    servicio_hash: ServicioHashContrasenas

    def ejecutar(
        self,
        correo: str,
        contrasena: str,
        rol: Rol | str,
        rol_solicitante: Rol | str | None = None,
    ) -> Usuario:
        rol_valido = Rol.desde_str(rol)
        solicitante = (
            Rol.desde_str(rol_solicitante)
            if rol_solicitante is not None
            else None
        )
        hay_entrenador = any(
            u.rol == Rol.ENTRENADOR for u in self.repositorio.listar_todos()
        )

        es_bootstrap = (
            not hay_entrenador
            and rol_valido == Rol.ENTRENADOR
            and solicitante in (None, Rol.ENTRENADOR)
        )
        if not es_bootstrap and solicitante != Rol.ENTRENADOR:
            raise ErrorAutenticacion(
                "Acceso denegado: sólo el entrenador puede crear usuarios "
                "y asignar roles."
            )
        if not hay_entrenador and not es_bootstrap:
            raise ErrorValidacion(
                "Debe existir un entrenador administrador antes de crear "
                "otros usuarios."
            )

        correo_limpio = (correo or "").strip().lower()
        self._validar_datos(correo_limpio, contrasena)
        if self.repositorio.existe(correo_limpio):
            raise ErrorValidacion("Ya existe un usuario con ese correo.")

        if rol_valido == Rol.ENTRENADOR and hay_entrenador:
            raise ErrorValidacion(
                "Solo puede existir un usuario con rol ENTRENADOR como administrador."
            )
        hash_cont = self.servicio_hash.hashear(contrasena)
        usuario = Usuario(
            id=nuevo_id_entero(),
            correo=correo_limpio,
            hash_contrasena=hash_cont,
            rol=rol_valido,
        )
        return self.repositorio.guardar(usuario)

    @staticmethod
    def _validar_datos(correo: str, contrasena: str) -> None:
        if (
            not isinstance(correo, str)
            or len(correo) > 100
            or not _PATRON_CORREO.match(correo)
        ):
            raise ErrorValidacion("El correo es inválido o excede el límite permitido.")
        if not isinstance(contrasena, str) or not contrasena or len(contrasena) < 8:
            raise ErrorValidacion("La contraseña debe tener al menos 8 caracteres.")

@dataclass
class CambiarRolUsuario:
    """Permite gestionar y cambiar el rol de un usuario existente.

 Reglas de negocio:
 - Solo el ENTRENADOR (administrador) puede cambiar roles de usuario.
 - Se debe validar que el nuevo rol pertenezca a los tres roles permitidos.
 - Solo puede existir un único ENTRENADOR en el sistema.
 - No se puede degradar al único ENTRENADOR del sistema dejando al sistema acéfalo.
 """

    repositorio: RepositorioUsuarios

    def ejecutar(
        self,
        id_usuario: int,
        nuevo_rol: Rol | str,
        rol_solicitante: Rol | str,
    ) -> Usuario:
        rol_sol = Rol.desde_str(rol_solicitante)
        if rol_sol != Rol.ENTRENADOR:
            raise ErrorAutenticacion(
                "Acceso denegado: sólo el entrenador puede modificar roles de usuario."
            )
        exigir_entero(id_usuario, "id_usuario", minimo=1)

        usuario = self.repositorio.buscar_por_id(id_usuario)
        if usuario is None:
            raise EntidadNoEncontrada("Usuario no encontrado.")

        rol_destino = Rol.desde_str(nuevo_rol)
        if usuario.rol == rol_destino:
            return usuario

        if rol_destino == Rol.ENTRENADOR:
            entrenadores = [
                u for u in self.repositorio.listar_todos()
                if u.rol == Rol.ENTRENADOR and u.id != id_usuario
            ]
            if entrenadores:
                raise ErrorValidacion(
                    "Solo puede existir un usuario con rol ENTRENADOR como administrador."
                )

        if usuario.rol == Rol.ENTRENADOR and rol_destino != Rol.ENTRENADOR:
            otros_entrenadores = [
                u for u in self.repositorio.listar_todos()
                if u.rol == Rol.ENTRENADOR and u.id != id_usuario
            ]
            if not otros_entrenadores:
                raise ErrorValidacion(
                    "No se puede cambiar el rol del único ENTRENADOR del sistema."
                )

        usuario_actualizado = Usuario(
            id=usuario.id,
            correo=usuario.correo,
            hash_contrasena=usuario.hash_contrasena,
            rol=rol_destino,
            fecha_creacion=usuario.fecha_creacion,
        )
        return self.repositorio.guardar(usuario_actualizado)

@dataclass
class ListarUsuariosPorRol:
    """Consulta y filtra usuarios según cualquiera de los tres roles permitidos."""

    repositorio: RepositorioUsuarios

    def ejecutar(
        self, rol: Rol | str, *, solicitante: Solicitante
    ) -> List[UsuarioResumen]:
        exigir_entrenador(solicitante, "listar usuarios por rol")
        rol_valido = Rol.desde_str(rol)
        return [
            UsuarioResumen(
                id=usuario.id,
                correo=usuario.correo,
                rol=usuario.rol,
                fecha_creacion=usuario.fecha_creacion,
            )
            for usuario in self.repositorio.listar_todos()
            if usuario.rol == rol_valido
        ]

@dataclass
class VerificarPermiso:
    """Verifica y hace cumplir la política de control de acceso basada en roles (RBAC)."""

    def ejecutar(self, usuario: Optional[Usuario], permiso: Permiso | str) -> bool:
        """Verifica si el usuario posee el permiso solicitado; devuelve False ante usuario nulo o datos inválidos."""
        if usuario is None or not isinstance(usuario, Usuario):
            return False
        permiso_enum = self._normalizar_permiso(permiso)
        if permiso_enum is None:
            return False
        return PermisosPorRol.tiene_permiso(usuario.rol, permiso_enum)

    def exigir_permiso(self, usuario: Optional[Usuario], permiso: Permiso | str) -> None:
        """Exige autorización obligatoria; lanza ErrorAutenticacion si no cuenta con el permiso."""
        if not self.ejecutar(usuario, permiso):
            nombre_rol = usuario.rol.value if usuario and hasattr(usuario, "rol") else "ANÓNIMO"
            raise ErrorAutenticacion(
                f"Acceso denegado: el rol {nombre_rol} no cuenta con el permiso '{permiso}' requerido."
            )

    @staticmethod
    def _normalizar_permiso(permiso: Permiso | str) -> Optional[Permiso]:
        if isinstance(permiso, Permiso):
            return permiso
        if isinstance(permiso, str) and permiso.strip():
            try:
                return Permiso(permiso.strip().upper())
            except ValueError:
                return None
        return None

@dataclass
class ObtenerUsuarioActual:
    repositorio: RepositorioUsuarios

    def ejecutar(self, id_usuario: int, *, solicitante: Solicitante) -> Usuario:
        exigir_entero(id_usuario, "id_usuario", minimo=1)
        if (
            solicitante.rol != Rol.ENTRENADOR
            and solicitante.id_usuario != id_usuario
        ):
            raise ErrorAutenticacion(
                "Acceso denegado: sólo puede consultar su propio usuario."
            )
        usuario = self.repositorio.buscar_por_id(id_usuario)
        if usuario is None:
            raise EntidadNoEncontrada("Usuario no encontrado.")
        return usuario

@dataclass
class ConsultarInformacionAutorizada:
    """el invitado consulta sólo las secciones que autorizó el entrenador."""

    repositorio_configuracion: RepositorioConfiguracion
    proveedor: ProveedorInformacionAutorizada

    def ejecutar(self, solicitante: Solicitante) -> InformacionAutorizada:
        if solicitante is None or solicitante.rol != Rol.INVITADO:
            raise ErrorAutenticacion(
                "Acceso denegado: esta vista es exclusiva del usuario invitado."
            )
        configuracion = self.repositorio_configuracion.obtener()
        secciones = tuple(configuracion.secciones_autorizadas_invitado)
        return InformacionAutorizada(
            secciones=secciones,
            datos={
                seccion: self.proveedor.obtener(seccion) for seccion in secciones
            },
        )
