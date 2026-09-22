#!/usr/bin/env python3
"""Extract gate capacitance (C_gg) vs frequency and Vgate from an HSPICE .lis file.

Reads the plain-text ".print ac" table that HSPICE writes into the .lis
output (i real/i imag of vgate, volt real/volt imag of gate vs freq, one
table per Vgate sweep step) and computes C_gg = Ii / (2*pi*f*Vac), where Vac
is the AC excitation magnitude on VGATE.

HSPICE prints numbers with SI-style suffixes (e.g. "217.7078a", "1.12202k",
"3.54813g") rather than plain scientific notation, so values are parsed with
that in mind.

Usage:
    python3 extract_cgg.py [--lis results_pmos_vdd/ac_pmos_vdd.lis]
                            [--sp ac_pmos_vdd.sp]
                            [--out results_pmos_vdd/cgg.csv]
"""

import argparse
import csv
import math
import re
import sys

NUM = r"[-+]?\d+\.?\d*(?:[eE][-+]?\d+)?"

SOURCE_RE = re.compile(rf"\*\*\*\s*source\s+\S+:vgate\s*=\s*({NUM})\s*\*\*\*", re.IGNORECASE)
HEADER_RE = re.compile(r"^\s*freq\b", re.IGNORECASE)
VAC_RE = re.compile(rf"VGATE\s+\S+\s+\S+\s+DC\s+\S+\s+AC\s+({NUM})", re.IGNORECASE)

SI_SUFFIXES = {
    "t": 1e12,
    "g": 1e9,
    "x": 1e6,  # HSPICE uses 'x' (or 'meg') for mega since 'm' means milli
    "k": 1e3,
    "m": 1e-3,
    "u": 1e-6,
    "n": 1e-9,
    "p": 1e-12,
    "f": 1e-15,
    "a": 1e-18,
}
NUM_TOKEN_RE = re.compile(r"^([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)([a-zA-Z]*)$")


def parse_num(token):
    """Parse an HSPICE-formatted number (plain or with an SI suffix)."""
    m = NUM_TOKEN_RE.match(token)
    if not m:
        return None
    num_part, suf = m.groups()
    value = float(num_part)
    if suf:
        mult = SI_SUFFIXES.get(suf.lower())
        if mult is None:
            return None
        value *= mult
    return value


def parse_data_row(line):
    tokens = line.split()
    if len(tokens) != 5:
        return None
    values = [parse_num(t) for t in tokens]
    if any(v is None for v in values):
        return None
    return tuple(values)


def get_vac(sp_path):
    with open(sp_path) as f:
        text = f.read()
    m = VAC_RE.search(text)
    if not m:
        sys.exit(f"Could not find VGATE ... AC <magnitude> in {sp_path}")
    return float(m.group(1))


def parse_lis(lis_path):
    """Yield (vgate, freq, ir, ii, vr, vi) tuples in file order."""
    with open(lis_path) as f:
        lines = f.readlines()

    vgate = None
    rows = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]

        src_match = SOURCE_RE.search(line)
        if src_match:
            vgate = float(src_match.group(1))
            i += 1
            continue

        if HEADER_RE.match(line):
            # Header spans two lines: column names, then per-column variable
            # names (e.g. "vgate vgate gate gate"). Skip both, then read
            # data rows until one fails to parse as 5 numbers.
            i += 2
            while i < n:
                row = parse_data_row(lines[i])
                if row is None:
                    break
                if vgate is None:
                    sys.exit("Found a data row before any '*** source ... vgate' line")
                freq, ir, ii, vr, vi = row
                rows.append((vgate, freq, ir, ii, vr, vi))
                i += 1
            continue

        i += 1

    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lis", default="results_pmos_vdd/ac_pmos_vdd.lis")
    ap.add_argument("--sp", default="ac_pmos_vdd.sp")
    ap.add_argument("--out", default="results_pmos_vdd/cgg.csv")
    args = ap.parse_args()

    vac = get_vac(args.sp)
    rows = parse_lis(args.lis)
    if not rows:
        sys.exit(
            f"No AC data rows found in {args.lis}. Make sure the netlist has a "
            "'.print ac ir(vgate) ii(vgate) vr(gate) vi(gate)' statement after "
            "the .ac card and that HSPICE has been rerun."
        )

    with open(args.out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["frequency", "Vgate", "Ir", "Ii", "Vr", "Vi", "C_gg"])
        for vgate, freq, ir, ii, vr, vi in rows:
            # HSPICE reports current through a voltage source with the sign
            # convention "into the + terminal", so for a capacitive load Ii
            # comes out negative; flip it so C_gg is reported as positive.
            cgg = -ii / (2 * math.pi * freq * vac)
            writer.writerow([freq, vgate, ir, ii, vr, vi, cgg])

    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
