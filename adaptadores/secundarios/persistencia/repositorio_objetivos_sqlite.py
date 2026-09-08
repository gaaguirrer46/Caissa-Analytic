"""Repositorio SQLite para Objetivos SMART (RF-03).

Implementa el adaptador secundario de persistencia, traduciendo las operaciones
del dominio a instrucciones SQLite mediante transacciones seguras y mapeo relacional.
"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime
from typing import List, Optional, Union

from dominio.comun.errores import EntidadNoEncontrada, ErrorValidacion
from dominio.objetivos.entidades import (
    EstadoObjetivo,
    ObjetivoSMART,
    TipoIndicadorAvance,
)
from dominio.objetivos.puertos import RepositorioObjetivos
from dominio.objetivos.validador import ObjetivoSMARTValidator


class RepositorioObjetivosSQLite(RepositorioObjetivos):
    """Adaptador secundario de persistencia en SQLite para Objetivos SMART.
    
    Características clave:
    - Compatible tanto con el esquema canónico oficial ('BD profesor.txt', PK 'id')
      como con esquemas extendidos (PK 'id_objetivo', columnas de auditoría).
    - Inspecciona dinámicamente la estructura de la tabla para prevenir errores de columnas inexistentes.
    - Captura violaciones de CHECK constraints y NOT NULL a nivel de motor de base de datos
      y las transforma en excepciones de negocio comprensibles (ErrorValidacion).
    """

    def __init__(self, conexion: sqlite3.Connection):
        """Inicializa el repositorio configurando la conexión y el formato de filas."""
        self.conn = conexion
        self.conn.row_factory = sqlite3.Row
        self._detectar_columnas()

    def _detectar_columnas(self):
        """Inspecciona la tabla 'objetivos_smart' para autoconfigurar el mapeo de columnas."""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(objetivos_smart)")
        columnas = [fila[1] for fila in cursor.fetchall()]
        self.columnas = columnas
        # Determinar si la clave primaria es 'id_objetivo' o 'id' (oficial del profesor)
        self.pk_col = "id_objetivo" if "id_objetivo" in columnas else "id"
        self.tiene_titulo = "titulo" in columnas
        self.tiene_creado_por = "creado_por" in columnas
        self.tiene_fecha_registro = "fecha_registro" in columnas

    def _mapear_fila(self, fila: sqlite3.Row) -> ObjetivoSMART:
        """Convierte una fila cruda de SQLite en una instancia rica de ObjetivoSMART.
        
        Args:
            fila: Objeto sqlite3.Row con los datos de la base de datos.
            
        Returns:
            Instancia reconstruida de ObjetivoSMART.
        """
        keys = fila.keys()
        id_obj = fila[self.pk_col] if self.pk_col in keys else (fila["id_objetivo"] if "id_objetivo" in keys else fila["id"])
        
        # Parseo seguro de fechas a objetos date estándar
        f_inicio = ObjetivoSMARTValidator.parsear_fecha(fila["fecha_inicio"], "fecha de inicio")
        f_limite = ObjetivoSMARTValidator.parsear_fecha(fila["fecha_limite"], "fecha límite")

        titulo = fila["titulo"] if "titulo" in keys and fila["titulo"] is not None else ""
        creado_por = fila["creado_por"] if "creado_por" in keys else None
        fecha_reg = fila["fecha_registro"] if "fecha_registro" in keys else None

        # Deserialización de enums
        indicador_raw = fila["indicador_meta"] if "indicador_meta" in keys and fila["indicador_meta"] else "RATING"
        try:
            indicador_meta = TipoIndicadorAvance(indicador_raw)
        except ValueError:
            indicador_meta = TipoIndicadorAvance.RATING

        estado_raw = fila["estado"] if "estado" in keys and fila["estado"] else "PENDIENTE_APROBACION"
        try:
            estado = EstadoObjetivo(estado_raw)
        except ValueError:
            estado = EstadoObjetivo.PENDIENTE_APROBACION

        valor_meta = float(fila["valor_meta"]) if "valor_meta" in keys and fila["valor_meta"] is not None else 0.0
        porcentaje_avance = float(fila["porcentaje_avance"]) if "porcentaje_avance" in keys and fila["porcentaje_avance"] is not None else 0.0
        aprobado = bool(fila["aprobado_por_entrenador"]) if "aprobado_por_entrenador" in keys else False
        cumplido = bool(fila["cumplido_por_entrenador"]) if "cumplido_por_entrenador" in keys else False
        r_actual = int(fila["rating_actual"]) if "rating_actual" in keys and fila["rating_actual"] is not None else 0
        r_meta = int(fila["rating_meta"]) if "rating_meta" in keys and fila["rating_meta"] is not None else 0

        return ObjetivoSMART(
            id=id_obj,
            id_objetivo=id_obj,
            id_atleta=fila["id_atleta"],
            titulo=titulo,
            descripcion=fila["descripcion"],
            indicador_meta=indicador_meta,
            valor_meta=valor_meta,
            rating_actual=r_actual,
            rating_meta=r_meta,
            fecha_inicio=f_inicio,
            fecha_limite=f_limite,
            porcentaje_avance=porcentaje_avance,
            estado=estado,
            aprobado_por_entrenador=aprobado,
            cumplido_por_entrenador=cumplido,
            creado_por=creado_por,
            fecha_registro=fecha_reg,
        )

    def guardar(self, objetivo: ObjetivoSMART) -> ObjetivoSMART:
        """Inserta un nuevo objetivo en la base de datos previa validación temporal (RF-03.3).
        
        Args:
            objetivo: Objeto ObjetivoSMART a insertar.
            
        Returns:
            ObjetivoSMART con el identificador autogenerado asignado.
            
        Raises:
            ErrorValidacion: Si falta fecha_inicio, fecha_limite o si fecha_limite < fecha_inicio.
        """
        # 1. Validación de fechas obligatorias antes del INSERT (RF-03.3)
        validado = ObjetivoSMARTValidator.validar(
            fecha_inicio=objetivo.fecha_inicio,
            fecha_limite=objetivo.fecha_limite,
            descripcion=objetivo.descripcion,
            titulo=objetivo.titulo,
        )

        cursor = self.conn.cursor()
        cols = [
            "id_atleta", "descripcion", "rating_actual", "rating_meta",
            "fecha_inicio", "fecha_limite", "porcentaje_avance", "estado",
            "indicador_meta", "valor_meta", "aprobado_por_entrenador", "cumplido_por_entrenador"
        ]
        vals = [
            objetivo.id_atleta,
            validado["descripcion"],
            objetivo.rating_actual,
            objetivo.rating_meta,
            validado["fecha_inicio"].isoformat(),
            validado["fecha_limite"].isoformat(),
            objetivo.porcentaje_avance,
            objetivo.estado.value if hasattr(objetivo.estado, "value") else str(objetivo.estado),
            objetivo.indicador_meta.value if hasattr(objetivo.indicador_meta, "value") else str(objetivo.indicador_meta),
            objetivo.valor_meta,
            1 if objetivo.aprobado_por_entrenador else 0,
            1 if objetivo.cumplido_por_entrenador else 0,
        ]

        if self.tiene_titulo:
            cols.append("titulo")
            vals.append(validado["titulo"])
        if self.tiene_creado_por:
            cols.append("creado_por")
            vals.append(objetivo.creado_por)

        placeholders = ", ".join(["?"] * len(cols))
        query = f"INSERT INTO objetivos_smart ({', '.join(cols)}) VALUES ({placeholders})"

        try:
            cursor.execute(query, tuple(vals))
            self.conn.commit()
            nuevo_id = cursor.lastrowid
            objetivo.id = nuevo_id
            objetivo.id_objetivo = nuevo_id
            return objetivo
        except sqlite3.IntegrityError as e:
            msg = str(e).lower()
            if "chk_fechasvalidas" in msg or ("check constraint failed" in msg and "fecha" in msg):
                raise ErrorValidacion("La fecha límite no puede ser anterior a la fecha de inicio.")
            if "not null" in msg and "fecha_inicio" in msg:
                raise ErrorValidacion("La fecha de inicio es estrictamente obligatoria.")
            if "not null" in msg and "fecha_limite" in msg:
                raise ErrorValidacion("La fecha límite es estrictamente obligatoria.")
            raise ErrorValidacion(f"Error de integridad en la base de datos: {e}")

    def actualizar(self, objetivo: ObjetivoSMART) -> ObjetivoSMART:
        """Actualiza un objetivo existente revalidando que las nuevas fechas cumplan RF-03.3.
        
        Args:
            objetivo: Objeto ObjetivoSMART modificado.
            
        Returns:
            ObjetivoSMART actualizado en la base de datos.
            
        Raises:
            EntidadNoEncontrada: Si el registro no existe en la base de datos.
            ErrorValidacion: Si las fechas violan las reglas temporales.
        """
        id_target = objetivo.id_objetivo or objetivo.id
        if id_target is None:
            raise ErrorValidacion("No se puede actualizar un objetivo sin identificador.")

        # Validación temporal preventiva (RF-03.3)
        validado = ObjetivoSMARTValidator.validar(
            fecha_inicio=objetivo.fecha_inicio,
            fecha_limite=objetivo.fecha_limite,
            descripcion=objetivo.descripcion,
            titulo=objetivo.titulo,
        )

        sets = [
            "descripcion = ?", "rating_actual = ?", "rating_meta = ?",
            "fecha_inicio = ?", "fecha_limite = ?", "porcentaje_avance = ?",
            "estado = ?", "indicador_meta = ?", "valor_meta = ?",
            "aprobado_por_entrenador = ?", "cumplido_por_entrenador = ?"
        ]
        vals = [
            validado["descripcion"],
            objetivo.rating_actual,
            objetivo.rating_meta,
            validado["fecha_inicio"].isoformat(),
            validado["fecha_limite"].isoformat(),
            objetivo.porcentaje_avance,
            objetivo.estado.value if hasattr(objetivo.estado, "value") else str(objetivo.estado),
            objetivo.indicador_meta.value if hasattr(objetivo.indicador_meta, "value") else str(objetivo.indicador_meta),
            objetivo.valor_meta,
            1 if objetivo.aprobado_por_entrenador else 0,
            1 if objetivo.cumplido_por_entrenador else 0,
        ]

        if self.tiene_titulo:
            sets.append("titulo = ?")
            vals.append(validado["titulo"])

        vals.append(id_target)
        query = f"UPDATE objetivos_smart SET {', '.join(sets)} WHERE {self.pk_col} = ?"

        cursor = self.conn.cursor()
        try:
            cursor.execute(query, tuple(vals))
            self.conn.commit()
            if cursor.rowcount == 0:
                raise EntidadNoEncontrada(f"No se encontró el objetivo con id {id_target}.")
            return objetivo
        except sqlite3.IntegrityError as e:
            msg = str(e).lower()
            if "chk_fechasvalidas" in msg or ("check constraint failed" in msg and "fecha" in msg):
                raise ErrorValidacion("La fecha límite no puede ser anterior a la fecha de inicio.")
            if "not null" in msg and "fecha_inicio" in msg:
                raise ErrorValidacion("La fecha de inicio es estrictamente obligatoria.")
            if "not null" in msg and "fecha_limite" in msg:
                raise ErrorValidacion("La fecha límite es estrictamente obligatoria.")
            raise ErrorValidacion(f"Error de integridad en la base de datos: {e}")

    def buscar_por_id(self, id_objetivo: Union[int, str]) -> Optional[ObjetivoSMART]:
        """Recupera un objetivo por su identificador primario numérico."""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM objetivos_smart WHERE {self.pk_col} = ?", (id_objetivo,))
        fila = cursor.fetchone()
        if not fila:
            return None
        return self._mapear_fila(fila)

    def buscar_por_atleta(self, id_atleta: Union[int, str]) -> List[ObjetivoSMART]:
        """Recupera todos los objetivos asignados a un atleta ordenados por fecha de inicio descendente."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM objetivos_smart WHERE id_atleta = ? ORDER BY fecha_inicio DESC", (id_atleta,))
        filas = cursor.fetchall()
        return [self._mapear_fila(f) for f in filas]

    def listar_por_estado(self, estado: EstadoObjetivo) -> List[ObjetivoSMART]:
        """Lista objetivos filtrando por estado de su ciclo de vida."""
        val = estado.value if hasattr(estado, "value") else str(estado)
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM objetivos_smart WHERE estado = ? ORDER BY fecha_limite ASC", (val,))
        filas = cursor.fetchall()
        return [self._mapear_fila(f) for f in filas]

    def eliminar(self, id_objetivo: Union[int, str]) -> None:
        """Elimina un objetivo de la base de datos por su identificador."""
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM objetivos_smart WHERE {self.pk_col} = ?", (id_objetivo,))
        self.conn.commit()
