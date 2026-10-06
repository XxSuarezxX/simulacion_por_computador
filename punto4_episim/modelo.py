"""
modelo.py - Núcleo del modelo EpiSim (SEIR estocástico tipo Montecarlo).

Estados por individuo: 0 = S, 1 = E, 2 = I, 3 = R (recuperado o fallecido).

Uso de números pseudoaleatorios (todos vienen de gen.uniformes, ver generador.py):
    1. Parámetros de la simulación .... 6 uniformes, transformados a U(a,b) (método 3.5)
    2. Estado de vacunación ............ N uniformes,  vacunado = r < tasa_vacunacion
    3. Casos índice .................... uniformes -> índices distintos floor(r*N)
    4. Contactos por infectado y día ... 1 uniforme por infectado: floor(r·β)
    5. Contacto -> individuo ........... 1 uniforme por contacto: floor(r*N)
    6. Transmisión ..................... 1 uniforme por contacto con susceptible: r < p*factor
    7. Desenlace al recuperarse ........ 1 uniforme por individuo: r < letalidad -> fallece
"""
import re
import numpy as np

PARAMS = ["beta", "incubacion", "periodo_infeccioso", "p_transmision",
          "tasa_vacunacion", "efectividad_vacuna"]
_RE_U = re.compile(r"U\(\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)")


def cargar_config(ruta):
    """Lee un archivo .txt con líneas `clave = valor` o `clave = U(a, b)`."""
    cfg = {}
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.split("#")[0].strip()
            if not linea:
                continue
            clave, valor = (s.strip() for s in linea.split("=", 1))
            m = _RE_U.fullmatch(valor)
            if m:
                cfg[clave] = (float(m[1]), float(m[2]))
                continue
            for conv in (int, float, str):
                try:
                    cfg[clave] = conv(valor)
                    break
                except ValueError:
                    pass
    for p in PARAMS:
        if p not in cfg:
            raise KeyError(f"Falta el parámetro '{p}' en {ruta}")
        if not isinstance(cfg[p], tuple):
            cfg[p] = (float(cfg[p]), float(cfg[p]))
    return cfg


def muestrear_parametros(cfg, gen, fijos=None):
    """Un uniforme por parámetro -> valor = a + (b-a)*r. `fijos` fuerza valores concretos
    (análisis de sensibilidad) pero consume igualmente el uniforme para mantener la
    alineación de las secuencias entre escenarios (números aleatorios comunes)."""
    r = gen.uniformes(len(PARAMS))
    par = {}
    for nombre, ri in zip(PARAMS, r):
        a, b = cfg[nombre]
        par[nombre] = fijos[nombre] if fijos and nombre in fijos else a + (b - a) * ri
    return par


def contactos_medios(beta, modo, beta_max):
    """Media teórica de contactos por infectado y día según la regla (para calcular R0)."""
    if modo == "estocastico":
        return beta
    tope = beta_max if modo == "literal" else beta
    k = np.floor(tope)
    return k - k * (k + 1) / (2.0 * tope)


def generar_contactos(cfg, gen, n_infectados, beta):
    """PASO 1. Un uniforme por infectado; devuelve el total de contactos del día.
    piso_beta:   floor(r · β), con β muestreado por réplica (β ~ U(3,5), indicación del docente)
    literal:     floor(r · β_máx), β_máx = límite superior del rango
    estocastico: floor(β + r) (media β; pensado para el rango original U(0.3, 0.5))"""
    r = gen.uniformes(n_infectados)
    modo = cfg.get("modo_contactos", "piso_beta")
    if modo == "literal":
        return int(np.floor(r * cfg["beta"][1]).sum())
    if modo == "piso_beta":
        return int(np.floor(r * beta).sum())
    return int(np.floor(beta + r).sum())


def seleccionar_contactados(cfg, gen, estado, n_contactos):
    """PASO 2. Un uniforme por contacto -> índice del individuo contactado."""
    N = estado.size
    if cfg.get("seleccion_contacto", "poblacion") == "susceptibles":
        sus = np.flatnonzero(estado == 0)
        return sus[(gen.uniformes(n_contactos) * sus.size).astype(np.int64)]
    obj = (gen.uniformes(n_contactos) * N).astype(np.int64)
    return obj[estado[obj] == 0]              # contactos con no susceptibles se pierden


