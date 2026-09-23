#!/usr/bin/env python3
"""Generate one HSPICE deck per chain length N for the tapered-buffer sweep.

The load is a single inverter M=F times the minimum inverter (F=14000,
~14000 * 71.3 aF = 1.0 pF from Lab 4 Part C). For a chain of N stages the
per-stage fanout is alpha = F^(1/N), so stage i (i = 0..N-1) has M = alpha^i
and the load has M = alpha^N = F. Chain length is a netlist topology change,
which .SWEEP/.ALTER can't express cleanly, so each N gets its own deck.

Usage (from lab5/):
    python3 gen_chain.py                 # writes chain_01.sp ... chain_12.sp
    python3 gen_chain.py --nmax 15
    python3 gen_chain.py --ngspice       # ngspice-flavoured decks, for a local sanity check
"""
import argparse
from pathlib import Path

HEADER = """\
* Lab 5 -- tapered inverter chain driving a 1pF load (modelled as INV with M=F)
* N = {n} stages, alpha = F^(1/N) = {alpha:.4f}
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
.include "{sub}"

.param nom_vdd=0.8
.param k=1.3
.param F=14000
.param alpha={alpha:.6f}

VDD vdd 0 DC nom_vdd
VSS vss 0 DC 0

* ideal pulse -> min-size shaping inverter, so stage 1 sees a realistic edge
V1 in0 vss PULSE(0 nom_vdd 100p 20p 20p {pw} {per})
XDRV in0 in vdd vss INV K=k

* chain: stage i is alpha^i times the minimum inverter
"""


def stage_pulse_width(n):
    # N=1 is a min inverter charging 1 pF directly (~10s of ns); N=2 has a
    # ~118x fanout in each stage. Everything else settles well within 2 ns.
    return {1: 60e-9, 2: 6e-9}.get(n, 2e-9)


def write_deck(n, out_dir, ngspice):
    alpha = 14000 ** (1.0 / n)
    pw = stage_pulse_width(n)
    per = 2 * pw
    tstop = per + 100e-12
    nodes = ["in"] + [f"out{i}" for i in range(1, n + 1)]
    lines = [HEADER.format(n=n, alpha=alpha, sub="inv.sub",
                           pw=f"{pw * 1e9:g}n", per=f"{per * 1e9:g}n")]
    for i in range(n):
        m = "1" if i == 0 else f"'pow(alpha,{i})'"
        if ngspice:
            m = f"{alpha ** i:.6f}"
        lines.append(f"X{i + 1} {nodes[i]} {nodes[i + 1]} vdd vss INV K=k M={m}")
    load_m = "'F'" if not ngspice else "14000"
    lines.append(f"\n* 1pF load: one inverter 14000x the minimum\n"
                 f"XLOAD {nodes[-1]} outload vdd vss INV K=k M={load_m}\n")

    out = nodes[-1]
    half = "'nom_vdd/2'" if not ngspice else "0.4"
    lines.append(f".tran 1p {tstop * 1e9:g}n\n")
    # CROSS makes the measure polarity-independent (odd N inverts, even N doesn't)
    lines.append(f"* tp1/tp2: chain input edge -> chain output (input of the load), 50% points")
    lines.append(f".measure tran tp1 trig v(in) val={half} cross=1 targ v({out}) val={half} cross=1")
    lines.append(f".measure tran tp2 trig v(in) val={half} cross=2 targ v({out}) val={half} cross=2")
    lines.append(f".measure tran tpd param='(tp1+tp2)/2'")
    if ngspice:
        lines.append(".control\nrun\n.endc")
    else:
        lines.append(".option post=2\n.probe tran v(in) v(" + out + ")")
    lines.append(".end\n")

    path = out_dir / f"chain_{n:02d}.sp"
    path.write_text("\n".join(lines))
    return path, alpha


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nmax", type=int, default=12, help="largest chain length to generate (default: 12)")
    ap.add_argument("--out-dir", default=".", help="directory to write decks into; must sit next to inv.sub (default: .)")
    ap.add_argument("--ngspice", action="store_true", help="emit ngspice-compatible decks instead of HSPICE")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for n in range(1, args.nmax + 1):
        path, alpha = write_deck(n, out_dir, args.ngspice)
        print(f"N={n:2d}  alpha={alpha:9.3f}  -> {path}")
