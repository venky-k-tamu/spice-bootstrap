* Lab 5 -- tapered inverter chain driving a 1pF load (modelled as INV of size F)
* sizing by M (parallel copies of the min inverter, WN = 44n)
* alpha = 14000, N = round(ln F / ln alpha) = 1 stages
* last stage fanout into the load = F / alpha^(N-1) = 1.4e+04
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
.include "inv.sub"

.param nom_vdd=0.8
.param k=1.3
.param F=14000
.param alpha=14000

VDD vdd 0 DC nom_vdd
VSS vss 0 DC 0

* input of the first inverter: starts at VDD, single falling edge with 5ps slew
V1 in vss PULSE(nom_vdd 0 100p 5p 5p 60n 120n)

* chain: stage i is alpha^i times the minimum inverter

X1 in out1 vdd vss INV K=k M=1

* 1pF load: one inverter 14000x the minimum
XLOAD out1 outload vdd vss INV K=k M='F'

.tran 0.1p 60n

* tpd: VDD/2 fall at the first inverter's input -> VDD/2 at the load's input
.measure tran tpd trig v(in) val='nom_vdd/2' fall=1 targ v(out1) val='nom_vdd/2' cross=1
.option post=2
.probe tran v(in) v(out1)
.end
