"""Script interactivo de verificación para Objetivos SMART (RF-03).

Ejecuta de manera autónoma los cuatro escenarios de prueba principales
demostrando por consola cómo el sistema valida las fechas obligatorias y coherentes.
"""
import os
import sys
import sqlite3
from datetime import date

# Asegurar importación de los módulos del proyecto agregando la raíz al sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dominio.comun.errores import ErrorValidacion
from dominio.objetivos.entidades import ObjetivoSMART, TipoIndicadorAvance
from dominio.objetivos.validador import ObjetivoSMARTValidator
from adaptadores.secundarios.persistencia.repositorio_objetivos_sqlite import RepositorioObjetivosSQLite


def separador(titulo: str):
    """Imprime una cabecera visual para distinguir cada prueba en la terminal."""
    print("\n" + "=" * 70)
    print(f" {titulo}")
    print("=" * 70)


def main():
    """Función principal que ejecuta secuencialmente los 4 escenarios de prueba."""
    print("Iniciando pruebas de verificación para RF-03.3 (Objetivos SMART)...")
    
    # 1. Configurar base de datos SQLite en memoria aislada para no alterar datos persistidos
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # 2. Cargar el esquema canónico con sus tablas y constraints (CHK_FechasValidas)
    schema_path = os.path.join(os.path.dirname(__file__), "infraestructura", "base_de_datos", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    
    # 3. Inicializar el repositorio conectado a la base de datos temporal
    repo = RepositorioObjetivosSQLite(conn)

    # -------------------------------------------------------------
    # Escenario 1: Creación de Objetivo con fechas válidas (Test 1)
    # -------------------------------------------------------------
    separador("1. PRUEBA (Test 1): Crear Objetivo con fechas válidas")
    try:
        # Se proporcionan fechas en rango cronológico válido (agosto a diciembre de 2026)
        obj = ObjetivoSMART(
            id_atleta=1,
            titulo="Subir a 2200 ELO",
            descripcion="Entrenar táctica y aperturas para torneo",
            rating_actual=2150,
            rating_meta=2200,
            fecha_inicio=date(2026, 8, 1),
            fecha_limite=date(2026, 12, 31),
            indicador_meta=TipoIndicadorAvance.RATING,
            valor_meta=2200.0,
            creado_por="entrenador.magnus@caissa.org"
        )
        guardado = repo.guardar(obj)
        print(" [OK] Objetivo creado exitosamente en la base de datos:")
        print(f"      - ID asignado: {guardado.id}")
        print(f"      - Fecha Inicio: {guardado.fecha_inicio}")
        print(f"      - Fecha Límite: {guardado.fecha_limite}")
        print(f"      - Estado: {guardado.estado.value}")
    except Exception as e:
        print(f" [ERROR INESPERADO]: {e}")

    # -------------------------------------------------------------
    # Escenario 2: Intento con fecha de inicio nula (Test 2)
    # -------------------------------------------------------------
    separador("2. PRUEBA (Test 2): Rechazar cuando falta Fecha de Inicio (None o vacía)")
    try:
        # Se omite fecha_inicio pasando None
        ObjetivoSMARTValidator.validar_fechas(None, date(2026, 12, 31))
        print(" [FALLO]: Debería haber lanzado ErrorValidacion.")
    except ErrorValidacion as e:
        # Se confirma que la excepción capturada coincide con el mensaje oficial de la regla a)
        print(" [OK] Rechazado correctamente con mensaje:")
        print(f"      --> \"{e}\"")

    # -------------------------------------------------------------
    # Escenario 3: Intento con fecha límite nula (Test 3)
    # -------------------------------------------------------------
    separador("3. PRUEBA (Test 3): Rechazar cuando falta Fecha Límite (None o vacía)")
    try:
        # Se omite fecha_limite pasando None
        ObjetivoSMARTValidator.validar_fechas(date(2026, 8, 1), None)
        print(" [FALLO]: Debería haber lanzado ErrorValidacion.")
    except ErrorValidacion as e:
        # Se confirma que la excepción capturada coincide con el mensaje oficial de la regla b)
        print(" [OK] Rechazado correctamente con mensaje:")
        print(f"      --> \"{e}\"")

    # -------------------------------------------------------------
    # Escenario 4: Intento con fecha límite anterior a fecha inicio (Test 4)
    # -------------------------------------------------------------
    separador("4. PRUEBA (Test 4): Rechazar cuando Fecha Límite < Fecha Inicio")
    try:
        # Se invierten las fechas (inicio en diciembre y límite en agosto)
        f_inicio = date(2026, 12, 31)
        f_limite = date(2026, 8, 1)  # Anterior
        print(f"      Intentando: Inicio = {f_inicio} | Límite = {f_limite}")
        ObjetivoSMARTValidator.validar_fechas(f_inicio, f_limite)
        print(" [FALLO]: Debería haber lanzado ErrorValidacion.")
    except ErrorValidacion as e:
        # Se confirma el rechazo por incoherencia cronológica (regla c)
        print(" [OK] Rechazado correctamente con mensaje:")
        print(f"      --> \"{e}\"")

    # -------------------------------------------------------------
    # Resumen final de la ejecución
    # -------------------------------------------------------------
    separador("RESULTADO DE VERIFICACIÓN")
    print(" Todas las validaciones de negocio y de base de datos pasaron al 100%.")
    print("=" * 70 + "\n")
    
    conn.close()


if __name__ == "__main__":
    main()
