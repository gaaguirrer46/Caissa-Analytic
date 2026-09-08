"""Adaptador Primario: Interfaz de Línea de Comandos (CLI) para Objetivos SMART.

Permite interactuar de forma amigable con el sistema para crear, listar y validar objetivos,
manejando excepciones de negocio para presentar mensajes limpios al usuario sin caídas abruptas.
"""
from __future__ import annotations

import os
import sqlite3
from datetime import date
from typing import Optional

from dominio.comun.errores import ErrorValidacion, EntidadNoEncontrada
from dominio.objetivos.casos_de_uso import (
    CrearObjetivoSmart,
    ModificarObjetivoSmart,
    ListarObjetivosPorAtleta,
)
from dominio.objetivos.entidades import TipoIndicadorAvance
from dominio.usuarios.entidades import Rol
from adaptadores.secundarios.persistencia.repositorio_objetivos_sqlite import (
    RepositorioObjetivosSQLite,
)


def obtener_conexion_bd() -> sqlite3.Connection:
    """Abre y configura una conexión activa a la base de datos SQLite oficial del sistema (caissa.db).
    
    Habilita las claves foráneas (PRAGMA foreign_keys = ON) para garantizar la integridad referencial.
    """
    ruta_db = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        "infraestructura",
        "base_de_datos",
        "caissa.db",
    )
    conn = sqlite3.connect(ruta_db)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


