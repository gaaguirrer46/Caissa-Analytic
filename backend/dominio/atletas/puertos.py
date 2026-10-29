"""Puertos secundarios (driven) del módulo de Atletas."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entrenamientos.entidades import PlanEntrenamientoSemanal, SesionEntrenamiento
from ..objetivos.entidades import ObjetivoSmart
from ..partidas.entidades import EstadisticasFaseJuego, Partida
from .entidades import Atleta, Categoria, PerfilHistorico

class RepositorioAtletas(ABC):
    @abstractmethod
    def guardar(self, atleta: Atleta) -> Atleta:
        """Persiste un atleta nuevo o actualizado."""

    @abstractmethod
    def actualizar(self, atleta: Atleta) -> Atleta:
        """Actualiza el expediente de un atleta existente."""

    @abstractmethod
    def buscar_por_id(self, id_atleta: int) -> Optional[Atleta]:
        """Devuelve el atleta por id, o None."""

    @abstractmethod
    def listar_por_entrenador(self, id_entrenador: int) -> List[Atleta]:
        """Devuelve los atletas asignados a un entrenador."""

    @abstractmethod
    def listar_activos(self) -> List[Atleta]:
        """Devuelve todos los atletas activos."""

    @abstractmethod
    def buscar_por_categoria(self, id_categoria: int) -> List[Atleta]:
        """Devuelve los atletas que pertenecen a una categoría."""

    @abstractmethod
    def existe(self, id_atleta: int) -> bool:
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
    def eliminar(self, id_categoria: int) -> None:
        """Elimina una categoría editable."""

class ResolutorAtletaUsuario(ABC):
    """contrato mínimo para resolver la identidad del atleta."""

    @abstractmethod
    def atleta_de_usuario(self, id_usuario: int) -> Optional[int]:
        """Devuelve el id del atleta vinculado al usuario, o None."""

class ProveedorInformacionAtleta(ResolutorAtletaUsuario):
    """composición de la información propia sin acoplar los módulos.

 El adaptador resuelve el vínculo usuario↔atleta y consulta cada sección con
 los repositorios de su módulo.
 """

    @abstractmethod
    def vincular_usuario(self, id_usuario: int, id_atleta: int) -> None:
        """Vincula una cuenta de usuario con su expediente de atleta."""

    @abstractmethod
    def calendario(self, id_atleta: int) -> List[SesionEntrenamiento]:
        """Sesiones planificadas del atleta."""

    @abstractmethod
    def entrenamientos(self, id_atleta: int) -> List[PlanEntrenamientoSemanal]:
        """Historial de planes semanales del atleta."""

    @abstractmethod
    def objetivos(self, id_atleta: int) -> List[ObjetivoSmart]:
        """Objetivos SMART del atleta."""

    @abstractmethod
    def estadisticas(self, id_atleta: int) -> EstadisticasFaseJuego:
        """Estadísticas agregadas de sus partidas."""

    @abstractmethod
    def partidas(self, id_atleta: int) -> List[Partida]:
        """Partidas registradas del atleta."""

    @abstractmethod
    def reportes_disponibles(self, id_atleta: int) -> List[str]:
        """Reportes que el atleta puede solicitar sobre sí mismo."""
