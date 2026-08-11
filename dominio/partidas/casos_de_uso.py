"""Casos de uso (puertos primarios / driving) del módulo de Partidas."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorValidacion,
)
from ..usuarios.entidades import Rol
from .entidades import (
    AnalisisTecnico,
    ClasificacionPartida,
    EstadisticasApertura,
    EstadisticasFaseJuego,
    EstadisticasFinales,
    EstadisticasMedioJuego,
    Partida,
    ResultadoPartida,
)
from .puertos import (
    ProveedorPGN,
    RepositorioAnalisisTecnico,
    RepositorioPartidas,
)

UMBRAL_VENTAJA_PARTIDA_BOTADA = 3.0


@dataclass
class RegistrarPartida:
    repositorio: RepositorioPartidas

    def ejecutar(self, partida: Partida) -> Partida:
        self._validar_obligatorios(partida)
        return self.repositorio.guardar(partida)

    @staticmethod
    def _validar_obligatorios(partida: Partida) -> None:
        if not partida.evento:
            raise ErrorValidacion("El evento es obligatorio.")
        if partida.fecha is None:
            raise ErrorValidacion("La fecha es obligatoria.")
        if not partida.jugador_blancas or not partida.jugador_negras:
            raise ErrorValidacion("Los jugadores de blancas y negras son obligatorios.")
        if partida.rating_blancas < 0 or partida.rating_negras < 0:
            raise ErrorValidacion("Los ratings no pueden ser negativos.")
        if partida.resultado not in ResultadoPartida:
            raise ErrorValidacion("El resultado es inválido.")
        if not partida.apertura_eco:
            raise ErrorValidacion("La apertura (código ECO) es obligatoria.")


@dataclass
class RegistrarAnalisisTecnico:
    repositorio: RepositorioAnalisisTecnico
    repositorio_partidas: RepositorioPartidas

    def ejecutar(
        self,
        analisis: AnalisisTecnico,
        rol_usuario: Rol,
    ) -> AnalisisTecnico:
        if rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el entrenador puede completar el análisis técnico."
            )
        if self.repositorio_partidas.buscar_por_id(analisis.id_partida) is None:
            raise EntidadNoEncontrada("La partida no existe.")
        if analisis.accuracy is not None and not (
            0 <= analisis.accuracy <= 100
        ):
            raise ErrorValidacion("El accuracy debe estar entre 0 y 100.")
        if analisis.acpl is not None and analisis.acpl < 0:
            raise ErrorValidacion("El ACPL no puede ser negativo.")
        return self.repositorio.guardar_resumen(analisis)


@dataclass
class ClasificarPartida:
    """Asigna automáticamente la categoría según reglas del dominio."""

    def ejecutar(
        self,
        analisis: AnalisisTecnico,
        resultado: ResultadoPartida,
        ventaja_maxima: float = 0.0,
        es_partida_de_libro: bool = False,
    ) -> ClasificacionPartida:
        if es_partida_de_libro:
            return ClasificacionPartida.LIBRO

        es_resultado_perdedor = resultado in (
            ResultadoPartida.VICTORIA_NEGRAS,
            ResultadoPartida.VICTORIA_BLANCAS,
        )

        partida_botada = ventaja_maxima > UMBRAL_VENTAJA_PARTIDA_BOTADA and (
            es_resultado_perdedor and analisis.blunders > 0
        )
        if partida_botada:
            return ClasificacionPartida.PARTIDA_BOTADA

        accuracy = analisis.accuracy if analisis.accuracy is not None else 0.0
        if accuracy >= 85 and analisis.blunders == 0:
            return ClasificacionPartida.EXCELENTE
        return ClasificacionPartida.BUENA


@dataclass
class ConsultarEstadisticasPorFase:
    repositorio_partidas: RepositorioPartidas
    repositorio_analisis: RepositorioAnalisisTecnico

    def ejecutar(self, id_atleta: str) -> EstadisticasFaseJuego:
        partidas = self.repositorio_partidas.listar_por_atleta(id_atleta)
        analisis_list = self.repositorio_analisis.listar_por_atleta(id_atleta)

        estadisticas = EstadisticasFaseJuego(id_atleta=id_atleta)
        if not partidas:
            return estadisticas

        analisis_por_partida = {a.id_partida: a for a in analisis_list}
        total = len(partidas)
        puntos = 0.0
        for partida in partidas:
            puntos += _puntos_partida(partida.resultado)
            analisis = analisis_por_partida.get(partida.id)
            if analisis:
                estadisticas.apertura.errores_cometidos += analisis.errores
                estadisticas.medio_juego.errores_tacticos += analisis.blunders
                estadisticas.finales.errores_tecnicos += analisis.errores
                if analisis.accuracy is not None:
                    estadisticas.medio_juego.precision = (
                        _promedio(
                            estadisticas.medio_juego.precision, analisis.accuracy
                        )
                    )
        estadisticas.apertura.porcentaje_exito = (puntos / (total * 1.0)) * 100
        return estadisticas


@dataclass
class ImportarPartidaDesdePGN:
    repositorio_partidas: RepositorioPartidas
    proveedor_pgn: ProveedorPGN

    def ejecutar(self, contenido_pgn: str, id_atleta: str) -> List[Partida]:
        partidas = self.proveedor_pgn.parsear(contenido_pgn)
        registradas: List[Partida] = []
        for partida in partidas:
            partida.id_atleta = id_atleta
            registradas.append(self.repositorio_partidas.guardar(partida))
        return registradas


def _puntos_partida(resultado: ResultadoPartida) -> float:
    if resultado == ResultadoPartida.VICTORIA_BLANCAS:
        return 1.0
    if resultado == ResultadoPartida.TABLAS:
        return 0.5
    return 0.0


def _promedio(actual: Optional[float], nuevo: float) -> float:
    if actual is None:
        return nuevo
    return (actual + nuevo) / 2.0
