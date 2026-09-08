#!/usr/bin/env python3
"""Parse an HSPICE .mt0 measure-table file into a CSV, and plot chosen
measure columns against the swept parameter.

.mt0 is plain ASCII but line-wrapped at a fixed token count, so both the
header and each data record spill across multiple physical lines. This
reads it as a flat token stream instead of assuming a line layout:
  1. Accumulate header tokens until a line's first token parses as a
     float -- that's where the data section starts, and the token count
     so far is the column count N.
  2. Flatten every remaining token and chunk it into rows of N.

Usage (run from the repo root, one directory above lab1/):
    python3 mt0_report.py lab1/results_10p/results.mt0 -o lab1/results_10p/k_sweep_results.csv
    python3 mt0_report.py lab1/results_10p/results.mt0 -o out.csv \
        --plot tphl,tplh --plot tr,tf --plot-dir lab1/results_10p
"""
import argparse
import csv
from pathlib import Path


def is_float(tok):
    try:
        float(tok)
        return True
    except ValueError:
        return False


def parse_mt0(path):
    lines = Path(path).read_text().splitlines()
    # skip the two metadata lines ($DATA1 ..., .TITLE ...)
    body = [l for l in lines[2:] if l.strip()]

    columns = []
    data_start = 0
    for i, line in enumerate(body):
        toks = line.split()
        if toks and is_float(toks[0]):
            data_start = i
            break
        columns.extend(toks)

    all_tokens = []
    for line in body[data_start:]:
        all_tokens.extend(line.split())

    n = len(columns)
    rows = [all_tokens[i:i + n] for i in range(0, len(all_tokens), n)]
    rows = [r for r in rows if len(r) == n]
    return columns, rows


def write_csv(columns, rows, out_path, unit_suffix, skip_cols):
    keep_idx = [i for i, c in enumerate(columns) if c not in skip_cols]
    header = []
    for i in keep_idx:
        c = columns[i]
        header.append(f"{c}{unit_suffix}" if i > 0 and unit_suffix else c)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow([r[i] for i in keep_idx])
    print(f"wrote {out_path} ({len(rows)} rows, columns: {header})")


def plot_pairs(columns, rows, pairs, scale, xlabel, ylabel, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    idx = {c: i for i, c in enumerate(columns)}
    x = [float(r[0]) for r in rows]
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]

    for pair in pairs:
        fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
        for series, color in zip(pair, colors):
            y = [float(r[idx[series]]) * scale for r in rows]
            ax.plot(x, y, color=color, marker="o", ms=3, lw=1.8, label=series)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(" / ".join(pair) + f" vs. {columns[0]}")
        ax.grid(alpha=0.3, linewidth=0.6)
        ax.legend()
        fig.tight_layout()
        out_path = Path(out_dir) / f"{'_'.join(pair)}_vs_{columns[0]}.png"
        fig.savefig(out_path)
        plt.close(fig)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mt0", help="path to the .mt0 file")
    ap.add_argument("-o", "--out", required=True, help="output CSV path")
    ap.add_argument("--unit-suffix", default="_ps", help="suffix appended to measure column names (default: _ps)")
    ap.add_argument("--skip", default="temper,alter#", help="comma-separated columns to drop (default: temper,alter#)")
    ap.add_argument("--plot", action="append", default=[], help="comma-separated pair of columns to plot together, e.g. tphl,tplh; repeatable")
    ap.add_argument("--plot-dir", default=".", help="directory to write PNGs into")
    ap.add_argument("--scale", type=float, default=1e12, help="multiply measure values by this before writing/plotting (default: 1e12, seconds->ps)")
    args = ap.parse_args()

    columns, rows = parse_mt0(args.mt0)
    skip = set(args.skip.split(","))

    # scale every non-skipped, non-first column by --scale before writing
    scaled_rows = []
    for r in rows:
        nr = list(r)
        nr[0] = f"{float(r[0]):.2f}"
        for i, c in enumerate(columns):
            if i > 0 and c not in skip:
                nr[i] = f"{float(r[i]) * args.scale:.3f}"
        scaled_rows.append(nr)

    write_csv(columns, scaled_rows, args.out, args.unit_suffix, skip)

    if args.plot:
        pairs = [p.split(",") for p in args.plot]
        plot_pairs(columns, rows, pairs, args.scale, columns[0], f"time (ps)", args.plot_dir)
