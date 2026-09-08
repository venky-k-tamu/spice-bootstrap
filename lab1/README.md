# Lab 1 — 7-Stage CMOS Inverter Chain (22nm PTM-HP)

Files:
- `../22nm_HP.pm` — PTM 22nm High-Performance BSIM4 (level=54) model card for `nmos`/`pmos`, nominal VDD = 0.8V.
- `inv.sub` — inverter subcircuit `INV(in, out, vdd, vss)`, params `K` (PMOS/NMOS width ratio), `WN`, `LNCH`, `LPCH`. Internally sets `WP = K*WN`.
- `deck_7_inv.cir` — 7 `INV` stages chained `in0 -> out0 -> out1 -> ... -> out6`, driven by a single pulsed source on `in0`. Transient analysis only; dumps the raw waveforms to `tran_data.txt` (binary rawfile, read with ngspice/gnuplot or `scipy.io` / `PySpice`'s raw reader).

## Circuit
- Sizing: `K=0.5` (PMOS half as wide as NMOS) on every stage, `WN=44n`, `LNCH=LPCH=22n` — these come from `inv.sub`'s subcircuit defaults, not the `.param WN/WP/LNCH/LPCH` block at the top of `deck_7_inv.cir` (see gotcha below).
- Input: `V1` on `in0`, `PULSE(0.8 0 1n X X 1n 2n)` with `X=10p` rise/fall time — a single 0.8V-to-0V pulse.
- `.tran 0.01p 3n` — 0.01ps step, 3ns stop time (300k points).

## Running (ngspice, installed via Homebrew)
```
cd lab1
ngspice -b deck_7_inv.cir     # writes tran_data.txt (binary rawfile)
```
Batch mode has no interactive plot window; open `tran_data.txt` in ngspice interactively (`ngspice -r tran_data.txt` then `plot in0 out0 out6`) or with gnuplot/PySpice to view the waveforms.

## Implementation notes (ngspice quirks worth knowing if you edit this file)
- **Subcircuit calls need an `X` prefix, not `I`.** An `I0 ... INV K=k` line is parsed as a current source, not a subcircuit instance — the extra tokens (`vdd`, `vss`, `K=k`) then get misread as current-source parameters, producing a cryptic `unknown parameter (vdd)` error. Every stage here uses `X0`...`X6`.
- **Top-level `.param WN/WP/LNCH/LPCH` (line 6) are currently dead** — none of the `X0`...`X6` calls pass them through, so every stage falls back to `inv.sub`'s own subcircuit defaults (`WN=44n`, `LNCH=LPCH=22n`, `WP` derived from `K*WN`). To actually size the chain from this file, pass them explicitly on each instance line, e.g. `X0 in0 out0 vdd vss INV K=k WN=100n`.
- **Batch mode needs an explicit output command** — no `.print`/`.plot`/`.control ... write` means ngspice exits with `no simulations run!` even if the netlist is otherwise valid. This deck uses a `.control` block with `tran` + `write`.
- **Don't mix a top-level `.tran` directive with an explicit `tran`/`run` inside `.control`** — ngspice executes the analysis twice (a real duplicate solve, not just duplicate printing). This deck only triggers the analysis once, from inside `.control`.
- **`plot` is ignored in batch mode** (`-b`) with a harmless warning — use `write` to dump data instead, then plot afterward from an interactive session or an external tool.
- **Don't name a `.param` `LN`** — ngspice's expression parser reads `{LN}` as the natural-log function `ln()`, not a parameter, and throws a cryptic `Expression err: ln`. That's why channel lengths are `LNCH`/`LPCH` here, not `LN`/`LP`.
