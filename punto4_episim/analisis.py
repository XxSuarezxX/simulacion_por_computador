"""
analisis.py - Ejecución de lotes de simulaciones, estadísticas, sensibilidad y gráficos.
"""
import csv
import os
import time
import tracemalloc

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from generador import GeneradorCongruencial, semilla_subflujo
from modelo import simular, PARAMS, contactos_medios

ETIQ = {"beta": "β (contactos/día)", "incubacion": "Incubación σ⁻¹", "periodo_infeccioso": "Período infeccioso γ⁻¹",
        "p_transmision": "Prob. transmisión p", "tasa_vacunacion": "Tasa de vacunación",
        "efectividad_vacuna": "Efectividad vacuna"}
COL = {"sin": "#c0392b", "con": "#2471a3"}


# ------------------------------------------------------------------ ejecución de lotes
def correr(cfg, con_vac, n_sim, fijos=None):
    """n_sim simulaciones; la simulación k usa el subflujo k (misma semilla en todos los
    escenarios -> números aleatorios comunes, comparación con menor varianza)."""
    T, base = int(cfg["dias"]), int(cfg["semilla_base"])
    res = {"curvas": np.zeros((n_sim, 4, T + 1), dtype=np.int32),
           **{k: np.zeros(n_sim) for k in ("total", "muertes", "pico_dia", "pico_mag", "dia_control", "uniformes")},
           "params": {k: np.zeros(n_sim) for k in PARAMS}}
    t0 = time.perf_counter()
    for k in range(n_sim):
        gen = GeneradorCongruencial(semilla_subflujo(base, k))
        r = simular(cfg, gen, con_vac, fijos)
        res["curvas"][k] = r["curvas"]
        res["total"][k], res["muertes"][k] = r["total_infectados"], r["muertes"]
        res["pico_dia"][k], res["pico_mag"][k] = r["pico_dia"], r["pico_mag"]
        res["dia_control"][k], res["uniformes"][k] = r["dia_control"], r["uniformes"]
        for p in PARAMS:
            res["params"][p][k] = r["params"][p]
    res["tiempo"] = time.perf_counter() - t0
    return res


def medir_memoria(cfg, con_vac=True):
    """Memoria pico (MB) de UNA simulación, con tracemalloc."""
    tracemalloc.start()
    simular(cfg, GeneradorCongruencial(semilla_subflujo(int(cfg["semilla_base"]), 0)), con_vac)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return pico / 1e6


# ------------------------------------------------------------------ estadísticas
def _resumen(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    n = x.size
    if n == 0:
        return [0] + [float("nan")] * 7
    m = x.mean()
    s = x.std(ddof=1) if n > 1 else 0.0
    se = s / np.sqrt(n)
    return [n, m, s, np.median(x), x.min(), x.max(), m - 1.96 * se, m + 1.96 * se]


def tabla_estadisticas(res_por_escenario, cfg, ruta_csv):
    N, umbral = int(cfg["N"]), float(cfg.get("umbral_brote", 0.05))
    filas = []
    for nombre, r in res_por_escenario.items():
        brote = r["total"] >= umbral * N
        filas += [
            [nombre, "Proporción de brotes mayores"] + _resumen(brote.astype(float)),
            [nombre, "Total infectados (todas)"] + _resumen(r["total"]),
            [nombre, "Total infectados (brotes mayores)"] + _resumen(r["total"][brote]),
            [nombre, "Muertes (todas)"] + _resumen(r["muertes"]),
            [nombre, "Muertes (brotes mayores)"] + _resumen(r["muertes"][brote]),
            [nombre, "Magnitud del pico de I (brotes mayores)"] + _resumen(r["pico_mag"][brote]),
            [nombre, "Día del pico de I (brotes mayores)"] + _resumen(r["pico_dia"][brote]),
            [nombre, "Días hasta control E+I=0 (controladas)"] + _resumen(r["dia_control"]),
        ]
    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "metrica", "n", "media", "desv_est", "mediana", "min", "max", "ic95_inf", "ic95_sup"])
        for fila in filas:
            w.writerow([fila[0], fila[1], fila[2]] + [round(float(v), 4) for v in fila[3:]])
    return filas


