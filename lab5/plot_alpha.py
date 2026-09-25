#!/usr/bin/env python3
"""Collect tpd from every results/chain_[<C>pF_]<m|w>_a<alpha>.mt0 and plot delay vs alpha.

The sizing mode (m = parallel copies via M, w = wider devices via WN) and alpha
come from the filename ('p' for '.'); N is recomputed from alpha the same way
gen_chain.py does, so the decks don't need to emit either as a measure. The M-
and W-sized sweeps each get their own plot.

Usage (from lab5/, after run_all.sh):
    python3 plot_alpha.py                      # -> results/alpha_delay.csv, results/delay_vs_alpha_{m,w}.png
    python3 plot_alpha.py --cload 10           # -> results/alpha_delay_10pF.csv, results/delay_vs_alpha_10pF_{m,w}.png
"""
import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mt0_report import parse_mt0  # noqa: E402
from gen_chain import F_PER_PF, n_stages, prefix  # noqa: E402

STYLE = {"m": ("sized by M", "#2b6cb0", "o"),
         "w": ("sized by W", "#c05621", "s")}


def collect(results_dir, cload):
    """{scale: [(N, alpha, tpd_ps), ...] sorted by alpha}"""
    F = round(F_PER_PF * cload)
    pattern = re.compile(rf"chain_{re.escape(prefix(cload))}([mw])_a([\dp]+)\.mt0")
    series = {}
    for mt0 in sorted(Path(results_dir).glob("chain_*.mt0")):
        match = pattern.fullmatch(mt0.name)
        if not match:  # another load's results
            continue
        scale, alpha = match.groups()
        alpha = float(alpha.replace("p", "."))
        columns, data = parse_mt0(mt0)
        rec = dict(zip(columns, data[0]))
        series.setdefault(scale, []).append((n_stages(alpha, F), alpha, float(rec["tpd"]) * 1e12))
    return {s: sorted(rows, key=lambda r: r[1]) for s, rows in series.items()}


def plot(scale, rows, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    name, color, marker = STYLE[scale]
    # alpha <= 10 only: alpha = F (a min inverter driving the load directly) is
    # off the scale and stays in the table
    rows = [r for r in rows if r[1] <= 10]
    best = min(rows, key=lambda r: r[2])
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=150)
    ax.plot([r[1] for r in rows], [r[2] for r in rows], color=color,
            marker=marker, ms=5, mfc="white", mew=1.3, lw=1.4)
    ax.plot(best[1], best[2], marker=marker, ms=7, color=color, zorder=3)
    ax.set_xlabel("α")
    ax.set_ylabel("delay (ps)")
    ax.grid(alpha=0.3, linewidth=0.6)
    fig.tight_layout()
    fig.savefig(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default="results", help="directory holding chain_*_a*.mt0 (default: results)")
    ap.add_argument("--cload", type=float, default=1, help="load capacitance in pF (default: 1)")
    args = ap.parse_args()

    series = collect(args.results, args.cload)
    tag = prefix(args.cload)
    csv_path = Path(args.results) / f"alpha_delay{'_' + tag.rstrip('_') if tag else ''}.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["scale", "alpha", "N", "tpd_ps"])
        for scale, rows in sorted(series.items()):
            for n, a, t in rows:
                w.writerow([scale, f"{a:g}", n, f"{t:.3f}"])
    print(f"wrote {csv_path}")
    for scale, rows in sorted(series.items()):
        plot(scale, rows, Path(args.results) / f"delay_vs_alpha_{tag}{scale}.png")
