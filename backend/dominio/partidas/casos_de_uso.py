"""Casos de uso (puertos primarios / driving) del módulo de Partidas."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorAutenticacion,
    ErrorValidacion,
)
from ..comun.validaciones import (
    convertir_enum,
    exigir_decimal,
    exigir_entero,
    exigir_fecha,
    exigir_texto,
)
from ..usuarios.entidades import Rol
from .entidades import (
    AnalisisTecnico,
    ClasificacionPartida,
    ColorPartida,
    EstadisticasFaseJuego,
    FuentePartida,
    Partida,
    ResultadoPartida,
)
from .puertos import (
    ProveedorPGN,
    RepositorioAnalisisTecnico,
    RepositorioPartidas,
)

UMBRAL_VENTAJA_PARTIDA_BOTADA = 3.0
RATING_MINIMO = 0
RATING_MAXIMO = 4000
_PATRON_ECO = re.compile(r"^[A-E][0-9]{2}$")

HORAS_MINIMAS_ANALISIS = 24
HORAS_MAXIMAS_ANALISIS = 72

def _exigir_entrenador(rol_usuario: Rol, accion: str) -> None:
    """los registros oficiales son competencia del entrenador."""
    if rol_usuario != Rol.ENTRENADOR:
        raise ErrorAutenticacion(
            f"Acceso denegado: sólo el entrenador puede {accion}."
        )

def validar_partida(partida: Partida, hoy: Optional[date] = None) -> None:
    """valida y normaliza los datos obligatorios de una partida."""
    if not isinstance(partida, Partida):
        raise ErrorValidacion("La partida es inválida.")
    exigir_entero(partida.id_atleta, "id_atleta", minimo=1)
    partida.evento = exigir_texto(partida.evento, "evento", max_longitud=100)
    fecha = exigir_fecha(partida.fecha, "fecha")
    if fecha > (hoy or date.today()):
        raise ErrorValidacion("La fecha de la partida no puede ser futura.")
    partida.jugador_blancas = exigir_texto(
        partida.jugador_blancas, "jugador_blancas", max_longitud=60
    )
    partida.jugador_negras = exigir_texto(
        partida.jugador_negras, "jugador_negras", max_longitud=60
    )
    partida.rating_blancas = exigir_entero(
        partida.rating_blancas, "rating_blancas", minimo=RATING_MINIMO, maximo=RATING_MAXIMO
    )
    partida.rating_negras = exigir_entero(
        partida.rating_negras, "rating_negras", minimo=RATING_MINIMO, maximo=RATING_MAXIMO
    )
    partida.resultado = convertir_enum(
        ResultadoPartida, partida.resultado, "resultado"
    )
    eco = exigir_texto(partida.apertura_eco, "apertura_eco", max_longitud=5).upper()
    if not _PATRON_ECO.match(eco):
        raise ErrorValidacion(
            "El código ECO es inválido; debe tener una letra A-E y dos dígitos (ej. B90)."
        )
    partida.apertura_eco = eco
    partida.fuente = convertir_enum(FuentePartida, partida.fuente, "fuente")
    if partida.color_atleta is not None:
        partida.color_atleta = convertir_enum(
            ColorPartida, partida.color_atleta, "color_atleta"
        )
    if partida.control_tiempo is not None:
        partida.control_tiempo = exigir_texto(
            partida.control_tiempo, "control_tiempo", max_longitud=20
        )

def _validar_analisis(analisis: AnalisisTecnico) -> None:
    if not isinstance(analisis, AnalisisTecnico):
        raise ErrorValidacion("El análisis técnico es inválido.")
    exigir_entero(analisis.id_partida, "id_partida", minimo=1)
    if analisis.accuracy is not None:
        analisis.accuracy = exigir_decimal(
            analisis.accuracy, "accuracy", minimo=0.0, maximo=100.0
        )
    if analisis.acpl is not None:
        analisis.acpl = exigir_decimal(analisis.acpl, "acpl", minimo=0.0)
    if analisis.tiempo_promedio_jugada is not None:
        analisis.tiempo_promedio_jugada = exigir_decimal(
            analisis.tiempo_promedio_jugada, "tiempo_promedio_jugada", minimo=0.0
        )
    for campo in (
        "blunders",
        "errores",
        "imprecisiones",
        "brilliant_moves",
        "excelente",
        "buena",
        "libro",
        "perdidas_por_tiempo",
    ):
        setattr(
            analisis,
            campo,
            exigir_entero(getattr(analisis, campo), campo, minimo=0),
        )

@dataclass
class RegistrarPartida:
    """registra una partida manual ya validada."""

    repositorio: RepositorioPartidas

    def ejecutar(
        self,
        partida: Partida,
        rol_usuario: Rol | str,
    ) -> Partida:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "registrar partidas")
        validar_partida(partida)
        return self.repositorio.guardar(partida)

@dataclass
class RegistrarAnalisisTecnico:
    """el entrenador completa el resumen técnico."""

    repositorio: RepositorioAnalisisTecnico
    repositorio_partidas: RepositorioPartidas

    def ejecutar(
        self,
        analisis: AnalisisTecnico,
        rol_usuario: Rol | str,
        fecha_analisis: Optional[date] = None,
        ventaja_maxima: Optional[float] = None,
        es_partida_de_libro: bool = False,
    ) -> AnalisisTecnico:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "completar el análisis técnico")
        _validar_analisis(analisis)
        partida = self.repositorio_partidas.buscar_por_id(analisis.id_partida)
        if partida is None:
            raise EntidadNoEncontrada("La partida no existe.")

        if fecha_analisis is not None:
            fecha = exigir_fecha(fecha_analisis, "fecha_analisis")
            horas = (fecha - partida.fecha).total_seconds() / 3600
            if horas < 0:
                raise ErrorValidacion(
                    "La fecha de análisis no puede ser anterior a la partida."
                )

            if not HORAS_MINIMAS_ANALISIS <= horas <= HORAS_MAXIMAS_ANALISIS:
                raise ErrorValidacion(
                    "El análisis debe realizarse dentro de las 24 a 72 horas "
                    f"posteriores al torneo (transcurridas {horas:.0f} h)."
                )
        registrado = self.repositorio.guardar_resumen(analisis)

        if ventaja_maxima is not None or es_partida_de_libro:
            clasificacion = ClasificarPartida().ejecutar(
                analisis,
                partida.resultado,
                ventaja_maxima=ventaja_maxima or 0.0,
                es_partida_de_libro=es_partida_de_libro,
                color_atleta=partida.color_atleta,
            )
            partida.clasificacion = clasificacion
            partida.ventaja_maxima = ventaja_maxima
            self.repositorio_partidas.guardar(partida)
        return registrado

def _es_resultado_perdedor(
    resultado: ResultadoPartida,
    color_atleta: Optional[ColorPartida],
) -> bool:
    """Indica si el resultado es una derrota para el atleta según su color.

 Si no hay color registrado se asume la perspectiva de blancas (criterio
 documentado): ``1-0`` es victoria y ``0-1`` es derrota.
 """
    resultado = convertir_enum(ResultadoPartida, resultado, "resultado")
    if color_atleta == ColorPartida.NEGRAS:
        return resultado == ResultadoPartida.VICTORIA_BLANCAS
    return resultado == ResultadoPartida.VICTORIA_NEGRAS

@dataclass
class ClasificarPartida:
    """asigna automáticamente la categoría según reglas del dominio."""

    def ejecutar(
        self,
        analisis: AnalisisTecnico,
        resultado: ResultadoPartida,
        ventaja_maxima: float = 0.0,
        es_partida_de_libro: bool = False,
        color_atleta: Optional[ColorPartida] = None,
    ) -> ClasificacionPartida:
        _validar_analisis(analisis)
        resultado_enum = convertir_enum(ResultadoPartida, resultado, "resultado")
        ventaja = exigir_decimal(
            ventaja_maxima, "ventaja_maxima", minimo=0.0
        )
        if not isinstance(es_partida_de_libro, bool):
            raise ErrorValidacion("'es_partida_de_libro' debe ser booleano.")
        color = None
        if color_atleta is not None:
            color = convertir_enum(ColorPartida, color_atleta, "color_atleta")

        if es_partida_de_libro:
            return ClasificacionPartida.LIBRO

        es_derrota = _es_resultado_perdedor(resultado_enum, color)
        es_tablas = resultado_enum == ResultadoPartida.TABLAS
        partida_botada = (
            ventaja > UMBRAL_VENTAJA_PARTIDA_BOTADA
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
    """agrega métricas por apertura, medio juego y finales.

 Limitación de modelo: ``analisis_tecnico_partidas`` no distingue en
 qué fase ocurrió cada error, por lo que la conversión de posiciones
 ganadas y las tablas salvadas no pueden calcularse con los datos
 actuales y se devuelven en cero. Las partidas botadas sí se calculan desde
 la clasificación persistida, misma fuente que
 ``DetectarPatronesError``.
 """

    repositorio_partidas: RepositorioPartidas
    repositorio_analisis: RepositorioAnalisisTecnico

    def ejecutar(
        self, id_atleta: int, *, solicitante: Solicitante
    ) -> EstadisticasFaseJuego:
        exigir_entrenador(solicitante, "consultar estadísticas por fase")
        return self.calcular(id_atleta)

    def calcular(self, id_atleta: int) -> EstadisticasFaseJuego:
        """Cálculo puro reutilizable por el autoservicio del atleta."""
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        partidas = self.repositorio_partidas.listar_por_atleta(id_atleta)
        analisis_list = self.repositorio_analisis.listar_por_atleta(id_atleta)

        estadisticas = EstadisticasFaseJuego(
            id_atleta=id_atleta,
            partidas_totales=len(partidas),
            partidas_analizadas=len(analisis_list),
        )
        if not partidas:
            return estadisticas

        analisis_por_partida = {a.id_partida: a for a in analisis_list}
        total = len(partidas)
        puntos = sum(p.puntos_obtenidos() for p in partidas)

        estadisticas.finales.partidas_botadas = sum(
            1
            for p in partidas
            if p.clasificacion == ClasificacionPartida.PARTIDA_BOTADA
        )

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
            estadisticas.medio_juego.errores_estrategicos += analisis.imprecisiones
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
    """orquesta la lectura del proveedor PGN y el registro validado."""

    repositorio_partidas: RepositorioPartidas
    proveedor_pgn: ProveedorPGN

    def ejecutar(
        self,
        contenido_pgn: str,
        id_atleta: int,
        rol_usuario: Rol | str,
    ) -> List[Partida]:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "importar partidas")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        contenido = exigir_texto(contenido_pgn, "contenido_pgn")
        partidas = self.proveedor_pgn.parsear(contenido)
        if not partidas:
            raise ErrorValidacion("El archivo PGN no contiene partidas válidas.")

        for partida in partidas:
            partida.id_atleta = id_atleta
            partida.fuente = FuentePartida.PGN
            validar_partida(partida)
        return [
            self.repositorio_partidas.guardar(partida) for partida in partidas
        ]

__all__ = [
    "ClasificarPartida",
    "ConsultarEstadisticasPorFase",
    "HORAS_MAXIMAS_ANALISIS",
    "HORAS_MINIMAS_ANALISIS",
    "ImportarPartidaDesdePGN",
    "RegistrarAnalisisTecnico",
    "RegistrarPartida",
    "UMBRAL_VENTAJA_PARTIDA_BOTADA",
    "validar_partida",
]
