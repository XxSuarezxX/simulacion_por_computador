"""
Generador Congruencial Multiplicativo.

Fórmula:
    X_{n+1} = (a · X_n) mod m

    ri = X_{n+1} / m   →   ri ∈ (0, 1)

Es un caso especial del congruencial lineal con c = 0.
La semilla debe ser coprima con m para garantizar un período largo.

Parámetros típicos (Park-Miller):
    - m = 2^31 - 1 = 2147483647
    - a = 7^5 = 16807

Referencia:
    Park, S.K. & Miller, K.W. (1988). "Random number generators:
    good ones are hard to find." Communications of the ACM, 31(10).
"""


def congruencial_multiplicativo(semilla, a, m, cantidad):
    """
    Genera números pseudoaleatorios mediante el método congruencial multiplicativo.

    Fórmula: X_{n+1} = (a * X_n) mod m   (equivalente a lineal con c = 0)

    Parámetros
    ----------
    semilla : int
        Valor inicial X_0 (entero positivo, debe ser coprimo con m).
    a : int
        Multiplicador (entero positivo).
    m : int
        Módulo (entero positivo). Define el período máximo (m - 1).
    cantidad : int
        Cantidad de números a generar.

    Retorna
    -------
    tuple[list[int], list[float]]
        (xi_lista, ri_lista) donde:
        - xi_lista: secuencia de valores X_i generados.
        - ri_lista: secuencia normalizada ri = X_i / m ∈ (0, 1).

    Ejemplo
    -------
    >>> xi, ri = congruencial_multiplicativo(semilla=7, a=5, m=16, cantidad=5)
    >>> print(xi)  # [3, 15, 11, 7, 3]
    """
    xi_lista = []
    ri_lista = []
    x = semilla

    for _ in range(cantidad):
        # --- Fórmula congruencial multiplicativa (c = 0) ---
        x = (a * x) % m

        # --- Normalizar a (0, 1) ---
        ri = x / m

        xi_lista.append(x)
        ri_lista.append(ri)

    return xi_lista, ri_lista
