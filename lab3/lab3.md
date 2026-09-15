# LAB 3 MOSFET I-V Characteristics

Technology: 22nm PTM-HP\
Nominal VDD = 0.8 V\
k = 1.3 (Wp/Wn), Wn = 44nm, Wp = k\*Wn (from Lab 1)\
Single PMOS (`MP1`) and single NMOS (`MN1`) devices, each characterized separately with `VGATE` and `VDRAIN` sweeping the gate and drain nodes. I_D is reported in a consistent drain-to-source reference direction for both devices.

## Lab 3.0
### PMOS Drain current vs. VDS, family of curves over VGS

RON (from plot) = 9.09 kohm
RON (calculated) = 3.80 kohm  (1/(u0*Cox*(W/L)*Vov), u0=0.0095 m^2/Vs, Cox=3.14e-2 F/m^2 from toxe=1.1nm, W/L=2.6, Vov=0.8-0.4606=0.339V)
![PMOS I_D vs V_DS family of curves](results_pmos/iv_curves.png)

## Lab 3.1
### NMOS drain current vs. VDS, family of curves over VGS

RON (from plot) = 5.55 kohm 
RON (calculated) = 1.28 kohm  (1/(u0*Cox*(W/L)*Vov), u0=0.04 m^2/Vs, Cox=3.29e-2 F/m^2 from toxe=1.05nm, W/L=2.0, Vov=0.8-0.50308=0.297V)

![NMOS I_D vs V_DS family of curves](results_nmos/iv_curves.png)

## Appendix: I-V sweep data

Full per-point sweep data (VGS, VDS, ID) for both devices is in CSV form:

- PMOS: [`results_pmos/iv_table.csv`](results_pmos/iv_table.csv)
- NMOS: [`results_nmos/iv_table.csv`](results_nmos/iv_table.csv)
