"""Adaptador ProveedorPGN: parser de archivos PGN.

El proyecto no usa dependencias externas, por lo que el parser se implementa
sólo con ``re``/``datetime``. Valida la estructura del archivo (etiquetas
obligatorias, fecha, ELOs, resultado y movidas en notación SAN) y traduce
cualquier problema de parseo a ``ErrorValidacion``: nunca se filtra una
excepción cruda al dominio. Un PGN bien formado produce una ``Partida``
estructurada lista para la validación de negocio de ``validar_partida``."""
from __future__ import annotations

import re
from datetime import date
from typing import Dict, List, Match, Tuple

from dominio.comun.errores import ErrorValidacion
from dominio.partidas.entidades import FuentePartida, Partida, ResultadoPartida
from dominio.partidas.puertos import ProveedorPGN

_ETIQUETA = re.compile(r'\[(?P<clave>[A-Za-z0-9_]+)\s+"(?P<valor>[^"]*)"\s*\]')

_ETIQUETAS_OBLIGATORIAS = (
    "Event", "Date", "White", "Black", "WhiteElo", "BlackElo", "Result", "ECO",
)

_FECHA = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})$")

_ELO = re.compile(r"^\d+$")

_RESULTADOS = {"1-0", "0-1", "1/2-1/2"}

_SAN = re.compile(
    r"^(?:O-O(?:-O)?|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?)[+#]?$"
)

_POR_NUMERO = re.compile(r"^\d+\.+")

_ANOTACION = re.compile(r"[!?]+$")

def _limpiar_movetext(movetext: str) -> str:
    """Elimina comentarios, variantes, NAGs y directivas; conserva las movidas."""
    texto = re.sub(r"\{[^}]*\}", " ", movetext)
    texto = re.sub(r";[^\n]*", " ", texto)
    while "(" in texto:
        reducido = re.sub(r"\([^()]*\)", " ", texto)
        if reducido == texto:
            break
        texto = reducido
    texto = re.sub(r"\$\d+", " ", texto)
    texto = re.sub(r"%[A-Za-z]+\s[^\n]*", " ", texto)
    return texto

class ProveedorPGNEstandar(ProveedorPGN):
    """Implementación estándar (stdlib) del proveedor de importación PGN."""

    def parsear(self, contenido_pgn: str) -> List[Partida]:
        if not isinstance(contenido_pgn, str):
            raise ErrorValidacion("El contenido PGN no es texto.")
        bloques = _separar_bloques(contenido_pgn)
        return [
            self._a_partida(etiquetas, movetext, indice)
            for indice, (etiquetas, movetext) in enumerate(bloques, start=1)
        ]

    def _a_partida(
        self, etiquetas: Dict[str, str], movetext: str, indice: int
    ) -> Partida:
        faltantes = [
            nombre for nombre in _ETIQUETAS_OBLIGATORIAS
            if not etiquetas.get(nombre, "").strip()
        ]
        if faltantes:
            raise ErrorValidacion(
                f"El juego {indice} del PGN no tiene las etiquetas obligatorias: "
                f"{', '.join(faltantes)}."
            )
        resultado = self._resultado(etiquetas["Result"], movetext, indice)
        return Partida(
            id=0,
            id_atleta=0,
            evento=etiquetas["Event"].strip(),
            fecha=self._fecha(etiquetas["Date"], indice),
            jugador_blancas=etiquetas["White"].strip(),
            jugador_negras=etiquetas["Black"].strip(),
            rating_blancas=self._entero(etiquetas["WhiteElo"], "WhiteElo", indice),
            rating_negras=self._entero(etiquetas["BlackElo"], "BlackElo", indice),
            resultado=resultado,
            apertura_eco=etiquetas["ECO"].strip(),
            control_tiempo=etiquetas.get("TimeControl") or None,
            fuente=FuentePartida.PGN,
        )

    def _resultado(
        self, tag_result: str, movetext: str, indice: int
    ) -> ResultadoPartida:
        if tag_result == "*":
            raise ErrorValidacion(
                f"El juego {indice} del PGN no tiene resultado concluido (Result = '*')."
            )
        if tag_result not in _RESULTADOS:
            raise ErrorValidacion(
                f"El juego {indice} del PGN tiene un resultado inválido: '{tag_result}'."
            )
        self._validar_movidas(movetext, tag_result, indice)
        return ResultadoPartida(tag_result)

    @staticmethod
    def _validar_movidas(movetext: str, resultado: str, indice: int) -> None:
        movidas = _limpiar_movetext(movetext).split()
        if not movidas:
            raise ErrorValidacion(f"El juego {indice} del PGN no tiene movidas.")
        if movidas[-1] not in _RESULTADOS | {"*"}:
            raise ErrorValidacion(
                f"El juego {indice} del PGN no termina con un resultado "
                "(1-0, 0-1 o 1/2-1/2)."
            )
        if movidas.pop() != resultado:
            raise ErrorValidacion(
                f"El juego {indice} del PGN tiene un resultado en la movetext "
                f"diferente de la etiqueta Result ({resultado})."
            )
        for movida in movidas:
            token = _POR_NUMERO.sub("", movida)
            token = _ANOTACION.sub("", token)
            if not token:
                continue
            if not _SAN.match(token):
                raise ErrorValidacion(
                    f"El juego {indice} del PGN tiene una movida ilegible: '{movida}'."
                )

    @staticmethod
    def _fecha(valor: str, indice: int) -> date:
        coincidencia = _FECHA.match(valor.strip())
        if coincidencia is None:
            raise ErrorValidacion(
                f"El juego {indice} del PGN tiene una fecha inválida: '{valor}' "
                "(se espera AAAA.MM.DD)."
            )
        anio, mes, dia = (int(g) for g in coincidencia.groups())
        try:
            return date(anio, mes, dia)
        except ValueError as error:
            raise ErrorValidacion(
                f"El juego {indice} del PGN tiene una fecha inexistente: '{valor}'."
            ) from error

    @staticmethod
    def _entero(valor: str, etiqueta: str, indice: int) -> int:
        if not _ELO.match(valor.strip()):
            raise ErrorValidacion(
                f"El juego {indice} del PGN tiene un {etiqueta} no numérico: '{valor}'."
            )
        return int(valor)

def _separar_bloques(contenido: str) -> List[Tuple[Dict[str, str], str]]:
    """Agrupa las etiquetas contiguas de cada juego y su movetext posterior.

 Devuelve una lista de ``(etiquetas, movetext)``; un archivo sin etiquetas
 no contiene juegos parseables y produce una lista vacía.
 """
    coincidencias = list(_ETIQUETA.finditer(contenido))
    if not coincidencias:
        return []
    grupos: List[List[Match]] = [[coincidencias[0]]]
    for actual in coincidencias[1:]:
        entre = contenido[grupos[-1][-1].end():actual.start()]
        if entre.strip():
            grupos.append([])
        grupos[-1].append(actual)
    bloques: List[Tuple[Dict[str, str], str]] = []
    for posicion, grupo in enumerate(grupos):
        etiquetas = {m.group("clave"): m.group("valor") for m in grupo}
        inicio = grupo[-1].end()
        fin = grupos[posicion + 1][0].start() if posicion + 1 < len(grupos) else len(contenido)
        bloques.append((etiquetas, contenido[inicio:fin]))
    return bloques

__all__ = ["ProveedorPGNEstandar"]
