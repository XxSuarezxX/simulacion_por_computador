"""
Transformación a Distribución Normal — Método de Box-Muller.

Fórmula:
    Dados U1, U2 ∈ (0, 1) (uniformes independientes):

    Z0 = √(-2 · ln(U1)) · cos(2π · U2)
    Z1 = √(-2 · ln(U1)) · sin(2π · U2)

    Luego se escala:
    X = μ + σ · Z

Produce pares de variables normales estándar N(0, 1) que luego se
transforman a N(μ, σ²) mediante escala y desplazamiento.

Nota: Solo usa math.sqrt, math.log, math.cos, math.sin — funciones
matemáticas puras, NO generación aleatoria.

Referencia:
    Box, G.E.P. & Muller, M.E. (1958). "A note on the generation of
    random normal deviates." The Annals of Mathematical Statistics, 29(2).
"""

import math


def distribucion_normal(numeros_base, mu=0.0, sigma=1.0):
    """
    Transforma números uniformes en [0, 1) a distribución normal N(μ, σ²)
    usando el método de Box-Muller.

    Parámetros
    ----------
    numeros_base : list[float]
        Lista de números ri ∈ (0, 1) generados por cualquier generador.
        Se toman de a pares (U1, U2). Si la cantidad es impar, el último
        número se descarta.
    mu : float
        Media de la distribución normal. Por defecto 0.0.
    sigma : float
        Desviación estándar de la distribución normal. Por defecto 1.0.

    Retorna
    -------
    list[float]
        Lista de números con distribución N(μ, σ²). La longitud será
        igual a len(numeros_base) si es par, o len(numeros_base) - 1 si es impar.

    Raises
    ------
    ValueError
        Si sigma <= 0 o si la lista tiene menos de 2 números.

    Ejemplo
    -------
    >>> from generadores.congruencial_lineal import congruencial_lineal
    >>> _, ri = congruencial_lineal(semilla=7, a=5, c=3, m=16, cantidad=100)
    >>> normales = distribucion_normal(ri, mu=50.0, sigma=10.0)
    >>> print(f"Media aprox: {sum(normales)/len(normales):.2f}")
    """
    if sigma <= 0:
        raise ValueError(f"La desviación estándar sigma={sigma} debe ser positiva.")
    if len(numeros_base) < 2:
        raise ValueError("Se necesitan al menos 2 números base para Box-Muller.")

    DOS_PI = 2.0 * math.pi
    resultado = []

    # Procesar de a pares
    n_pares = len(numeros_base) // 2

    for i in range(n_pares):
        u1 = numeros_base[2 * i]
        u2 = numeros_base[2 * i + 1]

        # --- Evitar log(0): reemplazar 0.0 por valor muy pequeño ---
        if u1 == 0.0:
            u1 = 1e-10
        if u2 == 0.0:
            u2 = 1e-10

        # --- Transformación Box-Muller ---
        magnitud = math.sqrt(-2.0 * math.log(u1))
        angulo = DOS_PI * u2

        z0 = magnitud * math.cos(angulo)
        z1 = magnitud * math.sin(angulo)

        # --- Escalar a N(μ, σ²) ---
        x0 = mu + sigma * z0
        x1 = mu + sigma * z1

        resultado.append(x0)
        resultado.append(x1)

    return resultado
