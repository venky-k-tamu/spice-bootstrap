#!/usr/bin/env python3
"""Extract gate capacitance (C_gg) vs frequency and Vgate from an HSPICE .lis file.

Reads the plain-text .print ac table that HSPICE writes into the .lis output
(ir(vgate), ii(vgate), vr(gate), vi(gate) vs freq, one table per Vgate sweep
step) and computes C_gg = Ii / (2*pi*f*Vac), where Vac is the AC excitation
magnitude on VGATE.

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
DATA_ROW_RE = re.compile(rf"^\s*({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s+({NUM})\s*$")
VAC_RE = re.compile(rf"VGATE\s+\S+\s+\S+\s+DC\s+\S+\s+AC\s+({NUM})", re.IGNORECASE)


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
    in_table = False
    for line in lines:
        src_match = SOURCE_RE.search(line)
        if src_match:
            vgate = float(src_match.group(1))
            in_table = False
            continue

        if HEADER_RE.match(line):
            in_table = True
            continue

        if in_table:
            m = DATA_ROW_RE.match(line)
            if m:
                freq, ir, ii, vr, vi = (float(g) for g in m.groups())
                if vgate is None:
                    sys.exit("Found a data row before any '*** source ... vgate' line")
                yield vgate, freq, ir, ii, vr, vi
            elif line.strip():
                # Non-numeric, non-blank line ends the data table.
                in_table = False


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lis", default="results_pmos_vdd/ac_pmos_vdd.lis")
    ap.add_argument("--sp", default="ac_pmos_vdd.sp")
    ap.add_argument("--out", default="results_pmos_vdd/cgg.csv")
    args = ap.parse_args()

    vac = get_vac(args.sp)

    rows = list(parse_lis(args.lis))
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
            cgg = ii / (2 * math.pi * freq * vac)
            writer.writerow([freq, vgate, ir, ii, vr, vi, cgg])

    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
