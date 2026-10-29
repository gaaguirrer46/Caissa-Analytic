"""Módulo de base de datos de infraestructura."""
from .conexion import obtener_conexion, transaccion
from .inicializador import inicializar_base_de_datos

__all__ = ["obtener_conexion", "transaccion", "inicializar_base_de_datos"]
