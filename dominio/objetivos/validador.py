"""Validador de reglas de negocio para Objetivos SMART (RF-03).

Este módulo concentra exclusivamente la lógica pura de validación temporal,
garantizando la integridad y obligatoriedad de fechas según el requerimiento RF-03.3.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional, Tuple, Union

from ..comun.errores import ErrorValidacion


class ObjetivoSMARTValidator:
    """Validador estricto de negocio para la temporalidad de Objetivos SMART (RF-03.3).
    
    Aplica el principio de diseño defensivo: exige la presencia obligatoria y la
    coherencia cronológica de la fecha de inicio y la fecha límite.
    """

    @classmethod
    def parsear_fecha(cls, valor: Any, nombre_campo: str) -> date:
        """Convierte y valida un valor recibido como un objeto de tipo datetime.date.
        
        Soporta:
        - None / cadenas vacías: Rechazados de inmediato con ErrorValidacion.
        - Cadenas de texto: Se intentan parsear en formato ISO (YYYY-MM-DD).
        - Objetos datetime: Se extrae exclusivamente la componente .date().
        - Objetos date nativos: Se devuelven tal cual.
        
        Args:
            valor: Dato de entrada a convertir (str, datetime, date, None).
            nombre_campo: Nombre legible para el mensaje de error (ej: 'fecha de inicio').
            
        Returns:
            Objeto date validado y normalizado.
            
        Raises:
            ErrorValidacion: Si el valor es nulo, vacío o tiene un formato no válido.
        """
        # Paso 1: Comprobar nulidad
        if valor is None:
            raise ErrorValidacion(f"La {nombre_campo} es estrictamente obligatoria.")
        
        # Paso 2: Si es cadena de texto, limpiar espacios y parsear
        if isinstance(valor, str):
            texto = valor.strip()
            # Cadena vacía o sólo espacios se considera ausencia del dato
            if not texto:
                raise ErrorValidacion(f"La {nombre_campo} es estrictamente obligatoria.")
            try:
                # Formato ISO estándar 'YYYY-MM-DD'
                return date.fromisoformat(texto)
            except ValueError:
                try:
                    # Alternativa strptime
                    return datetime.strptime(texto, "%Y-%m-%d").date()
                except ValueError:
                    raise ErrorValidacion(f"Formato de {nombre_campo} inválido. Se espera YYYY-MM-DD.")
        
        # Paso 3: Si es datetime, obtener solo la fecha (descartar horas/minutos)
        if isinstance(valor, datetime):
            return valor.date()
        
        # Paso 4: Si ya es un objeto date nativo de Python, retornarlo directamente
        if isinstance(valor, date):
            return valor
        
        # Cualquier otro tipo no soportado dispara error
        raise ErrorValidacion(f"La {nombre_campo} es estrictamente obligatoria.")

    @classmethod
    def validar_fechas(
        cls,
        fecha_inicio: Union[date, datetime, str, None],
        fecha_limite: Union[date, datetime, str, None]
    ) -> Tuple[date, date]:
        """Aplica las reglas obligatorias de validación temporal del requerimiento RF-03.3.
        
        Reglas evaluadas:
        a) Rechazar si fecha_inicio es None o vacía ->
           'La fecha de inicio es estrictamente obligatoria.'
        b) Rechazar si fecha_limite es None o vacía ->
           'La fecha límite es estrictamente obligatoria.'
        c) Rechazar si date(fecha_limite) < date(fecha_inicio) ->
           'La fecha límite no puede ser anterior a la fecha de inicio.'
           
        Args:
            fecha_inicio: Fecha inicial del periodo de entrenamiento/objetivo.
            fecha_limite: Fecha máxima para el cumplimiento del objetivo.
            
        Returns:
            Tupla con (fecha_inicio, fecha_limite) convertidas a objetos date.
            
        Raises:
            ErrorValidacion: Ante el incumplimiento de cualquiera de las tres reglas.
        """
        # Evaluación de la Regla a): Obligatoriedad estricta de fecha_inicio
        if fecha_inicio is None or (isinstance(fecha_inicio, str) and not fecha_inicio.strip()):
            raise ErrorValidacion("La fecha de inicio es estrictamente obligatoria.")

        # Evaluación de la Regla b): Obligatoriedad estricta de fecha_limite
        if fecha_limite is None or (isinstance(fecha_limite, str) and not fecha_limite.strip()):
            raise ErrorValidacion("La fecha límite es estrictamente obligatoria.")

        # Parsear y normalizar ambos valores a objetos date canónicos
        d_inicio = cls.parsear_fecha(fecha_inicio, "fecha de inicio")
        d_limite = cls.parsear_fecha(fecha_limite, "fecha límite")

        # Evaluación de la Regla c): Coherencia cronológica (límite no puede ser previa a inicio)
        if d_limite < d_inicio:
            raise ErrorValidacion("La fecha límite no puede ser anterior a la fecha de inicio.")

        return d_inicio, d_limite

    @classmethod
    def validar(
        cls,
        fecha_inicio: Union[date, datetime, str, None],
        fecha_limite: Union[date, datetime, str, None],
        descripcion: Optional[str] = None,
        titulo: Optional[str] = None,
    ) -> dict[str, Any]:
        """Método fachada que ejecuta las validaciones temporales previas a la persistencia.
        
        Returns:
            Diccionario con fecha_inicio y fecha_limite validadas y strings saneados.
        """
        # Validar fechas obligatorias (RF-03.3)
        d_inicio, d_limite = cls.validar_fechas(fecha_inicio, fecha_limite)

        # Validar presencia de texto en la descripción si se proporciona
        if descripcion is not None and not descripcion.strip():
            raise ErrorValidacion("La descripción del objetivo es obligatoria.")

        return {
            "fecha_inicio": d_inicio,
            "fecha_limite": d_limite,
            "descripcion": descripcion.strip() if descripcion else "",
            "titulo": titulo.strip() if titulo else "",
        }
