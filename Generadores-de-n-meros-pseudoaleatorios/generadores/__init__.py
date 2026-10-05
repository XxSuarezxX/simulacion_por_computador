"""
Paquete de Generadores de Números Pseudoaleatorios.

Implementa desde cero los siguientes métodos:
- Cuadrados Medios
- Congruencial Lineal
- Congruencial Multiplicativo
- Congruencial Aditivo
- Distribución Uniforme (transformación)
- Distribución Normal (Box-Muller)

Ningún generador utiliza librerías de generación aleatoria del lenguaje.
"""

from generadores.cuadrados_medios import cuadrados_medios
from generadores.congruencial_lineal import congruencial_lineal
from generadores.congruencial_multiplicativo import congruencial_multiplicativo
from generadores.congruencial_aditivo import congruencial_aditivo
from generadores.distribucion_uniforme import distribucion_uniforme
from generadores.distribucion_normal import distribucion_normal

__all__ = [
    "cuadrados_medios",
    "congruencial_lineal",
    "congruencial_multiplicativo",
    "congruencial_aditivo",
    "distribucion_uniforme",
    "distribucion_normal",
]
