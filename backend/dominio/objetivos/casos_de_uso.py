"""Casos de uso (puertos primarios / driving) del módulo de Objetivos SMART."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from ..atletas.puertos import ResolutorAtletaUsuario
from ..auditoria.casos_de_uso import RegistrarCambio
from ..auditoria.entidades import TipoOperacion
from ..comun.acceso import Solicitante, exigir_entrenador
from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorAutenticacion,
    ErrorValidacion,
)
from ..comun.ids import nuevo_id_entero
from ..comun.validaciones import (
    convertir_enum,
    exigir_decimal,
    exigir_entero,
    exigir_fecha,
    exigir_texto,
)
from ..usuarios.entidades import Rol
from .entidades import (
    COLOR_POR_ESTADO,
    EstadoObjetivo,
    IndicadorAvance,
    ObjetivoSmart,
    TipoIndicadorAvance,
)
from .puertos import ProveedorDatosAvance, RepositorioObjetivos

_ROLES_PROPONENTES = (Rol.ENTRENADOR, Rol.ATLETA)

def _exigir_entrenador(rol_usuario: Rol, accion: str) -> None:
    """la aprobación y validación son exclusivas del entrenador."""
    if rol_usuario != Rol.ENTRENADOR:
        raise ErrorAutenticacion(
            f"Acceso denegado: sólo el entrenador puede {accion}."
        )

@dataclass
class CrearObjetivoSmart:
    """propone un objetivo pendiente de aprobación.

 Frecuencia: el objetivo se registra al inicio del ciclo con
 ``fecha_inicio``/``fecha_limite`` obligatorias y coherentes; las
 actualizaciones del ciclo (avance y validación de cumplimiento) quedan
 trazadas en la auditoría. La cadencia "inicio de ciclo" no es
 automatizable: el modelo oficial no tiene entidad de ciclo ni tabla
 de temporadas.
 """

    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_atleta: int,
        descripcion: str,
        indicador_meta: TipoIndicadorAvance | str,
        valor_meta: float,
        rating_actual: int,
        rating_meta: int,
        fecha_inicio: date,
        fecha_limite: date,
        rol_proponente: Rol | str,
    ) -> ObjetivoSmart:
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        descripcion_limpia = exigir_texto(descripcion, "descripción", max_longitud=300)
        indicador = convertir_enum(
            TipoIndicadorAvance, indicador_meta, "indicador_meta"
        )
        meta = exigir_decimal(valor_meta, "valor_meta", minimo=0.01)
        rating_inicial = exigir_entero(
            rating_actual, "rating_actual", minimo=0, maximo=4000
        )
        rating_final = exigir_entero(
            rating_meta, "rating_meta", minimo=0, maximo=4000
        )
        inicio = exigir_fecha(fecha_inicio, "fecha_inicio")
        limite = exigir_fecha(fecha_limite, "fecha_limite")
        if limite < inicio:
            raise ErrorValidacion("La fecha límite no puede ser anterior a la inicial.")
        proponente = convertir_enum(Rol, rol_proponente, "rol_proponente")
        if proponente not in _ROLES_PROPONENTES:
            raise ErrorValidacion("Solo el entrenador o el atleta pueden proponer.")
        if indicador == TipoIndicadorAvance.RATING and rating_final <= rating_inicial:
            raise ErrorValidacion(
                "Para objetivos de rating, el rating meta debe ser mayor al actual."
            )

        objetivo = ObjetivoSmart(
            id=nuevo_id_entero(),
            id_atleta=id_atleta,
            descripcion=descripcion_limpia,
            indicador_meta=indicador,
            valor_meta=meta,
            rating_actual=rating_inicial,
            rating_meta=rating_final,
            fecha_inicio=inicio,
            fecha_limite=limite,
            estado=EstadoObjetivo.PENDIENTE_APROBACION,
        )
        return self.repositorio.guardar(objetivo)

@dataclass
class ProponerObjetivoAtleta:
    """el atleta propone un objetivo para su propio expediente.

 La identidad autenticada llega como ``Solicitante`` (contrato del dominio):
 el id de usuario no se acepta como parámetro suelto, de modo que un atleta
 no puede proponer objetivos impersonando la cuenta de otro.
 """

    repositorio: RepositorioObjetivos
    resolutor: ResolutorAtletaUsuario

    def ejecutar(
        self,
        solicitante: Solicitante,
        descripcion: str,
        indicador_meta: TipoIndicadorAvance | str,
        valor_meta: float,
        rating_actual: int,
        rating_meta: int,
        fecha_inicio: date,
        fecha_limite: date,
    ) -> ObjetivoSmart:
        id_atleta = self.resolutor.atleta_de_usuario(solicitante.id_usuario)
        if id_atleta is None:
            raise EntidadNoEncontrada(
                "No existe un atleta vinculado a este usuario."
            )

        if solicitante.rol != Rol.ATLETA:
            raise ErrorAutenticacion(
                "Acceso denegado: sólo una cuenta con rol ATLETA puede "
                "proponer objetivos."
            )
        return CrearObjetivoSmart(self.repositorio).ejecutar(
            id_atleta=id_atleta,
            descripcion=descripcion,
            indicador_meta=indicador_meta,
            valor_meta=valor_meta,
            rating_actual=rating_actual,
            rating_meta=rating_meta,
            fecha_inicio=fecha_inicio,
            fecha_limite=fecha_limite,
            rol_proponente=Rol.ATLETA,
        )

@dataclass
class AprobarObjetivoSmart:
    """la aprobación obligatoria corresponde exclusivamente al entrenador."""

    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_objetivo: int,
        rol_usuario: Rol | str,
    ) -> ObjetivoSmart:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "aprobar objetivos")
        exigir_entero(id_objetivo, "id_objetivo", minimo=1)
        objetivo = self.repositorio.buscar_por_id(id_objetivo)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")
        if objetivo.estado == EstadoObjetivo.FINALIZADO:
            raise ErrorValidacion("Un objetivo finalizado no puede reabrirse.")
        if objetivo.aprobado_por_entrenador:
            return objetivo
        objetivo.aprobado_por_entrenador = True
        objetivo.estado = EstadoObjetivo.EN_PROCESO
        return self.repositorio.actualizar(objetivo)

@dataclass
class CalcularAvanceObjetivo:
    """calcula el porcentaje de avance con datos reales del atleta.

 Para objetivos de rating el avance es relativo a la línea base del objetivo
 (``rating_actual``) y no al rating absoluto, evitando que un objetivo recién
 creado aparezca cumplido al 97 %.
 """

    repositorio: RepositorioObjetivos
    proveedor_datos: ProveedorDatosAvance

    def ejecutar(self, id_objetivo: int) -> ObjetivoSmart:
        exigir_entero(id_objetivo, "id_objetivo", minimo=1)
        objetivo = self.repositorio.buscar_por_id(id_objetivo)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")

        valor_actual, valor_esperado = self._valores(objetivo)
        porcentaje = (
            min(100.0, max(0.0, (valor_actual / valor_esperado) * 100))
            if valor_esperado > 0
            else 0.0
        )
        objetivo.porcentaje_avance = porcentaje
        objetivo.avances = [
            IndicadorAvance(
                tipo=objetivo.indicador_meta,
                valor_actual=valor_actual,
                valor_esperado=valor_esperado,
            )
        ]
        return self.repositorio.actualizar(objetivo)

    def _valores(self, objetivo: ObjetivoSmart) -> tuple[float, float]:
        tipo = convertir_enum(
            TipoIndicadorAvance, objetivo.indicador_meta, "indicador_meta"
        )
        desde, hasta = objetivo.fecha_inicio, objetivo.fecha_limite
        if tipo == TipoIndicadorAvance.HORAS_ENTRENADAS:
            return (
                self.proveedor_datos.horas_entrenadas(
                    objetivo.id_atleta, desde, hasta
                ),
                objetivo.valor_meta,
            )
        if tipo == TipoIndicadorAvance.TAREAS:
            return (
                self.proveedor_datos.tareas_completadas(
                    objetivo.id_atleta, desde, hasta
                ),
                objetivo.valor_meta,
            )
        if tipo == TipoIndicadorAvance.TORNEOS:
            return (
                self.proveedor_datos.torneos_jugados(
                    objetivo.id_atleta, desde, hasta
                ),
                objetivo.valor_meta,
            )
        if tipo == TipoIndicadorAvance.MEDALLAS:
            return (
                self.proveedor_datos.medallas_obtenidas(
                    objetivo.id_atleta, desde, hasta
                ),
                objetivo.valor_meta,
            )
        if tipo == TipoIndicadorAvance.RATING:
            actual = self.proveedor_datos.rating_actual(
                objetivo.id_atleta, "clasicas"
            )
            base = float(objetivo.rating_actual)
            meta = float(objetivo.rating_meta)
            esperado = meta - base
            if esperado <= 0:
                raise ErrorValidacion(
                    "El objetivo de rating no define una meta superior a la línea base."
                )
            return (float(actual or 0) - base, esperado)
        raise ErrorValidacion(f"Indicador de avance no soportado: {tipo}.")

@dataclass
class EvaluarEstadoObjetivo:
    """determina el semáforo según fecha y porcentaje."""

    repositorio: RepositorioObjetivos

    def ejecutar(
        self, id_objetivo: int, hoy: Optional[date] = None
    ) -> ObjetivoSmart:
        exigir_entero(id_objetivo, "id_objetivo", minimo=1)
        fecha = hoy or date.today()
        exigir_fecha(fecha, "hoy")
        objetivo = self.repositorio.buscar_por_id(id_objetivo)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")
        objetivo.estado = self.calcular_estado(objetivo, fecha)
        return self.repositorio.actualizar(objetivo)

    @staticmethod
    def calcular_estado(objetivo: ObjetivoSmart, hoy: date) -> EstadoObjetivo:
        if not objetivo.aprobado_por_entrenador:
            return EstadoObjetivo.PENDIENTE_APROBACION
        if objetivo.cumplido_por_entrenador or objetivo.porcentaje_avance >= 100:
            return EstadoObjetivo.FINALIZADO
        return EvaluarEstadoObjetivo._evaluar_temporal(hoy, objetivo)

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
    """sólo el entrenador confirma el cumplimiento alcanzado.

