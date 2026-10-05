"""
Generador Congruencial Aditivo (Fibonacci retardado).

Fórmula:
    X_n = (X_{n-j} + X_{n-k}) mod m       con j < k

    ri = X_n / m   →   ri ∈ [0, 1)

Requiere un vector de k semillas iniciales (al menos k valores).
El período puede ser muy largo dependiendo de j, k y m.

Caso particular común: j = 1, k = len(semillas), lo que produce:
    X_n = (X_{n-1} + X_{n-k}) mod m

Referencia:
    Knuth, D.E. (1997). "The Art of Computer Programming, Vol. 2:
    Seminumerical Algorithms." 3ra edición, Addison-Wesley.
"""


def congruencial_aditivo(semillas, m, cantidad, j=1):
    """
    Genera números pseudoaleatorios mediante el método congruencial aditivo.

    Fórmula: X_n = (X_{n-j} + X_{n-k}) mod m, donde k = len(semillas).

    Parámetros
    ----------
    semillas : list[int]
        Vector de semillas iniciales [X_0, X_1, ..., X_{k-1}].
        Debe contener al menos 2 valores.
    m : int
        Módulo (entero positivo).
    cantidad : int
        Cantidad de números **nuevos** a generar (sin contar las semillas).
    j : int, opcional
        Retardo menor (por defecto 1). Debe cumplir j < len(semillas).

    Retorna
    -------
    tuple[list[int], list[float]]
        (xi_lista, ri_lista) donde:
        - xi_lista: secuencia de valores X_i generados (sin las semillas iniciales).
        - ri_lista: secuencia normalizada ri = X_i / m ∈ [0, 1).

    Ejemplo
    -------
    >>> xi, ri = congruencial_aditivo(
    ...     semillas=[65, 89, 91, 53, 78, 15, 47, 22],
    ...     m=100, cantidad=10
    ... )
    """
    k = len(semillas)

    # Validar parámetros
    if k < 2:
        raise ValueError("Se necesitan al menos 2 semillas iniciales.")
    if j >= k:
        raise ValueError(f"El retardo j={j} debe ser menor que k={k} (cantidad de semillas).")

    # Copiar semillas para no modificar la lista original
    secuencia = list(semillas)

    xi_lista = []
    ri_lista = []

    for _ in range(cantidad):
        # --- Fórmula congruencial aditiva ---
        # X_n = (X_{n-j} + X_{n-k}) mod m
        nuevo = (secuencia[-j] + secuencia[-k]) % m

        secuencia.append(nuevo)
        xi_lista.append(nuevo)
        ri_lista.append(nuevo / m)

    return xi_lista, ri_lista
