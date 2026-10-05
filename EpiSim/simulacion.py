import sys
import os
import csv

from modelo_seir import crear_poblacion, contar_estados
from contactos import calcular_numero_contactos
from seleccion_suceptible import seleccionar_susceptible
from transmision import evaluar_transmision
from progresion import actualizar_estado
from vacunacion import (
    aplicar_vacunacion,
    calcular_factor_vacunacion
)


# =========================================================
# RUTA AL GENERADOR PSEUDOALEATORIO
# =========================================================

ruta_generadores = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "Generadores-de-n-meros-pseudoaleatorios"
    )
)

sys.path.append(ruta_generadores)

from generadores import congruencial_lineal


# =========================================================
# CARGAR PARÁMETROS DESDE CSV
# =========================================================

def cargar_parametros(
    nombre_archivo="parametros.csv"
):

    parametros = {}

    ruta_archivo = os.path.join(
        os.path.dirname(__file__),
        nombre_archivo
    )

    with open(
        ruta_archivo,
        "r",
        encoding="utf-8"
    ) as archivo:

        lector = csv.DictReader(
            archivo
        )

        for fila in lector:

            nombre = fila["parametro"]

            parametros[nombre] = {
                "valor_min": float(
                    fila["valor_min"]
                ),
                "valor_max": float(
                    fila["valor_max"]
                ),
                "tipo": fila["tipo"]
            }

    return parametros


# =========================================================
# GENERADOR PSEUDOALEATORIO CONTINUO
# =========================================================

class SecuenciaPseudoaleatoria:

    def __init__(self, semilla):

        self.estado = semilla

        self.a = 1664525
        self.c = 1013904223
        self.m = 4294967296

    def siguiente(self):

        xi, ri = congruencial_lineal(
            semilla=self.estado,
            a=self.a,
            c=self.c,
            m=self.m,
            cantidad=1
        )

        self.estado = xi[0]

        return ri[0]


# =========================================================
# GENERAR VALOR UNIFORME CONTINUO
# =========================================================

def generar_uniforme(
    r,
    minimo,
    maximo
):

    return minimo + (
        maximo - minimo
    ) * r


# =========================================================
# GENERAR VALOR UNIFORME ENTERO
# =========================================================

def generar_uniforme_entero(
    r,
    minimo,
    maximo
):

    return int(
        minimo
        + r * (
            maximo
            - minimo
            + 1
        )
    )


# =========================================================
# GENERAR PARÁMETROS INICIALES
# =========================================================

def generar_parametros_iniciales(
    generador,
    parametros
):

    r_beta = generador.siguiente()

    beta = generar_uniforme(
        r_beta,
        parametros["beta"]["valor_min"],
        parametros["beta"]["valor_max"]
    )

    r_p = generador.siguiente()

    p_base = generar_uniforme(
        r_p,
        parametros[
            "probabilidad_transmision"
        ]["valor_min"],
        parametros[
            "probabilidad_transmision"
        ]["valor_max"]
    )

    r_vacunacion = generador.siguiente()

    tasa_vacunacion = generar_uniforme(
        r_vacunacion,
        parametros[
            "tasa_vacunacion"
        ]["valor_min"],
        parametros[
            "tasa_vacunacion"
        ]["valor_max"]
    )

    r_efectividad = generador.siguiente()

    efectividad_vacuna = generar_uniforme(
        r_efectividad,
        parametros[
            "efectividad_vacuna"
        ]["valor_min"],
        parametros[
            "efectividad_vacuna"
        ]["valor_max"]
    )

    return {
        "beta": beta,
        "p_base": p_base,
        "tasa_vacunacion": tasa_vacunacion,
        "efectividad_vacuna": efectividad_vacuna
    }


# =========================================================
# SIMULAR UN DÍA
# =========================================================

