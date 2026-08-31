"""Casos de uso (puertos primarios / driving) del módulo de Objetivos SMART."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorValidacion,
)
from ..comun.ids import nuevo_id_entero
from ..usuarios.entidades import Rol
from .entidades import (
    EstadoObjetivo,
    ObjetivoSmart,
    TipoIndicadorAvance,
)
from .puertos import ProveedorDatosAvance, RepositorioObjetivos


@dataclass
class CrearObjetivoSmart:
    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_atleta: int,
        descripcion: str,
        indicador_meta: TipoIndicadorAvance,
        valor_meta: float,
        rating_actual: int,
        rating_meta: int,
        fecha_inicio: date,
        fecha_limite: date,
        rol_proponente: Rol,
    ) -> ObjetivoSmart:
        if not descripcion:
            raise ErrorValidacion("La descripción del objetivo es obligatoria.")
        if fecha_inicio is None or fecha_limite is None:
            raise ErrorValidacion(
                "La fecha de inicio y la fecha límite son obligatorias."
            )
        if fecha_limite < fecha_inicio:
            raise ErrorValidacion("La fecha límite no puede ser anterior a la inicial.")
        if valor_meta <= 0:
            raise ErrorValidacion("El valor meta debe ser mayor que cero.")
        if rol_proponente not in (Rol.ENTRENADOR, Rol.ATLETA):
            raise ErrorValidacion("Solo el entrenador o el atleta pueden proponer.")

        objetivo = ObjetivoSmart(
            id=nuevo_id_entero(),
            id_atleta=id_atleta,
            descripcion=descripcion,
            indicador_meta=indicador_meta,
            valor_meta=valor_meta,
            rating_actual=rating_actual,
            rating_meta=rating_meta,
            fecha_inicio=fecha_inicio,
            fecha_limite=fecha_limite,
        )
        return self.repositorio.guardar(objetivo)


@dataclass
class AprobarObjetivoSmart:
    repositorio: RepositorioObjetivos

    def ejecutar(self, id_objetivo: int) -> ObjetivoSmart:
        objetivo = self.repositorio.buscar_por_id(id_objetivo)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")
        objetivo.aprobado_por_entrenador = True
        objetivo.estado = EstadoObjetivo.EN_PROCESO
        return self.repositorio.actualizar(objetivo)


@dataclass
class CalcularAvanceObjetivo:
    repositorio: RepositorioObjetivos
    proveedor_datos: ProveedorDatosAvance

    def ejecutar(self, id_objetivo: int) -> ObjetivoSmart:
        objetivo = self.repositorio.buscar_por_id(id_objetivo)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")

        valor_actual = self._obtener_valor_actual(
            objetivo,
            objetivo.fecha_inicio,
            objetivo.fecha_limite,
        )
        avance = objetivo.valor_meta
        objetivo.porcentaje_avance = (
            min(100.0, (valor_actual / avance) * 100) if avance > 0 else 0.0
        )
        return self.repositorio.actualizar(objetivo)

    def _obtener_valor_actual(
        self,
        objetivo: ObjetivoSmart,
        desde: date,
        hasta: date,
    ) -> float:
        tipo = objetivo.indicador_meta
        if tipo == TipoIndicadorAvance.HORAS_ENTRENADAS:
            return self.proveedor_datos.horas_entrenadas(
                objetivo.id_atleta, desde, hasta
            )
        if tipo == TipoIndicadorAvance.RATING:
            valor = self.proveedor_datos.rating_actual(
                objetivo.id_atleta, "clasicas"
            )
            return float(valor or 0)
        if tipo == TipoIndicadorAvance.TAREAS:
            return self.proveedor_datos.tareas_completadas(
                objetivo.id_atleta, desde, hasta
            )
        if tipo == TipoIndicadorAvance.TORNEOS:
            return self.proveedor_datos.torneos_jugados(
                objetivo.id_atleta, desde, hasta
            )
        if tipo == TipoIndicadorAvance.MEDALLAS:
            return self.proveedor_datos.medallas_obtenidas(
                objetivo.id_atleta, desde, hasta
            )
        raise ErrorValidacion(f"Indicador de avance no soportado: {tipo}.")


@dataclass
class EvaluarEstadoObjetivo:
    """Determina EN_PROCESO, RETRASADO o FINALIZADO según fecha y porcentaje."""

    repositorio: RepositorioObjetivos

    def ejecutar(self, id_objetivo: str, hoy: Optional[date] = None) -> ObjetivoSmart:
        objetivo = self.repositorio.buscar_por_id(id_objetivo)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")
        if not objetivo.aprobado_por_entrenador:
            objetivo.estado = EstadoObjetivo.PENDIENTE_APROBACION
        elif objetivo.cumplido_por_entrenador or objetivo.porcentaje_avance >= 100:
            objetivo.estado = EstadoObjetivo.FINALIZADO
        else:
            objetivo.estado = self._evaluar_temporal(hoy or date.today(), objetivo)
        return self.repositorio.actualizar(objetivo)

    @staticmethod
    def _evaluar_temporal(hoy: date, objetivo: ObjetivoSmart) -> EstadoObjetivo:
        if objetivo.fecha_limite < hoy:
            return EstadoObjetivo.RETRASADO
        total_dias = max(
            1, (objetivo.fecha_limite - objetivo.fecha_inicio).days
        )
        transcurridos = max(0, (hoy - objetivo.fecha_inicio).days)
        porcentaje_esperado = (transcurridos / total_dias) * 100
        if objetivo.porcentaje_avance < porcentaje_esperado:
            return EstadoObjetivo.RETRASADO
        return EstadoObjetivo.EN_PROCESO


@dataclass
class ValidarCumplimientoObjetivo:
    """Solo el entrenador puede marcar un objetivo como cumplido."""

    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_objetivo: str,
        rol_usuario: Rol,
    ) -> ObjetivoSmart:
        if rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el entrenador puede validar el cumplimiento de objetivos."
            )
        objetivo = self.repositorio.buscar_por_id(id_objetivo)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")
        objetivo.cumplido_por_entrenador = True
        objetivo.estado = EstadoObjetivo.FINALIZADO
        return self.repositorio.actualizar(objetivo)


@dataclass
class ListarObjetivosPorAtleta:
    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_atleta: str,
        estado: Optional[EstadoObjetivo] = None,
    ) -> List[ObjetivoSmart]:
        objetivos = self.repositorio.buscar_por_atleta(id_atleta)
        if estado is not None:
            objetivos = [o for o in objetivos if o.estado == estado]
        return objetivos

