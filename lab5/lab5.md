# LAB 5 Gate Sizing

Technology: 22nm PTM-HP\
Nominal VDD = 0.8 V\
k = 1.3 (Wp/Wn), Wn = 44nm, Wp = k\*Wn (from Lab 1)\
Identify how many inverters and what sizes to drive a large capacitance like 1pF or 10pF.\
Answer is a chain of inverters, each inverter $\alpha$ times larger than last inverter.
## Lab 5 Step A
### Modeling load capacitance as an inverter
```
M = C/Cmin
Cmin = capacitance of min sized inverter
Cmin = 71.337 aF 
```
| C (pF) | M |
|:---------:|:-----------------------:|
| 1        | 14018                  |
| 10       | 140180                 |

A load of 1pF is equivalent to an inverter of size ~14000 the min sized inverter.

## Lab 5 Step B
### Plot of delay against $\alpha$

Delay is propagation delay from input of first inverter to input of last inverter (Vdd/2 fall on first inverter to Vdd/2 rise/fall on input of last inverter)
