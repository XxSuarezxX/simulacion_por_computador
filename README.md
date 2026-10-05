# Simulación por Computador – EpiSim

Proyecto académico desarrollado para la asignatura **Simulación por Computador**.

El repositorio integra dos componentes principales:

1. Un módulo de generación de números pseudoaleatorios.
2. **EpiSim**, un simulador epidemiológico estocástico basado en el modelo SEIR.

El objetivo de EpiSim es representar la propagación de una enfermedad en una población de 10.000 individuos utilizando variables y parámetros generados mediante números pseudoaleatorios.

---

## Importante: autoría del generador pseudoaleatorio

El módulo ubicado en:

```text
Generadores-de-n-meros-pseudoaleatorios/
```

**no fue desarrollado originalmente por el propietario de este repositorio.**

Este componente corresponde al trabajo realizado por **jdCarrillo15** y se encuentra originalmente publicado en:

https://github.com/jdCarrillo15/Generadores-de-n-meros-pseudoaleatorios

En este repositorio se incluye como dependencia del módulo **EpiSim**, ya que el simulador utiliza el generador congruencial lineal desarrollado en dicho proyecto para producir los números pseudoaleatorios necesarios durante la simulación.

Se mantiene esta referencia con el propósito de reconocer explícitamente la autoría del código original.

---

# EpiSim

EpiSim implementa un modelo epidemiológico **SEIR** con cuatro estados:

- **S – Susceptible:** individuo que puede contraer la enfermedad.
- **E – Expuesto:** individuo infectado que se encuentra en período de incubación.
- **I – Infectado:** individuo capaz de transmitir la enfermedad.
- **R – Recuperado/Removido:** individuo que ha terminado su período infeccioso y deja de participar en la transmisión.

La transición general es:

```text
S → E → I → R
```

---

## Población inicial

Por defecto, el modelo utiliza:

```text
Población total:        10.000
Infectados iniciales:   10
Duración:               365 días
```

Estos valores pueden modificarse mediante el archivo:

```text
EpiSim/parametros.csv
```

---

## Parámetros estocásticos

El modelo utiliza diferentes distribuciones uniformes para representar la incertidumbre de los parámetros epidemiológicos.

| Parámetro | Distribución utilizada |
|---|---|
| Población | Fijo: 10.000 |
| Infectados iniciales | Fijo: 10 |
| Tasa de contacto β | U(3, 5) |
| Período de incubación | U(2, 5) días |
| Período infeccioso | U(7, 14) días |
| Probabilidad de transmisión | U(0.4, 0.6) |
| Tasa de vacunación | U(0.3, 0.7) |
| Efectividad de la vacuna | U(0.80, 0.95) |

> **Nota:** para el parámetro β se empleó el intervalo **U(3,5)** como ajuste adoptado durante el desarrollo del modelo, debido a que al aplicar directamente la expresión de contactos con valores entre 0.3 y 0.5 se obtenían valores enteros iguales a cero después de utilizar la función piso.

---

## Generación pseudoaleatoria

EpiSim utiliza el **generador congruencial lineal** disponible en el módulo desarrollado por jdCarrillo15.

La generación de números pseudoaleatorios se separó en tres secuencias independientes:

```text
Generador de parámetros
        ↓
β, p, tasa de vacunación y efectividad

Generador de vacunación
        ↓
Selección pseudoaleatoria de personas vacunadas

Generador de epidemia
        ↓
Contactos
Selección de susceptibles
Transmisión
Período de incubación
Período infeccioso
```

Esta separación permite realizar comparaciones más consistentes entre escenarios con y sin vacunación.

---

## Semillas

El sistema utiliza semillas para garantizar la reproducibilidad de las simulaciones.

Por ejemplo:

```python
semilla = 12345
```

Una misma semilla produce la misma secuencia pseudoaleatoria y, por tanto, permite reproducir una simulación.

