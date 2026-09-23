#!/usr/bin/env python3
"""Collect tpd from every results/chain_NN.mt0 and plot total delay vs alpha.

alpha is recomputed from N as F^(1/N) (N comes from the filename), so the
decks don't need to emit it as a measure.

Usage (from lab5/, after run_all.sh):
    python3 plot_alpha.py                      # -> results/alpha_delay.csv, results/delay_vs_alpha.png
"""
import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mt0_report import parse_mt0  # noqa: E402

F = 14000


def collect(results_dir):
    rows = []
    for mt0 in sorted(Path(results_dir).glob("chain_*.mt0")):
        n = int(re.search(r"chain_(\d+)", mt0.name).group(1))
        columns, data = parse_mt0(mt0)
        rec = dict(zip(columns, data[0]))
        rows.append((n, F ** (1.0 / n), *(float(rec[c]) * 1e12 for c in ("tp1", "tp2", "tpd"))))
    return sorted(rows, key=lambda r: r[1])


def plot(rows, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    best = min(rows, key=lambda r: r[4])

    # left: every N on log-log; right: linear zoom around the optimum
    fig, (ax_all, ax_zoom) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=150)
    zoom = [r for r in rows if r[1] <= 12]
    for ax, sel in ((ax_all, rows), (ax_zoom, zoom)):
        ax.plot([r[1] for r in sel], [r[4] for r in sel], color="#2b2b2b",
                marker="o", ms=6, mfc="white", mew=1.3, lw=1.4)
        ax.plot(best[1], best[4], marker="o", ms=8, color="#c0392b", zorder=3)
        ax.set_xlabel("per-stage fanout alpha = F^(1/N)   (F = 14000)")
        ax.set_ylabel("total delay tpd (ps)")
        ax.grid(alpha=0.3, linewidth=0.6, which="both")
    for n, a, _, _, t in zoom:
        ax_zoom.annotate(f"N={n}", (a, t), textcoords="offset points", xytext=(0, 7),
                         ha="center", fontsize=7, color="#555")
    ax_all.set_xscale("log")
    ax_all.set_yscale("log")
    ax_all.set_title("all N (log-log)")
    ax_zoom.set_title("zoom: alpha <= 12")
    fig.suptitle(f"Inverter chain into 1 pF: min {best[4]:.1f} ps at N={best[0]}, alpha={best[1]:.2f}")
    fig.tight_layout()
    fig.savefig(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results", help="directory holding chain_NN.mt0 (default: results)")
    args = ap.parse_args()

    rows = collect(args.results)
    csv_path = Path(args.results) / "alpha_delay.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["N", "alpha", "tp1_ps", "tp2_ps", "tpd_ps"])
        for n, a, t1, t2, t in rows:
            w.writerow([n, f"{a:.3f}", f"{t1:.3f}", f"{t2:.3f}", f"{t:.3f}"])
    print(f"wrote {csv_path}")
    plot(rows, Path(args.results) / "delay_vs_alpha.png")
