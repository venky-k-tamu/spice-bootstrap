# Lab 1 — CMOS Inverter (22nm PTM-HP)

Files:
- `../22nm_HP.pm` — PTM 22nm High-Performance BSIM4 (level=54) model card for `nmos`/`pmos`, nominal VDD = 0.8V.
- `inv_cell.sub` — inverter subcircuit `INV(in, out, vdd, vss)` built from the two transistors, sized via params `WN, WP, LNCH, LPCH`.
- `inverter_vtc.cir` — DC sweep, produces the voltage transfer characteristic (VTC). Measures `VM`, `VOH`, `VOL` directly; dumps `vtc_data.txt`.
- `inverter_tran.cir` — transient sim with a pulsed input. Measures `tpHL`, `tpLH`, `trise`, `tfall`; dumps `tran_data.txt`.
- `plot_vtc.py` / `plot_tran.py` — read the dumped data, compute `VIL`/`VIH`/noise margins (via the unity-slope points of the VTC), and render `vtc_plot.png` / `tran_plot.png`.

## Sizing
Default: `WN=200n`, `WP=800n`, `LNCH=LPCH=22n` (drawn min length for this node). The 4x width ratio compensates for the PMOS having much lower `u0` than the NMOS in this model card, so `VM` lands near VDD/2. Override `WN/WP/LNCH/LPCH/VDD` at the top of either `.cir` file to explore sizing.

## Running (ngspice, installed via Homebrew)
```
cd lab1
ngspice -b inverter_vtc.cir     # prints VM/VOH/VOL, writes vtc_data.txt
python3 plot_vtc.py             # prints VIL/VIH/NML/NMH, writes vtc_plot.png

ngspice -b inverter_tran.cir    # prints tpHL/tpLH/trise/tfall, writes tran_data.txt
python3 plot_tran.py            # writes tran_plot.png
```

## Measured results (default sizing, VDD=0.8V)
```
VOH  = 0.8000 V      tpHL  = 14.7 ps
VOL  = 0.0001 V      tpLH  = 7.8 ps
VM   = 0.4248 V      trise = 13.2 ps
VIL  = 0.3098 V      tfall = 22.7 ps
VIH  = 0.5558 V
NML  = 0.3097 V
NMH  = 0.2442 V
```
tpHL/tpLH are asymmetric because the PMOS is only 4x wider than the NMOS while its `u0` is ~4.2x lower — the fall edge (NMOS pulling down through the extra series resistance implied by `rdsw`) ends up slower than the rise edge (PMOS charging a tiny 5fF load) once you include the transistors' own parasitic caps. Try `WP=1000n` (or larger) if you want to see `tpHL`/`tpLH` converge.

## Implementation notes (ngspice quirks worth knowing if you edit these files)
- **Don't name a `.param` `LN`** — ngspice's expression parser reads `{LN}` as the natural-log function `ln()`, not a parameter, and throws a cryptic `Expression err: ln`. That's why channel lengths are `LNCH`/`LPCH` here, not `LN`/`LP`.
- **`{...}` param expressions don't expand inside typed `.control` commands** (`dc ...`, `tran ...`) — only inside netlist directive lines (`.dc`, `.tran`, `V1 ... {VDD}`, etc). So the sweep/stop-time values are hardcoded numerically inside the `.control` block (with a comment pointing back at the `.param` they correspond to) rather than passed as `{VDD}`/`{4*PW}`.
- **Don't mix a top-level `.dc`/`.tran` directive with an explicit `run`/`dc`/`tran` inside `.control`** — ngspice will actually execute the analysis twice (real duplicate solves, not just duplicate printing). These files only trigger the analysis once, from inside `.control`.
- ngspice always reprints the final `.meas` summary a second time at the very end of batch execution (cosmetic; no `No. of Data Rows` line accompanies it, and no second solve happens) — that's expected, not an error.
- This ngspice build doesn't support `deriv()` inside a `.meas ... WHEN` clause, so `VIL`/`VIH`/`NML`/`NMH` are computed in `plot_vtc.py` from the exported sweep data instead of via `.meas`.
