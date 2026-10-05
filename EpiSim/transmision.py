def evaluar_transmision(
    susceptible,
    r_transmision,
    p_base,
    factor_vacunacion=1.0
):
    """
    Evalúa si un contacto entre un infectado y un susceptible
    produce contagio.

    Si:
        r_transmision < p_efectiva

    entonces el individuo pasa de S a E.
    """

    # Calcular la probabilidad efectiva de transmisión
    p_efectiva = p_base * factor_vacunacion

    # Evaluar si ocurre el contagio
    if r_transmision < p_efectiva:

        susceptible["estado"] = "E"
        susceptible["dias_estado"] = 0

        contagio = True

    else:

        contagio = False

    return {
        "r_transmision": r_transmision,
        "p_base": p_base,
        "p_efectiva": p_efectiva,
        "contagio": contagio
    }