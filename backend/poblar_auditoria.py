"""Script para poblar registros de auditoría y trazabilidad en caissa.db."""
import sqlite3
from datetime import datetime, timezone, timedelta

def poblar_auditoria():
    conn = sqlite3.connect("backend/caissa.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM registros_auditoria")

    ahora = datetime.now(timezone.utc)

    registros = [
        {
            "usuario": "entrenador.magnus@caissa.org",
            "fecha_hora": (ahora - timedelta(days=12, hours=3)).isoformat(),
            "entidad_afectada": "Atleta",
            "tipo_operacion": "MODIFICAR",
            "campo_modificado": "rating_clasicas",
            "valor_anterior": "2140",
            "valor_nuevo": "2150",
        },
        {
            "usuario": "entrenador.magnus@caissa.org",
            "fecha_hora": (ahora - timedelta(days=10, hours=5)).isoformat(),
            "entidad_afectada": "ObjetivoSmart",
            "tipo_operacion": "CREAR",
            "campo_modificado": "descripcion",
            "valor_anterior": None,
            "valor_nuevo": "Superar los 2200 de ELO FIDE en ritmo clásico antes de finalizar el ciclo 2026-I",
        },
        {
            "usuario": "entrenador.magnus@caissa.org",
            "fecha_hora": (ahora - timedelta(days=9, hours=2)).isoformat(),
            "entidad_afectada": "PlanEntrenamientoSemanal",
            "tipo_operacion": "MODIFICAR",
            "campo_modificado": "ejecucion_aprobada",
            "valor_anterior": "False",
            "valor_nuevo": "True",
        },
        {
            "usuario": "atleta.kasparov@caissa.org",
            "fecha_hora": (ahora - timedelta(days=8, hours=6)).isoformat(),
            "entidad_afectada": "SesionEntrenamiento",
            "tipo_operacion": "MODIFICAR",
            "campo_modificado": "horas_ejecutadas",
            "valor_anterior": "0.0",
            "valor_nuevo": "2.5",
        },
        {
            "usuario": "entrenador.magnus@caissa.org",
            "fecha_hora": (ahora - timedelta(days=7, hours=4)).isoformat(),
            "entidad_afectada": "AperturaRepertorio",
            "tipo_operacion": "CREAR",
            "campo_modificado": "codigo_eco",
            "valor_anterior": None,
            "valor_nuevo": "B90 - Siciliana Najdorf (Variante Adams)",
        },
        {
            "usuario": "sistema@caissa.org",
            "fecha_hora": (ahora - timedelta(days=6, hours=1)).isoformat(),
            "entidad_afectada": "Partida",
            "tipo_operacion": "CREAR",
            "campo_modificado": "importacion_pgn",
            "valor_anterior": None,
            "valor_nuevo": "Partida Garry Kasparov Jr. vs GM Magnus Carlsen (Torneo Magistral)",
        },
        {
            "usuario": "entrenador.magnus@caissa.org",
            "fecha_hora": (ahora - timedelta(days=5, hours=8)).isoformat(),
            "entidad_afectada": "ObjetivoSmart",
            "tipo_operacion": "MODIFICAR",
            "campo_modificado": "valor_actual",
            "valor_anterior": "78.0",
            "valor_nuevo": "85.0",
        },
        {
            "usuario": "entrenador.magnus@caissa.org",
            "fecha_hora": (ahora - timedelta(days=3, hours=2)).isoformat(),
            "entidad_afectada": "EvaluacionAtleta",
            "tipo_operacion": "CREAR",
            "campo_modificado": "dictamen_tecnico",
            "valor_anterior": None,
            "valor_nuevo": "Evaluación Oficial Mesociclo Táctico - Garry Kasparov Jr. (Promedio: 9.25/10)",
        },
        {
            "usuario": "entrenador.magnus@caissa.org",
            "fecha_hora": (ahora - timedelta(days=2, hours=1)).isoformat(),
            "entidad_afectada": "Atleta",
            "tipo_operacion": "MODIFICAR",
            "campo_modificado": "rating_blitz",
            "valor_anterior": "2280",
            "valor_nuevo": "2310",
        },
        {
            "usuario": "administrador@caissa.org",
            "fecha_hora": (ahora - timedelta(hours=14)).isoformat(),
            "entidad_afectada": "Configuracion",
            "tipo_operacion": "MODIFICAR",
            "campo_modificado": "acceso_invitados",
            "valor_anterior": "False",
            "valor_nuevo": "True",
        },
        {
            "usuario": "entrenador.magnus@caissa.org",
            "fecha_hora": (ahora - timedelta(hours=3)).isoformat(),
            "entidad_afectada": "EvaluacionAtleta",
            "tipo_operacion": "CREAR",
            "campo_modificado": "dictamen_tecnico",
            "valor_anterior": None,
            "valor_nuevo": "Evaluación Mensual Octubre - Carlos Daniel Morales (Promedio: 7.88/10)",
        },
    ]

    for reg in registros:
        cur.execute(
            """
            INSERT INTO registros_auditoria (
                usuario, fecha_hora, entidad_afectada, tipo_operacion,
                campo_modificado, valor_anterior, valor_nuevo
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                reg["usuario"],
                reg["fecha_hora"],
                reg["entidad_afectada"],
                reg["tipo_operacion"],
                reg["campo_modificado"],
                reg["valor_anterior"],
                reg["valor_nuevo"],
            ),
        )

    conn.commit()
    print(f"Poblados {len(registros)} registros de auditoría exitosamente.")
    conn.close()

if __name__ == "__main__":
    poblar_auditoria()