def simular_dia(
    poblacion,
    generador_epidemia,
    beta,
    p_base,
    efectividad_vacuna,
    usar_vacunacion,
    parametros
):

    infectados = [
        individuo
        for individuo in poblacion
        if individuo["estado"] == "I"
    ]

    nuevos_expuestos = set()

    # =====================================================
    # PERÍODO INFECCIOSO
    # =====================================================

    for infectado in infectados:

        if infectado["periodo_infeccioso"] == 0:

            r_periodo = (
                generador_epidemia.siguiente()
            )

            infectado[
                "periodo_infeccioso"
            ] = generar_uniforme_entero(
                r_periodo,
                int(
                    parametros[
                        "periodo_infeccioso"
                    ]["valor_min"]
                ),
                int(
                    parametros[
                        "periodo_infeccioso"
                    ]["valor_max"]
                )
            )

    # =====================================================
    # CONTACTOS
    # =====================================================

    for infectado in infectados:

        r_contactos = (
            generador_epidemia.siguiente()
        )

        numero_contactos = (
            calcular_numero_contactos(
                r_contactos,
                beta_maximo=beta
            )
        )

        for _ in range(
            numero_contactos
        ):

            # ---------------------------------------------
            # SELECCIÓN DE SUSCEPTIBLE
            # ---------------------------------------------

            r_seleccion = (
                generador_epidemia.siguiente()
            )

            susceptible = (
                seleccionar_susceptible(
                    poblacion,
                    r_seleccion
                )
            )

            if susceptible is None:
                break

            # ---------------------------------------------
            # FACTOR DE VACUNACIÓN
            # ---------------------------------------------

            if usar_vacunacion:

                factor_vacunacion = (
                    calcular_factor_vacunacion(
                        susceptible,
                        efectividad_vacuna
                    )
                )

            else:

                factor_vacunacion = 1.0

            # ---------------------------------------------
            # TRANSMISIÓN
            # ---------------------------------------------

            r_transmision = (
                generador_epidemia.siguiente()
            )

            resultado = evaluar_transmision(
                susceptible=susceptible,
                r_transmision=r_transmision,
                p_base=p_base,
                factor_vacunacion=
                    factor_vacunacion
            )

            # ---------------------------------------------
            # S -> E
            # ---------------------------------------------

            if resultado["contagio"]:

                r_incubacion = (
                    generador_epidemia.siguiente()
                )

                susceptible[
                    "periodo_incubacion"
                ] = generar_uniforme_entero(
                    r_incubacion,
                    int(
                        parametros[
                            "periodo_incubacion"
                        ]["valor_min"]
                    ),
                    int(
                        parametros[
                            "periodo_incubacion"
                        ]["valor_max"]
                    )
                )

                nuevos_expuestos.add(
                    susceptible["id"]
                )

    # =====================================================
    # PROGRESIÓN E -> I -> R
    # =====================================================

    for individuo in poblacion:

        if (
            individuo["id"]
            in nuevos_expuestos
        ):
            continue

        actualizar_estado(
            individuo
        )

    return contar_estados(
        poblacion
    )


# =========================================================
# EJECUTAR SIMULACIÓN COMPLETA
# =========================================================

