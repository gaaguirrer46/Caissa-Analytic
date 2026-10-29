"""Casos de uso (puertos primarios / driving) del módulo de Atletas."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..auditoria.casos_de_uso import RegistrarCambio
from ..auditoria.entidades import TipoOperacion
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
from ..comun.reglas_limites import (
    validar_capacidad_entrenador,
    validar_entrenadores_por_atleta,
)
from ..comun.validaciones import (
    convertir_enum,
    exigir_entero,
    exigir_fecha,
    exigir_texto,
)
from ..configuracion.puertos import RepositorioConfiguracion
from ..usuarios.entidades import Rol
from ..usuarios.puertos import RepositorioUsuarios
from .entidades import Atleta, Categoria, MiInformacion, PerfilHistorico, Rating, TipoCategoria
from .puertos import (
    ProveedorInformacionAtleta,
    RepositorioAtletas,
    RepositorioCategorias,
)

RATING_MINIMO = 0
RATING_MAXIMO = 4000
ANIO_MINIMO = 2000
ANIO_MAXIMO = 2100

def _exigir_entrenador(rol_usuario: Rol, accion: str) -> None:
    """sólo el entrenador administra el expediente del atleta."""
    if rol_usuario != Rol.ENTRENADOR:
        raise ErrorAutenticacion(
            f"Acceso denegado: sólo el entrenador puede {accion}."
        )

def _maximo_atletas(
    repositorio_configuracion: Optional[RepositorioConfiguracion],
) -> int:
    """el límite es configurable; 40 es el valor por defecto."""
    if repositorio_configuracion is None:
        return MAXIMO_ATLETAS_POR_ENTRENADOR
    return repositorio_configuracion.obtener().maximo_atletas_por_entrenador

def _validar_ratings(rating: Rating) -> None:
    """los ratings deben estar en el rango FIDE del modelo (0-4000)."""
    for campo, valor in (
        ("clasicas", rating.clasicas),
        ("rapidas", rating.rapidas),
        ("blitz", rating.blitz),
        ("chess_com", rating.chess_com),
        ("lichess", rating.lichess),
    ):
        if valor is None:
            continue
        exigir_entero(
            valor,
            f"rating.{campo}",
            minimo=RATING_MINIMO,
            maximo=RATING_MAXIMO,
        )

def _validar_campos_obligatorios_atleta(atleta: Atleta, hoy: Optional[date] = None) -> None:
    """campos obligatorios y coherencia de fechas."""
    if not isinstance(atleta, Atleta):
        raise ErrorValidacion("El expediente del atleta es inválido.")
    atleta.nombre = exigir_texto(atleta.nombre, "nombre", max_longitud=100)
    exigir_fecha(atleta.fecha_nacimiento, "fecha_nacimiento")
    if atleta.fecha_nacimiento > (hoy or date.today()):
        raise ErrorValidacion("La fecha de nacimiento no puede ser futura.")
    atleta.sexo = exigir_texto(atleta.sexo, "sexo", max_longitud=10).upper()
    for campo, maximo in (
        ("identidad_opcional", 20),
        ("fotografia_opcional", 255),
        ("federacion", 50),
        ("universidad", 80),
        ("institucion", 80),
        ("carrera", 80),
    ):
        valor = getattr(atleta, campo)
        if valor is not None:
            setattr(atleta, campo, exigir_texto(valor, campo, max_longitud=maximo))

    if not atleta.categorias:
        raise ErrorValidacion("El atleta debe tener al menos una categoría.")

    rating = atleta.rating_actual
    if not isinstance(rating, Rating):
        raise ErrorValidacion("El rating del atleta es inválido.")
    if rating.clasicas is None or rating.rapidas is None or rating.blitz is None:
        raise ErrorValidacion(
            "Los ratings FIDE (clásicas, rápidas, blitz) son obligatorios."
        )
    if rating.chess_com is None or rating.lichess is None:
        raise ErrorValidacion("Los ratings de Chess.com y Lichess son obligatorios.")
    _validar_ratings(rating)

    for club in atleta.clubs:
        exigir_texto(club, "club", max_longitud=60)
    for id_categoria in atleta.categorias:
        exigir_entero(id_categoria, "id_categoria", minimo=1)
    for id_entrenador in atleta.entrenadores_asignados:
        exigir_entero(id_entrenador, "id_entrenador", minimo=1)

@dataclass
class RegistrarAtleta:
    """alta del expediente con validaciones completas."""

    repositorio_atletas: RepositorioAtletas
    repositorio_categorias: RepositorioCategorias
    repositorio_configuracion: Optional[RepositorioConfiguracion] = None

    def ejecutar(
        self,
        atleta: Atleta,
        rol_usuario: Rol,
    ) -> Atleta:
        _exigir_entrenador(rol_usuario, "registrar atletas")
        _validar_campos_obligatorios_atleta(atleta)
        validar_entrenadores_por_atleta(len(atleta.entrenadores_asignados))
        maximo = _maximo_atletas(self.repositorio_configuracion)

        for id_entrenador in atleta.entrenadores_asignados:
            validar_capacidad_entrenador(
                len(self.repositorio_atletas.listar_por_entrenador(id_entrenador)),
                maximo,
            )
        if self.repositorio_atletas.existe(atleta.id):
            raise ErrorValidacion("Ya existe un atleta con ese id.")
        self._validar_categorias_existentes(atleta)
        return self.repositorio_atletas.guardar(atleta)

    def _validar_categorias_existentes(self, atleta: Atleta) -> None:
        predefinidas = {
            c.id for c in self.repositorio_categorias.listar_predefinidas()
        }
        desconocidas = set(atleta.categorias) - predefinidas
        if desconocidas:
            raise ErrorValidacion(
                f"Categorías inexistentes: {', '.join(str(x) for x in sorted(desconocidas))}."
            )

@dataclass
class ActualizarPerfilAtleta:
    """modificación del expediente por parte del entrenador."""

    repositorio_atletas: RepositorioAtletas
    repositorio_configuracion: Optional[RepositorioConfiguracion] = None

    def ejecutar(
        self,
        atleta: Atleta,
        rol_usuario: Rol,
    ) -> Atleta:
        _exigir_entrenador(rol_usuario, "modificar expedientes de atletas")
        if not isinstance(atleta, Atleta):
            raise ErrorValidacion("El expediente del atleta es inválido.")
        actual = self.repositorio_atletas.buscar_por_id(atleta.id)
        if actual is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        _validar_campos_obligatorios_atleta(atleta)
        validar_entrenadores_por_atleta(len(atleta.entrenadores_asignados))

        maximo = _maximo_atletas(self.repositorio_configuracion)
        anteriores = set(actual.entrenadores_asignados)
        for id_entrenador in atleta.entrenadores_asignados:
            if id_entrenador not in anteriores:
                validar_capacidad_entrenador(
                    len(
                        self.repositorio_atletas.listar_por_entrenador(
                            id_entrenador
                        )
                    ),
                    maximo,
                )
        return self.repositorio_atletas.actualizar(atleta)

@dataclass
class ConsultarPerfilAtleta:
    """el entrenador consulta el expediente completo con la edad calculada.

 El atleta no usa este caso de uso: consulta su propia información mediante
 ``ConsultarMiInformacion``, que resuelve el vínculo usuario↔atleta.
 """

    repositorio_atletas: RepositorioAtletas

    def ejecutar(self, id_atleta: int, rol_usuario: Rol) -> Atleta:
        _exigir_entrenador(rol_usuario, "consultar expedientes completos de atletas")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        return atleta

@dataclass
class ConsultarSerieHistorica:
    """serie temporal del perfil para las gráficas históricas.

 Expone los snapshots inmutables del historial ordenados por
 año y torneo; cada nueva información incorporada al perfil (snapshot y
 ratings enlazados) se convierte automáticamente en un punto de la serie.
 """

    repositorio_atletas: RepositorioAtletas

    def ejecutar(self, id_atleta: int, rol_usuario: Rol) -> List[PerfilHistorico]:
        _exigir_entrenador(rol_usuario, "consultar gráficas históricas de atletas")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        return sorted(atleta.historial, key=lambda p: (p.anio, p.torneo or ""))

@dataclass
class AsignarCategoriaAAtleta:
    """vincula categorías existentes y configurables."""

    repositorio_atletas: RepositorioAtletas
    repositorio_categorias: RepositorioCategorias

    def ejecutar(
        self,
        id_atleta: int,
        id_categoria: int,
        rol_usuario: Rol,
    ) -> Atleta:
        _exigir_entrenador(rol_usuario, "asignar categorías")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        exigir_entero(id_categoria, "id_categoria", minimo=1)
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        existe_categoria = any(
            c.id == id_categoria
            for c in self.repositorio_categorias.listar_predefinidas()
        )
        if not existe_categoria:
            raise ErrorValidacion("La categoría no existe.")
        if id_categoria not in atleta.categorias:
            atleta.categorias.append(id_categoria)
        return self.repositorio_atletas.actualizar(atleta)

@dataclass
class ConfigurarCategoria:
    """ / RNF-07.1: el administrador configura las categorías sin tocar código.

 Sólo se pueden editar o eliminar categorías marcadas como ``editable_por_admin``.
 """

    repositorio_categorias: RepositorioCategorias

    def crear(
        self, categoria: Categoria, rol_usuario: Rol
    ) -> Categoria:
        _exigir_entrenador(rol_usuario, "configurar categorías")
        if not isinstance(categoria, Categoria):
            raise ErrorValidacion("La categoría es inválida.")
        nombre = exigir_texto(categoria.nombre, "nombre", max_longitud=50)
        rango = exigir_texto(categoria.rango, "rango", max_longitud=30)
        tipo = convertir_enum(TipoCategoria, categoria.tipo, "tipo")
        if not categoria.editable_por_admin:
            raise ErrorValidacion(
                "Sólo se pueden crear categorías editables por el administrador."
            )
        nueva = Categoria(
            id=categoria.id,
            nombre=nombre,
            tipo=tipo,
            rango=rango,
            editable_por_admin=True,
        )
        return self.repositorio_categorias.crear_personalizada(nueva)

    def editar(
        self, categoria: Categoria, rol_usuario: Rol
    ) -> Categoria:
        _exigir_entrenador(rol_usuario, "configurar categorías")
        if not isinstance(categoria, Categoria):
            raise ErrorValidacion("La categoría es inválida.")
        existentes = {c.id: c for c in self.repositorio_categorias.listar_predefinidas()}
        actual = existentes.get(categoria.id)
        if actual is None:
            raise EntidadNoEncontrada("Categoría no encontrada.")
        if not actual.editable_por_admin:
            raise ErrorValidacion("La categoría no es editable por el administrador.")
        editada = Categoria(
            id=categoria.id,
            nombre=exigir_texto(categoria.nombre, "nombre", max_longitud=50),
            tipo=convertir_enum(TipoCategoria, categoria.tipo, "tipo"),
            rango=exigir_texto(categoria.rango, "rango", max_longitud=30),
            editable_por_admin=True,
        )
        return self.repositorio_categorias.editar(editada)

    def eliminar(self, id_categoria: int, rol_usuario: Rol) -> None:
        _exigir_entrenador(rol_usuario, "configurar categorías")
        exigir_entero(id_categoria, "id_categoria", minimo=1)
        existentes = {c.id: c for c in self.repositorio_categorias.listar_predefinidas()}
        actual = existentes.get(id_categoria)
        if actual is None:
            raise EntidadNoEncontrada("Categoría no encontrada.")
        if not actual.editable_por_admin:
            raise ErrorValidacion("La categoría no es editable por el administrador.")
        self.repositorio_categorias.eliminar(id_categoria)

@dataclass
class AsignarEntrenadorAAtleta:
    """entre 1 y 3 entrenadores y máximo 40 atletas por entrenador."""

    repositorio_atletas: RepositorioAtletas
    repositorio_configuracion: Optional[RepositorioConfiguracion] = None

    def ejecutar(
        self,
        id_atleta: int,
        id_entrenador: int,
        rol_usuario: Rol,
    ) -> Atleta:
        _exigir_entrenador(rol_usuario, "asignar entrenadores")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        exigir_entero(id_entrenador, "id_entrenador", minimo=1)
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")

        ya_asignado = id_entrenador in atleta.entrenadores_asignados
        if not ya_asignado:

            validar_capacidad_entrenador(
                len(self.repositorio_atletas.listar_por_entrenador(id_entrenador)),
                _maximo_atletas(self.repositorio_configuracion),
            )

            validar_entrenadores_por_atleta(
                len(atleta.entrenadores_asignados) + 1
            )
            atleta.entrenadores_asignados.append(id_entrenador)

        return self.repositorio_atletas.actualizar(atleta)

@dataclass
class RetirarEntrenadorDeAtleta:
    """un atleta nunca puede quedar sin entrenador asignado."""

    repositorio_atletas: RepositorioAtletas

    def ejecutar(
        self,
        id_atleta: int,
        id_entrenador: int,
        rol_usuario: Rol,
    ) -> Atleta:
        _exigir_entrenador(rol_usuario, "retirar entrenadores")
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        if id_entrenador not in atleta.entrenadores_asignados:
            raise ErrorValidacion("El entrenador no está asignado al atleta.")
        if len(atleta.entrenadores_asignados) - 1 < MINIMO_ENTRENADORES_POR_ATLETA:
            raise ErrorValidacion("El atleta debe conservar al menos 1 entrenador.")
        atleta.entrenadores_asignados.remove(id_entrenador)
        return self.repositorio_atletas.actualizar(atleta)

@dataclass
class ActualizarRating:
    """actualiza el rating y registra un snapshot inmutable.