def _rangos(x):
    """Rangos con promedio en empates (para Spearman sin scipy)."""
    _, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    fin = np.cumsum(cnt)
    return ((fin - cnt + 1 + fin) / 2.0)[inv]


def spearman(res):
    y = _rangos(res["total"])
    out = {}
    for p in PARAMS:
        xr = _rangos(res["params"][p])
        out[p] = float(np.corrcoef(xr, y)[0, 1])
    return out


def sensibilidad(cfg, n):
    """Un-parámetro-a-la-vez: los demás fijos en el punto medio; el evaluado en mín y máx."""
    medios = {p: (cfg[p][0] + cfg[p][1]) / 2 for p in PARAMS}
    base = correr(cfg, True, n, fijos=medios)["total"].mean()
    filas = []
    for p in PARAMS:
        a, b = cfg[p]
        if a == b:
            continue
        v = []
        for val in (a, b):
            f = dict(medios)
            f[p] = val
            v.append(correr(cfg, True, n, fijos=f)["total"].mean())
        filas.append((p, v[0], v[1]))
    filas.sort(key=lambda t: abs(t[2] - t[1]), reverse=True)
    return base, filas


def validacion_teorica(res, N, umbral, con_vac, cfg):
    """Compara los resultados con la teoría: R0 = β·p·γ⁻¹, R_ef = R0(1 − v·e), tamaño final
    z = 1 − exp(−R z) y probabilidad de brote por proceso de ramificación 1 − R^(−I0)."""
    P = res["params"]
    gam = np.round(P["periodo_infeccioso"])
    v = P["tasa_vacunacion"] if con_vac else np.zeros(len(gam))
    cm = contactos_medios(P["beta"], cfg.get("modo_contactos", "piso_beta"), cfg["beta"][1])
    R0 = cm * P["p_transmision"] * gam
    Ref = R0 * (1 - v * P["efectividad_vacuna"])
    z = np.zeros(len(Ref))
    for i, R in enumerate(Ref):
        if R > 1:
            x = 0.9
            for _ in range(300):
                x = 1 - np.exp(-R * x)
            z[i] = x
    brote = res["total"] >= umbral * N
    return {"R0_medio": R0.mean(), "R0_min": R0.min(), "R0_max": R0.max(), "Ref_medio": Ref.mean(),
            "frac_Ref_menor_1": float((Ref <= 1).mean()),
            "P_brote_si_Ref_menor_1": float(brote[Ref <= 1].mean()) if (Ref <= 1).any() else float("nan"),
            "P_brote_si_Ref_mayor_1": float(brote[Ref > 1].mean()) if (Ref > 1).any() else float("nan"),
            "P_brote_teorica_ramificacion": float(np.where(Ref > 1, 1 - (1 / np.maximum(Ref, 1)) ** 10, 0).mean()),
            "P_brote_observada": float(brote.mean()),
            "tasa_ataque_teorica": float(z.mean()), "tasa_ataque_observada": float((res["total"] / N).mean())}


# ------------------------------------------------------------------ gráficos
def _guardar(fig, ruta):
    fig.tight_layout()
    fig.savefig(ruta, dpi=140)
    plt.close(fig)


def graf_curvas(res, titulo, ruta):
    dias = np.arange(res["curvas"].shape[2])
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, (nom, col) in enumerate(zip("SEIR", ["#2e86c1", "#f39c12", "#c0392b", "#27ae60"])):
        c = res["curvas"][:, i, :]
        ax.plot(dias, c.mean(0), color=col, label=f"{nom} (promedio)")
        ax.fill_between(dias, np.percentile(c, 2.5, 0), np.percentile(c, 97.5, 0), color=col, alpha=0.15)
    ax.set(xlabel="Día", ylabel="Individuos", title=titulo)
    ax.grid(alpha=0.3)
    ax.legend(title="Banda: percentiles 2.5–97.5")
    _guardar(fig, ruta)