Al utilizar semillas diferentes:

```text
12345
54321
12346
...
```

se obtienen diferentes valores para los parámetros y diferentes evoluciones de la epidemia.

Este comportamiento permite posteriormente realizar análisis mediante simulación Monte Carlo.

---

# Escenarios

El programa principal ejecuta dos escenarios.

### Con vacunación

La población susceptible puede estar vacunada y la probabilidad efectiva de transmisión se reduce según la efectividad de la vacuna.

Para una persona vacunada:

```text
factor_vacunacion = 1 - efectividad_vacuna
```

y:

```text
p_efectiva = p_base × factor_vacunacion
```

### Sin vacunación

En este escenario:

```text
factor_vacunacion = 1
```

por lo que la probabilidad de transmisión no recibe reducción asociada a la vacuna.

---

# Estructura del proyecto

```text
simulacion_por_computador/
│
├── EpiSim/
│   ├── contactos.py
│   ├── main.py
│   ├── modelo_seir.py
│   ├── parametros.csv
│   ├── progresion.py
│   ├── seleccion_suceptible.py
│   ├── simulacion.py
│   ├── transmision.py
│   ├── vacunacion.py
│   │
│   └── resultados/
│       ├── historial_con_vacunacion.csv
│       ├── historial_sin_vacunacion.csv
│       └── resumen_simulaciones.csv
│
├── Generadores-de-n-meros-pseudoaleatorios/
│   ├── generadores/
│   ├── utils/
│   ├── validaciones/
│   └── ...
│
├── .gitignore
└── README.md
```

---

# Descripción de los módulos de EpiSim

### `modelo_seir.py`

Define la población y los estados:

```text
S
E
I
R
```

También permite contabilizar cuántos individuos se encuentran en cada estado.

### `contactos.py`

Calcula el número de contactos realizados por cada individuo infectado utilizando un número pseudoaleatorio y el parámetro β.

### `seleccion_suceptible.py`

Selecciona pseudoaleatoriamente un individuo susceptible para representar un contacto.

### `transmision.py`

Evalúa si un contacto produce transmisión de la enfermedad utilizando:

```text
r_transmision
p_base
factor_vacunacion
```

### `progresion.py`

Controla la evolución:

```text
E → I
I → R
```

según los períodos de incubación e infección asignados a cada individuo.

### `vacunacion.py`

Gestiona:

- tasa de vacunación;
- efectividad de la vacuna;
- asignación pseudoaleatoria de vacunados;
- reducción de susceptibilidad.

### `simulacion.py`

Contiene la lógica principal del modelo estocástico, integra el generador pseudoaleatorio y carga los parámetros desde el archivo de configuración.

### `main.py`

Ejecuta los escenarios:

```text
CON VACUNACIÓN
SIN VACUNACIÓN
```

muestra los principales resultados y genera los archivos CSV.

---

# Archivo de configuración

Los parámetros pueden modificarse desde:

```text
EpiSim/parametros.csv
```

Ejemplo:

```csv
parametro,valor_min,valor_max,tipo
poblacion,10000,10000,fijo
infectados_iniciales,10,10,fijo
dias_simulacion,365,365,fijo
beta,3,5,uniforme
periodo_incubacion,2,5,uniforme
periodo_infeccioso,7,14,uniforme
probabilidad_transmision,0.4,0.6,uniforme
tasa_vacunacion,0.3,0.7,uniforme
efectividad_vacuna,0.80,0.95,uniforme
```

Esto permite modificar escenarios sin alterar directamente el código fuente.

---

# Ejecución

## Requisitos

- Python 3
- Git
- Sistema operativo Linux, Windows o macOS

No se utiliza la librería `random` para la generación principal de números pseudoaleatorios.

---

## Ejecutar EpiSim

Desde la raíz del repositorio:

```bash
cd EpiSim
python main.py
```

En algunos sistemas también puede utilizarse:

