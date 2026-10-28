"""Inicializador de la base de datos a partir del script DDL oficial."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

try:
    from .conexion import RUTA_BD_DEFECTO, obtener_conexion
except ImportError:
    from conexion import RUTA_BD_DEFECTO, obtener_conexion

RUTA_SCRIPT_SQL = Path(__file__).resolve().parent.parent.parent / "BD profesor.txt"

def leer_script_ddl(ruta_script: Optional[Path] = None) -> str:
    """Lee el archivo SQL oficial de la base de datos."""
    ruta = ruta_script or RUTA_SCRIPT_SQL
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el script DDL en: {ruta}")
    with open(ruta, "r", encoding="utf-8") as archivo:
        return archivo.read()

def inicializar_base_de_datos(
    ruta_bd: Optional[str | Path] = None,
    en_memoria: bool = False,
    ruta_script_sql: Optional[Path] = None,
    reiniciar: bool = False,
) -> sqlite3.Connection:
    """Crea la estructura de tablas e inserta los datos de prueba oficiales.

 Si reiniciar=True y se trata de un archivo físico, elimina el archivo previo antes de crear.
 """
    if reiniciar and not en_memoria:
        ruta = Path(ruta_bd or RUTA_BD_DEFECTO)
        if ruta.exists():
            ruta.unlink()

    conexion = obtener_conexion(ruta_bd=ruta_bd, en_memoria=en_memoria)
    script_sql = leer_script_ddl(ruta_script_sql)

    conexion.executescript(script_sql)

    conexion.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_usuarios_unico_entrenador "
        "ON usuarios(rol) WHERE rol = 'ENTRENADOR';"
    )

    conexion.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_planes_una_semana "
        "ON planes_entrenamiento(id_atleta, anio, semana);"
    )

    conexion.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_asistencia_unica "
        "ON asistencias(id_atleta, id_sesion);"
    )
    conexion.commit()
    return conexion

if __name__ == "__main__":
    print(f"Inicializando base de datos en: {RUTA_BD_DEFECTO}...")
    conn = inicializar_base_de_datos(reiniciar=True)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tablas = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
    print(f"¡Base de datos creada exitosamente con {len(tablas)} tablas!")
    for t in tablas:
        cursor.execute(f"SELECT COUNT(*) FROM {t};")
        print(f"  - {t}: {cursor.fetchone()[0]} registros")
    conn.close()