def evaluar_transmision(gen, objetivos, p, factor):
    """PASO 3. Contagio si r < p · factor_vacunación. Devuelve los nuevos expuestos (únicos)."""
    if objetivos.size == 0:
        return objetivos
    ok = gen.uniformes(objetivos.size) < p * factor[objetivos]
    return np.unique(objetivos[ok])


def progresion_estados(t, estado, a_inf, a_rec, gen, letalidad):
    """Progresión determinística: E -> I y I -> R según la agenda. Al salir de I, un uniforme
    por individuo decide el fallecimiento. Devuelve (n_E_a_I, n_I_a_R, muertes_del_dia)."""
    n_ei = n_ir = muertes = 0
    for arr in a_inf[t]:
        estado[arr] = 2
        n_ei += arr.size
    for arr in a_rec[t]:
        estado[arr] = 3
        n_ir += arr.size
        muertes += int((gen.uniformes(arr.size) < letalidad).sum())
    return n_ei, n_ir, muertes


def simular(cfg, gen, con_vacunacion=True, fijos=None):
    """Ejecuta UNA simulación de T días y devuelve curvas y métricas."""
    N, T = int(cfg["N"]), int(cfg["dias"])
    I0 = int(cfg["infectados_iniciales"])
    letal = float(cfg.get("letalidad", 0.01))

    # --- Inicialización: parámetros, vacunación y casos índice -----------------------
    par = muestrear_parametros(cfg, gen, fijos)
    sigma = max(1, int(round(par["incubacion"])))            # días en E (constante en la corrida)
    gamma = max(1, int(round(par["periodo_infeccioso"])))    # días en I
    beta, p, e = par["beta"], par["p_transmision"], par["efectividad_vacuna"]
    v = par["tasa_vacunacion"] if con_vacunacion else 0.0

    vacunado = gen.uniformes(N) < v                          # cada individuo se vacuna con prob. v
    factor = np.where(vacunado, 1.0 - e, 1.0)               # factor_vacunación

    estado = np.zeros(N, dtype=np.int8)                      # 0=S, 1=E, 2=I, 3=R
    idx = np.empty(0, dtype=np.int64)
    while idx.size < I0:                                     # I0 casos índice distintos
        cand = (gen.uniformes(I0 - idx.size) * N).astype(np.int64)
        idx = np.unique(np.concatenate((idx, cand)))
    estado[idx] = 2

    # Agenda determinística: a_inf[d] entra a I el día d; a_rec[d] sale de I el día d
    L = T + sigma + gamma + 3
    a_inf = [[] for _ in range(L)]
    a_rec = [[] for _ in range(L)]
    a_rec[gamma + 1].append(idx)          # los casos índice transmiten los días 1..gamma
    nS, nE, nI, nR = N - I0, 0, I0, 0
    muertes = 0
    dia_control = np.nan
    curvas = np.zeros((4, T + 1), dtype=np.int32)
    curvas[:, 0] = (nS, nE, nI, nR)

    for t in range(1, T + 1):
        n_ei, n_ir, m_dia = progresion_estados(t, estado, a_inf, a_rec, gen, letal)
        nE -= n_ei
        nI += n_ei - n_ir
        nR += n_ir
        muertes += m_dia

        if nI > 0 and nS > 0:
            c = generar_contactos(cfg, gen, nI, beta)                    # Paso 1
            if c > 0:
                objetivos = seleccionar_contactados(cfg, gen, estado, c)  # Paso 2
                nuevos = evaluar_transmision(gen, objetivos, p, factor)   # Paso 3
                if nuevos.size:
                    estado[nuevos] = 1
                    nS -= nuevos.size
                    nE += nuevos.size
                    a_inf[t + sigma].append(nuevos)
                    a_rec[t + sigma + gamma].append(nuevos)

        curvas[:, t] = (nS, nE, nI, nR)
        if nE == 0 and nI == 0:                    # epidemia extinguida: el resto es constante
            curvas[:, t + 1:] = curvas[:, t:t + 1]
            dia_control = t
            break

    return {
        "curvas": curvas,
        "pico_dia": int(np.argmax(curvas[2])),
        "pico_mag": int(curvas[2].max()),
        "total_infectados": int(N - curvas[0, -1]),
        "muertes": muertes,
        "dia_control": dia_control,
        "params": {**par, "v_aplicada": v},
        "uniformes": gen.consumidos,
    }
