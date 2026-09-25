#!/usr/bin/env python3
"""Collect tpd from every results/chain_<m|w>_a<alpha>.mt0 and plot delay vs alpha.

The sizing mode (m = parallel copies via M, w = wider devices via WN) and alpha
come from the filename ('p' for '.'); N is recomputed from alpha the same way
gen_chain.py does, so the decks don't need to emit either as a measure. The M-
and W-sized sweeps each get their own plot.

Usage (from lab5/, after run_all.sh):
    python3 plot_alpha.py                      # -> results/alpha_delay.csv, results/delay_vs_alpha_{m,w}.png
"""
import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mt0_report import parse_mt0  # noqa: E402
from gen_chain import n_stages  # noqa: E402

STYLE = {"m": ("sized by M", "#2b6cb0", "o"),
         "w": ("sized by W", "#c05621", "s")}


def collect(results_dir):
    """{scale: [(N, alpha, tpd_ps), ...] sorted by alpha}"""
    series = {}
    for mt0 in sorted(Path(results_dir).glob("chain_*_a*.mt0")):
        scale, alpha = re.search(r"chain_([mw])_a([\dp]+)\.mt0", mt0.name).groups()
        alpha = float(alpha.replace("p", "."))
        columns, data = parse_mt0(mt0)
        rec = dict(zip(columns, data[0]))
        series.setdefault(scale, []).append((n_stages(alpha), alpha, float(rec["tpd"]) * 1e12))
    return {s: sorted(rows, key=lambda r: r[1]) for s, rows in series.items()}


def plot(scale, rows, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    name, color, marker = STYLE[scale]
    best = min(rows, key=lambda r: r[2])
    # left: every alpha on log-log; right: linear zoom around the optimum
    fig, (ax_all, ax_zoom) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=150)
    zoom = [r for r in rows if r[1] <= 10]
    for ax, sel in ((ax_all, rows), (ax_zoom, zoom)):
        ax.plot([r[1] for r in sel], [r[2] for r in sel], color=color,
                marker=marker, ms=5, mfc="white", mew=1.3, lw=1.4)
        ax.plot(best[1], best[2], marker=marker, ms=7, color=color, zorder=3)
        ax.set_xlabel("per-stage fanout alpha")
        ax.set_ylabel("tpd, input fall -> load input (ps)")
        ax.grid(alpha=0.3, linewidth=0.6, which="both")
    ax_all.set_xscale("log")
    ax_all.set_yscale("log")
    ax_all.set_title("all alpha (log-log)")
    ax_zoom.set_title("zoom: alpha <= 10")
    fig.suptitle(f"Inverter chain into 1 pF, {name}: "
                 f"min {best[2]:.1f} ps at alpha={best[1]:g} (N={best[0]})", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results", help="directory holding chain_*_a*.mt0 (default: results)")
    args = ap.parse_args()

    series = collect(args.results)
    csv_path = Path(args.results) / "alpha_delay.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["scale", "alpha", "N", "tpd_ps"])
        for scale, rows in sorted(series.items()):
            for n, a, t in rows:
                w.writerow([scale, f"{a:g}", n, f"{t:.3f}"])
    print(f"wrote {csv_path}")
    for scale, rows in sorted(series.items()):
        plot(scale, rows, Path(args.results) / f"delay_vs_alpha_{scale}.png")