def graf_hist_picos(rs, N, umbral, ruta):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for k, r in rs.items():
        b = r["total"] >= umbral * N
        ax[0].hist(r["pico_dia"][b], bins=25, alpha=0.55, color=COL[k], label=f"{k} vacunación (n={b.sum()})")
        ax[1].hist(r["pico_mag"][b], bins=25, alpha=0.55, color=COL[k], label=f"{k} vacunación")
    ax[0].set(title="Día del pico de infectados (brotes mayores)", xlabel="Día", ylabel="Frecuencia")
    ax[1].set(title="Magnitud del pico de infectados (brotes mayores)", xlabel="Individuos en I")
    for a in ax:
        a.legend()
        a.grid(alpha=0.3)
    _guardar(fig, ruta)


def graf_hist(rs, campo, titulo, xlabel, ruta, bins=40):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for k, r in rs.items():
        x = r[campo][~np.isnan(r[campo])]
        ax.hist(x, bins=bins, alpha=0.55, color=COL[k], label=f"{k} vacunación (n={x.size})")
    ax.set(title=titulo, xlabel=xlabel, ylabel="Frecuencia")
    ax.legend()
    ax.grid(alpha=0.3)
    _guardar(fig, ruta)


def graf_comparativo(rs, ruta):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [2, 1]})
    dias = np.arange(rs["sin"]["curvas"].shape[2])
    for k, r in rs.items():
        c = r["curvas"][:, 2, :]
        ax[0].plot(dias, c.mean(0), color=COL[k], label=f"I promedio, {k} vacunación")
        ax[0].fill_between(dias, np.percentile(c, 2.5, 0), np.percentile(c, 97.5, 0), color=COL[k], alpha=0.15)
    ax[0].set(title="Infectados activos: sin vs con vacunación", xlabel="Día", ylabel="I(t)")
    ax[0].legend()
    ax[0].grid(alpha=0.3)
    xs = np.arange(2)
    ancho = 0.35
    for j, (campo, nom) in enumerate((("total", "Total infectados"), ("muertes", "Muertes"))):
        m = [rs[k][campo].mean() for k in ("sin", "con")]
        e = [1.96 * rs[k][campo].std(ddof=1) / np.sqrt(rs[k][campo].size) for k in ("sin", "con")]
        ax[1].bar(xs + (j - 0.5) * ancho, m, ancho, yerr=e, capsize=4, label=nom,
                  color=["#7f8c8d", "#34495e"][j])
    ax[1].set_xticks(xs)
    ax[1].set_xticklabels(["Sin vac.", "Con vac."])
    ax[1].set(title="Promedio ± IC 95%")
    ax[1].legend()
    ax[1].grid(alpha=0.3, axis="y")
    _guardar(fig, ruta)


def graf_tornado(base, filas, ruta):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for i, (p, lo, hi) in enumerate(reversed(filas)):
        ax.barh(i, lo - base, left=base, color="#5dade2", edgecolor="k")
        ax.barh(i, hi - base, left=base, color="#ec7063", edgecolor="k")
    ax.set_yticks(range(len(filas)))
    ax.set_yticklabels([ETIQ[p] for p, _, _ in reversed(filas)])
    ax.axvline(base, color="k", lw=1)
    ax.set(title="Sensibilidad (tornado): total de infectados promedio",
           xlabel="Total infectados (azul = parámetro en mínimo, rojo = en máximo)")
    ax.grid(alpha=0.3, axis="x")
    _guardar(fig, ruta)


def graf_spearman(rho, ruta):
    orden = sorted(rho, key=lambda k: abs(rho[k]))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh([ETIQ[p] for p in orden], [rho[p] for p in orden],
            color=["#ec7063" if rho[p] > 0 else "#5dade2" for p in orden], edgecolor="k")
    ax.axvline(0, color="k", lw=1)
    ax.set(title="Correlación de Spearman con el total de infectados (escenario con vacunación)",
           xlabel="ρ de Spearman")
    ax.grid(alpha=0.3, axis="x")
    _guardar(fig, ruta)
