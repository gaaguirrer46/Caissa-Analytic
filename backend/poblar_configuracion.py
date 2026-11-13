"""Script para inicializar la configuración oficial del sistema en caissa.db."""
import sqlite3
import json
from datetime import datetime, timezone

def poblar_configuracion():
    conn = sqlite3.connect("backend/caissa.db")
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS configuracion_sistema (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            maximo_atletas_por_entrenador INTEGER NOT NULL,
            minimo_entrenadores_por_atleta INTEGER NOT NULL,
            maximo_entrenadores_por_atleta INTEGER NOT NULL,
            permitir_autoevaluacion BOOLEAN NOT NULL,
            rangos_json TEXT NOT NULL DEFAULT '{}',
            secciones_invitado_json TEXT NOT NULL DEFAULT '[]',
            actualizado_por VARCHAR(100) NOT NULL,
            fecha_actualizacion TIMESTAMP NOT NULL
        );
        """
    )

    rangos_oficiales = {
        "ACCURACY": [92.0, 82.0, 70.0],
        "CUMPLIMIENTO_ENTRENAMIENTO": [90.0, 75.0, 60.0],
        "CUMPLIMIENTO_OBJETIVOS": [85.0, 70.0, 50.0],
        "ACPL": [20.0, 35.0, 50.0],
        "ASISTENCIA": [95.0, 85.0, 75.0],
        "RENDIMIENTO_POR_APERTURA": [70.0, 55.0, 45.0],
        "GESTION_DEL_TIEMPO": [85.0, 70.0, 55.0],
    }

    secciones_invitado = ["perfil_publico", "ranking", "resumen_equipo"]

    cur.execute(
        """
        INSERT INTO configuracion_sistema (
            id, maximo_atletas_por_entrenador, minimo_entrenadores_por_atleta,
            maximo_entrenadores_por_atleta, permitir_autoevaluacion,
            rangos_json, secciones_invitado_json, actualizado_por,
            fecha_actualizacion
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            maximo_atletas_por_entrenador = excluded.maximo_atletas_por_entrenador,
            minimo_entrenadores_por_atleta = excluded.minimo_entrenadores_por_atleta,
            maximo_entrenadores_por_atleta = excluded.maximo_entrenadores_por_atleta,
            permitir_autoevaluacion = excluded.permitir_autoevaluacion,
            rangos_json = excluded.rangos_json,
            secciones_invitado_json = excluded.secciones_invitado_json,
            actualizado_por = excluded.actualizado_por,
            fecha_actualizacion = excluded.fecha_actualizacion;
        """,
        (
            40,
            1,
            3,
            1,
            json.dumps(rangos_oficiales, ensure_ascii=False),
            json.dumps(secciones_invitado, ensure_ascii=False),
            "entrenador.magnus@caissa.org",
            datetime.now(timezone.utc).isoformat(),
        ),
    )

    conn.commit()
    print("Configuración del sistema inicializada y guardada exitosamente en caissa.db.")
    conn.close()

if __name__ == "__main__":
    poblar_configuracion()
