"""Casos de uso (puertos primarios / driving) del módulo de Patrones de Error."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional

from ..comun.errores import ErrorValidacion
from ..partidas.entidades import (
    AnalisisTecnico,
    ColorPartida,
    Partida,
)
from .entidades import (
    AnalisisPatrones,
    MINIMO_PARTIDAS_PATRON,
    MINIMOS_PARTIDAS,
    NivelMinimoPartidas,
    PatronDetectado,
    PORCENTAJE_MINIMO_PATRON,
    TipoPatron,
)
from .puertos import ProveedorDatosPartidas

# Rendimiento de puntos por debajo del cual un grupo se considera patrón débil.
UMBRAL_RENDIMIENTO_DEBIL = 40.0


@dataclass
class DetectarPatronesError:
    """RF-06: detecta patrones recurrentes sin generar sugerencias (RF-06.10)."""

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

        conteos = self.proveedor_datos.conteos_disciplina(
            id_atleta, periodo_inicio, periodo_fin
        )
        patrones: List[PatronDetectado] = []
        patrones.extend(_patrones_tacticos(datos, total))
        patrones.extend(_patrones_estrategicos(datos, total))
        patrones.extend(_patrones_apertura(datos, total))
        patrones.extend(_patrones_finales(datos, total))
        patrones.extend(_patrones_gestion_tiempo(datos, total))
        patrones.extend(_patrones_competitivos(datos, total))
        patrones.extend(_patrones_disciplina(conteos, total))
        patrones.extend(_patrones_rendimiento_por_color(datos))
        patrones.extend(_patrones_rivales(datos))
        patrones.extend(_patrones_control_tiempo(datos))

        return AnalisisPatrones(
            id_atleta=id_atleta,
            patrones=patrones,
            minimo_requerido=minimo,
        )


def _minimo_para_nivel(nivel: NivelMinimoPartidas) -> int:
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


def _porcentaje_puntos(partidas: List[Partida]) -> float:
    """Porcentaje de puntos obtenidos por el atleta sobre el total posible."""
    if not partidas:
        return 0.0
    return sum(p.puntos_obtenidos() for p in partidas) / len(partidas) * 100


def _patrones_tacticos(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    """RF-06.1: blunders recurrentes, errores tácticos frecuentes."""
    patrones: List[PatronDetectado] = []
    blunders = sum(1 for _, a in datos if a.blunders >= 1)
    _registrar(
        patrones,
        TipoPatron.TACTICO,
        "Blunders recurrentes (al menos 1 por partida).",
        blunders,
        total,
    )
    errores_tacticos = sum(1 for _, a in datos if a.errores >= 2)
    _registrar(
        patrones,
        TipoPatron.TACTICO,
        "Errores tácticos frecuentes (>=2 errores por partida).",
        errores_tacticos,
        total,
    )
    return patrones


def _patrones_estrategicos(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    """RF-06.2: imprecisiones estratégicas frecuentes."""
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
    """RF-06.3: salidas tempranas de la teoría."""
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
    """RF-06.4: pérdidas por tiempo como patrón de finales."""
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
    """RF-06.5: apuros recurrentes de tiempo."""
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
    """RF-06.6: derrotas asociadas a blunders."""
    patrones: List[PatronDetectado] = []
    derrotas_con_blunder = sum(
        1
        for p, a in datos
        if a.blunders >= 1 and p.puntos_obtenidos() == 0.0
    )
    _registrar(
        patrones,
        TipoPatron.COMPETITIVO,
        "Derrotas asociadas a blunders.",
        derrotas_con_blunder,
        total,
    )
    return patrones


def _patrones_disciplina(
    conteos: Dict[str, int], total_partidas: int
) -> List[PatronDetectado]:
    """RF-06.7: incumplimiento del plan, baja asistencia y baja frecuencia
    de análisis de partidas."""
    patrones: List[PatronDetectado] = []
    universo = total_partidas + conteos.get("partidas_sin_analisis", 0)

    sin_analisis = conteos.get("partidas_sin_analisis", 0)
    if universo > 0 and _es_patron(sin_analisis, universo):
        patrones.append(
            PatronDetectado(
                tipo=TipoPatron.DISCIPLINA,
                descripcion="Baja frecuencia de análisis de partidas.",
                frecuencia_absoluta=sin_analisis,
                frecuencia_relativa=sin_analisis / universo * 100,
            )
        )

    for clave, descripcion in (
        ("incumplimientos_semanales", "Incumplimiento recurrente del plan semanal."),
        ("inasistencias", "Baja asistencia a los entrenamientos."),
    ):
        frecuencia = conteos.get(clave, 0)
        if frecuencia >= MINIMO_PARTIDAS_PATRON:
            patrones.append(
                PatronDetectado(
                    tipo=TipoPatron.DISCIPLINA,
                    descripcion=descripcion,
                    frecuencia_absoluta=frecuencia,
                    frecuencia_relativa=frecuencia / total_partidas * 100,
                )
            )
    return patrones


def _patrones_rendimiento_por_color(
    datos: List[tuple[Partida, AnalisisTecnico]],
) -> List[PatronDetectado]:
    """RF-06.6: rendimiento por color de piezas (requiere >=20 partidas)."""
    patrones: List[PatronDetectado] = []
    minimo = MINIMOS_PARTIDAS[NivelMinimoPartidas.COLOR]
    for color in ColorPartida:
        partidas = [p for p, _ in datos if p.color_atleta == color]
        if len(partidas) >= minimo:
            rendimiento = _porcentaje_puntos(partidas)
            if rendimiento < UMBRAL_RENDIMIENTO_DEBIL:
                patrones.append(
                    PatronDetectado(
                        tipo=TipoPatron.COMPETITIVO,
                        descripcion=(
                            f"Rendimiento débil jugando con {color.value} "
                            f"({rendimiento:.0f}% de puntos)."
                        ),
                        frecuencia_absoluta=len(partidas),
                        frecuencia_relativa=rendimiento,
                    )
                )
    return patrones


def _patrones_rivales(
    datos: List[tuple[Partida, AnalisisTecnico]],
) -> List[PatronDetectado]:
    """RF-06.6: rendimiento contra rivales de mayor rating (>=20 partidas)."""
    patrones: List[PatronDetectado] = []
    minimo = MINIMOS_PARTIDAS[NivelMinimoPartidas.RIVAL]
    contra_superiores = [
        p
        for p, _ in datos
        if p.color_atleta is not None and _rating_rival(p) > _rating_atleta(p)
    ]
    if len(contra_superiores) >= minimo:
        rendimiento = _porcentaje_puntos(contra_superiores)
        if rendimiento < UMBRAL_RENDIMIENTO_DEBIL:
            patrones.append(
                PatronDetectado(
                    tipo=TipoPatron.COMPETITIVO,
                    descripcion=(
                        "Rendimiento débil contra rivales de mayor rating "
                        f"({rendimiento:.0f}% de puntos)."
                    ),
                    frecuencia_absoluta=len(contra_superiores),
                    frecuencia_relativa=rendimiento,
                )
            )
    return patrones


def _patrones_control_tiempo(
    datos: List[tuple[Partida, AnalisisTecnico]],
) -> List[PatronDetectado]:
    """RF-06.6: desempeño por control de tiempo (agrupación avanzada, >=20)."""
    patrones: List[PatronDetectado] = []
    minimo = MINIMOS_PARTIDAS[NivelMinimoPartidas.COLOR]
    por_control: Dict[str, List[Partida]] = {}
    for partida, _ in datos:
        if partida.control_tiempo:
            por_control.setdefault(partida.control_tiempo, []).append(partida)
    for control, partidas in por_control.items():
        if len(partidas) >= minimo:
            rendimiento = _porcentaje_puntos(partidas)
            if rendimiento < UMBRAL_RENDIMIENTO_DEBIL:
                patrones.append(
                    PatronDetectado(
                        tipo=TipoPatron.COMPETITIVO,
                        descripcion=(
                            f"Rendimiento débil en control de tiempo {control} "
                            f"({rendimiento:.0f}% de puntos)."
                        ),
                        frecuencia_absoluta=len(partidas),
                        frecuencia_relativa=rendimiento,
                    )
                )
    return patrones


def _rating_atleta(partida: Partida) -> int:
    if partida.color_atleta == ColorPartida.NEGRAS:
        return partida.rating_negras
    return partida.rating_blancas


def _rating_rival(partida: Partida) -> int:
    if partida.color_atleta == ColorPartida.NEGRAS:
        return partida.rating_blancas
    return partida.rating_negras
