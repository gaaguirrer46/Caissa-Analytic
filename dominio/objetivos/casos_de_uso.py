"""Casos de uso (puertos primarios / driving) del módulo de Objetivos SMART.

Este módulo implementa la lógica de aplicación para la gestión de objetivos,
orquestando las entidades del dominio, las reglas de validación y los puertos de persistencia.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Union

from ..comun.errores import (
    EntidadNoEncontrada,
    ErrorValidacion,
)
from ..comun.ids import nuevo_id_entero
from ..usuarios.entidades import Rol
from .entidades import (
    EstadoObjetivo,
    ObjetivoSMART,
    ObjetivoSmart,
    TipoIndicadorAvance,
)
from .puertos import ProveedorDatosAvance, RepositorioObjetivos
from .validador import ObjetivoSMARTValidator


@dataclass
class CrearObjetivoSmart:
    """Caso de uso: Crear un nuevo Objetivo SMART en el sistema.
    
    Aplica de manera estricta las reglas de negocio del requerimiento RF-03.3:
    - Exige fecha de inicio obligatoria.
    - Exige fecha límite obligatoria.
    - Exige que fecha_limite >= fecha_inicio.
    """
    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_atleta: Union[int, str],
        descripcion: str,
        indicador_meta: TipoIndicadorAvance = TipoIndicadorAvance.RATING,
        valor_meta: float = 0.0,
        rating_actual: Optional[int] = None,
        rating_meta: Optional[int] = None,
        fecha_inicio: Union[date, datetime, str, None] = None,
        fecha_limite: Union[date, datetime, str, None] = None,
        rol_proponente: Rol = Rol.ENTRENADOR,
        titulo: str = "",
        creado_por: Optional[str] = None,
    ) -> ObjetivoSMART:
        """Ejecuta la creación del objetivo tras validar las fechas obligatorias (RF-03.3).
        
        Args:
            id_atleta: Identificador del atleta destinatario del objetivo.
            descripcion: Texto descriptivo del objetivo.
            indicador_meta: Tipo de métrica SMART.
            valor_meta: Cuantía esperada.
            rating_actual: Elo actual.
            rating_meta: Elo esperado.
            fecha_inicio: Fecha obligatoria de inicio.
            fecha_limite: Fecha obligatoria de término.
            rol_proponente: Rol proponente (Entrenador o Atleta).
            titulo: Título corto descriptivo.
            creado_por: Identificador/correo del creador.
            
        Returns:
            ObjetivoSMART creado y persistido.
            
        Raises:
            ErrorValidacion: Si falta fecha_inicio, fecha_limite o si están invertidas.
        """
        if not descripcion or not descripcion.strip():
            raise ErrorValidacion("La descripción del objetivo es obligatoria.")

        # 1. Validación estricta y exclusiva de fechas obligatorias (RF-03.3)
        d_inicio, d_limite = ObjetivoSMARTValidator.validar_fechas(fecha_inicio, fecha_limite)

        if valor_meta < 0:
            raise ErrorValidacion("El valor meta no puede ser negativo.")
        if rol_proponente not in (Rol.ENTRENADOR, Rol.ATLETA):
            raise ErrorValidacion("Solo el entrenador o el atleta pueden proponer.")

        # 2. Conversión segura a entero de id_atleta
        try:
            atleta_id_num = int(id_atleta)
        except (ValueError, TypeError):
            atleta_id_num = id_atleta

        # 3. Construcción y persistencia de la entidad
        objetivo = ObjetivoSMART(
            id=nuevo_id_entero(),
            id_atleta=atleta_id_num,
            titulo=titulo.strip() if titulo else "",
            descripcion=descripcion.strip(),
            indicador_meta=indicador_meta,
            valor_meta=valor_meta,
            rating_actual=int(rating_actual) if rating_actual is not None else 0,
            rating_meta=int(rating_meta) if rating_meta is not None else 0,
            fecha_inicio=d_inicio,
            fecha_limite=d_limite,
            creado_por=creado_por,
        )
        return self.repositorio.guardar(objetivo)


@dataclass
class ModificarObjetivoSmart:
    """Caso de uso: Modificar atributos de un Objetivo SMART existente.
    
    Permite prorrogar fechas garantizando que ninguna actualización
    deje fechas nulas o cree incoherencias temporales (RF-03.3).
    """
    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_objetivo: Union[int, str],
        descripcion: Optional[str] = None,
        fecha_inicio: Union[date, datetime, str, None] = None,
        fecha_limite: Union[date, datetime, str, None] = None,
        rating_actual: Optional[int] = None,
        rating_meta: Optional[int] = None,
        titulo: Optional[str] = None,
    ) -> ObjetivoSMART:
        """Actualiza un objetivo verificando el cumplimiento estricto de fechas (RF-03.3).
        
        Args:
            id_objetivo: Identificador del objetivo a actualizar.
            descripcion: Nueva descripción (opcional).
            fecha_inicio: Nueva fecha de inicio (opcional).
            fecha_limite: Nueva fecha límite (opcional).
            rating_actual: Nuevo rating actual (opcional).
            rating_meta: Nuevo rating meta (opcional).
            titulo: Nuevo título (opcional).
            
        Returns:
            ObjetivoSMART con los cambios aplicados y persistidos.
            
        Raises:
            EntidadNoEncontrada: Si el ID no existe en la base de datos.
            ErrorValidacion: Si las fechas resultantes violan RF-03.3.
        """
        try:
            obj_id_num = int(id_objetivo)
        except (ValueError, TypeError):
            obj_id_num = id_objetivo

        objetivo = self.repositorio.buscar_por_id(obj_id_num)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")

        # Determinar valores combinados
        nueva_f_inicio = fecha_inicio if fecha_inicio is not None else objetivo.fecha_inicio
        nueva_f_limite = fecha_limite if fecha_limite is not None else objetivo.fecha_limite

        # Validación estricta de fechas resultantes (RF-03.3)
        d_inicio, d_limite = ObjetivoSMARTValidator.validar_fechas(nueva_f_inicio, nueva_f_limite)

        if descripcion is not None:
            if not descripcion.strip():
                raise ErrorValidacion("La descripción del objetivo es obligatoria.")
            objetivo.descripcion = descripcion.strip()

        if titulo is not None:
            objetivo.titulo = titulo.strip()

        if rating_actual is not None:
            objetivo.rating_actual = int(rating_actual)
        if rating_meta is not None:
            objetivo.rating_meta = int(rating_meta)

        objetivo.fecha_inicio = d_inicio
        objetivo.fecha_limite = d_limite

        return self.repositorio.actualizar(objetivo)


@dataclass
class AprobarObjetivoSmart:
    """Caso de uso: Aprobación formal de un objetivo por el entrenador."""
    repositorio: RepositorioObjetivos

    def ejecutar(self, id_objetivo: Union[int, str]) -> ObjetivoSmart:
        """Cambia el estado de PENDIENTE_APROBACION a EN_PROCESO."""
        try:
            obj_id_num = int(id_objetivo)
        except (ValueError, TypeError):
            obj_id_num = id_objetivo

        objetivo = self.repositorio.buscar_por_id(obj_id_num)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")
        objetivo.aprobado_por_entrenador = True
        objetivo.estado = EstadoObjetivo.EN_PROCESO
        return self.repositorio.actualizar(objetivo)


@dataclass
class CalcularAvanceObjetivo:
    """Caso de uso: Calcular el porcentaje cuantitativo de avance hacia la meta."""
    repositorio: RepositorioObjetivos
    proveedor_datos: ProveedorDatosAvance

    def ejecutar(self, id_objetivo: Union[int, str]) -> ObjetivoSmart:
        """Calcula el progreso numérico contra el proveedor de datos."""
        try:
            obj_id_num = int(id_objetivo)
        except (ValueError, TypeError):
            obj_id_num = id_objetivo

        objetivo = self.repositorio.buscar_por_id(obj_id_num)
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
        """Consulta el valor real alcanzado en el periodo temporal definido."""
        tipo = objetivo.indicador_meta
        atleta_id = int(objetivo.id_atleta) if isinstance(objetivo.id_atleta, int) or str(objetivo.id_atleta).isdigit() else objetivo.id_atleta
        if tipo == TipoIndicadorAvance.HORAS_ENTRENADAS:
            return self.proveedor_datos.horas_entrenadas(atleta_id, desde, hasta)
        if tipo == TipoIndicadorAvance.RATING:
            valor = self.proveedor_datos.rating_actual(atleta_id, "clasicas")
            return float(valor or 0)
        if tipo == TipoIndicadorAvance.TAREAS:
            return self.proveedor_datos.tareas_completadas(atleta_id, desde, hasta)
        if tipo == TipoIndicadorAvance.TORNEOS:
            return self.proveedor_datos.torneos_jugados(atleta_id, desde, hasta)
        if tipo == TipoIndicadorAvance.MEDALLAS:
            return self.proveedor_datos.medallas_obtenidas(atleta_id, desde, hasta)
        raise ErrorValidacion(f"Indicador de avance no soportado: {tipo}.")


@dataclass
class EvaluarEstadoObjetivo:
    """Caso de uso: Determina EN_PROCESO, RETRASADO o FINALIZADO según fechas y avance."""
    repositorio: RepositorioObjetivos

    def ejecutar(self, id_objetivo: Union[int, str], hoy: Optional[date] = None) -> ObjetivoSmart:
        """Evalúa el estado temporal comparando el avance esperado vs avance real."""
        try:
            obj_id_num = int(id_objetivo)
        except (ValueError, TypeError):
            obj_id_num = id_objetivo

        objetivo = self.repositorio.buscar_por_id(obj_id_num)
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
        """Determina si el objetivo está en tiempo o atrasado comparando la fecha límite obligatoria."""
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
    """Caso de uso: Cierre y certificación de cumplimiento de un objetivo."""
    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_objetivo: Union[int, str],
        rol_usuario: Rol,
    ) -> ObjetivoSmart:
        """Marca formalmente como cumplido el objetivo (operación exclusiva de ENTRENADOR)."""
        if rol_usuario != Rol.ENTRENADOR:
            raise ErrorValidacion(
                "Solo el entrenador puede validar el cumplimiento de objetivos."
            )
        try:
            obj_id_num = int(id_objetivo)
        except (ValueError, TypeError):
            obj_id_num = id_objetivo

        objetivo = self.repositorio.buscar_por_id(obj_id_num)
        if objetivo is None:
            raise EntidadNoEncontrada("Objetivo no encontrado.")
        objetivo.cumplido_por_entrenador = True
        objetivo.estado = EstadoObjetivo.FINALIZADO
        return self.repositorio.actualizar(objetivo)


@dataclass
class ListarObjetivosPorAtleta:
    """Caso de uso: Consulta y filtrado de objetivos de un atleta."""
    repositorio: RepositorioObjetivos

    def ejecutar(
        self,
        id_atleta: Union[int, str],
        estado: Optional[EstadoObjetivo] = None,
    ) -> List[ObjetivoSmart]:
        """Obtiene la lista de objetivos asociados al atleta, filtrados opcionalmente por estado."""
        try:
            atleta_id_num = int(id_atleta)
        except (ValueError, TypeError):
            atleta_id_num = id_atleta

        objetivos = self.repositorio.buscar_por_atleta(atleta_id_num)
        if estado is not None:
            objetivos = [o for o in objetivos if o.estado == estado]
        return objetivos
