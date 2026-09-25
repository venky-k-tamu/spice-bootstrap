#!/usr/bin/env python3
"""Generate one HSPICE deck per per-stage fanout alpha for the tapered-buffer sweep.

The load is a single inverter M=F times the minimum (F=14000, ~14000 * 71.3 aF
= 1.0 pF from Lab 4 Part C) and stays fixed for every alpha. The chain has
N = round(ln F / ln alpha) stages, stage i (i = 0..N-1) has M = alpha^i, so the
last stage drives the load with fanout F / alpha^(N-1), which absorbs the
rounding of N. Chain length is a netlist topology change, which .SWEEP/.ALTER
can't express cleanly, so each alpha gets its own deck.

Every size (chain stages and the load) is applied one of two ways:
  m -- M = size, WN = 44n: parallel copies of the minimum inverter
  w -- WN = 44n * size, M = 1: one wider inverter (WP = k*WN follows)
Decks are named chain_<m|w>_a<alpha>.sp, with '.' written as 'p'
(e.g. chain_w_a3p25.sp).

The first inverter's input is driven straight from a PULSE with 5 ps edges
whose first transition is a fall; tpd is measured from that VDD/2 fall to the
VDD/2 crossing (rise or fall, depending on N) at the load's input.

Usage (from lab5/):
    python3 gen_chain.py                 # writes one deck per alpha in ALPHAS
    python3 gen_chain.py --alphas 2 3 4
    python3 gen_chain.py --scale w       # only the W-scaled decks
    python3 gen_chain.py --ngspice       # ngspice-flavoured decks, for a local sanity check
"""
import argparse
import math
from pathlib import Path

F = 14000
ALPHAS = [1.5, 2, 2.5, 3, 3.25, 3.5, 3.75, 4, 4.5, 5, 6, 7, 8, 9, 10, 14000]
SLEW = 5e-12  # PULSE rise/fall time (0-100%)
WN_MIN = 44e-9  # must match the WN default in inv.sub

HEADER = """\
* Lab 5 -- tapered inverter chain driving a 1pF load (modelled as INV of size F)
* sizing by {how}
* alpha = {alpha:g}, N = round(ln F / ln alpha) = {n} stages
* last stage fanout into the load = F / alpha^(N-1) = {last_fo:.4g}
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
.include "{sub}"

.param nom_vdd=0.8
.param k=1.3
.param F={F}
.param alpha={alpha:g}

VDD vdd 0 DC nom_vdd
VSS vss 0 DC 0

* input of the first inverter: starts at VDD, single falling edge with 5ps slew
V1 in vss PULSE({vhi} 0 100p {slew} {slew} {pw} {per})

* chain: stage i is alpha^i times the minimum inverter
"""
HOW = {"m": "M (parallel copies of the min inverter, WN = 44n)",
       "w": "W (WN = 44n * size, M = 1)"}


def label(alpha):
    return f"{alpha:g}".replace(".", "p")


def n_stages(alpha):
    return max(1, round(math.log(F) / math.log(alpha)))


def sim_time(n, scale):
    # N=1 is a min inverter charging 1 pF directly (~10s of ns). M-sized chains
    # finish their first transition well within 3 ns; W-sized ones are much
    # slower because a single wide finger carries a large gate resistance
    # (rgatemod=1, Rg ~ rshg*W/(3L)), so they get a longer window.
    if n == 1:
        return 60e-9
    return 3e-9 if scale == "m" else 20e-9


def size_arg(scale, size_expr, size_val, ngspice):
    """Instance parameter that makes an INV size_expr times the minimum."""
    if scale == "m":
        return f"M={size_val:.6f}" if ngspice else f"M={size_expr}"
    if ngspice:
        return f"WN={WN_MIN * size_val:.6e}"
    return f"WN='{WN_MIN * 1e9:g}n*{size_expr.strip(chr(39))}'"


def write_deck(alpha, scale, out_dir, ngspice):
    n = n_stages(alpha)
    last_fo = F / alpha ** (n - 1)
    tstop = sim_time(n, scale)
    nodes = ["in"] + [f"out{i}" for i in range(1, n + 1)]
    lines = [HEADER.format(how=HOW[scale], alpha=alpha, n=n, last_fo=last_fo, sub="inv.sub", F=F,
                           vhi="0.8" if ngspice else "nom_vdd", slew=f"{SLEW * 1e12:g}p",
                           pw=f"{tstop * 1e9:g}n", per=f"{2 * tstop * 1e9:g}n")]
    for i in range(n):
        size = "1" if i == 0 else f"'pow(alpha,{i})'"
        arg = size_arg(scale, size, alpha ** i, ngspice)
        lines.append(f"X{i + 1} {nodes[i]} {nodes[i + 1]} vdd vss INV K=k {arg}")
    lines.append(f"\n* 1pF load: one inverter {F}x the minimum\n"
                 f"XLOAD {nodes[-1]} outload vdd vss INV K=k {size_arg(scale, chr(39) + 'F' + chr(39), F, ngspice)}\n")

    out = nodes[-1]
    half = "'nom_vdd/2'" if not ngspice else "0.4"
    lines.append(f".tran 0.1p {tstop * 1e9:g}n\n")
    # CROSS on the target makes the measure polarity-independent (odd N rises, even N falls)
    lines.append("* tpd: VDD/2 fall at the first inverter's input -> VDD/2 at the load's input")
    lines.append(f".measure tran tpd trig v(in) val={half} fall=1 targ v({out}) val={half} cross=1")
    if ngspice:
        lines.append(".control\nrun\n.endc")
    else:
        lines.append(".option post=2\n.probe tran v(in) v(" + out + ")")
    lines.append(".end\n")

    path = out_dir / f"chain_{scale}_a{label(alpha)}.sp"
    path.write_text("\n".join(lines))
    return path, n, last_fo


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--alphas", type=float, nargs="+", default=ALPHAS, help="per-stage fanouts to generate")
    ap.add_argument("--scale", choices=["m", "w", "both"], default="both",
                    help="size stages with M, with W, or write both sets (default: both)")
    ap.add_argument("--out-dir", default=".", help="directory to write decks into; must sit next to inv.sub (default: .)")
    ap.add_argument("--ngspice", action="store_true", help="emit ngspice-compatible decks instead of HSPICE")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for scale in (["m", "w"] if args.scale == "both" else [args.scale]):
        for alpha in args.alphas:
            path, n, last_fo = write_deck(alpha, scale, out_dir, args.ngspice)
            print(f"{scale}  alpha={alpha:8g}  N={n:2d}  last fanout={last_fo:8.3f}  -> {path}")
