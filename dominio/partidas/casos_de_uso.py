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
    ColorPartida,
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


def validar_partida(partida: Partida) -> None:
    """RF-05.1: datos obligatorios de una partida (registro manual e importación PGN)."""
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
    if partida.color_atleta is not None and partida.color_atleta not in ColorPartida:
        raise ErrorValidacion("El color del atleta es inválido.")


@dataclass
class RegistrarPartida:
    repositorio: RepositorioPartidas

    def ejecutar(self, partida: Partida) -> Partida:
        validar_partida(partida)
        return self.repositorio.guardar(partida)


@dataclass
class RegistrarAnalisisTecnico:
    """RF-05.3/05.4: el entrenador completa el resumen técnico post-partida."""

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


def _es_resultado_perdedor(
    resultado: ResultadoPartida,
    color_atleta: Optional[ColorPartida],
) -> bool:
    """Determina si el resultado es una derrota para el atleta según su color."""
    if color_atleta == ColorPartida.NEGRAS:
        return resultado == ResultadoPartida.VICTORIA_BLANCAS
    if color_atleta == ColorPartida.BLANCAS:
        return resultado == ResultadoPartida.VICTORIA_NEGRAS
    # Sin información de color, se asume perspectiva de blancas.
    return resultado in (
        ResultadoPartida.VICTORIA_BLANCAS,
        ResultadoPartida.VICTORIA_NEGRAS,
    )


@dataclass
class ClasificarPartida:
    """RF-05.6: asigna automáticamente la categoría según reglas del dominio."""

    def ejecutar(
        self,
        analisis: AnalisisTecnico,
        resultado: ResultadoPartida,
        ventaja_maxima: float = 0.0,
        es_partida_de_libro: bool = False,
        color_atleta: Optional[ColorPartida] = None,
    ) -> ClasificacionPartida:
        if es_partida_de_libro:
            return ClasificacionPartida.LIBRO

        # Partida botada: ventaja > +3 y pérdida/empate con blunder (RF-05.6).
        es_derrota = _es_resultado_perdedor(resultado, color_atleta)
        es_tablas = resultado == ResultadoPartida.TABLAS
        partida_botada = (
            ventaja_maxima > UMBRAL_VENTAJA_PARTIDA_BOTADA
            and analisis.blunders > 0
            and (es_derrota or es_tablas)
        )
        if partida_botada:
            return ClasificacionPartida.PARTIDA_BOTADA

        accuracy = analisis.accuracy if analisis.accuracy is not None else 0.0
        if accuracy >= 85 and analisis.blunders == 0:
            return ClasificacionPartida.EXCELENTE
        return ClasificacionPartida.BUENA


@dataclass
class ConsultarEstadisticasPorFase:
    """RF-07: agrega métricas por apertura, medio juego y finales."""

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
        puntos = sum(p.puntos_obtenidos() for p in partidas)

        suma_accuracy = 0.0
        n_accuracy = 0
        suma_tiempo = 0.0
        n_tiempo = 0
        for partida in partidas:
            analisis = analisis_por_partida.get(partida.id)
            if analisis is None:
                continue
            estadisticas.apertura.errores_cometidos += analisis.errores
            estadisticas.medio_juego.errores_tacticos += analisis.blunders
            estadisticas.finales.errores_tecnicos += analisis.imprecisiones
            if analisis.accuracy is not None:
                suma_accuracy += analisis.accuracy
                n_accuracy += 1
            if analisis.tiempo_promedio_jugada is not None:
                suma_tiempo += analisis.tiempo_promedio_jugada
                n_tiempo += 1

        estadisticas.apertura.porcentaje_exito = (puntos / total) * 100
        estadisticas.apertura.tiempo_utilizado = (
            suma_tiempo / n_tiempo if n_tiempo else None
        )
        estadisticas.medio_juego.precision = (
            suma_accuracy / n_accuracy if n_accuracy else None
        )
        return estadisticas


@dataclass
class ImportarPartidaDesdePGN:
    """RF-05.2: orquesta la lectura del proveedor PGN y el registro validado."""

    repositorio_partidas: RepositorioPartidas
    proveedor_pgn: ProveedorPGN

    def ejecutar(self, contenido_pgn: str, id_atleta: str) -> List[Partida]:
        partidas = self.proveedor_pgn.parsear(contenido_pgn)
        registradas: List[Partida] = []
        for partida in partidas:
            partida.id_atleta = id_atleta
            validar_partida(partida)
            registradas.append(self.repositorio_partidas.guardar(partida))
        return registradas
