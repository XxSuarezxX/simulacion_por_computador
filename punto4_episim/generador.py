"""
generador.py - Fuente de números pseudoaleatorios de EpiSim (Punto 4).

Implementa el método congruencial MULTIPLICATIVO del módulo del Punto 3:

        X_{n+1} = (a * X_n) mod m ,      r_n = X_n / m  ∈ (0, 1)

con a = 48271 y m = 2^31 - 1 (primo de Mersenne, periodo completo m - 1).
No se usa random ni numpy.random: numpy solo se emplea como aritmética de arreglos.

Aceleración (sin cambiar la secuencia):
    Como c = 0, X_{n+L} = (a^L mod m) * X_n mod m. Por lo tanto, un bloque de 2^k
    valores se construye duplicando: dado un bloque de longitud L, los siguientes L
    valores son (a^L mod m) * bloque mod m. El resultado es EXACTAMENTE la misma
    secuencia que el bucle secuencial (ver _autotest), pero ~100 veces más rápido.

Subflujos disjuntos:
    Cada simulación recibe una semilla distinta obtenida saltando k*ESPACIADO posiciones
    en el ciclo: X_start = X_0 * a^(k*ESPACIADO) mod m. Así las 1.000 simulaciones usan
    tramos NO solapados del mismo ciclo (independencia práctica, sin traslapes).
"""
import numpy as np

A_DEFECTO = 48271
M_DEFECTO = 2**31 - 1
ESPACIADO = 2_000_000          # uniformes reservados por simulación (m-1)/ESPACIADO ≈ 1073 subflujos


class GeneradorCongruencial:
    """Generador congruencial multiplicativo con entrega de uniformes por bloques."""

    def __init__(self, semilla, a=A_DEFECTO, m=M_DEFECTO, tam_bloque=1 << 15):
        if tam_bloque & (tam_bloque - 1):
            raise ValueError("tam_bloque debe ser potencia de 2")
        self.a, self.m = a, m
        self.x = int(semilla) % m
        if self.x == 0:
            raise ValueError("La semilla no puede ser 0 módulo m.")
        self.tam_bloque = tam_bloque
        self._saltos = [pow(a, 1 << j, m) for j in range(tam_bloque.bit_length())]
        self._buf = np.empty(0)
        self._pos = 0
        self.consumidos = 0          # contador de uniformes entregados (auditoría)

    def _rellenar(self):
        """Construye el siguiente bloque de tam_bloque valores por duplicación."""
        m64 = np.uint64(self.m)
        bloque = np.array([self.a * self.x % self.m], dtype=np.uint64)
        j = 0
        while bloque.size < self.tam_bloque:
            bloque = np.concatenate((bloque, bloque * np.uint64(self._saltos[j]) % m64))
            j += 1
        self.x = int(bloque[-1])
        self._buf = bloque / self.m
        self._pos = 0

    def uniformes(self, n):
        """Devuelve un arreglo con n uniformes U(0,1) consecutivos de la secuencia."""
        n = int(n)
        salida = np.empty(n)
        i = 0
        while i < n:
            if self._pos >= self._buf.size:
                self._rellenar()
            k = min(n - i, self._buf.size - self._pos)
            salida[i:i + k] = self._buf[self._pos:self._pos + k]
            i += k
            self._pos += k
        self.consumidos += n
        return salida

    def siguiente(self):
        """Un único uniforme (compatibilidad con interfaces escalares)."""
        return float(self.uniformes(1)[0])


class GeneradorExterno:
    """
    Adaptador para enchufar el módulo del Punto 3 (o cualquier otro) al modelo.
    `siguiente` debe ser una función sin argumentos que devuelva un uniforme en (0,1).
    Es más lento que GeneradorCongruencial (llamadas una a una), pero cumple la misma
    interfaz (`uniformes`, `consumidos`), de modo que modelo.py no necesita cambios.
    """

    def __init__(self, siguiente):
        self._f = siguiente
        self.consumidos = 0

    def uniformes(self, n):
        self.consumidos += int(n)
        return np.fromiter((self._f() for _ in range(int(n))), dtype=float, count=int(n))


def semilla_subflujo(semilla_base, k, espaciado=ESPACIADO, a=A_DEFECTO, m=M_DEFECTO):
    """Semilla del subflujo k: salta k*espaciado posiciones desde la semilla base."""
    return (int(semilla_base) % m) * pow(a, k * espaciado, m) % m


def validar_flujo(u, alfa_z=1.96, chi_crit_k10=16.919):
    """Verificación rápida de un flujo (media, chi-cuadrado k=10, KS). Las seis pruebas
    completas están en el módulo del Punto 3; esta es solo una comprobación de cordura."""
    u = np.asarray(u)
    n = u.size
    z = (u.mean() - 0.5) / np.sqrt(1.0 / (12.0 * n))
    obs = np.bincount(np.minimum((u * 10).astype(int), 9), minlength=10)
    chi2 = float(((obs - n / 10.0) ** 2 / (n / 10.0)).sum())
    x = np.sort(u)
    i = np.arange(1, n + 1)
    d = max((i / n - x).max(), (x - (i - 1) / n).max())
    return {"media": float(u.mean()), "z_media": float(z), "chi2": chi2,
            "ks_D": float(d), "ks_crit": 1.36 / np.sqrt(n),
            "aprobado": bool(abs(z) < alfa_z and chi2 < chi_crit_k10 and d < 1.36 / np.sqrt(n))}


def _autotest():
    # 1) La versión vectorizada reproduce exactamente el bucle secuencial
    g = GeneradorCongruencial(1597)
    vec = g.uniformes(70_000)                      # cruza varios bloques
    x, sec = 1597, np.empty(70_000)
    for i in range(70_000):
        x = A_DEFECTO * x % M_DEFECTO
        sec[i] = x / M_DEFECTO
    assert np.array_equal(vec, sec), "La secuencia vectorizada difiere de la secuencial"
    # 2) Los subflujos no se solapan: el subflujo 1 empieza donde termina el tramo 0
    primero_sub1 = GeneradorCongruencial(semilla_subflujo(1597, 1)).uniformes(1)[0]
    esperado = (1597 * pow(A_DEFECTO, ESPACIADO + 1, M_DEFECTO) % M_DEFECTO) / M_DEFECTO
    assert primero_sub1 == esperado, "El subflujo 1 no comienza tras el tramo 0"
    print("Autotest OK: secuencia vectorizada == secuencial (70.000 valores) y subflujos disjuntos")
    print("Validación de 100.000 uniformes:", validar_flujo(GeneradorCongruencial(2026).uniformes(100_000)))


if __name__ == "__main__":
    _autotest()
