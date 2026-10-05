# Estados posibles dentro del modelo SEIR
SUSCEPTIBLE = "S"
EXPUESTO = "E"
INFECTADO = "I"
RECUPERADO = "R"


def crear_poblacion(total=10000, infectados_iniciales=10):
    """
    Crea la población inicial del modelo SEIR.

    Cada individuo almacena su estado y los datos
    necesarios posteriormente para controlar la
    progresión de la enfermedad.
    """
    poblacion = []

    # Primero se crean todos como susceptibles
    for identificador in range(total):
        individuo = {
            "id": identificador,
            "estado": SUSCEPTIBLE,
            "dias_estado": 0,
            "periodo_incubacion": 0,
            "periodo_infeccioso": 0,
            "vacunado": False
        }
        poblacion.append(individuo)

    # Los primeros individuos corresponden
    # a los casos índice de la simulación
    for i in range(infectados_iniciales):
        poblacion[i]["estado"] = INFECTADO
    return poblacion

def contar_estados(poblacion):
    """
    Cuenta cuántos individuos existen actualmente
    en cada estado del modelo SEIR.
    """
    conteo = {
        "S": 0,
        "E": 0,
        "I": 0,
        "R": 0
    }

    for individuo in poblacion:
        conteo[individuo["estado"]] += 1

    return conteo