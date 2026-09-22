# LAB 4 MOSFET Gate Capacitance (AC Analysis)

Technology: 22nm PTM-HP\
Nominal VDD = 0.8 V\
k = 1.3 (Wp/Wn), Wn = 44nm, Wp = k\*Wn (from Lab 1)\
Single PMOS or single NMOS device wired as a MOS capacitor: drain, and source tied together to either VDD or GND, with the gate driven by `VGATE` (DC bias swept 0.2-0.8 V, AC magnitude 1 mV). Total gate capacitance C_gg is extracted from the AC gate current at each DC bias point.

## Lab 4 Part A
### Gate capacitance extracted vs. VGATE

```
C_gg = -Ii / (2·π·f·Vac)
```
| VGATE (V) | PMOS, S,D @ VDD (aF) | PMOS, S,D @ GND (aF) | NMOS, S,D @ GND (aF) | NMOS, S,D @ VDD (aF) |
|:---------:|:-----------------------:|:-----------------------:|:-----------------------:|:-----------------------:|
| 0.2       | 55.105                  | 30.096                  | 31.376                  | 18.524                  |
| 0.4       | 45.690                  | 26.705                  | 32.854                  | 19.445                  |
| 0.6       | 43.249                  | 25.406                  | 39.855                  | 21.877                  |
| 0.8       | 37.990                  | 24.968                  | 41.736                  | 26.846                  |

## Lab 4 Part B
### Gate capacitance from the model card


```
C_ox = epsrox * eps0 / toxe        (F/m^2, oxide capacitance per unit area)
C_gg = C_ox * W * L                (F, total gate capacitance)
```

eps0 = 8.854e-12 F/m (vacuum permittivity), epsrox = 3.9 (both devices, same high-k/metal-gate stack)

| Device | toxe (nm) | C per area (fF/um²) | W (nm) | L (nm) | C_gg (aF) |
|:------:|:---------:|:--------------------:|:------:|:------:|:---------:|
| NMOS   | 1.05      | 32.886                | 44.0   | 22.0   | 31.834    |
| PMOS   | 1.1       | 31.391                | 57.2   | 22.0   | 39.503    |



### Comparison to a typical MIM capacitor


```
C_MIM = epsrox * eps0 / t_MIM = 7 * 8.854e-12 F/m / 30e-9 m = 2.065e-3 F/m² = 2.065 fF/um²
```

| Capacitor              | Dielectric thickness | epsrox | C per area (fF/um²) |
|:-----------------------|:---------------------:|:------:|:--------------------:|
| Typical MIM capacitor  | ~30 nm                | 7     | 2.065                 |

NMOS gate oxide capacitance per unit area (32.886 fF/um²) is about **15x** higher than this typical MIM capacitor.

## Lab 4 Part C
### Inverter gate capacitance

```
C_inv = C_gg,NMOS + C_gg,PMOS = 31.834 aF + 39.503 aF = 71.337 aF
```

| Component | C_gg (aF) |
|:----------|:---------:|
| NMOS      | 31.834    |
| PMOS      | 39.503    |
| **Inverter total** | **71.337** |