cada ritmo que cambia genera una entrada en el historial de
 auditoría con el valor anterior y el nuevo.
 """

    repositorio_atletas: RepositorioAtletas

    auditor: Optional[RegistrarCambio] = None

    def ejecutar(
        self,
        id_atleta: int,
        nuevo_rating: Rating,
        anio: int,
        torneo: Optional[str],
        rol_usuario: Rol,
        *,
        solicitante: Optional[Solicitante] = None,
    ) -> Atleta:
        _exigir_entrenador(rol_usuario, "actualizar ratings")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        exigir_entero(anio, "anio", minimo=ANIO_MINIMO, maximo=ANIO_MAXIMO)
        if not isinstance(nuevo_rating, Rating):
            raise ErrorValidacion("El rating es inválido.")
        _validar_ratings(nuevo_rating)
        torneo_limpio = None
        if torneo is not None:
            torneo_limpio = exigir_texto(torneo, "torneo", max_longitud=100)

        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")

        rating_previo = atleta.rating_actual
        snapshot = PerfilHistorico(
            id=0,
            id_atleta=id_atleta,
            anio=anio,
            torneo=torneo_limpio,
            rating=nuevo_rating,
        )
        guardado = self.repositorio_atletas.guardar_snapshot(snapshot)
        atleta.historial.append(guardado)
        atleta.rating_actual = nuevo_rating
        actualizado = self.repositorio_atletas.actualizar(atleta)
        self._registrar_en_auditoria(
            id_atleta, rating_previo, nuevo_rating, rol_usuario, solicitante
        )
        return actualizado

    def _registrar_en_auditoria(
        self,
        id_atleta: int,
        previo: Rating,
        nuevo: Rating,
        rol_usuario: Rol,
        solicitante: Optional[Solicitante],
    ) -> None:
        """un registro por ritmo que haya cambiado de valor."""
        if self.auditor is None:
            return
        usuario = (
            str(solicitante.id_usuario)
            if solicitante is not None
            else f"rol:{rol_usuario.value}"
        )
        for ritmo, antes, despues in (
            ("clasicas", previo.clasicas, nuevo.clasicas),
            ("rapidas", previo.rapidas, nuevo.rapidas),
            ("blitz", previo.blitz, nuevo.blitz),
            ("chess_com", previo.chess_com, nuevo.chess_com),
            ("lichess", previo.lichess, nuevo.lichess),
        ):
            if antes == despues:
                continue
            self.auditor.ejecutar(
                usuario,
                "Atleta",
                TipoOperacion.MODIFICAR,
                f"rating_{ritmo}",
                None if antes is None else str(antes),
                None if despues is None else str(despues),
            )

@dataclass
class ListarAtletasPorEntrenador:
    """atletas asignados al entrenador autenticado."""

    repositorio_atletas: RepositorioAtletas

    def ejecutar(self, id_entrenador: int, rol_usuario: Rol) -> List[Atleta]:
        _exigir_entrenador(rol_usuario, "listar atletas de un entrenador")
        exigir_entero(id_entrenador, "id_entrenador", minimo=1)
        return self.repositorio_atletas.listar_por_entrenador(id_entrenador)

@dataclass
class ConsultarMiInformacion:
    """el atleta consulta su información personal y deportiva.

 El vínculo usuario↔atleta se resuelve con ``ProveedorInformacionAtleta``.
 Un atleta no puede indicar el id de otro atleta; el entrenador sí debe
 indicarlo explícitamente.

