"""
Utilidades de entrada/salida para semillas y resultados.

Funciones:
    - cargar_semillas: Lee semillas desde archivos .txt o .csv.
    - exportar_tabla: Exporta secuencias generadas a archivo .csv.
"""

import csv
import os


def cargar_semillas(ruta):
    """
    Carga semillas desde un archivo .txt o .csv.

    Formatos soportados:
        - .txt: Una semilla por línea (enteros).
        - .csv: Primera columna contiene las semillas (ignora encabezado si
                el primer valor no es numérico).

    Parámetros
    ----------
    ruta : str
        Ruta al archivo de semillas (.txt o .csv).

    Retorna
    -------
    list[int]
        Lista de semillas leídas como enteros.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    ValueError
        Si el archivo tiene extensión no soportada o contiene datos inválidos.

    Ejemplo
    -------
    >>> semillas = cargar_semillas("datos/semillas_ejemplo.csv")
    >>> print(semillas)  # [5735, 1234, 7, 42, ...]
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    extension = os.path.splitext(ruta)[1].lower()
    semillas = []

    if extension == ".txt":
        semillas = _cargar_txt(ruta)
    elif extension == ".csv":
        semillas = _cargar_csv(ruta)
    else:
        raise ValueError(
            f"Extensión '{extension}' no soportada. Use .txt o .csv."
        )

    if not semillas:
        raise ValueError(f"No se encontraron semillas válidas en: {ruta}")

    print(f"  [Archivo] {len(semillas)} semilla(s) cargada(s) desde '{ruta}'.")
    return semillas


def _cargar_txt(ruta):
    """Lee semillas de un archivo .txt (una semilla por línea)."""
    semillas = []
    with open(ruta, "r", encoding="utf-8") as f:
        for num_linea, linea in enumerate(f, 1):
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue  # Ignorar líneas vacías y comentarios
            try:
                semillas.append(int(linea))
            except ValueError:
                print(f"  [Archivo] Advertencia: línea {num_linea} ignorada "
                      f"(valor no entero: '{linea}').")
    return semillas


def _cargar_csv(ruta):
    """Lee semillas de la primera columna de un archivo .csv."""
    semillas = []
    with open(ruta, "r", encoding="utf-8") as f:
        lector = csv.reader(f)
        for num_linea, fila in enumerate(lector, 1):
            if not fila:
                continue
            valor = fila[0].strip()
            # Ignorar encabezado o líneas no numéricas
            try:
                semillas.append(int(valor))
            except ValueError:
                if num_linea == 1:
                    continue  # Probablemente encabezado
                print(f"  [Archivo] Advertencia: fila {num_linea} ignorada "
                      f"(valor no entero: '{valor}').")
    return semillas


def exportar_tabla(datos, ruta, encabezados=None):
    """
    Exporta datos tabulares a un archivo .csv.

    Parámetros
    ----------
    datos : list[list]
        Lista de filas, donde cada fila es una lista de valores.
        Ejemplo: [[1, 0.5], [2, 0.75], ...]
    ruta : str
        Ruta de destino para el archivo .csv.
    encabezados : list[str], opcional
        Lista de nombres de columnas. Si se proporciona, se escribe como
        primera fila del archivo.

    Ejemplo
    -------
    >>> exportar_tabla(
    ...     datos=[[1, 5735, 0.5735], [2, 8904, 0.8904]],
    ...     ruta="resultados/cuadrados_medios.csv",
    ...     encabezados=["i", "Xi", "ri"]
    ... )
    """
    # Crear directorio si no existe
    directorio = os.path.dirname(ruta)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        if encabezados:
            escritor.writerow(encabezados)
        escritor.writerows(datos)

    print(f"  [Archivo] Tabla exportada a '{ruta}' ({len(datos)} filas).")
