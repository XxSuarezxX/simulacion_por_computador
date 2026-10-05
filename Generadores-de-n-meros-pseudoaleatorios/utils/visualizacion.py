"""
Utilidades de visualización: histogramas y tablas formateadas.

Funciones:
    - histograma_generador: Genera histograma de frecuencias con matplotlib.
    - mostrar_tabla: Imprime tabla formateada en consola.
"""

import os

# matplotlib se usa SOLO para visualización, NO para generar números aleatorios.
import matplotlib
matplotlib.use("Agg")  # Backend no interactivo para guardar imágenes
import matplotlib.pyplot as plt


# ─────────────────────────────────────────────────────────────────────────────
# Directorio por defecto para guardar gráficos
# ─────────────────────────────────────────────────────────────────────────────
DIRECTORIO_RESULTADOS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "resultados"
)


def histograma_generador(numeros, titulo, ruta_guardado=None, bins=20,
                          color="#4C72B0", mostrar=False):
    """
    Genera un histograma de frecuencias para una secuencia de números.

    Parámetros
    ----------
    numeros : list[float]
        Secuencia de números a graficar.
    titulo : str
        Título del histograma.
    ruta_guardado : str, opcional
        Ruta completa donde guardar la imagen (.png). Si no se especifica,
        se guarda automáticamente en resultados/ con nombre basado en el título.
    bins : int
        Número de intervalos del histograma. Por defecto 20.
    color : str
        Color de las barras. Por defecto azul "#4C72B0".
    mostrar : bool
        Si True, muestra el gráfico en pantalla (requiere backend interactivo).

    Retorna
    -------
    str
        Ruta donde se guardó la imagen.

    Ejemplo
    -------
    >>> histograma_generador([0.1, 0.5, 0.9, 0.3], "Congruencial Lineal")
    """
    # Determinar ruta de guardado
    if ruta_guardado is None:
        nombre_archivo = titulo.lower().replace(" ", "_").replace(".", "")
        nombre_archivo = "".join(c for c in nombre_archivo if c.isalnum() or c == "_")
        ruta_guardado = os.path.join(DIRECTORIO_RESULTADOS, f"hist_{nombre_archivo}.png")

    # Crear directorio si no existe
    directorio = os.path.dirname(ruta_guardado)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio)

    # --- Crear figura ---
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(numeros, bins=bins, color=color, edgecolor="black",
            alpha=0.85, density=False)

    ax.set_title(titulo, fontsize=14, fontweight="bold")
    ax.set_xlabel("Valor generado", fontsize=12)
    ax.set_ylabel("Frecuencia", fontsize=12)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Agregar línea de frecuencia esperada (uniforme)
    if numeros:
        freq_esperada = len(numeros) / bins
        ax.axhline(y=freq_esperada, color="red", linestyle="--",
                    linewidth=1.5, label=f"Frecuencia esperada ({freq_esperada:.1f})")
        ax.legend(fontsize=10)

    # Estadísticas básicas en el gráfico
    if numeros:
        media = sum(numeros) / len(numeros)
        n = len(numeros)
        varianza = sum((x - media) ** 2 for x in numeros) / n
        texto_stats = (f"n = {n}\n"
                       f"Media = {media:.4f}\n"
                       f"Varianza = {varianza:.4f}")
        ax.text(0.97, 0.97, texto_stats, transform=ax.transAxes,
                fontsize=9, verticalalignment="top", horizontalalignment="right",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.8))

    plt.tight_layout()
    fig.savefig(ruta_guardado, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"  [Gráfico] Histograma guardado en '{ruta_guardado}'.")
    return ruta_guardado


def mostrar_tabla(datos, encabezados, titulo=None, max_filas=30):
    """
    Imprime una tabla formateada en la consola.

    Parámetros
    ----------
    datos : list[list]
        Lista de filas con los valores a mostrar.
    encabezados : list[str]
        Nombres de las columnas.
    titulo : str, opcional
        Título a mostrar sobre la tabla.
    max_filas : int
        Máximo de filas a mostrar. Si hay más, se muestran las primeras y
        últimas con indicador "...".

    Ejemplo
    -------
    >>> mostrar_tabla(
    ...     datos=[[1, 5735, 0.5735], [2, 8904, 0.8904]],
    ...     encabezados=["i", "Xi", "ri"],
    ...     titulo="Cuadrados Medios"
    ... )
    """
    if titulo:
        print(f"\n{'=' * 60}")
        print(f"  {titulo}")
        print(f"{'=' * 60}")

    # Calcular anchos de columna
    n_cols = len(encabezados)
    anchos = [len(str(h)) for h in encabezados]

    # Determinar filas a mostrar
    if len(datos) <= max_filas:
        filas_mostrar = datos
        truncado = False
    else:
        mitad = max_filas // 2
        filas_mostrar = datos[:mitad] + datos[-mitad:]
        truncado = True

    # Actualizar anchos con los datos
    for fila in filas_mostrar:
        for j in range(min(n_cols, len(fila))):
            valor_str = _formatear_valor(fila[j])
            anchos[j] = max(anchos[j], len(valor_str))

    # Construir formato
    formato = " | ".join(f"{{:<{a}}}" for a in anchos)
    separador = "-+-".join("-" * a for a in anchos)

    # Imprimir encabezados
    print(formato.format(*[str(h) for h in encabezados]))
    print(separador)

    # Imprimir filas
    if not truncado:
        for fila in filas_mostrar:
            valores = [_formatear_valor(fila[j]) if j < len(fila) else ""
                       for j in range(n_cols)]
            print(formato.format(*valores))
    else:
        mitad = max_filas // 2
        for fila in filas_mostrar[:mitad]:
            valores = [_formatear_valor(fila[j]) if j < len(fila) else ""
                       for j in range(n_cols)]
            print(formato.format(*valores))
        print(formato.format(*["..." for _ in range(n_cols)]))
        for fila in filas_mostrar[mitad:]:
            valores = [_formatear_valor(fila[j]) if j < len(fila) else ""
                       for j in range(n_cols)]
            print(formato.format(*valores))

    print(f"\nTotal: {len(datos)} filas.\n")


def _formatear_valor(valor):
    """Formatea un valor para mostrar en tabla."""
    if isinstance(valor, float):
        return f"{valor:.6f}"
    return str(valor)
