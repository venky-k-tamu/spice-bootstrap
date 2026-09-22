# LAB 4 MOSFET Gate Capacitance (AC Analysis)

Technology: 22nm PTM-HP\
Nominal VDD = 0.8 V\
k = 1.3 (Wp/Wn), Wn = 44nm, Wp = k\*Wn (from Lab 1)\
Single PMOS or single NMOS device wired as a MOS capacitor: drain, source, and body tied together to either VDD or GND, with the gate driven by `VGATE` (DC bias swept 0.2-0.8 V, AC magnitude 1 mV). Total gate capacitance C_gg is extracted from the AC gate current at each DC bias point.

## Lab 4 Part A
### Gate capacitance vs. VGATE

**Method:** `.ac dec 20 10 10g sweep vgate 0.2 0.8 0.2` drives the gate with a small-signal AC excitation (Vac = 1 mV) on top of each DC bias. The resulting gate current phasor decomposes into a real part (Ir, gate leakage conductance — frequency-independent, from BSIM4's gate tunneling current model) and an imaginary part (Ii, capacitive susceptance, Ii = ωC·Vac). Since capacitance is a reactive quantity, only the imaginary part carries capacitance information:

```
C_gg = -Ii / (2·π·f·Vac)
```

(sign flipped to account for HSPICE's current-into-positive-terminal convention for voltage sources). C_gg is frequency-independent for a pure capacitor, confirmed across the full 10 Hz - 10 GHz sweep, and matches HSPICE's own analytic `cgtot` (from BSIM4 charge equations, printed at each operating point) to 4+ significant figures — see the Appendix CSVs for full per-frequency data.

| VGATE (V) | PMOS, S/D/B @ VDD (aF) | PMOS, S/D/B @ GND (aF) | NMOS, S/D/B @ GND (aF) | NMOS, S/D/B @ VDD (aF) |
|:---------:|:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:|
| 0.2       | 55.105                  | 30.096                  | 31.376                  | 18.524                  |
| 0.4       | 45.690                  | 26.705                  | 32.854                  | 19.445                  |
| 0.6       | 43.249                  | 25.406                  | 39.855                  | 21.877                  |
| 0.8       | 37.990                  | 24.968                  | 41.736                  | 26.846                  |

PMOS C_gg decreases monotonically with VGATE in both configurations (moving away from strong inversion at low VGATE, toward cutoff at VGATE = VDD). NMOS C_gg increases monotonically with VGATE (moving from cutoff at low VGATE into strong inversion as VGATE approaches VDD) — the expected mirror-image behavior between the two device types.

## Lab 4 Part B
### Gate capacitance, hand-calculated from the model card

Ideal parallel-plate oxide capacitance, using each device's `toxe` and `epsrox` from `22nm_HP.pm`, and drawn W/L (not BSIM4's bias-dependent effective geometry):

```
C_ox = epsrox * eps0 / toxe        (F/m^2, oxide capacitance per unit area)
C_gg = C_ox * W * L                (F, total gate capacitance)
```

eps0 = 8.854e-12 F/m (vacuum permittivity), epsrox = 3.9 (both devices, same high-k/metal-gate stack)

| Device | toxe (nm) | C per area (fF/um²) | W (nm) | L (nm) | C_gg (aF) |
|:------:|:---------:|:--------------------:|:------:|:------:|:---------:|
| NMOS   | 1.05      | 32.886                | 44.0   | 22.0   | 31.834    |
| PMOS   | 1.1       | 31.391                | 57.2   | 22.0   | 39.503    |

(W_N = 44 nm, W_P = k·W_N = 1.3·44 nm = 57.2 nm, from Lab 1; L = 22 nm for both, from the model card's minimum-length process node.)

### Comparison to a typical MIM capacitor

`22nm_HP.pm` only models the two transistors, not a MIM cap, so there's no model-card `toxe`/`epsrox` to pull for one. Instead, the MIM number below uses the same parallel-plate formula with representative values for a standard SiO2-dielectric MIM option (the kind commonly offered as an analog/RF back-end-of-line option around this process generation): relative permittivity epsrox = 3.9 (same as SiO2/the transistors' oxide) and a dielectric thickness of ~30 nm (foundry MIM plates are typically tens of nm apart, vs. ~1 nm for a gate oxide, to keep leakage low and breakdown voltage high):

```
C_MIM = epsrox * eps0 / t_MIM = 3.9 * 8.854e-12 F/m / 30e-9 m = 1.151e-3 F/m² = 1.151 fF/um²
```

| Capacitor              | Dielectric thickness | epsrox | C per area (fF/um²) |
|:-----------------------|:---------------------:|:------:|:--------------------:|
| Typical MIM capacitor  | ~30 nm                | 3.9    | 1.151                 |

NMOS gate oxide capacitance per unit area (32.886 fF/um²) is about **28.6x** higher than this typical MIM capacitor, purely because the gate oxide (1.05 nm) is ~30x thinner than the assumed MIM dielectric (~30 nm).

## Lab 4 Part C
### Inverter gate capacitance

A CMOS inverter's gate node connects directly to both the NMOS and PMOS gates, so its total gate capacitance is just the sum of the two devices' C_gg from Part B:

```
C_inv = C_gg,NMOS + C_gg,PMOS = 31.834 aF + 39.503 aF = 71.337 aF
```

| Component | C_gg (aF) |
|:----------|:---------:|
| NMOS      | 31.834    |
| PMOS      | 39.503    |
| **Inverter total** | **71.337** |

## Appendix: AC sweep data

Full per-frequency, per-VGATE data (frequency, VGATE, Ir, Ii, Vr, Vi, C_gg) for all four configurations is in CSV form:

- PMOS, S/D/B @ VDD: [`results_pmos_vdd/cgg.csv`](results_pmos_vdd/cgg.csv)
- PMOS, S/D/B @ GND: [`results_pmos_gnd/cgg.csv`](results_pmos_gnd/cgg.csv)
- NMOS, S/D/B @ GND: [`results_nmos_gnd/cgg.csv`](results_nmos_gnd/cgg.csv)
- NMOS, S/D/B @ VDD: [`results_nmos_vdd/cgg.csv`](results_nmos_vdd/cgg.csv)

Data was extracted from the HSPICE `.lis` `.print ac` tables with [`extract_cgg.py`](extract_cgg.py).
