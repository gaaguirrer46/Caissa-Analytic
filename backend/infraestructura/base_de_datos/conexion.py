"""Gestor de conexión y transacciones a la base de datos SQLite."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent.parent
RUTA_BD_DEFECTO = RAIZ_PROYECTO / "caissa.db"

def obtener_conexion(
    ruta_bd: Optional[str | Path] = None,
    en_memoria: bool = False,
) -> sqlite3.Connection:
    """Crea y configura una conexión SQLite con foreign keys habilitadas."""
    if en_memoria:
        destino = ":memory:"
    else:
        destino = str(ruta_bd or os.environ.get("CAISSA_DB_PATH", str(RUTA_BD_DEFECTO)))

    conexion = sqlite3.connect(destino, timeout=15.0)
    conexion.row_factory = sqlite3.Row

    conexion.execute("PRAGMA foreign_keys = ON;")
    return conexion

@contextmanager
def transaccion(conexion: sqlite3.Connection) -> Generator[sqlite3.Connection, None, None]:
    """Context manager para ejecutar operaciones dentro de una transacción atómica."""
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
