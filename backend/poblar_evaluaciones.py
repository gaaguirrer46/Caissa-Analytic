"""Script para poblar evaluaciones técnicas del DT en caissa.db."""
import sqlite3
from datetime import date

def poblar_evaluaciones():
    conn = sqlite3.connect("backend/caissa.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("DELETE FROM evaluacion_calificaciones_indicador")
    cur.execute("DELETE FROM evaluaciones_atleta")

    evaluaciones = [
        # Garry Kasparov Jr. (Atleta 1) - Mesociclo Táctico Septiembre 2026
        {
            "id_atleta": 1,
            "id_entrenador": 1,
            "periodo": "MESOCICLO",
            "referencia_periodo": "Mesociclo Fuerza Táctica - Sep 2026",
            "fecha_realizacion": "2026-09-30",
            "fortalezas": "Dominio agresivo de la iniciativa con piezas blancas en esquemas Siciliana Najdorf. Alta velocidad de cálculo en posiciones dinámicas.",
            "aspectos_por_mejorar": "Paciencia en posiciones profilácticas cerradas. Tendencia a forzar simplificaciones prematuras cuando el rival se repliega.",
            "recomendaciones": "Estudiar partidas clásicas de Petrosian y Karpov sobre profilaxis y maniobras de piezas menores sin contacto directo.",
            "es_autoevaluacion": False,
            "calificaciones": {
                "CUMPLIMIENTO_PLAN": 9,
                "DESARROLLO_TECNICO_TACTICO": 9,
                "PROGRESO_RATING": 8,
                "CUMPLIMIENTO_OBJETIVOS_SMART": 8,
                "ORGANIZACION": 9,
                "GESTION_COMPETENCIAS": 8,
                "DESARROLLO_APERTURAS": 9,
                "SEGUIMIENTO_INDIVIDUAL": 9
            }
        },
        # Garry Kasparov Jr. (Atleta 1) - Evaluación Octubre 2026 (reciente)
        {
            "id_atleta": 1,
            "id_entrenador": 1,
            "periodo": "MES",
            "referencia_periodo": "Evaluación Mensual - Octubre 2026",
            "fecha_realizacion": "2026-10-31",
            "fortalezas": "Excelente preparación en la Defensa Siciliana (ECO B90) y cálculo preciso en complicaciones tácticas complejas. Gran recuperación psicológica tras derrotas.",
            "aspectos_por_mejorar": "Gestión del tiempo en la jugada 30-38 previo al primer control. Apuros innecesarios que provocan descuidos tácticos.",
            "recomendaciones": "Mantener al menos 15 minutos en el reloj antes de la jugada 35. Entrenar ejercicios de finales de damas con incremento de 30 segundos.",
            "es_autoevaluacion": False,
            "calificaciones": {
                "CUMPLIMIENTO_PLAN": 10,
                "DESARROLLO_TECNICO_TACTICO": 9,
                "PROGRESO_RATING": 9,
                "CUMPLIMIENTO_OBJETIVOS_SMART": 9,
                "ORGANIZACION": 9,
                "GESTION_COMPETENCIAS": 9,
                "DESARROLLO_APERTURAS": 9,
                "SEGUIMIENTO_INDIVIDUAL": 10
            }
        },
        # Carlos Daniel Morales (Atleta 2) - Evaluación Mensual Octubre 2026
        {
            "id_atleta": 2,
            "id_entrenador": 1,
            "periodo": "MES",
            "referencia_periodo": "Evaluación Mensual - Octubre 2026",
            "fecha_realizacion": "2026-10-30",
            "fortalezas": "Sólido juego posicional en aperturas de peón dama (1.d4). Comprensión clara de estructuras Carlsbad e islas de peones.",
            "aspectos_por_mejorar": "Agresividad táctica en momentos críticos y cálculo de líneas forzadas agudas. Dificultad para castigar jugadas pasivas del oponente.",
            "recomendaciones": "Incrementar volumen de resolución de ejercicios tácticos de nivel 2200+ (mínimo 45 minutos diarios de cálculo forzado).",
            "es_autoevaluacion": False,
            "calificaciones": {
                "CUMPLIMIENTO_PLAN": 8,
                "DESARROLLO_TECNICO_TACTICO": 7,
                "PROGRESO_RATING": 8,
                "CUMPLIMIENTO_OBJETIVOS_SMART": 8,
                "ORGANIZACION": 9,
                "GESTION_COMPETENCIAS": 7,
                "DESARROLLO_APERTURAS": 8,
                "SEGUIMIENTO_INDIVIDUAL": 8
            }
        },
        # Sofía Valentina Castro (Atleta 3) - Torneo Magistral ITT
        {
            "id_atleta": 3,
            "id_entrenador": 1,
            "periodo": "TORNEO",
            "referencia_periodo": "Post-Torneo Nacional Universitario 2026",
            "fecha_realizacion": "2026-10-25",
            "fortalezas": "Gran inventiva estratégica en defensas asimétricas (Defensa Francesa variante Winawer). Tenacidad en posiciones inferiores.",
            "aspectos_por_mejorar": "Finales teóricos de torres y peones con peón de ventaja. Necesita mecanizar el método de Lucena y puente de Philidor con total seguridad.",
            "recomendaciones": "Simulaciones intensivas de finales de torres contra el módulo Stockfish 16 con posiciones de Dvoretsky.",
            "es_autoevaluacion": False,
            "calificaciones": {
                "CUMPLIMIENTO_PLAN": 8,
                "DESARROLLO_TECNICO_TACTICO": 7,
                "PROGRESO_RATING": 8,
                "CUMPLIMIENTO_OBJETIVOS_SMART": 8,
                "ORGANIZACION": 8,
                "GESTION_COMPETENCIAS": 7,
                "DESARROLLO_APERTURAS": 8,
                "SEGUIMIENTO_INDIVIDUAL": 8
            }
        },
        # Alejandro José Rivas (Atleta 4) - Evaluación Mensual Octubre 2026
        {
            "id_atleta": 4,
            "id_entrenador": 1,
            "periodo": "MES",
            "referencia_periodo": "Evaluación Mensual - Octubre 2026",
            "fecha_realizacion": "2026-10-29",
            "fortalezas": "Visión combinatoria sobresaliente en el medio juego. Excelente preparación en la Apertura Española y Gambito de Dama Aceptado.",
            "aspectos_por_mejorar": "Constancia en el registro de horas de entrenamiento personal y análisis riguroso de partidas perdidas.",
            "recomendaciones": "Completar la bitácora semanal en Caissa Analytic antes del domingo a las 20:00 sin excepción.",
            "es_autoevaluacion": False,
            "calificaciones": {
                "CUMPLIMIENTO_PLAN": 9,
                "DESARROLLO_TECNICO_TACTICO": 9,
                "PROGRESO_RATING": 9,
                "CUMPLIMIENTO_OBJETIVOS_SMART": 9,
                "ORGANIZACION": 8,
                "GESTION_COMPETENCIAS": 9,
                "DESARROLLO_APERTURAS": 9,
                "SEGUIMIENTO_INDIVIDUAL": 9
            }
        }
    ]

    for ev in evaluaciones:
        cur.execute(
            """
            INSERT INTO evaluaciones_atleta (
                id_atleta, id_entrenador, periodo, referencia_periodo,
                fecha_realizacion, fortalezas, aspectos_por_mejorar,
                recomendaciones, es_autoevaluacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                ev["id_atleta"],
                ev["id_entrenador"],
                ev["periodo"],
                ev["referencia_periodo"],
                ev["fecha_realizacion"],
                ev["fortalezas"],
                ev["aspectos_por_mejorar"],
                ev["recomendaciones"],
                1 if ev["es_autoevaluacion"] else 0,
            ),
        )
        ev_id = cur.lastrowid
        for ind, nota in ev["calificaciones"].items():
            cur.execute(
                """
                INSERT INTO evaluacion_calificaciones_indicador (
                    id_evaluacion, tipo_indicador, calificacion
                ) VALUES (?, ?, ?);
                """,
                (ev_id, ind, nota),
            )

    conn.commit()
    print(f"Pobladas exitosamente {len(evaluaciones)} evaluaciones con sus rubricas e indicadores.")
    conn.close()

if __name__ == "__main__":
    poblar_evaluaciones()
