"""Casos de uso (puertos primarios / driving) del módulo de Patrones de Error."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..partidas.entidades import AnalisisTecnico, Partida, ResultadoPartida
from ..comun.errores import ErrorValidacion
from .entidades import (
    AnalisisPatrones,
    MINIMO_PARTIDAS_PATRON,
    NivelMinimoPartidas,
    PatronDetectado,
    PORCENTAJE_MINIMO_PATRON,
    TipoPatron,
)
from .puertos import ProveedorDatosPartidas


@dataclass
class DetectarPatronesError:
    proveedor_datos: ProveedorDatosPartidas

    def ejecutar(
        self,
        id_atleta: str,
        nivel: NivelMinimoPartidas = NivelMinimoPartidas.BASICO,
        periodo_inicio: Optional[date] = None,
        periodo_fin: Optional[date] = None,
    ) -> AnalisisPatrones:
        datos = self.proveedor_datos.partidas_con_analisis(
            id_atleta, periodo_inicio, periodo_fin
        )
        minimo = _minimo_para_nivel(nivel)
        total = len(datos)
        if total < minimo:
            raise ErrorValidacion(
                f"Se requieren al menos {minimo} partidas para mostrar "
                f"tendencias de nivel {nivel.value} (actual: {total})."
            )

        patrones: List[PatronDetectado] = []
        patrones.extend(_patrones_tacticos(datos, total))
        patrones.extend(_patrones_estrategicos(datos, total))
        patrones.extend(_patrones_apertura(datos, total))
        patrones.extend(_patrones_finales(datos, total))
        patrones.extend(_patrones_gestion_tiempo(datos, total))
        patrones.extend(_patrones_competitivos(datos, total))

        return AnalisisPatrones(
            id_atleta=id_atleta,
            patrones=patrones,
            minimo_requerido=minimo,
        )


def _minimo_para_nivel(nivel: NivelMinimoPartidas) -> int:
    from .entidades import MINIMOS_PARTIDAS

    return MINIMOS_PARTIDAS.get(nivel, MINIMO_PARTIDAS_PATRON)


def _es_patron(frecuencia: int, total: int) -> bool:
    """Regla RF-06.8: se repite en >=5 partidas o en >40% de las analizadas."""
    return frecuencia >= MINIMO_PARTIDAS_PATRON or (
        (frecuencia / total * 100) > PORCENTAJE_MINIMO_PATRON
    )


def _registrar(
    patrones: List[PatronDetectado],
    tipo: TipoPatron,
    descripcion: str,
    frecuencia: int,
    total: int,
) -> None:
    if _es_patron(frecuencia, total):
        patrones.append(
            PatronDetectado(
                tipo=tipo,
                descripcion=descripcion,
                frecuencia_absoluta=frecuencia,
                frecuencia_relativa=frecuencia / total * 100,
            )
        )


def _patrones_tacticos(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    patrones: List[PatronDetectado] = []
    blunders = sum(1 for _, a in datos if a.blunders >= 1)
    _registrar(
        patrones,
        TipoPatron.TACTICO,
        "Blunders recurrentes (al menos 1 por partida).",
        blunders,
        total,
    )
    piezas_colgadas = sum(1 for _, a in datos if a.errores >= 2)
    _registrar(
        patrones,
        TipoPatron.TACTICO,
        "Errores tácticos frecuentes (>=2 errores por partida).",
        piezas_colgadas,
        total,
    )
    return patrones


def _patrones_estrategicos(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    patrones: List[PatronDetectado] = []
    imprecisiones = sum(1 for _, a in datos if a.imprecisiones >= 3)
    _registrar(
        patrones,
        TipoPatron.ESTRATEGICO,
        "Imprecisiones estratégicas frecuentes (>=3 por partida).",
        imprecisiones,
        total,
    )
    return patrones


def _patrones_apertura(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    patrones: List[PatronDetectado] = []
    malas_salidas = sum(1 for _, a in datos if a.libro == 0)
    _registrar(
        patrones,
        TipoPatron.APERTURA,
        "Salidas tempranas de la teoría (0 movimientos de libro).",
        malas_salidas,
        total,
    )
    return patrones


def _patrones_finales(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    patrones: List[PatronDetectado] = []
    perdidas_tiempo = sum(1 for _, a in datos if a.perdidas_por_tiempo >= 1)
    _registrar(
        patrones,
        TipoPatron.FINALES,
        "Pérdidas por tiempo recurrentes (>=1 por partida).",
        perdidas_tiempo,
        total,
    )
    return patrones


def _patrones_gestion_tiempo(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    patrones: List[PatronDetectado] = []
    apuros = sum(
        1
        for _, a in datos
        if a.tiempo_promedio_jugada is not None and a.tiempo_promedio_jugada < 20
    )
    _registrar(
        patrones,
        TipoPatron.GESTION_TIEMPO,
        "Apuros recurrentes (tiempo promedio por jugada < 20s).",
        apuros,
        total,
    )
    return patrones


def _patrones_competitivos(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    patrones: List[PatronDetectado] = []
    derrotas_con_blunder = sum(
        1
        for p, a in datos
        if a.blunders >= 1
        and p.resultado
        in (ResultadoPartida.VICTORIA_NEGRAS, ResultadoPartida.VICTORIA_BLANCAS)
    )
    _registrar(
        patrones,
        TipoPatron.COMPETITIVO,
        "Derrotas asociadas a blunders.",
        derrotas_con_blunder,
        total,
    )
    return patrones
