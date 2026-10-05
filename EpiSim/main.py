from simulacion import (
    ejecutar_simulacion,
    guardar_historial_csv,
    guardar_resumen_csv)

# =========================================================
# ANALIZAR RESULTADOS
# =========================================================

def analizar_resultados(
    poblacion,
    historial,
    configuracion,
    escenario):

    # =====================================================
    # PICO DE INFECTADOS
    # =====================================================

    pico = max(
        historial,
        key=lambda registro: registro["I"]
    )

    # =====================================================
    # PRIMER DÍA CON S = 0
    # =====================================================

    dia_s_cero = None

    for registro in historial:

        if registro["S"] == 0:
            dia_s_cero = registro["dia"]
            break

    # =====================================================
    # PERSONAS VACUNADAS
    # =====================================================

    personas_vacunadas = sum(
        1
        for individuo in poblacion
        if individuo["vacunado"]
    )

    # =====================================================
    # ESTADO FINAL
    # =====================================================

    final = historial[-1]

    # =====================================================
    # RESUMEN
    # =====================================================

    resumen = {
        "escenario": escenario,

        "semilla":
            configuracion["semilla"],

        "beta":
            configuracion["beta"],

        "p_base":
            configuracion["p_base"],

        "tasa_vacunacion":
            configuracion["tasa_vacunacion"],

        "efectividad_vacuna":
            configuracion["efectividad_vacuna"],

        "personas_vacunadas":
            personas_vacunadas,

        "dia_pico":
            pico["dia"],

        "pico_infectados":
            pico["I"],

        "dia_s_cero":
            dia_s_cero
            if dia_s_cero is not None
            else "No",

        "S_final":
            final["S"],

        "E_final":
            final["E"],

        "I_final":
            final["I"],

        "R_final":
            final["R"]
    }

    return resumen


# =========================================================
# MOSTRAR RESULTADOS
# =========================================================

def mostrar_resultados(
    historial,
    configuracion,
    resumen
):

    print("\n====================================")
    print(
        f"ESCENARIO: {resumen['escenario']}"
    )
    print("====================================")

    print(
        f"Semilla: "
        f"{configuracion['semilla']}"
    )

    print(
        f"Beta: "
        f"{configuracion['beta']:.4f}"
    )

    print(
        f"Probabilidad de transmisión: "
        f"{configuracion['p_base']:.4f}"
    )

    print(
        f"Tasa de vacunación: "
        f"{configuracion['tasa_vacunacion']:.4f}"
    )

    print(
        f"Efectividad de vacuna: "
        f"{configuracion['efectividad_vacuna']:.4f}"
    )

    print(
        f"Personas vacunadas: "
        f"{resumen['personas_vacunadas']}"
    )

    # =====================================================
    # ESTADO INICIAL
    # =====================================================

    print("\nEstado inicial:")

    print(
        historial[0]
    )

    # =====================================================
    # PRIMEROS 15 DÍAS
    # =====================================================

    print(
        "\n--- Primeros 15 días ---\n"
    )

    for registro in historial[:16]:

        print(
            f"Día {registro['dia']:3d}: "
            f"S={registro['S']:5d} | "
            f"E={registro['E']:5d} | "
            f"I={registro['I']:5d} | "
            f"R={registro['R']:5d}"
        )

    # =====================================================
    # PICO DE INFECTADOS
    # =====================================================

    print(
        "\nPico de infectados:"
    )

    print(
        f"Día {resumen['dia_pico']} "
        f"con "
        f"{resumen['pico_infectados']} "
        f"infectados."
    )

    # =====================================================
    # SUSCEPTIBLES
    # =====================================================

    if resumen["dia_s_cero"] == "No":

        print(
            "La población susceptible "
            "no llegó a cero."
        )

    else:

        print(
            f"Primer día con S = 0: "
            f"{resumen['dia_s_cero']}"
        )

    # =====================================================
    # ESTADO FINAL
    # =====================================================

    final = historial[-1]

    print("\nEstado final:")

    print(
        f"Día {final['dia']}: "
        f"S={final['S']} | "
        f"E={final['E']} | "
        f"I={final['I']} | "
        f"R={final['R']}"
    )


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

def main():

    print("\n====================================")
    print("       EPISIM - MODELO SEIR")
    print("====================================")

    # =====================================================
    # SEMILLA DE PRUEBA
    # =====================================================

    semilla = 12345

    # Lista donde se guardarán
    # los resúmenes de cada escenario
    resumenes = []

    # =====================================================
    # ESCENARIO CON VACUNACIÓN
    # =====================================================

    poblacion_vac, historial_vac, config_vac = (
        ejecutar_simulacion(
            semilla=semilla,
            usar_vacunacion=True
        )
    )

    resumen_vac = analizar_resultados(
        poblacion_vac,
        historial_vac,
        config_vac,
        "CON VACUNACION"
    )

    resumenes.append(
        resumen_vac
    )

    mostrar_resultados(
        historial_vac,
        config_vac,
        resumen_vac
    )

    guardar_historial_csv(
        historial_vac,
        "resultados/historial_con_vacunacion.csv"
    )

    # =====================================================
    # ESCENARIO SIN VACUNACIÓN
    # =====================================================

    poblacion_sin, historial_sin, config_sin = (
        ejecutar_simulacion(
            semilla=semilla,
            usar_vacunacion=False
        )
    )

    resumen_sin = analizar_resultados(
        poblacion_sin,
        historial_sin,
        config_sin,
        "SIN VACUNACION"
    )

    resumenes.append(
        resumen_sin
    )

    mostrar_resultados(
        historial_sin,
        config_sin,
        resumen_sin
    )

    guardar_historial_csv(
        historial_sin,
        "resultados/historial_sin_vacunacion.csv"
    )

    # =====================================================
    # GUARDAR RESUMEN GENERAL
    # =====================================================

    guardar_resumen_csv(
        resumenes,
        "resultados/resumen_simulaciones.csv"
    )

    # =====================================================
    # ARCHIVOS GENERADOS
    # =====================================================

    print("\n====================================")
    print("       ARCHIVOS GENERADOS")
    print("====================================")

    print(
        "resultados/historial_con_vacunacion.csv"
    )

    print(
        "resultados/historial_sin_vacunacion.csv"
    )

    print(
        "resultados/resumen_simulaciones.csv"
    )


# =========================================================
# INICIO DEL PROGRAMA
# =========================================================

if __name__ == "__main__":
    main()