class CLIObjetivosSMART:
    """Controlador de consola que expone los casos de uso a la terminal."""

    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        """Inicializa el CLI instanciando el repositorio SQLite y los casos de uso."""
        self.conn = conn or obtener_conexion_bd()
        self.repo = RepositorioObjetivosSQLite(self.conn)
        self.caso_crear = CrearObjetivoSmart(self.repo)
        self.caso_modificar = ModificarObjetivoSmart(self.repo)
        self.caso_listar = ListarObjetivosPorAtleta(self.repo)

    def crear_objetivo(
        self,
        id_atleta: int = 1,
        titulo: str = "Nuevo Objetivo",
        descripcion: str = "Descripción del objetivo",
        fecha_inicio: str = "",
        fecha_limite: str = "",
        rating_actual: int = 2150,
        rating_meta: int = 2200,
        creado_por: str = "entrenador@caissa.org",
        **kwargs,
    ) -> Optional[ObjetivoSMART]:
        """Invoca el caso de uso CrearObjetivoSmart capturando y formateando errores de negocio.
        
        Args:
            id_atleta: ID del atleta.
            titulo: Título del objetivo.
            descripcion: Descripción detallada.
            fecha_inicio: Fecha de inicio ingresada.
            fecha_limite: Fecha límite ingresada.
            rating_actual: ELO actual (opcional, default 2150).
            rating_meta: ELO meta (opcional, default 2200).
            creado_por: Correo del usuario creador.
            
        Returns:
            ObjetivoSMART si fue creado con éxito; None si fue rechazado por validación.
        """
        # Soporte para firma posicional alternativa: (id_atleta, titulo, descripcion, r_act, r_meta, f_ini, f_lim)
        if isinstance(fecha_inicio, int) and (isinstance(rating_actual, str) or rating_actual is None):
            r_act_temp, r_meta_temp = fecha_inicio, fecha_limite
            f_ini_temp = rating_actual
            f_lim_temp = rating_meta
            rating_actual, rating_meta = r_act_temp, r_meta_temp
            fecha_inicio, fecha_limite = f_ini_temp, f_lim_temp

        print(f"\n [>] Intentando registrar objetivo: '{titulo}'...")
        try:
            nuevo = self.caso_crear.ejecutar(
                id_atleta=id_atleta,
                titulo=titulo,
                descripcion=descripcion,
                rating_actual=rating_actual,
                rating_meta=rating_meta,
                fecha_inicio=fecha_inicio,
                fecha_limite=fecha_limite,
                rol_proponente=Rol.ENTRENADOR,
                creado_por=creado_por,
            )
            print(f" [V] [EXITO] Objetivo #{nuevo.id} creado correctamente.")
            print(f"     * Rango de fechas : {nuevo.fecha_inicio} al {nuevo.fecha_limite}")
            print(f"     * Atleta ID       : {nuevo.id_atleta}")
            print(f"     * Calificación    : {nuevo.rating_actual} -> Meta: {nuevo.rating_meta}")
            return nuevo
        except ErrorValidacion as ev:
            print(f" [X] [RECHAZADO POR VALIDACION RF-03.3]: {ev}")
            return None
        except Exception as ex:
            print(f" [!] [ERROR DEL SISTEMA]: {ex}")
            return None

    def modificar_fechas(
        self,
        id_objetivo: int,
        nueva_fecha_inicio: Optional[str] = None,
        nueva_fecha_limite: Optional[str] = None,
    ) -> Optional[ObjetivoSMART]:
        """Modifica o prorroga las fechas de un objetivo aplicando validación RF-03.3.
        
        Args:
            id_objetivo: ID del objetivo a modificar.
            nueva_fecha_inicio: Nueva fecha de inicio (o None si no cambia).
            nueva_fecha_limite: Nueva fecha límite (o None si no cambia).
            
        Returns:
            ObjetivoSMART actualizado si la modificación fue válida; None si fue rechazada.
        """
        print(f"\n [>] Modificando fechas para objetivo #{id_objetivo}...")
        try:
            f_ini = nueva_fecha_inicio if (nueva_fecha_inicio and nueva_fecha_inicio.strip()) else None
            f_lim = nueva_fecha_limite if (nueva_fecha_limite and nueva_fecha_limite.strip()) else None

            actualizado = self.caso_modificar.ejecutar(
                id_objetivo=id_objetivo,
                fecha_inicio=f_ini,
                fecha_limite=f_lim,
            )
            print(f" [V] [EXITO] Objetivo #{actualizado.id} actualizado correctamente.")
            print(f"     * Nuevo rango de fechas: {actualizado.fecha_inicio} al {actualizado.fecha_limite}")
            return actualizado
        except EntidadNoEncontrada as ene:
            print(f" [X] [ERROR]: {ene}")
            return None
        except ErrorValidacion as ev:
            print(f" [X] [RECHAZADO POR VALIDACION RF-03.3]: {ev}")
            return None
        except Exception as ex:
            print(f" [!] [ERROR DEL SISTEMA]: {ex}")
            return None

    def buscar_objetivo(self, id_objetivo: int) -> Optional[ObjetivoSMART]:
        """Busca un objetivo por su ID."""
        return self.repo.buscar_por_id(id_objetivo)

    def eliminar_objetivo(self, id_objetivo: int) -> bool:
        """Elimina un objetivo por su ID (útil para limpieza tras pruebas)."""
        try:
            self.repo.eliminar(id_objetivo)
            return True
        except Exception:
            return False

    def listar_objetivos(self, id_atleta: int = 1) -> List[ObjetivoSMART]:
        """Consulta y muestra en una tabla formateada en consola los objetivos de un atleta.
        
        Args:
            id_atleta: ID del atleta a consultar (por defecto 1).
            
        Returns:
            Lista de objetivos recuperados.
        """
        print(f"\n==================== OBJETIVOS SMART (ATLETA #{id_atleta}) ====================")
        objetivos = self.caso_listar.ejecutar(id_atleta)
        if not objetivos:
            print("  (No hay objetivos registrados para este atleta)")
            print("=" * 75)
            return []

        print(f"{'ID':<5} | {'Título / Descripción':<26} | {'Inicio':<10} | {'Límite':<10} | {'Estado':<16}")
        print("-" * 75)
        for o in objetivos:
            texto = (o.titulo or o.descripcion or "Sin título")[:26]
            est = o.estado.value if hasattr(o.estado, "value") else str(o.estado)
            print(f"{str(o.id):<5} | {texto:<26} | {str(o.fecha_inicio):<10} | {str(o.fecha_limite):<10} | {est:<16}")
        print("-" * 75)
        print(f"Total registrados: {len(objetivos)} objetivo(s)")
        return objetivos