el rol no se confía al llamador; se resuelve desde la
 identidad persistida (``RepositorioUsuarios``) y se rechaza cualquier
 rol declarado que no coincida con el auténtico (anti-spoofing RBAC).
 """

    repositorio_usuarios: RepositorioUsuarios
    repositorio_atletas: RepositorioAtletas
    proveedor: ProveedorInformacionAtleta

    def ejecutar(
        self,
        solicitante: Solicitante,
        id_atleta: Optional[int] = None,
    ) -> MiInformacion:
        id_usuario = solicitante.id_usuario
        usuario = self.repositorio_usuarios.buscar_por_id(id_usuario)
        if usuario is None:
            raise EntidadNoEncontrada("Usuario no encontrado.")
        rol = usuario.rol
        if rol != solicitante.rol:
            raise ErrorAutenticacion(
                "Acceso denegado: el rol declarado no coincide con la "
                "identidad autenticada del usuario."
            )
        if rol == Rol.INVITADO:
            raise ErrorAutenticacion(
                "Acceso denegado: el usuario invitado no accede a expedientes."
            )

        if rol == Rol.ATLETA:
            vinculado = self.proveedor.atleta_de_usuario(id_usuario)
            if vinculado is None:
                raise EntidadNoEncontrada(
                    "No existe un atleta vinculado a este usuario."
                )
            if id_atleta is not None and id_atleta != vinculado:
                raise ErrorAutenticacion(
                    "Acceso denegado: sólo puede consultar su propia información."
                )
            id_objetivo = vinculado
        else:
            if id_atleta is None:
                raise ErrorValidacion(
                    "El entrenador debe indicar el atleta que desea consultar."
                )
            id_objetivo = exigir_entero(id_atleta, "id_atleta", minimo=1)

        atleta = self.repositorio_atletas.buscar_por_id(id_objetivo)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        if not atleta.activo:
            raise ErrorAutenticacion("Acceso denegado: el atleta está inactivo.")

        return MiInformacion(
            atleta=atleta,
            calendario=self.proveedor.calendario(id_objetivo),
            entrenamientos=self.proveedor.entrenamientos(id_objetivo),
            objetivos=self.proveedor.objetivos(id_objetivo),
            estadisticas=self.proveedor.estadisticas(id_objetivo),
            partidas=self.proveedor.partidas(id_objetivo),
            reportes=self.proveedor.reportes_disponibles(id_objetivo),
        )

@dataclass
class VincularUsuarioAtleta:
    """el entrenador vincula una cuenta de usuario con su expediente."""

    proveedor: ProveedorInformacionAtleta

    def ejecutar(
        self,
        solicitante: Solicitante,
        id_usuario_vinculado: int,
        id_atleta: int,
    ) -> None:
        """el entrenador vincula una cuenta ATLETA con su expediente."""
        exigir_entrenador(solicitante, "vincular cuentas")
        exigir_entero(id_usuario_vinculado, "id_usuario", minimo=1)
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        self.proveedor.vincular_usuario(id_usuario_vinculado, id_atleta)

__all__ = [
    "ActualizarPerfilAtleta",
    "ActualizarRating",
    "AsignarCategoriaAAtleta",
    "AsignarEntrenadorAAtleta",
    "ConfigurarCategoria",
    "ConsultarMiInformacion",
    "ConsultarPerfilAtleta",
    "ListarAtletasPorEntrenador",
    "RegistrarAtleta",
    "RetirarEntrenadorDeAtleta",
    "VincularUsuarioAtleta",
    "MAXIMO_ATLETAS_POR_ENTRENADOR",
    "MAXIMO_ENTRENADORES_POR_ATLETA",
    "MINIMO_ENTRENADORES_POR_ATLETA",
    "RATING_MINIMO",
    "RATING_MAXIMO",
]
