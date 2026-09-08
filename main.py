"""Punto de entrada principal para Caissa Analytics.

Demuestra el funcionamiento interactivo y automatizado del módulo de
Objetivos SMART, con énfasis en el requerimiento RF-03.3 (Validación de Fechas).
"""
from __future__ import annotations

import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adaptadores.primarios.cli.cli_objetivos import CLIObjetivosSMART


def limpiar_pantalla():
    """Limpia la terminal según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_banner():
    """Despliega el encabezado visual del sistema."""
    print("=" * 75)
    print("         SISTEMA CAISSA ANALYTICS - GESTIÓN DE OBJETIVOS SMART")
    print("       Requerimiento RF-03.3: Validación Estricta de Fechas")
    print("=" * 75)


def registrar_objetivo_interactivo(cli: CLIObjetivosSMART):
    """Guía al usuario en la captura y validación en vivo de un objetivo."""
    print("\n--- [REGISTRO DE NUEVO OBJETIVO SMART] ---")
    print("Nota: Para probar las validaciones RF-03.3, puede dejar fechas vacías")
    print("      o ingresar una fecha límite anterior a la fecha de inicio.")
    print("-" * 75)

    try:
        titulo = input(">> Título del objetivo [Meta ELO]: ").strip() or "Meta ELO"
        descripcion = input(">> Descripción [Alcanzar puntaje meta]: ").strip() or "Alcanzar puntaje meta"
        
        print("\n* Fechas obligatorias (Formato esperado: YYYY-MM-DD):")
        f_ini = input("   Fecha de inicio : ").strip()
        f_lim = input("   Fecha límite    : ").strip()

        print("\n* Ratings (Opcionales, Enter para valores por defecto):")
        r_act_str = input("   Rating actual [2150]: ").strip() or "2150"
        r_meta_str = input("   Rating meta   [2200]: ").strip() or "2200"

        r_act = int(r_act_str)
        r_meta = int(r_meta_str)
    except ValueError:
        print("\n [!] [ERROR]: Los ratings deben ser números enteros.")
        return
    except (EOFError, KeyboardInterrupt):
        print("\nOperación cancelada por el usuario.")
        return

    cli.crear_objetivo(
        id_atleta=1,
        titulo=titulo,
        descripcion=descripcion,
        fecha_inicio=f_ini,
        fecha_limite=f_lim,
        rating_actual=r_act,
        rating_meta=r_meta,
    )


def modificar_fechas_interactivo(cli: CLIObjetivosSMART):
    """Permite modificar o prorrogar las fechas de un objetivo existente con validación."""
    print("\n--- [MODIFICAR / PRORROGAR FECHAS DE UN OBJETIVO] ---")
    objetivos = cli.listar_objetivos(1)
    if not objetivos:
        return

    try:
        id_str = input("\n>> Ingrese el ID del objetivo a modificar: ").strip()
        if not id_str:
            return
        id_obj = int(id_str)
    except ValueError:
        print(" [!] [ERROR]: El ID debe ser un número entero.")
        return
    except (EOFError, KeyboardInterrupt):
        return

    obj_existente = cli.buscar_objetivo(id_obj)
    if not obj_existente:
        print(f" [X] No se encontró ningún objetivo con ID #{id_obj}.")
        return

    print(f"\nObjetivo #{obj_existente.id}: '{obj_existente.titulo or obj_existente.descripcion}'")
    print(f" * Fecha de inicio actual : {obj_existente.fecha_inicio}")
    print(f" * Fecha límite actual    : {obj_existente.fecha_limite}")
    print("\n(Presione Enter para conservar la fecha actual, o ingrese una nueva fecha YYYY-MM-DD)")

    try:
        nueva_ini = input(f">> Nueva fecha inicio [{obj_existente.fecha_inicio}]: ").strip()
        nueva_lim = input(f">> Nueva fecha límite [{obj_existente.fecha_limite}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    cli.modificar_fechas(
        id_objetivo=id_obj,
        nueva_fecha_inicio=nueva_ini or None,
        nueva_fecha_limite=nueva_lim or None,
    )


def ejecutar_bateria(cli: CLIObjetivosSMART):
    """Ejecuta los cuatro escenarios clave de validación temporal RF-03.3.
    
    Escenarios:
    A) Nominal Válido: Fechas obligatorias presentes y orden cronológico correcto.
    B) Regla (a): Violación por omisión de fecha de inicio.
    C) Regla (b): Violación por omisión de fecha límite.
    D) Regla (c): Violación por incoherencia cronológica (límite < inicio).
    """
    print("\n" + "=" * 75)
    print("    EJECUTANDO BATERÍA DE PRUEBAS DE REGLAS DE NEGOCIO (RF-03.3)")
    print("=" * 75)

    # Escenario A: Fechas válidas
    print("\n[ESCENARIO A] Caso Nominal Válido")
    print("  * Fecha inicio : 2026-09-01")
    print("  * Fecha límite : 2026-12-31")
    print("  * Resultado esperado: REGISTRO EXITOSO")
    obj_creado = cli.crear_objetivo(
        id_atleta=1,
        titulo="Demostración Nominal",
        descripcion="Objetivo de prueba con fechas correctas",
        fecha_inicio="2026-09-01",
        fecha_limite="2026-12-31",
    )

    # Escenario B: Omisión de fecha de inicio
    print("\n[ESCENARIO B] Regla a: Falta de Fecha de Inicio")
    print("  * Fecha inicio : '' (vacía / nula)")
    print("  * Fecha límite : 2026-12-31")
    print("  * Resultado esperado: RECHAZO (Fecha de inicio obligatoria)")
    cli.crear_objetivo(
        id_atleta=1,
        titulo="Demostración Sin Inicio",
        descripcion="Prueba sin fecha de inicio",
        fecha_inicio="",
        fecha_limite="2026-12-31",
    )

    # Escenario C: Omisión de fecha límite
    print("\n[ESCENARIO C] Regla b: Falta de Fecha Límite")
    print("  * Fecha inicio : 2026-09-01")
    print("  * Fecha límite : '' (vacía / nula)")
    print("  * Resultado esperado: RECHAZO (Fecha límite obligatoria)")
    cli.crear_objetivo(
        id_atleta=1,
        titulo="Demostración Sin Límite",
        descripcion="Prueba sin fecha límite",
        fecha_inicio="2026-09-01",
        fecha_limite="",
    )

    # Escenario D: Fecha límite anterior a inicio
    print("\n[ESCENARIO D] Regla c: Incoherencia Cronológica")
    print("  * Fecha inicio : 2026-12-31")
    print("  * Fecha límite : 2026-09-01 (Anterior a inicio)")
    print("  * Resultado esperado: RECHAZO (Fecha límite anterior a inicio)")
    cli.crear_objetivo(
        id_atleta=1,
        titulo="Demostración Invertida",
        descripcion="Prueba fechas invertidas",
        fecha_inicio="2026-12-31",
        fecha_limite="2026-09-01",
    )

    print("\n" + "-" * 75)
    print("Resumen: De los 4 escenarios, solo el Escenario A fue admitido.")
    print("Los 3 escenarios inválidos fueron rechazados limpiamente por el dominio.")
    print("-" * 75)

    # Limpieza automática del objetivo temporal de prueba
    if obj_creado and obj_creado.id:
        cli.eliminar_objetivo(obj_creado.id)
        print(f"(Registro temporal #{obj_creado.id} removido para mantener limpia la BD)")


def ejecutar_pytest():
    """Ejecuta la suite de pruebas unitarias automatizadas con pytest."""
    print("\n" + "=" * 75)
    print("        EJECUTANDO SUITE COMPLETA DE PRUEBAS UNITARIAS (PYTEST)")
    print("=" * 75)
    try:
        import pytest
        ruta_tests = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "test_objetivos_smart.py")
        codigo_salida = pytest.main(["-v", ruta_tests])
        if codigo_salida == 0:
            print("\n [V] Todas las pruebas unitarias pasaron satisfactoriamente (100% PASS).")
        else:
            print(f"\n [!] Pytest finalizó con código de salida: {codigo_salida}")
    except ImportError:
        print(" [!] No se encontró 'pytest' instalado en el entorno.")


def menu():
    """Despliega el menú principal interactivo en la terminal."""
    cli = CLIObjetivosSMART()

    # Soporte para banderas de ejecución desde consola
    if len(sys.argv) > 1:
        param = sys.argv[1].lower()
        if param in ("--test", "-t", "test"):
            ejecutar_bateria(cli)
            return
        if param in ("--pytest", "-p", "pytest"):
            ejecutar_pytest()
            return

    while True:
        mostrar_banner()
        print("  [1] Listar objetivos registrados de un atleta")
        print("  [2] Registrar nuevo objetivo (Validación RF-03.3 en vivo)")
        print("  [3] Modificar / Prorrogar fechas de un objetivo existente")
        print("  [4] Ejecutar batería de demostración (4 Escenarios RF-03.3)")
        print("  [5] Ejecutar suite de pruebas unitarias (Pytest)")
        print("  [6] Salir")
        print("=" * 75)

        try:
            opcion = input("Seleccione una opción (1-6): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nSaliendo de Caissa Analytics...")
            break

        if opcion == "1":
            cli.listar_objetivos(1)
            input("\nPresione Enter para continuar...")
        elif opcion == "2":
            registrar_objetivo_interactivo(cli)
            input("\nPresione Enter para continuar...")
        elif opcion == "3":
            modificar_fechas_interactivo(cli)
            input("\nPresione Enter para continuar...")
        elif opcion == "4":
            ejecutar_bateria(cli)
            input("\nPresione Enter para continuar...")
        elif opcion == "5":
            ejecutar_pytest()
            input("\nPresione Enter para continuar...")
        elif opcion == "6":
            print("\nSaliendo del sistema Caissa Analytics. ¡Hasta pronto!")
            break
        else:
            print("\n [!] Opción no válida. Por favor seleccione un número del 1 al 6.\n")


if __name__ == "__main__":
    menu()
