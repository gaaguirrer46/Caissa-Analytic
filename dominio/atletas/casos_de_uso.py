"""Casos de uso (puertos primarios / driving) del módulo de Atletas."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorValidacion,
)
from ..usuarios.casos_de_uso import (
    MAXIMO_ATLETAS_POR_ENTRENADOR,
    MAXIMO_ENTRENADORES_POR_ATLETA,
    MINIMO_ENTRENADORES_POR_ATLETA,
)
from .entidades import Atleta, Categoria, PerfilHistorico, Rating
from .puertos import RepositorioAtletas, RepositorioCategorias


@dataclass
class RegistrarAtleta:
    repositorio_atletas: RepositorioAtletas
    repositorio_categorias: RepositorioCategorias

    def ejecutar(self, atleta: Atleta) -> Atleta:
        self._validar_campos_obligatorios(atleta)
        self._validar_entrenadores(atleta)
        if self.repositorio_atletas.existe(atleta.id):
            raise ErrorValidacion("Ya existe un atleta con ese id.")
        self._validar_categorias_existentes(atleta)
        return self.repositorio_atletas.guardar(atleta)

    def _validar_campos_obligatorios(self, atleta: Atleta) -> None:
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
        for rating in (r.clasicas, r.rapidas, r.blitz, r.chess_com, r.lichess):
            if rating < 0:
                raise ErrorValidacion("Los ratings no pueden ser negativos.")

    def _validar_entrenadores(self, atleta: Atleta) -> None:
        cantidad = len(atleta.entrenadores_asignados)
        if cantidad < MINIMO_ENTRENADORES_POR_ATLETA:
            raise ErrorValidacion("El atleta debe tener al menos 1 entrenador.")
        if cantidad > MAXIMO_ENTRENADORES_POR_ATLETA:
            raise ErrorValidacion("El atleta no puede tener más de 3 entrenadores.")

    def _validar_categorias_existentes(self, atleta: Atleta) -> None:
        predefinidas = {
            c.id for c in self.repositorio_categorias.listar_predefinidas()
        }
        desconocidas = set(atleta.categorias) - predefinidas
        if desconocidas:
            raise ErrorValidacion(
                f"Categorías inexistentes: {', '.join(sorted(desconocidas))}."
            )


@dataclass
class ActualizarPerfilAtleta:
    repositorio_atletas: RepositorioAtletas

    def ejecutar(self, atleta: Atleta) -> Atleta:
        if not self.repositorio_atletas.existe(atleta.id):
            raise EntidadNoEncontrada("Atleta no encontrado.")
        if not atleta.nombre:
            raise ErrorValidacion("El nombre del atleta es obligatorio.")
        return self.repositorio_atletas.actualizar(atleta)


@dataclass
class ConsultarPerfilAtleta:
    repositorio_atletas: RepositorioAtletas

    def ejecutar(self, id_atleta: str) -> Atleta:
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        return atleta


@dataclass
class AsignarCategoriaAAtleta:
    repositorio_atletas: RepositorioAtletas
    repositorio_categorias: RepositorioCategorias

    def ejecutar(self, id_atleta: str, id_categoria: str) -> Atleta:
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

    def ejecutar(self, id_atleta: str, id_entrenador: str) -> Atleta:
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")

        ya_asignado = id_entrenador in atleta.entrenadores_asignados
        if not ya_asignado:
            cantidad_entrenador = len(
                self.repositorio_atletas.listar_por_entrenador(id_entrenador)
            )
            if cantidad_entrenador >= MAXIMO_ATLETAS_POR_ENTRENADOR:
                raise ErrorValidacion(
                    "El entrenador ya alcanzó el máximo de 40 atletas asignados."
                )
            if len(atleta.entrenadores_asignados) >= MAXIMO_ENTRENADORES_POR_ATLETA:
                raise ErrorValidacion(
                    "El atleta no puede tener más de 3 entrenadores asignados."
                )
            atleta.entrenadores_asignados.append(id_entrenador)

        return self.repositorio_atletas.actualizar(atleta)


@dataclass
class ActualizarRating:
    repositorio_atletas: RepositorioAtletas

    def ejecutar(
        self,
        id_atleta: str,
        nuevo_rating: Rating,
        anio: int,
        torneo: Optional[str],
    ) -> Atleta:
        atleta = self.repositorio_atletas.buscar_por_id(id_atleta)
        if atleta is None:
            raise EntidadNoEncontrada("Atleta no encontrado.")
        for r in (nuevo_rating.clasicas, nuevo_rating.rapidas,
                  nuevo_rating.blitz, nuevo_rating.chess_com,
                  nuevo_rating.lichess):
            if r is not None and r < 0:
                raise ErrorValidacion("Los ratings no pueden ser negativos.")

        snapshot = PerfilHistorico(
            id=f"hist_{atleta.id}_{anio}_{torneo or 'sin_torneo'}",
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

    def ejecutar(self, id_entrenador: str) -> List[Atleta]:
        return self.repositorio_atletas.listar_por_entrenador(id_entrenador)
