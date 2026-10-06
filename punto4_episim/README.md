# EpiSim – Simulación Montecarlo SEIR (Punto 4)

## Ejecución
```
pip install numpy matplotlib
python generador.py          # autotest del generador
python main.py               # 1.000 simulaciones por escenario (config_base.txt)
python main.py --n-sim 100   # 100 simulaciones
python main.py --config mi_escenario.txt --salida resultados_b
```
Salida en `resultados/`: 8 gráficos PNG, `estadisticas.csv`, `sensibilidad.csv`, `tiempos.csv`.

## Estructura
| Archivo | Rol |
|---|---|
| `generador.py` | PRNG congruencial multiplicativo (a=48271, m=2³¹−1) sin `random`/`numpy.random`; subflujos disjuntos; adaptador `GeneradorExterno` |
| `modelo.py` | `cargar_config`, `muestrear_parametros`, `simular` (contactos, selección, transmisión, progresión) |
| `analisis.py` | Lotes de simulaciones, estadísticas, Spearman, sensibilidad, gráficos |
| `main.py` | Orquestación por línea de comandos |
| `config_base.txt` | Parámetros ajustables (`clave = valor` o `clave = U(a,b)`) |

## Mecanismo estocástico (por día, por simulación)
0. **Inicio de la simulación**: 6 uniformes → parámetros `a+(b−a)r` (β, σ⁻¹, γ⁻¹, p, tasa de vacunación, efectividad). σ⁻¹ y γ⁻¹ se redondean a días enteros y son constantes durante la corrida ("sin más variabilidad"). N uniformes definen quién está vacunado (`r < tasa`). Los 10 casos índice se eligen con uniformes (`floor(r·N)`, índices distintos).
1. **Contactos**: cada infectado usa un uniforme `r`; contactos = `floor(r · β)`, con β ~ U(3, 5) muestreado por réplica (≈1.5 contactos por infectado y día).
2. **Selección**: cada contacto elige un individuo con `floor(r·N)`; si no es susceptible, el contacto se pierde (`seleccion_contacto = poblacion`).
3. **Transmisión**: `r < p · factor_vacunación`, con factor = `1 − efectividad` si el objetivo está vacunado y 1 si no. Si ocurre, S → E.
4. **Progresión determinística**: E → I tras σ⁻¹ días; I → R tras γ⁻¹ días. Al salir de I, un uniforme decide fallecimiento (`r < letalidad`).

Cada simulación k usa el subflujo k (`X₀·a^(k·2·10⁶) mod m`): 1.000 tramos disjuntos del ciclo. Los dos escenarios usan las mismas semillas (números aleatorios comunes), lo que reduce la varianza de la comparación.

## Decisiones y supuestos (documentar en el informe)
- **Paso 1 del enunciado**: con β ~ U(0.3, 0.5), `floor(r·β_máx)` da 0 contactos siempre (el propio ejemplo lo muestra). Se adoptó β ~ U(3, 5) (indicación atribuida al docente; confirmar) y `floor(r·β)` (`modo_contactos = piso_beta`). Otros modos: `literal` (usa β_máx = 5 fijo) y `estocastico` (`floor(β + r)`, pensado para el rango original).
- **Letalidad**: el enunciado pide "muertes" pero no da la probabilidad; se asumió 1 % (configurable).
- **Brote mayor**: simulación que infecta ≥ 5 % de N; las estadísticas de pico se reportan solo sobre brotes mayores.
- **Días hasta control**: primer día con E + I = 0.
- **Banda de las curvas**: percentiles 2.5–97.5 de las trayectorias; los IC del 95 % de las medias se reportan en `estadisticas.csv`.
- **Sensibilidad**: (a) un-parámetro-a-la-vez (los demás en su punto medio, el evaluado en mín y máx) y (b) correlación de Spearman en el escenario con vacunación.

## Integración con el módulo del Punto 3
`GeneradorCongruencial` implementa el método congruencial multiplicativo del Punto 3 (mismo recurrencia) y la transformación a U(a,b) del método 3.5; la versión vectorizada produce exactamente la misma secuencia que el bucle secuencial (verificado en `_autotest`). Para usar directamente las funciones de su módulo:
```python
from generador import GeneradorExterno
gen = GeneradorExterno(lambda: mi_modulo.siguiente_uniforme())   # más lento
```

## Uso de IA
Declarar explícitamente en el informe el rol de la IA en este punto (el enunciado lo exige): qué se generó con asistencia y qué decisiones técnicas tomó el equipo.

## Limitaciones
Mezcla homogénea, población cerrada y sin demografía; períodos constantes por corrida; vacunación fija al inicio; inmunidad permanente; letalidad uniforme; sin estructura por edad ni intervenciones. Posibles mejoras: heterogeneidad por edad, cuarentena/aislamiento, variantes, estructura espacial.
