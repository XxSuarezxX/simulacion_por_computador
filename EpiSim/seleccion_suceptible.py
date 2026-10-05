def seleccionar_susceptible(poblacion, r):
    """
    Selecciona aleatoriamente un individuo susceptible
    de la población utilizando un número pseudoaleatorio
    r en el intervalo [0, 1).
    """

    # Obtener únicamente los individuos susceptibles
    susceptibles = [
        individuo
        for individuo in poblacion
        if individuo["estado"] == "S"
    ]

    # Si no quedan susceptibles, no se puede seleccionar ninguno
    if len(susceptibles) == 0:
        return None

    # Convertir el número pseudoaleatorio en una posición válida
    indice = int(r * len(susceptibles))

    return susceptibles[indice]