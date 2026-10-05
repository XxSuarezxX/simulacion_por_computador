# Módulo de Validaciones Estadísticas — Guía de Integración

Este módulo está **pendiente de implementación**. A continuación se describe la
interfaz esperada para que las pruebas se integren correctamente con el sistema
principal (`main.py`) y los generadores.

## Pruebas a implementar

| Prueba | Archivo sugerido | Función principal |
|---|---|---|
| Prueba de medias | `prueba_medias.py` | `prueba_medias(ri, alfa=0.05)` |
| Prueba de varianza | `prueba_varianza.py` | `prueba_varianza(ri, alfa=0.05)` |
| Prueba Chi-cuadrado | `prueba_chi_cuadrado.py` | `prueba_chi_cuadrado(ri, k=10, alfa=0.05)` |
| Prueba Kolmogorov-Smirnov | `prueba_ks.py` | `prueba_ks(ri, alfa=0.05)` |
| Prueba de Póker | `prueba_poker.py` | `prueba_poker(ri, alfa=0.05)` |
| Prueba de rachas | `prueba_rachas.py` | `prueba_rachas(ri, alfa=0.05)` |

## Interfaz esperada

Cada función de prueba debe:

### Entrada
- `ri` — Lista de números pseudoaleatorios en [0, 1) generados por cualquier
  generador del paquete `generadores/`.
- `alfa` — Nivel de significancia (por defecto 0.05).
- Parámetros adicionales según la prueba (ej: `k` intervalos para Chi-cuadrado).

### Salida
Cada función debe retornar un **diccionario** con la siguiente estructura:

```python
{
    "nombre": "Prueba de Medias",           # Nombre legible de la prueba
    "estadistico": 1.234,                    # Valor del estadístico calculado
    "valor_critico": 1.96,                   # Valor crítico de referencia
    "aprobada": True,                        # True si pasa la prueba
    "detalles": {                            # Datos adicionales para gráficos
        # Datos específicos de cada prueba para visualización
    }
}
```

### Ejemplo de uso esperado

```python
from generadores import congruencial_lineal
from validaciones.prueba_medias import prueba_medias

# Generar números
xi, ri = congruencial_lineal(semilla=7, a=5, c=3, m=16, cantidad=100)

# Validar
resultado = prueba_medias(ri, alfa=0.05)
print(f"¿Aprobada? {resultado['aprobada']}")
```

## Visualización

Cada prueba debe incluir una función de graficación:

```python
def graficar_prueba_medias(resultado, ruta_guardado=None):
    """Genera el gráfico correspondiente a la prueba de medias."""
    ...
```

Los gráficos se guardan en la carpeta `resultados/`.

## Integración con main.py

El menú principal (`main.py`) tiene una opción reservada (opción 8) para las
pruebas de validación. Cuando estén listas, descomentar los imports en
`validaciones/__init__.py` y actualizar la función `menu_validacion()` en
`main.py`.
