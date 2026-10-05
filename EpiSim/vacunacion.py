def generar_tasa_vacunacion(r):
    """
    Genera una tasa de vacunación
    en el intervalo U(0.3, 0.7).
    """

    return 0.3 + (0.7 - 0.3) * r


def generar_efectividad_vacuna(r):
    """
    Genera la efectividad de la vacuna
    en el intervalo U(0.80, 0.95).
    """

    return 0.80 + (0.95 - 0.80) * r


def aplicar_vacunacion(
    poblacion,
    tasa_vacunacion,
    generador
):
    """
    Asigna vacunación a individuos susceptibles
    según la tasa definida.
    """

    for individuo in poblacion:

        if individuo["estado"] != "S":
            continue

        r = generador.siguiente()

        if r < tasa_vacunacion:
            individuo["vacunado"] = True
        else:
            individuo["vacunado"] = False


def calcular_factor_vacunacion(
    individuo,
    efectividad_vacuna
):
    """
    Calcula el factor que modifica la probabilidad
    de transmisión según el estado de vacunación.
    """

    if individuo["vacunado"]:
        return 1.0 - efectividad_vacuna

    return 1.0