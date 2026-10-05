# Módulo Integrado de Generación de Números Pseudoaleatorios

**Taller 1 — Simulación Computacional**

Biblioteca modular que implementa desde cero múltiples generadores de números
pseudoaleatorios y los somete a validación estadística.

## Cuadro Técnico

| Aspecto | Detalle |
|---|---|
| **Lenguaje** | Python 3.8+ |
| **Sistema operativo** | Windows / Linux / macOS |
| **Dependencias** | `matplotlib` (solo para gráficos) |

## Estructura del Proyecto

```
Taller1 SC/
├── main.py                              # Punto de entrada (menú interactivo)
├── generadores/                         # Paquete de generadores
│   ├── __init__.py
│   ├── cuadrados_medios.py              # Método de Cuadrados Medios
│   ├── congruencial_lineal.py           # Congruencial Lineal
│   ├── congruencial_multiplicativo.py   # Congruencial Multiplicativo
│   ├── congruencial_aditivo.py          # Congruencial Aditivo
│   ├── distribucion_uniforme.py         # Distribución Uniforme [a, b)
│   └── distribucion_normal.py           # Distribución Normal (Box-Muller)
├── validaciones/                        # Pruebas estadísticas (placeholder)
│   ├── __init__.py
│   └── README.md                        # Guía de integración
├── utils/                               # Utilidades compartidas
│   ├── __init__.py
│   ├── archivo.py                       # Lectura/escritura de archivos
│   └── visualizacion.py                 # Histogramas y tablas
├── datos/
│   └── semillas_ejemplo.csv             # Semillas de ejemplo
├── resultados/                          # Gráficos y exportaciones generadas
├── README.md                            # Este archivo
└── tarea.txt                            # Enunciado original
```

## Requisitos Previos

- **Python 3.8 o superior** instalado.
- **matplotlib** (única dependencia externa, solo para gráficos).

> Para verificar que tienes Python instalado, abre una terminal y escribe:
> ```bash
> python --version
> ```
> o en Linux/macOS:
> ```bash
> python3 --version
> ```

## Paso a Paso — Instalación y Ejecución

### 1. Clonar o descargar el proyecto

```bash
git clone https://github.com/jdCarrillo15/Generadores-de-n-meros-pseudoaleatorios.git
```

O descarga el ZIP desde GitHub y descomprímelo.

### 2. Instalar dependencias

**Windows** (CMD o PowerShell):
```bash
pip install matplotlib
```

**Linux / macOS** (Terminal):
```bash
pip3 install matplotlib
```

### 3. Ejecutar el programa

**Windows:**
```bash
python main.py
```

**Linux / macOS:**
```bash
python3 main.py
```

Se abrirá el menú interactivo en la terminal:

```
╔═══════════════════════════════════════════════════════╗
║   GENERADOR DE NÚMEROS PSEUDOALEATORIOS              ║
╠═══════════════════════════════════════════════════════╣
║   1. Configurar semillas                             ║
║   2. Seleccionar y ejecutar generador                ║
║   3. Ver resultados (tabla)                          ║
║   4. Generar histogramas                             ║
║   5. Exportar resultados a CSV                       ║
║   6. Validación estadística (pendiente)              ║
║   0. Salir                                           ║
╚═══════════════════════════════════════════════════════╝
```

### 4. Ejemplo rápido de uso

1. **Opción 1** → Cargar semillas desde archivo → escribir `datos/semillas_ejemplo.csv`
2. **Opción 2** → Seleccionar generador → `2` (Congruencial Lineal) → ingresar parámetros (ej: a=5, c=3, m=16, cantidad=100)
3. **Opción 3** → Ver la tabla de números generados en consola
4. **Opción 4** → Generar histograma → se guarda automáticamente en `resultados/`
5. **Opción 5** → Exportar a CSV → se guarda en `resultados/`

### 5. Ver los resultados

Los archivos generados se guardan en la carpeta `resultados/`:

```
resultados/
├── hist_congruencial_lineal.png       ← Histograma de frecuencias
├── hist_cuadrados_medios.png          ← Histograma de frecuencias
├── congruencial_lineal.csv            ← Tabla exportada
└── ...
```

- **Histogramas (.png)**: Abrirlos con cualquier visor de imágenes.
- **Tablas (.csv)**: Abrirlas con Excel, Google Sheets, LibreOffice Calc, o un editor de texto.

## Uso como biblioteca

```python
from generadores import cuadrados_medios, congruencial_lineal
from generadores import distribucion_uniforme, distribucion_normal

# Cuadrados Medios
xi, ri = cuadrados_medios(semilla=5735, cantidad=100)

# Congruencial Lineal
xi, ri = congruencial_lineal(semilla=7, a=5, c=3, m=16, cantidad=100)

# Transformar a Uniforme [2, 10)
uniformes = distribucion_uniforme(ri, a=2.0, b=10.0)

# Transformar a Normal N(50, 10²)
normales = distribucion_normal(ri, mu=50.0, sigma=10.0)
```

## Generadores Disponibles

### 1. Cuadrados Medios (`cuadrados_medios`)
- **Fórmula**: Elevar semilla al cuadrado, extraer dígitos centrales.
- **Parámetros**: `semilla`, `cantidad`, `n_digitos` (opcional, auto-detectado).
- **Nota**: Detecta ciclos automáticamente.

### 2. Congruencial Lineal (`congruencial_lineal`)
- **Fórmula**: X_{n+1} = (a · X_n + c) mod m
- **Parámetros**: `semilla`, `a`, `c`, `m`, `cantidad`.

### 3. Congruencial Multiplicativo (`congruencial_multiplicativo`)
- **Fórmula**: X_{n+1} = (a · X_n) mod m  (c = 0)
- **Parámetros**: `semilla`, `a`, `m`, `cantidad`.

### 4. Congruencial Aditivo (`congruencial_aditivo`)
- **Fórmula**: X_n = (X_{n-j} + X_{n-k}) mod m
- **Parámetros**: `semillas` (lista), `m`, `cantidad`, `j` (opcional, default=1).

### 5. Distribución Uniforme (`distribucion_uniforme`)
- **Fórmula**: X = a + (b - a) · ri
- **Parámetros**: `numeros_base` (lista de ri), `a`, `b`.

### 6. Distribución Normal (`distribucion_normal`)
- **Método**: Box-Muller.
- **Fórmula**: Z = √(-2·ln(U1)) · cos(2π·U2), X = μ + σ·Z
- **Parámetros**: `numeros_base` (lista de ri), `mu`, `sigma`.

## Formato de Archivos de Semillas

### .txt
```
# Comentarios con #
5735
1234
42
```

### .csv
```csv
semilla,descripcion
5735,Semilla para Cuadrados Medios
1234,Semilla genérica
42,Semilla alternativa
```

## Validaciones (Pendiente)

Ver `validaciones/README.md` para la guía de integración. Pruebas esperadas:
- Prueba de medias
- Prueba de varianza
- Prueba Chi-cuadrado
- Prueba Kolmogorov-Smirnov (KS)
- Prueba de Póker
- Prueba de rachas (runs test)
