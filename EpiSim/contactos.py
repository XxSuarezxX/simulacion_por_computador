import sys
import os
import math

# Ruta al módulo de generadores pseudoaleatorios del Punto 3
ruta_generadores = os.path.abspath(
    os.path.join(os.path.dirname(__file__),"..", "Generadores-de-n-meros-pseudoaleatorios"))

sys.path.append(ruta_generadores)

from generadores import congruencial_lineal


def generar_r_contactos(semilla, cantidad):
    """
    Genera una secuencia de números pseudoaleatorios
    r_contactos en el intervalo [0, 1).

    Cada valor puede utilizarse para un individuo infectado.
    """

    _, ri = congruencial_lineal(
        semilla=semilla,
        a=1664525,
        c=1013904223,
        m=4294967296,
        cantidad=cantidad)
    return ri

def calcular_numero_contactos(r_contactos, beta_maximo=5):
    """
    Calcula el número de contactos diarios de un infectado.

    Fórmula:
    contactos = piso(r_contactos * beta_maximo)
    """
    contactos = math.floor(r_contactos * beta_maximo)
    return contactos