"""
Generador de Números Pseudoaleatorios — Método de Cuadrados Medios.

Algoritmo:
    1. Se toma una semilla de n dígitos.
    2. Se eleva al cuadrado para obtener un número de hasta 2n dígitos.
    3. Se extraen los n dígitos centrales como nueva semilla.
    4. Se normaliza dividiendo entre 10^n para obtener ri ∈ [0, 1).
    5. Se repite hasta generar la cantidad deseada o detectar un ciclo.

Referencia:
    Von Neumann, J. (1951). "Various techniques used in connection with
    random digits." National Bureau of Standards Applied Mathematics Series, 12.
"""


def cuadrados_medios(semilla, cantidad, n_digitos=None):
    """
    Genera números pseudoaleatorios mediante el método de cuadrados medios.

    Parámetros
    ----------
    semilla : int
        Semilla inicial (entero positivo). Ejemplo: 5735.
    cantidad : int
        Cantidad de números pseudoaleatorios a generar.
    n_digitos : int, opcional
        Número de dígitos a considerar en la semilla. Si no se proporciona,
        se detecta automáticamente a partir de la semilla.

    Retorna
    -------
    tuple[list[int], list[float]]
        (xi_lista, ri_lista) donde:
        - xi_lista: secuencia de valores enteros generados (semillas sucesivas).
        - ri_lista: secuencia de valores normalizados en [0, 1).

    Notas
    -----
    - Si la semilla se repite (ciclo), la generación se detiene automáticamente.
    - Semillas con pocos dígitos tienden a degenerar rápidamente a 0.

    Ejemplo
    -------
    >>> xi, ri = cuadrados_medios(semilla=5735, cantidad=5)
    >>> print(xi)  # Secuencia de enteros generados
    >>> print(ri)  # Valores normalizados en [0, 1)
    """
    # Auto-detectar cantidad de dígitos si no se especifica
    if n_digitos is None:
        n_digitos = len(str(abs(semilla)))

    divisor = 10 ** n_digitos  # Para normalizar a [0, 1)
    doble_digitos = 2 * n_digitos  # Dígitos esperados tras elevar al cuadrado

    xi_lista = []
    ri_lista = []
    semillas_vistas = set()
    x = semilla

    for i in range(cantidad):
        # --- Detección de ciclo ---
        if x in semillas_vistas:
            print(f"  [Cuadrados Medios] Ciclo detectado en iteración {i} "
                  f"(semilla repetida: {x}). Generación detenida.")
            break
        semillas_vistas.add(x)

        # --- Paso 1: Elevar al cuadrado ---
        cuadrado = x * x

        # --- Paso 2: Rellenar con ceros a la izquierda hasta 2n dígitos ---
        cuadrado_str = str(cuadrado).zfill(doble_digitos)

        # --- Paso 3: Extraer los n dígitos centrales ---
        inicio = (len(cuadrado_str) - n_digitos) // 2
        x = int(cuadrado_str[inicio:inicio + n_digitos])

        # --- Paso 4: Normalizar a [0, 1) ---
        ri = x / divisor

        xi_lista.append(x)
        ri_lista.append(ri)

    return xi_lista, ri_lista