def ejecutar_simulacion(
    dias=None,
    semilla=12345,
    usar_vacunacion=True
):

    # =====================================================
    # CARGAR PARÁMETROS
    # =====================================================

    parametros = cargar_parametros()

    poblacion_total = int(
        parametros[
            "poblacion"
        ]["valor_min"]
    )

    infectados_iniciales = int(
        parametros[
            "infectados_iniciales"
        ]["valor_min"]
    )

    if dias is None:

        dias = int(
            parametros[
                "dias_simulacion"
            ]["valor_min"]
        )

    # =====================================================
    # CREAR POBLACIÓN
    # =====================================================

    poblacion = crear_poblacion(
        total=poblacion_total,
        infectados_iniciales=
            infectados_iniciales
    )

    # =====================================================
    # GENERADORES INDEPENDIENTES
    # =====================================================

    generador_parametros = (
        SecuenciaPseudoaleatoria(
            semilla
        )
    )

    generador_vacunacion = (
        SecuenciaPseudoaleatoria(
            semilla + 100000
        )
    )

    generador_epidemia = (
        SecuenciaPseudoaleatoria(
            semilla + 200000
        )
    )

    # =====================================================
    # PARÁMETROS PSEUDOALEATORIOS
    # =====================================================

    valores = (
        generar_parametros_iniciales(
            generador_parametros,
            parametros
        )
    )

    beta = valores["beta"]
    p_base = valores["p_base"]

    tasa_vacunacion = valores[
        "tasa_vacunacion"
    ]

    efectividad_vacuna = valores[
        "efectividad_vacuna"
    ]

    # =====================================================
    # VACUNACIÓN
    # =====================================================

    if usar_vacunacion:

        aplicar_vacunacion(
            poblacion,
            tasa_vacunacion,
            generador_vacunacion
        )

    # =====================================================
    # HISTORIAL
    # =====================================================

    historial = []

    estado_inicial = (
        contar_estados(
            poblacion
        )
    )

    historial.append({
        "dia": 0,
        "S": estado_inicial["S"],
        "E": estado_inicial["E"],
        "I": estado_inicial["I"],
        "R": estado_inicial["R"]
    })

    # =====================================================
    # SIMULAR DÍAS
    # =====================================================

    for dia in range(
        1,
        dias + 1
    ):

        resultado = simular_dia(
            poblacion=poblacion,
            generador_epidemia=
                generador_epidemia,
            beta=beta,
            p_base=p_base,
            efectividad_vacuna=
                efectividad_vacuna,
            usar_vacunacion=
                usar_vacunacion,
            parametros=parametros
        )

        historial.append({
            "dia": dia,
            "S": resultado["S"],
            "E": resultado["E"],
            "I": resultado["I"],
            "R": resultado["R"]
        })

    # =====================================================
    # CONFIGURACIÓN DE LA CORRIDA
    # =====================================================

    configuracion = {
        "semilla":
            semilla,

        "dias":
            dias,

        "poblacion":
            poblacion_total,

        "infectados_iniciales":
            infectados_iniciales,

        "beta":
            beta,

        "p_base":
            p_base,

        "usar_vacunacion":
            usar_vacunacion,

        "tasa_vacunacion":
            tasa_vacunacion
            if usar_vacunacion
            else 0.0,

        "efectividad_vacuna":
            efectividad_vacuna
            if usar_vacunacion
            else 0.0
    }

    return (
        poblacion,
        historial,
        configuracion
    )


# =========================================================
# GUARDAR HISTORIAL CSV
# =========================================================

def guardar_historial_csv(
    historial,
    nombre_archivo
):

    carpeta = os.path.dirname(
        nombre_archivo
    )

    if carpeta:
        os.makedirs(
            carpeta,
            exist_ok=True
        )

    with open(
        nombre_archivo,
        "w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        campos = [
            "dia",
            "S",
            "E",
            "I",
            "R",
            "total"
        ]

        escritor = csv.DictWriter(
            archivo,
            fieldnames=campos
        )

        escritor.writeheader()

        for registro in historial:

            total = (
                registro["S"]
                + registro["E"]
                + registro["I"]
                + registro["R"]
            )

            escritor.writerow({
                "dia": registro["dia"],
                "S": registro["S"],
                "E": registro["E"],
                "I": registro["I"],
                "R": registro["R"],
                "total": total
            })


# =========================================================
# GUARDAR RESUMEN CSV
# =========================================================

def guardar_resumen_csv(
    resumenes,
    nombre_archivo
):

    carpeta = os.path.dirname(
        nombre_archivo
    )

    if carpeta:
        os.makedirs(
            carpeta,
            exist_ok=True
        )

    campos = [
        "escenario",
        "semilla",
        "beta",
        "p_base",
        "tasa_vacunacion",
        "efectividad_vacuna",
        "personas_vacunadas",
        "dia_pico",
        "pico_infectados",
        "dia_s_cero",
        "S_final",
        "E_final",
        "I_final",
        "R_final"
    ]

    with open(
        nombre_archivo,
        "w",
        newline="",
        encoding="utf-8"
    ) as archivo:

        escritor = csv.DictWriter(
            archivo,
            fieldnames=campos
        )

        escritor.writeheader()

        for resumen in resumenes:

            escritor.writerow(
                resumen
            )