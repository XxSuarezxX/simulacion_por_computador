"""
Generador Congruencial Lineal.

Fórmula:
    X_{n+1} = (a · X_n + c) mod m

    ri = X_{n+1} / m   →   ri ∈ [0, 1)

Parámetros típicos (Hull-Dobell):
    - m = 2^31 - 1  (primo de Mersenne)
    - a = 7^5 = 16807
    - c = 0  (en ese caso se convierte en multiplicativo)

Referencia:
    Lehmer, D.H. (1951). "Mathematical methods in large-scale computing units."
"""


def congruencial_lineal(semilla, a, c, m, cantidad):
    """
    Genera números pseudoaleatorios mediante el método congruencial lineal.

    Fórmula: X_{n+1} = (a * X_n + c) mod m

    Parámetros
    ----------
    semilla : int
        Valor inicial X_0 (entero no negativo, 0 ≤ X_0 < m).
    a : int
        Multiplicador (entero positivo).
    c : int
        Incremento (entero no negativo). Si c = 0, usar congruencial_multiplicativo.
    m : int
        Módulo (entero positivo, m > 0). Define el período máximo.
    cantidad : int
        Cantidad de números a generar.

    Retorna
    -------
    tuple[list[int], list[float]]
        (xi_lista, ri_lista) donde:
        - xi_lista: secuencia de valores X_i generados.
        - ri_lista: secuencia normalizada ri = X_i / m ∈ [0, 1).

    Ejemplo
    -------
    >>> xi, ri = congruencial_lineal(semilla=7, a=5, c=3, m=16, cantidad=10)
    >>> print(xi)  # [6, 1, 8, 11, 10, 5, 12, 15, 14, 9]
    """
    xi_lista = []
    ri_lista = []
    x = semilla

    for _ in range(cantidad):
        # --- Fórmula congruencial lineal ---
        x = (a * x + c) % m

        # --- Normalizar a [0, 1) ---
        ri = x / m

        xi_lista.append(x)
        ri_lista.append(ri)

    return xi_lista, ri_lista
