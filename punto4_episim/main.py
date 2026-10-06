"""
main.py - Ejecuta EpiSim completo: escenarios sin/con vacunación, estadísticas,
sensibilidad y gráficos.

    python main.py                       # usa config_base.txt (1.000 simulaciones por escenario)
    python main.py --n-sim 100           # 100 simulaciones (requisito de la sección "Requisitos")
    python main.py --config otro.txt --salida resultados_b
"""
import argparse
import csv
import os
import platform

import numpy as np

import analisis as an
from generador import _autotest
from modelo import cargar_config


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config_base.txt")
    ap.add_argument("--n-sim", type=int, help="sobrescribe n_simulaciones")
    ap.add_argument("--n-sens", type=int, help="sobrescribe n_sim_sensibilidad")
    ap.add_argument("--salida", default="resultados")
    ap.add_argument("--sin-sensibilidad", action="store_true")
    a = ap.parse_args()

    cfg = cargar_config(a.config)
    n = a.n_sim or int(cfg["n_simulaciones"])
    n_sens = a.n_sens or int(cfg["n_sim_sensibilidad"])
    N, umbral = int(cfg["N"]), float(cfg.get("umbral_brote", 0.05))
    os.makedirs(a.salida, exist_ok=True)
    ruta = lambda f: os.path.join(a.salida, f)

    print("== Verificación del generador ==")
    _autotest()

    print(f"\n== Escenarios ({n} simulaciones c/u, {int(cfg['dias'])} días) ==")
    rs = {}
    for clave, con in (("sin", False), ("con", True)):
        rs[clave] = an.correr(cfg, con, n)
        r = rs[clave]
        print(f"  {clave} vacunación: {r['tiempo']:.1f} s ({r['tiempo'] / n * 1000:.1f} ms/sim), "
              f"uniformes/sim máx = {int(r['uniformes'].max())}")
        if r["uniformes"].max() >= 2_000_000:
            print("  ADVERTENCIA: una simulación excedió su subflujo (posible solapamiento)")

    mem = an.medir_memoria(cfg)
    an.tabla_estadisticas({"sin_vacunacion": rs["sin"], "con_vacunacion": rs["con"]}, cfg, ruta("estadisticas.csv"))
    with open(ruta("tiempos.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "n_sim", "tiempo_total_s", "ms_por_sim", "memoria_pico_1sim_MB", "python", "so", "procesador"])
        for k in ("sin", "con"):
            w.writerow([k, n, round(rs[k]["tiempo"], 2), round(rs[k]["tiempo"] / n * 1000, 2), round(mem, 2),
                        platform.python_version(), platform.platform(), platform.processor() or platform.machine()])

    with open(ruta("validacion_teorica.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "indicador", "valor"])
        for k, con in (("sin_vacunacion", False), ("con_vacunacion", True)):
            vt = an.validacion_teorica(rs["con" if con else "sin"], N, umbral, con, cfg)
            print(f"\n== Validación teórica ({k}) ==")
            for ind, val in vt.items():
                w.writerow([k, ind, round(float(val), 4)])
                print(f"  {ind:32s} {val:.4f}")

    an.graf_curvas(rs["sin"], "Curva epidémica sin vacunación (promedio y banda 95%)", ruta("01_curvas_sin_vacunacion.png"))
    an.graf_curvas(rs["con"], "Curva epidémica con vacunación (promedio y banda 95%)", ruta("02_curvas_con_vacunacion.png"))
    an.graf_hist_picos(rs, N, umbral, ruta("03_hist_picos.png"))
    an.graf_hist(rs, "total", "Distribución del total de infectados", "Total de infectados", ruta("04_hist_total_infectados.png"))
    an.graf_hist(rs, "dia_control", "Días hasta el control (E+I = 0)", "Día", ruta("05_hist_dias_control.png"))
    an.graf_comparativo(rs, ruta("06_comparativo_escenarios.png"))

    rho = an.spearman(rs["con"])
    an.graf_spearman(rho, ruta("07_spearman.png"))
    print("\n== Spearman (con vacunación) ==")
    for p, v in sorted(rho.items(), key=lambda t: -abs(t[1])):
        print(f"  {p:22s} {v:+.3f}")

    if not a.sin_sensibilidad:
        print(f"\n== Sensibilidad un-parámetro-a-la-vez ({n_sens} sim por punto) ==")
        base, filas = an.sensibilidad(cfg, n_sens)
        an.graf_tornado(base, filas, ruta("08_tornado.png"))
        with open(ruta("sensibilidad.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["parametro", "total_en_minimo", "total_en_maximo", "swing", "base_puntos_medios"])
            for p, lo, hi in filas:
                w.writerow([p, round(lo, 1), round(hi, 1), round(abs(hi - lo), 1), round(base, 1)])
        print(f"  base (puntos medios): {base:.1f}")
        for p, lo, hi in filas:
            print(f"  {p:22s} min→{lo:8.1f}  max→{hi:8.1f}  swing {abs(hi - lo):8.1f}")

    print(f"\nResultados en: {os.path.abspath(a.salida)}")


if __name__ == "__main__":
    main()
