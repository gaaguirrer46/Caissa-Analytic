"""Casos de uso (puertos primarios / driving) del módulo de Patrones de Error.

Limitación de modelo: el esquema oficial no almacena información por
fase del juego ni ventaja máxima por partida. Los patrones de finales
se cubren con la clasificación persistida: el patrón
``FINALES``-"partidas botadas" refleja la baja conversión de posiciones
ventajosas. Los finales técnicos (peones/torres) siguen sin datos por fase
y no se inventan."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional

from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.errores import ErrorValidacion
from ..comun.validaciones import convertir_enum, exigir_entero, exigir_fecha
from ..partidas.entidades import (
    AnalisisTecnico,
    ClasificacionPartida,
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

UMBRAL_RENDIMIENTO_DEBIL = 40.0

MINIMO_EVENTOS_DISCIPLINA = 2

@dataclass
class DetectarPatronesError:
    """detecta patrones recurrentes sin generar sugerencias."""

    proveedor_datos: ProveedorDatosPartidas

    def ejecutar(
        self,
        id_atleta: int,
        nivel: NivelMinimoPartidas | str = NivelMinimoPartidas.BASICO,
        periodo_inicio: Optional[date] = None,
        periodo_fin: Optional[date] = None,
        *,
        solicitante: Solicitante,
    ) -> AnalisisPatrones:
        exigir_entrenador(solicitante, "detectar patrones de un atleta")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        nivel_enum = convertir_enum(NivelMinimoPartidas, nivel, "nivel")
        if (periodo_inicio is None) != (periodo_fin is None):
            raise ErrorValidacion(
                "Debe indicar ambos extremos del periodo o ninguno."
            )
        if periodo_inicio is not None and periodo_fin is not None:
            exigir_fecha(periodo_inicio, "periodo_inicio")
            exigir_fecha(periodo_fin, "periodo_fin")
            if periodo_fin < periodo_inicio:
                raise ErrorValidacion(
                    "El fin del periodo no puede ser anterior a su inicio."
                )

        datos = self.proveedor_datos.partidas_con_analisis(
            id_atleta, periodo_inicio, periodo_fin
        )
        minimo = _minimo_para_nivel(nivel_enum)
        total = len(datos)
        if total < minimo:
            raise ErrorValidacion(
                f"Se requieren al menos {minimo} partidas para mostrar "
                f"tendencias de nivel {nivel_enum.value} (actual: {total})."
            )

        conteos = self.proveedor_datos.conteos_disciplina(
            id_atleta, periodo_inicio, periodo_fin
        )
        if not isinstance(conteos, dict):
            conteos = {}

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

        for patron in patrones:
            patron.periodo_inicio = periodo_inicio
            patron.periodo_fin = periodo_fin

        return AnalisisPatrones(
            id_atleta=id_atleta,
            patrones=patrones,
            minimo_requerido=minimo,
        )

def _minimo_para_nivel(nivel: NivelMinimoPartidas) -> int:
    return MINIMOS_PARTIDAS.get(nivel, MINIMO_PARTIDAS_PATRON)

def _es_patron(frecuencia: int, total: int) -> bool:
    """Regla: se repite en >=5 partidas o en >40% de las analizadas."""
    if total <= 0:
        return False
    return frecuencia >= MINIMO_PARTIDAS_PATRON or (
        (frecuencia / total * 100) > PORCENTAJE_MINIMO_PATRON
    )

def _es_patron_proporcional(
    frecuencia: int,
    universo: int,
    *,
    minimo_eventos: int = MINIMO_EVENTOS_DISCIPLINA,
) -> bool:
    """Regla proporcional para eventos que no son partidas (semanas, sesiones)."""
    if universo <= 0 or frecuencia < minimo_eventos:
        return False
    return (frecuencia / universo * 100) > PORCENTAJE_MINIMO_PATRON

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
    """blunders recurrentes y errores tácticos frecuentes."""
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
    """imprecisiones estratégicas frecuentes."""
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
    """salidas tempranas de la teoría."""
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
    """baja conversión detectada vía clasificación persistida.

 Una partida botada (ventaja > +3, blunder y derrota/tablas) que ya fue
 clasificada al registrar el análisis técnico es evidencia real de un error
 de conversión; se declara patrón con la regla . Las partidas sin
 clasificación contribuyen con cero: no se inventan datos.
 """
    patrones: List[PatronDetectado] = []
    botadas = sum(
        1 for p, _ in datos if p.clasificacion == ClasificacionPartida.PARTIDA_BOTADA
    )
    _registrar(
        patrones,
        TipoPatron.FINALES,
        "Partidas botadas: ventaja alcanzada no convertida (baja conversión).",
        botadas,
        total,
    )
    return patrones

def _patrones_gestion_tiempo(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    """apuros recurrentes y pérdidas de partidas por tiempo.

 Antes las pérdidas por tiempo se clasificaban erróneamente como patrón de
 finales; pertenecen a la gestión del tiempo.
 """
    patrones: List[PatronDetectado] = []
    apuros = sum(
        1
        for _, a in datos
        if a.tiempo_promedio_jugada is not None and a.tiempo_promedio_jugada < 20
    )
    _registrar(
        patrones,
        TipoPatron.GESTION_TIEMPO,
        "Apuros recurrentes (tiempo promedio por jugada < 20 s).",
        apuros,
        total,
    )
    perdidas_tiempo = sum(1 for _, a in datos if a.perdidas_por_tiempo >= 1)
    _registrar(
        patrones,
        TipoPatron.GESTION_TIEMPO,
        "Pérdidas de partidas por tiempo.",
        perdidas_tiempo,
        total,
    )
    return patrones

def _patrones_competitivos(
    datos: List[tuple[Partida, AnalisisTecnico]], total: int
) -> List[PatronDetectado]:
    """derrotas asociadas a blunders."""
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
    """incumplimiento del plan, baja asistencia y baja frecuencia de análisis.

 Los denominadores deben ser semanas y sesiones evaluadas, no partidas; antes
 se dividía por ``total_partidas`` produciendo porcentajes sin sentido.
 """
    patrones: List[PatronDetectado] = []

    sin_analisis = conteos.get("partidas_sin_analisis", 0)
    universo_analisis = conteos.get("partidas_totales", 0) or (
        total_partidas + sin_analisis
    )
    if _es_patron_proporcional(sin_analisis, universo_analisis):
        patrones.append(
            PatronDetectado(
                tipo=TipoPatron.DISCIPLINA,
                descripcion="Baja frecuencia de análisis de partidas.",
                frecuencia_absoluta=sin_analisis,
                frecuencia_relativa=sin_analisis / universo_analisis * 100,
            )
        )

    incumplimientos = conteos.get("incumplimientos_semanales", 0)
    semanas = conteos.get("semanas_evaluadas", 0)
    if _es_patron_proporcional(incumplimientos, semanas):
        patrones.append(
            PatronDetectado(
                tipo=TipoPatron.DISCIPLINA,
                descripcion="Incumplimiento recurrente del plan semanal.",
                frecuencia_absoluta=incumplimientos,
                frecuencia_relativa=incumplimientos / semanas * 100,
            )
        )

    inasistencias = conteos.get("inasistencias", 0)
    sesiones = conteos.get("sesiones_evaluadas", 0)
    if _es_patron_proporcional(inasistencias, sesiones):
        patrones.append(
            PatronDetectado(
                tipo=TipoPatron.DISCIPLINA,
                descripcion="Baja asistencia a los entrenamientos.",
                frecuencia_absoluta=inasistencias,
                frecuencia_relativa=inasistencias / sesiones * 100,
            )
        )
    return patrones

def _patrones_rendimiento_por_color(
    datos: List[tuple[Partida, AnalisisTecnico]],
) -> List[PatronDetectado]:
    """rendimiento por color de piezas (requiere >=20 partidas)."""
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
    """rendimiento contra rivales de mayor rating (>=20 partidas)."""
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
    """desempeño por control de tiempo (agrupación avanzada, >=20)."""
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

__all__ = [
    "DetectarPatronesError",
    "MINIMO_EVENTOS_DISCIPLINA",
    "UMBRAL_RENDIMIENTO_DEBIL",
]
