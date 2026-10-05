"""
Transformación a Distribución Uniforme en [a, b).

Fórmula:
    X = a + (b - a) · ri       donde ri ∈ [0, 1)

Toma números ri generados por cualquier generador base (que producen valores
en [0, 1)) y los transforma al rango [a, b) deseado.

Referencia:
    Law, A.M. (2015). "Simulation Modeling and Analysis." 5ta edición, McGraw-Hill.
"""


def distribucion_uniforme(numeros_base, a=0.0, b=1.0):
    """
    Transforma números pseudoaleatorios en [0, 1) a distribución uniforme [a, b).

    Fórmula: X = a + (b - a) * ri

    Parámetros
    ----------
    numeros_base : list[float]
        Lista de números ri ∈ [0, 1) generados por cualquier generador.
    a : float
        Límite inferior del rango (inclusive). Por defecto 0.0.
    b : float
        Límite superior del rango (exclusive). Por defecto 1.0.

    Retorna
    -------
    list[float]
        Lista de números transformados en [a, b).

    Raises
    ------
    ValueError
        Si a >= b.

    Ejemplo
    -------
    >>> from generadores.congruencial_lineal import congruencial_lineal
    >>> _, ri = congruencial_lineal(semilla=7, a=5, c=3, m=16, cantidad=10)
    >>> uniformes = distribucion_uniforme(ri, a=2.0, b=10.0)
    >>> print(uniformes)  # Valores en [2.0, 10.0)
    """
    if a >= b:
        raise ValueError(f"El límite inferior a={a} debe ser menor que b={b}.")

    rango = b - a
    resultado = []

    for ri in numeros_base:
        # --- Transformación lineal ---
        x = a + rango * ri
        resultado.append(x)

    return resultado
