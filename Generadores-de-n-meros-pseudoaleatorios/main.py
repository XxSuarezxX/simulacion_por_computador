#!/usr/bin/env python3
"""
=============================================================================
  Módulo Integrado de Generación de Números Pseudoaleatorios
  Taller 1 — Simulación Computacional
=============================================================================

Punto de entrada principal con menú interactivo en consola.

Generadores disponibles:
    1. Cuadrados Medios
    2. Congruencial Lineal
    3. Congruencial Multiplicativo
    4. Congruencial Aditivo
    5. Distribución Uniforme (transformación)
    6. Distribución Normal (Box-Muller)

Uso:
    python3 main.py
"""

import os
import sys

# Agregar directorio raíz al path para imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generadores.cuadrados_medios import cuadrados_medios
from generadores.congruencial_lineal import congruencial_lineal
from generadores.congruencial_multiplicativo import congruencial_multiplicativo
from generadores.congruencial_aditivo import congruencial_aditivo
from generadores.distribucion_uniforme import distribucion_uniforme
from generadores.distribucion_normal import distribucion_normal
from utils.archivo import cargar_semillas, exportar_tabla
from utils.visualizacion import histograma_generador, mostrar_tabla


# ═════════════════════════════════════════════════════════════════════════════
# Variables globales del estado de la sesión
# ═════════════════════════════════════════════════════════════════════════════
semillas_cargadas = []          # Semillas disponibles (desde archivo o manuales)
resultados = {}                 # {nombre_metodo: {"xi": [...], "ri": [...]}}


# ═════════════════════════════════════════════════════════════════════════════
# Funciones auxiliares de entrada
# ═════════════════════════════════════════════════════════════════════════════