el cambio de estado queda registrado en el historial de
 auditoría (anterior -> FINALIZADO).
 """

    repositorio: RepositorioObjetivos

    auditor: Optional[RegistrarCambio] = None

    def ejecutar(
        self,
        id_objetivo: int,
        rol_usuario: Rol | str,
        *,
        solicitante: Optional[Solicitante] = None,
    ) -> ObjetivoSmart:
        rol = convertir_enum(Rol, rol_usuario, "rol_usuario")
        _exigir_entrenador(rol, "validar el cumplimiento de objetivos")
        exigir_entero(id_objetivo, "id_objetivo", minimo=1)
        objetivo = self.repositorio.buscar_por_id(id_objetivo)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")
        if not objetivo.aprobado_por_entrenador:
            raise ErrorValidacion(
                "No se puede validar un objetivo que aún no ha sido aprobado."
            )
        if objetivo.cumplido_por_entrenador:

            return objetivo
        if objetivo.porcentaje_avance < 100:
            raise ErrorValidacion(
                "El objetivo no ha alcanzado el indicador establecido "
                f"(avance actual: {objetivo.porcentaje_avance:.2f}%)."
            )
        estado_previo = objetivo.estado
        objetivo.cumplido_por_entrenador = True
        objetivo.estado = EstadoObjetivo.FINALIZADO
        actualizado = self.repositorio.actualizar(objetivo)
        if self.auditor is not None:
            self.auditor.ejecutar(
                (
                    str(solicitante.id_usuario)
                    if solicitante is not None
                    else f"rol:{rol.value}"
                ),
                "ObjetivoSmart",
                TipoOperacion.MODIFICAR,
                "estado",
                estado_previo.value,
                EstadoObjetivo.FINALIZADO.value,
            )
        return actualizado

@dataclass
class ListarObjetivosPorAtleta:
    """objetivos de un atleta, opcionalmente filtrados por estado."""

    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_atleta: int,
        estado: Optional[EstadoObjetivo | str] = None,
        *,
        solicitante: Solicitante,
    ) -> List[ObjetivoSmart]:
        exigir_entrenador(solicitante, "consultar objetivos de un atleta")
        exigir_entero(id_atleta, "id_atleta", minimo=1)
        objetivos = self.repositorio.buscar_por_atleta(id_atleta)
        if estado is None:
            return objetivos
        estado_enum = convertir_enum(EstadoObjetivo, estado, "estado")
        return [o for o in objetivos if o.estado == estado_enum]

__all__ = [
    "AprobarObjetivoSmart",
    "CalcularAvanceObjetivo",
    "CrearObjetivoSmart",
    "EvaluarEstadoObjetivo",
    "ListarObjetivosPorAtleta",
    "ProponerObjetivoAtleta",
    "ValidarCumplimientoObjetivo",
    "COLOR_POR_ESTADO",
]