```bash
python3 main.py
```

---

# Resultados

Después de ejecutar el programa se generan:

```text
EpiSim/resultados/
```

con los archivos:

### `historial_con_vacunacion.csv`

Contiene por día:

```text
día
S
E
I
R
total
```

para el escenario con vacunación.

### `historial_sin_vacunacion.csv`

Contiene la evolución diaria del escenario sin vacunación.

### `resumen_simulaciones.csv`

Incluye información como:

```text
escenario
semilla
beta
p_base
tasa_vacunacion
efectividad_vacuna
personas_vacunadas
dia_pico
pico_infectados
dia_s_cero
S_final
E_final
I_final
R_final
```

Estos resultados pueden ser utilizados posteriormente para realizar análisis estadísticos y simulaciones Monte Carlo.

---

# Ejemplo de comportamiento

Utilizando la misma semilla para ambos escenarios es posible comparar el efecto de la vacunación manteniendo los parámetros epidemiológicos principales.

En una ejecución de prueba con semilla:

```text
12345
```

se obtuvieron:

```text
β = 3.0408
p = 0.4033
```

### Con vacunación

```text
Tasa de vacunación: 0.5173
Efectividad:        0.8952
Personas vacunadas: 5215

Pico de infectados:
2267 personas en el día 72

Estado final:
S = 2021
E = 0
I = 0
R = 7979
```

### Sin vacunación

```text
Personas vacunadas: 0

Pico de infectados:
7660 personas en el día 43

Primer día con S = 0:
día 38

Estado final:
S = 0
E = 0
I = 0
R = 10000
```

Estos datos corresponden únicamente a una corrida y **no deben interpretarse como conclusiones estadísticas generales**. Para obtener conclusiones robustas se requieren múltiples simulaciones independientes.

---

# Limitaciones actuales

El modelo constituye una simplificación de un proceso epidemiológico real.

Entre sus principales limitaciones se encuentran:

- población cerrada de 10.000 individuos;
- no se consideran nacimientos ni migraciones;
- no se consideran reinfecciones;
- el estado R agrupa recuperados/removidos;
- no se modela mortalidad como estado independiente;
- no existen grupos de edad;
- todos los individuos siguen reglas de contacto similares;
- no se representan redes sociales o geográficas;
- no se incluyen cuarentenas o aislamiento;
- la vacunación reduce susceptibilidad, pero no representa múltiples dosis ni pérdida de inmunidad;
- los parámetros se modelan mediante distribuciones uniformes simplificadas.

---

# Posibles mejoras

Entre las extensiones futuras se podrían implementar:

- mortalidad diferenciada;
- reinfección;
- pérdida de inmunidad;
- grupos etarios;
- redes de contactos;
- aislamiento y cuarentena;
- campañas de vacunación dinámicas;
- diferentes variantes de la enfermedad;
- parámetros epidemiológicos obtenidos de datos reales;
- optimización para grandes cantidades de simulaciones Monte Carlo.

---

# Créditos y colaboración

## EpiSim

El módulo EpiSim fue desarrollado como parte del trabajo académico de simulación epidemiológica y se integra con el módulo de números pseudoaleatorios del equipo.

## Generadores de números pseudoaleatorios

El código original del módulo:

```text
Generadores-de-n-meros-pseudoaleatorios
```

pertenece a **jdCarrillo15**.

Repositorio original:

**https://github.com/jdCarrillo15/Generadores-de-n-meros-pseudoaleatorios**

Su inclusión dentro de este repositorio tiene como finalidad permitir la integración y ejecución completa del proyecto académico.

No se pretende atribuir como propio el desarrollo original de dicho módulo.

---

# Uso académico

Este repositorio fue creado con fines académicos para la asignatura **Simulación por Computador**.

Los resultados obtenidos son producto de un modelo computacional simplificado y no deben utilizarse para realizar predicciones epidemiológicas reales.
