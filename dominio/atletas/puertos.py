"""Puertos secundarios (driven) del módulo de Atletas."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .entidades import Atleta, Categoria, PerfilHistorico


class RepositorioAtletas(ABC):
    @abstractmethod
    def guardar(self, atleta: Atleta) -> Atleta:
        """Persiste un atleta nuevo o actualizado."""

    @abstractmethod
    def actualizar(self, atleta: Atleta) -> Atleta:
        """Actualiza el expediente de un atleta existente."""

    @abstractmethod
    def buscar_por_id(self, id_atleta: str) -> Optional[Atleta]:
        """Devuelve el atleta por id, o None."""

    @abstractmethod
    def listar_por_entrenador(self, id_entrenador: str) -> List[Atleta]:
        """Devuelve los atletas asignados a un entrenador."""

    @abstractmethod
    def listar_activos(self) -> List[Atleta]:
        """Devuelve todos los atletas activos."""

    @abstractmethod
    def buscar_por_categoria(self, id_categoria: str) -> List[Atleta]:
        """Devuelve los atletas que pertenecen a una categoría."""

    @abstractmethod
    def existe(self, id_atleta: str) -> bool:
        """Indica si el atleta existe."""

    @abstractmethod
    def guardar_snapshot(self, historico: PerfilHistorico) -> PerfilHistorico:
        """Persiste un snapshot histórico inmutable."""


class RepositorioCategorias(ABC):
    @abstractmethod
    def listar_predefinidas(self) -> List[Categoria]:
        """Devuelve las categorías predefinidas por edad, nivel y ELO."""

    @abstractmethod
    def crear_personalizada(self, categoria: Categoria) -> Categoria:
        """Crea una categoría configurada por el administrador."""

    @abstractmethod
    def editar(self, categoria: Categoria) -> Categoria:
        """Edita una categoría editable."""

    @abstractmethod
    def eliminar(self, id_categoria: str) -> None:
        """Elimina una categoría editable."""
