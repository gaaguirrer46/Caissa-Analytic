"""
Script de inicialización de la base de datos SQLite para Caissa Analytics.
Crea las tablas, índices y datos semilla a partir de schema.sql.
"""
import os
import sqlite3

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_SCHEMA = os.path.join(DIR_ACTUAL, "schema.sql")
RUTA_DB = os.path.join(DIR_ACTUAL, "caissa.db")

def inicializar_base_datos():
    print(f"Leyendo esquema desde: {RUTA_SCHEMA}")
    with open(RUTA_SCHEMA, "r", encoding="utf-8") as f:
        sql_script = f.read()

    print(f"Creando base de datos en: {RUTA_DB}")
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()
    
    cursor.executescript(sql_script)
    conn.commit()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    tablas = cursor.fetchall()
    print(f"Tablas creadas ({len(tablas)}):")
    for (tabla,) in tablas:
        print(f"  - {tabla}")
        
    conn.close()
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    inicializar_base_datos()
