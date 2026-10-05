#!/usr/bin/env python3
"""
Script de prueba para verificar todos los generadores.
Ejecuta cada generador con parámetros conocidos, muestra resultados
y genera histogramas.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generadores.cuadrados_medios import cuadrados_medios
from generadores.congruencial_lineal import congruencial_lineal
from generadores.congruencial_multiplicativo import congruencial_multiplicativo
from generadores.congruencial_aditivo import congruencial_aditivo
from generadores.distribucion_uniforme import distribucion_uniforme
from generadores.distribucion_normal import distribucion_normal
from utils.archivo import cargar_semillas, exportar_tabla
from utils.visualizacion import histograma_generador, mostrar_tabla


def separador(titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")


# ── 1. Cuadrados Medios ──────────────────────────────────────────────────
separador("1. CUADRADOS MEDIOS")
xi, ri = cuadrados_medios(semilla=5735, cantidad=20)
datos = [[i+1, xi[i], ri[i]] for i in range(len(xi))]
mostrar_tabla(datos, ["i", "Xi", "ri"], titulo="Cuadrados Medios (semilla=5735)")
histograma_generador(ri, "Cuadrados Medios")
print(f"  Generados: {len(ri)} números")

# ── 2. Congruencial Lineal ───────────────────────────────────────────────
separador("2. CONGRUENCIAL LINEAL")
xi, ri = congruencial_lineal(semilla=7, a=5, c=3, m=16, cantidad=20)
datos = [[i+1, xi[i], ri[i]] for i in range(len(xi))]
mostrar_tabla(datos, ["i", "Xi", "ri"], titulo="Congruencial Lineal (a=5, c=3, m=16)")
histograma_generador(ri, "Congruencial Lineal")

# Verificación manual: X1 = (5*7 + 3) % 16 = 38 % 16 = 6
assert xi[0] == 6, f"Error: X1 debería ser 6, fue {xi[0]}"
print("  ✓ Verificación manual: X1 = (5*7+3)%16 = 6 ✓")

# ── 3. Congruencial Multiplicativo ───────────────────────────────────────
separador("3. CONGRUENCIAL MULTIPLICATIVO")
xi, ri = congruencial_multiplicativo(semilla=7, a=5, m=16, cantidad=20)
datos = [[i+1, xi[i], ri[i]] for i in range(len(xi))]
mostrar_tabla(datos, ["i", "Xi", "ri"], titulo="Congruencial Multiplicativo (a=5, m=16)")
histograma_generador(ri, "Congruencial Multiplicativo")

# Verificación: X1 = (5*7) % 16 = 35 % 16 = 3
assert xi[0] == 3, f"Error: X1 debería ser 3, fue {xi[0]}"
print("  ✓ Verificación manual: X1 = (5*7)%16 = 3 ✓")

# ── 4. Congruencial Aditivo ──────────────────────────────────────────────
separador("4. CONGRUENCIAL ADITIVO")
semillas_init = [65, 89, 91, 53, 78, 15, 47, 22]
xi, ri = congruencial_aditivo(semillas=semillas_init, m=100, cantidad=20)
datos = [[i+1, xi[i], ri[i]] for i in range(len(xi))]
mostrar_tabla(datos, ["i", "Xi", "ri"], titulo="Congruencial Aditivo (8 semillas, m=100)")
histograma_generador(ri, "Congruencial Aditivo")

# Verificación: X8 = (X7 + X0) % 100 = (22 + 65) % 100 = 87
assert xi[0] == 87, f"Error: X8 debería ser 87, fue {xi[0]}"
print("  ✓ Verificación manual: X8 = (22+65)%100 = 87 ✓")

# ── 5. Distribución Uniforme ─────────────────────────────────────────────
separador("5. DISTRIBUCIÓN UNIFORME [2, 10)")
# Usar ri del congruencial lineal como base
_, ri_base = congruencial_lineal(semilla=37, a=7, c=13, m=1024, cantidad=200)
uniformes = distribucion_uniforme(ri_base, a=2.0, b=10.0)
datos = [[i+1, uniformes[i]] for i in range(min(20, len(uniformes)))]
mostrar_tabla(datos, ["i", "Xi"], titulo="Uniforme [2, 10)")
histograma_generador(uniformes, "Distribución Uniforme [2, 10)")
print(f"  Rango: [{min(uniformes):.4f}, {max(uniformes):.4f}]")

# ── 6. Distribución Normal ───────────────────────────────────────────────
separador("6. DISTRIBUCIÓN NORMAL N(50, 10²)")
_, ri_base = congruencial_lineal(semilla=37, a=7, c=13, m=1024, cantidad=200)
normales = distribucion_normal(ri_base, mu=50.0, sigma=10.0)
datos = [[i+1, normales[i]] for i in range(min(20, len(normales)))]
mostrar_tabla(datos, ["i", "Xi"], titulo="Normal N(50, 10²)")
histograma_generador(normales, "Distribución Normal N(50, 10²)")
media = sum(normales) / len(normales)
print(f"  Media calculada: {media:.4f} (esperada: 50.0)")

# ── 7. Carga de semillas desde archivo ───────────────────────────────────
separador("7. CARGA DE SEMILLAS DESDE ARCHIVO")
semillas = cargar_semillas("datos/semillas_ejemplo.csv")
print(f"  Semillas: {semillas}")

# ── 8. Exportar tabla ────────────────────────────────────────────────────
separador("8. EXPORTAR TABLA")
_, ri_export = congruencial_lineal(semilla=7, a=5, c=3, m=16, cantidad=10)
xi_export, _ = congruencial_lineal(semilla=7, a=5, c=3, m=16, cantidad=10)
tabla_export = [[i+1, xi_export[i], ri_export[i]] for i in range(len(xi_export))]
exportar_tabla(tabla_export, "resultados/prueba_exportacion.csv", ["i", "Xi", "ri"])

print("\n" + "="*60)
print("  ✅ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
print("="*60)
print("  Histogramas guardados en: resultados/")
print("  CSV de prueba guardado en: resultados/prueba_exportacion.csv")
