"""Casos de uso (puertos primarios / driving) del módulo de Atletas."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..comun.constantes import (
    MAXIMO_ATLETAS_POR_ENTRENADOR,
    MAXIMO_ENTRENADORES_POR_ATLETA,
    MINIMO_ENTRENADORES_POR_ATLETA,
)
from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorValidacion,
)
from ..comun.ids import nuevo_id_entero
from ..comun.reglas_limites import (
    validar_capacidad_entrenador,
    validar_entrenadores_por_atleta,
)
from .entidades import Atleta, PerfilHistorico, Rating
from .puertos import RepositorioAtletas, RepositorioCategorias


def _validar_ratings_no_negativos(rating: Rating) -> None:
    for valor in (
        rating.clasicas,
        rating.rapidas,
        rating.blitz,
        rating.chess_com,
        rating.lichess,
    ):
        if valor is not None and valor < 0:
            raise ErrorValidacion("Los ratings no pueden ser negativos.")


def _validar_campos_obligatorios_atleta(atleta: Atleta) -> None:
    """RF-02.1 / RF-02.2: campos obligatorios del perfil completo."""
    if not atleta.nombre:
        raise ErrorValidacion("El nombre del atleta es obligatorio.")
    if atleta.fecha_nacimiento is None:
        raise ErrorValidacion("La fecha de nacimiento es obligatoria.")
    if not atleta.sexo:
        raise ErrorValidacion("El sexo del atleta es obligatorio.")
    r = atleta.rating_actual
    if r.clasicas is None or r.rapidas is None or r.blitz is None:
        raise ErrorValidacion(
            "Los ratings FIDE (clásicas, rápidas, blitz) son obligatorios."
        )
    if r.chess_com is None or r.lichess is None:
        raise ErrorValidacion(
            "Los ratings de Chess.com y Lichess son obligatorios."
        )
    _validar_ratings_no_negativos(r)


@dataclass
class RegistrarAtleta:
    repositorio_atletas: RepositorioAtletas
    repositorio_categorias: RepositorioCategorias

    def ejecutar(self, atleta: Atleta) -> Atleta:
        _validar_campos_obligatorios_atleta(atleta)
        validar_entrenadores_por_atleta(len(atleta.entrenadores_asignados))
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
    repositorio_atletas: RepositorioAtletas

    def ejecutar(self, atleta: Atleta) -> Atleta:
        if not self.repositorio_atletas.existe(atleta.id):
            raise EntidadNoEncontrada("Atleta no encontrado.")
        _validar_campos_obligatorios_atleta(atleta)
        return self.repositorio_atletas.actualizar(atleta)


@dataclass
class ConsultarPerfilAtleta:
    repositorio_atletas: RepositorioAtletas

    def ejecutar(self, id_atleta: int) -> Atleta:
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        return atleta


@dataclass
class AsignarCategoriaAAtleta:
    repositorio_atletas: RepositorioAtletas
    repositorio_categorias: RepositorioCategorias

    def ejecutar(self, id_atleta: int, id_categoria: int) -> Atleta:
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
class AsignarEntrenadorAAtleta:
    repositorio_atletas: RepositorioAtletas

    def ejecutar(self, id_atleta: int, id_entrenador: int) -> Atleta:
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")

        ya_asignado = id_entrenador in atleta.entrenadores_asignados
        if not ya_asignado:
            # RF-01.8: el entrenador no puede exceder 40 atletas.
            validar_capacidad_entrenador(
                len(self.repositorio_atletas.listar_por_entrenador(id_entrenador))
            )
            # RF-02.6: el atleta no puede exceder 3 entrenadores.
            validar_entrenadores_por_atleta(
                len(atleta.entrenadores_asignados) + 1
            )
            atleta.entrenadores_asignados.append(id_entrenador)

        return self.repositorio_atletas.actualizar(atleta)


@dataclass
class ActualizarRating:
    repositorio_atletas: RepositorioAtletas

    def ejecutar(
        self,
        id_atleta: int,
        nuevo_rating: Rating,
        anio: int,
        torneo: Optional[str],
    ) -> Atleta:
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        _validar_ratings_no_negativos(nuevo_rating)

        # RF-02.7 / RF-13.6: cada actualización genera un snapshot nuevo con id
        # único. El historial es inmutable: los snapshots previos nunca se
        # modifican ni eliminan, pero se permite actualizar el rating vigente
        # (p. ej. publicaciones oficiales periódicas del mismo año).
        snapshot = PerfilHistorico(
            id=nuevo_id_entero(),
            anio=anio,
            torneo=torneo,
            rating=atleta.rating_actual,
        )
        atleta.historial.append(snapshot)
        atleta.rating_actual = nuevo_rating
        return self.repositorio_atletas.actualizar(atleta)


@dataclass
class ListarAtletasPorEntrenador:
    repositorio_atletas: RepositorioAtletas

    def ejecutar(self, id_entrenador: int) -> List[Atleta]:
        return self.repositorio_atletas.listar_por_entrenador(id_entrenador)