def leer_entero(mensaje, minimo=None, maximo=None):
    """Lee un entero del usuario con validación de rango."""
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  Error: el valor debe ser >= {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  Error: el valor debe ser <= {maximo}.")
                continue
            return valor
        except ValueError:
            print("  Error: ingrese un número entero válido.")


def leer_float(mensaje):
    """Lee un número decimal del usuario."""
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("  Error: ingrese un número válido.")


def leer_lista_enteros(mensaje):
    """Lee una lista de enteros separados por comas."""
    while True:
        entrada = input(mensaje).strip()
        try:
            valores = [int(x.strip()) for x in entrada.split(",")]
            if len(valores) < 2:
                print("  Error: ingrese al menos 2 valores separados por comas.")
                continue
            return valores
        except ValueError:
            print("  Error: ingrese números enteros separados por comas.")


# ═════════════════════════════════════════════════════════════════════════════
# Menú: Cargar / Ingresar semillas
# ═════════════════════════════════════════════════════════════════════════════

def menu_semillas():
    """Submenú para cargar o ingresar semillas."""
    global semillas_cargadas

    print("\n┌─────────────────────────────────────┐")
    print("│       CONFIGURAR SEMILLAS           │")
    print("├─────────────────────────────────────┤")
    print("│  1. Cargar desde archivo (.txt/.csv) │")
    print("│  2. Ingresar manualmente             │")
    print("│  3. Ver semillas cargadas             │")
    print("│  4. Limpiar semillas                  │")
    print("│  0. Volver al menú principal          │")
    print("└─────────────────────────────────────┘")

    opcion = leer_entero("  Opción: ", 0, 4)

    if opcion == 1:
        ruta = input("  Ruta del archivo: ").strip()
        try:
            nuevas = cargar_semillas(ruta)
            semillas_cargadas.extend(nuevas)
            print(f"  ✓ {len(nuevas)} semilla(s) agregada(s). "
                  f"Total: {len(semillas_cargadas)}.")
        except (FileNotFoundError, ValueError) as e:
            print(f"  ✗ Error: {e}")

    elif opcion == 2:
        entrada = input("  Ingrese semilla(s) separadas por comas: ").strip()
        try:
            nuevas = [int(x.strip()) for x in entrada.split(",")]
            semillas_cargadas.extend(nuevas)
            print(f"  ✓ {len(nuevas)} semilla(s) agregada(s). "
                  f"Total: {len(semillas_cargadas)}.")
        except ValueError:
            print("  ✗ Error: ingrese números enteros separados por comas.")

    elif opcion == 3:
        if semillas_cargadas:
            print(f"  Semillas cargadas ({len(semillas_cargadas)}): "
                  f"{semillas_cargadas}")
        else:
            print("  No hay semillas cargadas.")

    elif opcion == 4:
        semillas_cargadas.clear()
        print("  ✓ Semillas limpiadas.")


# ═════════════════════════════════════════════════════════════════════════════
# Menú: Ejecutar generadores
# ═════════════════════════════════════════════════════════════════════════════

def menu_generador():
    """Submenú para seleccionar y ejecutar un generador."""
    global resultados

    print("\n┌──────────────────────────────────────────────┐")
    print("│          SELECCIONAR GENERADOR               │")
    print("├──────────────────────────────────────────────┤")
    print("│  1. Cuadrados Medios                         │")
    print("│  2. Congruencial Lineal                      │")
    print("│  3. Congruencial Multiplicativo              │")
    print("│  4. Congruencial Aditivo                     │")
    print("│  5. Distribución Uniforme (transformación)   │")
    print("│  6. Distribución Normal (Box-Muller)         │")
    print("│  0. Volver al menú principal                 │")
    print("└──────────────────────────────────────────────┘")

    opcion = leer_entero("  Opción: ", 0, 6)

    if opcion == 0:
        return

    if opcion == 1:
        _ejecutar_cuadrados_medios()
    elif opcion == 2:
        _ejecutar_congruencial_lineal()
    elif opcion == 3:
        _ejecutar_congruencial_multiplicativo()
    elif opcion == 4:
        _ejecutar_congruencial_aditivo()
    elif opcion == 5:
        _ejecutar_distribucion_uniforme()
    elif opcion == 6:
        _ejecutar_distribucion_normal()


def _ejecutar_cuadrados_medios():
    """Solicita parámetros y ejecuta el generador de Cuadrados Medios."""
    print("\n--- Cuadrados Medios ---")
    print("  Parámetros requeridos: semilla (entero), cantidad de números.")

    if semillas_cargadas:
        print(f"  Semillas disponibles: {semillas_cargadas}")
        usar = input("  ¿Usar primera semilla cargada? (s/n): ").strip().lower()
        if usar == "s":
            semilla = semillas_cargadas[0]
            print(f"  Usando semilla: {semilla}")
        else:
            semilla = leer_entero("  Semilla (entero positivo): ", minimo=1)
    else:
        semilla = leer_entero("  Semilla (entero positivo): ", minimo=1)

    cantidad = leer_entero("  Cantidad de números a generar: ", minimo=1)

    n_digitos_str = input("  Número de dígitos (Enter = auto-detectar): ").strip()
    n_digitos = int(n_digitos_str) if n_digitos_str else None

    print("\n  Generando...")
    xi, ri = cuadrados_medios(semilla, cantidad, n_digitos)

    nombre = "Cuadrados Medios"
    resultados[nombre] = {"xi": xi, "ri": ri}
    print(f"  ✓ {len(ri)} número(s) generado(s) con '{nombre}'.")

    # Mostrar tabla
    datos_tabla = [[i + 1, xi[i], ri[i]] for i in range(len(xi))]
    mostrar_tabla(datos_tabla, ["i", "Xi", "ri"], titulo=nombre)


def _ejecutar_congruencial_lineal():
    """Solicita parámetros y ejecuta el generador Congruencial Lineal."""
    print("\n--- Congruencial Lineal ---")
    print("  Fórmula: X_{n+1} = (a * X_n + c) mod m")

    if semillas_cargadas:
        print(f"  Semillas disponibles: {semillas_cargadas}")
        usar = input("  ¿Usar primera semilla cargada? (s/n): ").strip().lower()
        if usar == "s":
            semilla = semillas_cargadas[0]
            print(f"  Usando semilla X0: {semilla}")
        else:
            semilla = leer_entero("  Semilla X0: ", minimo=0)
    else:
        semilla = leer_entero("  Semilla X0: ", minimo=0)

    a = leer_entero("  Multiplicador (a): ", minimo=1)
    c = leer_entero("  Incremento (c): ", minimo=0)
    m = leer_entero("  Módulo (m): ", minimo=1)
    cantidad = leer_entero("  Cantidad de números a generar: ", minimo=1)

    print("\n  Generando...")
    xi, ri = congruencial_lineal(semilla, a, c, m, cantidad)

    nombre = "Congruencial Lineal"
    resultados[nombre] = {"xi": xi, "ri": ri}
    print(f"  ✓ {len(ri)} número(s) generado(s) con '{nombre}'.")

    datos_tabla = [[i + 1, xi[i], ri[i]] for i in range(len(xi))]
    mostrar_tabla(datos_tabla, ["i", "Xi", "ri"], titulo=nombre)


def _ejecutar_congruencial_multiplicativo():
    """Solicita parámetros y ejecuta el generador Congruencial Multiplicativo."""
    print("\n--- Congruencial Multiplicativo ---")
    print("  Fórmula: X_{n+1} = (a * X_n) mod m   (c = 0)")

    if semillas_cargadas:
        print(f"  Semillas disponibles: {semillas_cargadas}")
        usar = input("  ¿Usar primera semilla cargada? (s/n): ").strip().lower()
        if usar == "s":
            semilla = semillas_cargadas[0]
            print(f"  Usando semilla X0: {semilla}")
        else:
            semilla = leer_entero("  Semilla X0 (coprima con m): ", minimo=1)
    else:
        semilla = leer_entero("  Semilla X0 (coprima con m): ", minimo=1)

    a = leer_entero("  Multiplicador (a): ", minimo=1)
    m = leer_entero("  Módulo (m): ", minimo=1)
    cantidad = leer_entero("  Cantidad de números a generar: ", minimo=1)

    print("\n  Generando...")
    xi, ri = congruencial_multiplicativo(semilla, a, m, cantidad)

    nombre = "Congruencial Multiplicativo"
    resultados[nombre] = {"xi": xi, "ri": ri}
    print(f"  ✓ {len(ri)} número(s) generado(s) con '{nombre}'.")

    datos_tabla = [[i + 1, xi[i], ri[i]] for i in range(len(xi))]
    mostrar_tabla(datos_tabla, ["i", "Xi", "ri"], titulo=nombre)


def _ejecutar_congruencial_aditivo():
    """Solicita parámetros y ejecuta el generador Congruencial Aditivo."""
    print("\n--- Congruencial Aditivo ---")
    print("  Fórmula: X_n = (X_{n-j} + X_{n-k}) mod m")
    print("  Requiere un vector de semillas iniciales (al menos 2).")

    if len(semillas_cargadas) >= 2:
        print(f"  Semillas cargadas ({len(semillas_cargadas)}): {semillas_cargadas}")
        usar = input("  ¿Usar todas las semillas cargadas? (s/n): ").strip().lower()
        if usar == "s":
            semillas = list(semillas_cargadas)
            print(f"  Usando {len(semillas)} semillas.")
        else:
            semillas = leer_lista_enteros(
                "  Semillas iniciales (separadas por comas): "
            )
    else:
        semillas = leer_lista_enteros(
            "  Semillas iniciales (separadas por comas, mín. 2): "
        )

    m = leer_entero("  Módulo (m): ", minimo=1)
    cantidad = leer_entero("  Cantidad de números nuevos a generar: ", minimo=1)

    j_str = input("  Retardo j (Enter = 1): ").strip()
    j = int(j_str) if j_str else 1

    print("\n  Generando...")
    try:
        xi, ri = congruencial_aditivo(semillas, m, cantidad, j)
        nombre = "Congruencial Aditivo"
        resultados[nombre] = {"xi": xi, "ri": ri}
        print(f"  ✓ {len(ri)} número(s) generado(s) con '{nombre}'.")

        datos_tabla = [[i + 1, xi[i], ri[i]] for i in range(len(xi))]
        mostrar_tabla(datos_tabla, ["i", "Xi", "ri"], titulo=nombre)
    except ValueError as e:
        print(f"  ✗ Error: {e}")


def _ejecutar_distribucion_uniforme():
    """Solicita parámetros y ejecuta la transformación a distribución uniforme."""
    print("\n--- Distribución Uniforme [a, b) ---")
    print("  Transforma ri ∈ [0,1) a rango [a, b).")

    if not resultados:
        print("  ✗ Error: primero genere números con algún generador base "
              "(opciones 1-4).")
        return

    # Seleccionar generador base
    print("  Generadores disponibles con resultados:")
    nombres = list(resultados.keys())
    for idx, nombre in enumerate(nombres, 1):
        n = len(resultados[nombre]["ri"])
        print(f"    {idx}. {nombre} ({n} números)")

    sel = leer_entero("  Seleccione generador base: ", 1, len(nombres))
    ri_base = resultados[nombres[sel - 1]]["ri"]

    a = leer_float("  Límite inferior (a): ")
    b = leer_float("  Límite superior (b): ")

    print("\n  Transformando...")
    try:
        uniformes = distribucion_uniforme(ri_base, a, b)
        nombre = f"Uniforme [{a}, {b})"
        resultados[nombre] = {"xi": uniformes, "ri": ri_base}
        print(f"  ✓ {len(uniformes)} número(s) transformados a '{nombre}'.")

        datos_tabla = [[i + 1, uniformes[i]] for i in range(len(uniformes))]
        mostrar_tabla(datos_tabla, ["i", "Xi"], titulo=nombre)
    except ValueError as e:
        print(f"  ✗ Error: {e}")


def _ejecutar_distribucion_normal():
    """Solicita parámetros y ejecuta la transformación a distribución normal."""
    print("\n--- Distribución Normal N(μ, σ²) — Box-Muller ---")
    print("  Transforma pares de uniformes a normales.")

    if not resultados:
        print("  ✗ Error: primero genere números con algún generador base "
              "(opciones 1-4).")
        return

    # Seleccionar generador base
    print("  Generadores disponibles con resultados:")
    nombres = list(resultados.keys())
    for idx, nombre in enumerate(nombres, 1):
        n = len(resultados[nombre]["ri"])
        print(f"    {idx}. {nombre} ({n} números)")

    sel = leer_entero("  Seleccione generador base: ", 1, len(nombres))
    ri_base = resultados[nombres[sel - 1]]["ri"]

    mu = leer_float("  Media (μ): ")
    sigma = leer_float("  Desviación estándar (σ): ")

    print("\n  Transformando (Box-Muller)...")
    try:
        normales = distribucion_normal(ri_base, mu, sigma)
        nombre = f"Normal N({mu}, {sigma}²)"
        resultados[nombre] = {"xi": normales, "ri": ri_base}
        print(f"  ✓ {len(normales)} número(s) generados con '{nombre}'.")

        datos_tabla = [[i + 1, normales[i]] for i in range(len(normales))]
        mostrar_tabla(datos_tabla, ["i", "Xi"], titulo=nombre)
    except ValueError as e:
        print(f"  ✗ Error: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# Menú: Ver resultados
# ═════════════════════════════════════════════════════════════════════════════

def menu_ver_resultados():
    """Muestra las tablas de resultados generados."""
    if not resultados:
        print("\n  No hay resultados generados aún.")
        return

    print("\n  Resultados disponibles:")
    nombres = list(resultados.keys())
    for idx, nombre in enumerate(nombres, 1):
        n = len(resultados[nombre].get("xi", resultados[nombre].get("ri", [])))
        print(f"    {idx}. {nombre} ({n} números)")
    print(f"    0. Volver")

    sel = leer_entero("  Seleccione: ", 0, len(nombres))
    if sel == 0:
        return

    nombre = nombres[sel - 1]
    datos = resultados[nombre]

    if "xi" in datos and "ri" in datos and len(datos["xi"]) == len(datos["ri"]):
        tabla = [[i + 1, datos["xi"][i], datos["ri"][i]]
                 for i in range(len(datos["xi"]))]
        mostrar_tabla(tabla, ["i", "Xi", "ri"], titulo=nombre)
    elif "xi" in datos:
        tabla = [[i + 1, datos["xi"][i]] for i in range(len(datos["xi"]))]
        mostrar_tabla(tabla, ["i", "Xi"], titulo=nombre)


# ═════════════════════════════════════════════════════════════════════════════
# Menú: Histogramas
# ═════════════════════════════════════════════════════════════════════════════

def menu_histogramas():
    """Genera histogramas de los resultados."""
    if not resultados:
        print("\n  No hay resultados generados aún.")
        return

    print("\n┌──────────────────────────────────────┐")
    print("│         GENERAR HISTOGRAMAS          │")
    print("├──────────────────────────────────────┤")

    nombres = list(resultados.keys())
    for idx, nombre in enumerate(nombres, 1):
        print(f"│  {idx}. {nombre}")

    print(f"│  {len(nombres) + 1}. Todos los generadores")
    print("│  0. Volver")
    print("└──────────────────────────────────────┘")

    sel = leer_entero("  Seleccione: ", 0, len(nombres) + 1)

    if sel == 0:
        return

    if sel == len(nombres) + 1:
        # Generar todos
        for nombre in nombres:
            datos = resultados[nombre]
            numeros = datos.get("xi", datos.get("ri", []))
            histograma_generador(numeros, f"Histograma — {nombre}")
        print(f"\n  ✓ {len(nombres)} histograma(s) generado(s) en 'resultados/'.")
    else:
        nombre = nombres[sel - 1]
        datos = resultados[nombre]
        numeros = datos.get("xi", datos.get("ri", []))
        histograma_generador(numeros, f"Histograma — {nombre}")


# ═════════════════════════════════════════════════════════════════════════════
# Menú: Exportar
# ═════════════════════════════════════════════════════════════════════════════

def menu_exportar():
    """Exporta resultados a CSV."""
    if not resultados:
        print("\n  No hay resultados generados aún.")
        return

    print("\n  Resultados disponibles para exportar:")
    nombres = list(resultados.keys())
    for idx, nombre in enumerate(nombres, 1):
        print(f"    {idx}. {nombre}")
    print(f"    {len(nombres) + 1}. Exportar todos")
    print(f"    0. Volver")

    sel = leer_entero("  Seleccione: ", 0, len(nombres) + 1)

    if sel == 0:
        return

    if sel == len(nombres) + 1:
        for nombre in nombres:
            _exportar_un_resultado(nombre)
        print(f"\n  ✓ {len(nombres)} archivo(s) exportado(s) en 'resultados/'.")
    else:
        _exportar_un_resultado(nombres[sel - 1])


def _exportar_un_resultado(nombre):
    """Exporta un resultado individual a CSV."""
    datos = resultados[nombre]
    nombre_archivo = nombre.lower().replace(" ", "_").replace(".", "")
    nombre_archivo = "".join(c for c in nombre_archivo if c.isalnum() or c == "_")
    ruta = os.path.join("resultados", f"{nombre_archivo}.csv")

    if "xi" in datos and "ri" in datos and len(datos["xi"]) == len(datos["ri"]):
        tabla = [[i + 1, datos["xi"][i], datos["ri"][i]]
                 for i in range(len(datos["xi"]))]
        encabezados = ["i", "Xi", "ri"]
    elif "xi" in datos:
        tabla = [[i + 1, datos["xi"][i]] for i in range(len(datos["xi"]))]
        encabezados = ["i", "Xi"]
    else:
        tabla = [[i + 1, datos["ri"][i]] for i in range(len(datos["ri"]))]
        encabezados = ["i", "ri"]

    exportar_tabla(tabla, ruta, encabezados)


# ═════════════════════════════════════════════════════════════════════════════
# Menú: Validación (placeholder)
# ═════════════════════════════════════════════════════════════════════════════

def menu_validacion():
    """Placeholder para el módulo de validación estadística."""
    print("\n╔═══════════════════════════════════════════════════╗")
    print("║  MÓDULO DE VALIDACIÓN — PENDIENTE                ║")
    print("╠═══════════════════════════════════════════════════╣")
    print("║  Este módulo será implementado por otro          ║")
    print("║  desarrollador. Consultar validaciones/README.md ║")
    print("║  para instrucciones de integración.              ║")
    print("║                                                  ║")
    print("║  Pruebas pendientes:                             ║")
    print("║    • Prueba de medias                            ║")
    print("║    • Prueba de varianza                          ║")
    print("║    • Prueba Chi-cuadrado                         ║")
    print("║    • Prueba Kolmogorov-Smirnov (KS)              ║")
    print("║    • Prueba de Póker                             ║")
    print("║    • Prueba de rachas (runs test)                ║")
    print("╚═══════════════════════════════════════════════════╝")


# ═════════════════════════════════════════════════════════════════════════════
# Menú principal
# ═════════════════════════════════════════════════════════════════════════════

def menu_principal():
    """Bucle principal del menú interactivo."""
    while True:
        print("\n╔═══════════════════════════════════════════════════════╗")
        print("║   GENERADOR DE NÚMEROS PSEUDOALEATORIOS              ║")
        print("║   Taller 1 — Simulación Computacional                ║")
        print("╠═══════════════════════════════════════════════════════╣")
        print("║                                                      ║")
        print("║   1. Configurar semillas                             ║")
        print("║   2. Seleccionar y ejecutar generador                ║")
        print("║   3. Ver resultados (tabla)                          ║")
        print("║   4. Generar histogramas                             ║")
        print("║   5. Exportar resultados a CSV                       ║")
        print("║   6. Validación estadística (pendiente)              ║")
        print("║   0. Salir                                           ║")
        print("║                                                      ║")
        print("╚═══════════════════════════════════════════════════════╝")

        if semillas_cargadas:
            print(f"  📌 Semillas cargadas: {len(semillas_cargadas)}")
        if resultados:
            print(f"  📊 Generadores ejecutados: {len(resultados)}")

        opcion = leer_entero("  Opción: ", 0, 6)

        if opcion == 0:
            print("\n  ¡Hasta luego! 👋\n")
            break
        elif opcion == 1:
            menu_semillas()
        elif opcion == 2:
            menu_generador()
        elif opcion == 3:
            menu_ver_resultados()
        elif opcion == 4:
            menu_histogramas()
        elif opcion == 5:
            menu_exportar()
        elif opcion == 6:
            menu_validacion()


# ═════════════════════════════════════════════════════════════════════════════
# Punto de entrada
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    menu_principal()
