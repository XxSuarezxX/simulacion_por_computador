import sys
import os

# Ruta al módulo de generadores pseudoaleatorios del Punto 3
ruta_generadores = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),"..", "Generadores-de-n-meros-pseudoaleatorios"))

sys.path.append(ruta_generadores)

from generadores import congruencial_lineal


def generar_periodo_incubacion(semilla):
    """
    Genera un período de incubación entero
    entre 2 y 5 días.
    """

    _, ri = congruencial_lineal(
        semilla=semilla,
        a=1664525,
        c=1013904223,
        m=4294967296,
        cantidad=1)

    r = ri[0]

    # Valores posibles: 2, 3, 4 o 5 días
    return 2 + int(r * 4)

def generar_periodo_infeccioso(semilla):
    """
    Genera un período infeccioso entero
    entre 7 y 14 días.
    """
    _, ri = congruencial_lineal(
        semilla=semilla,
        a=1664525,
        c=1013904223,
        m=4294967296,
        cantidad=1)
    r = ri[0]
    # Valores posibles: 7, 8, ..., 14 días
    return 7 + int(r * 8)

def actualizar_estado(individuo):
    """
    Avanza un día en el estado actual del individuo
    y realiza las transiciones E -> I e I -> R.
    """
    if individuo["estado"] == "E":

        individuo["dias_estado"] += 1

        if individuo["dias_estado"] >= individuo["periodo_incubacion"]:
            individuo["estado"] = "I"
            individuo["dias_estado"] = 0

    elif individuo["estado"] == "I":

        individuo["dias_estado"] += 1

        if individuo["dias_estado"] >= individuo["periodo_infeccioso"]:
            individuo["estado"] = "R"
            individuo["dias_estado"] = 0