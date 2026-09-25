* Lab 5 -- tapered inverter chain driving a 1pF load (modelled as INV of size F)
* sizing by M (parallel copies of the min inverter, WN = 44n)
* alpha = 4.5, N = ceil(ln F / ln alpha) = 7 inverters before the load
* last stage fanout into the load = F / alpha^(N-1) = 1.686
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
.include "inv.sub"

.param nom_vdd=0.8
.param k=1.3
.param F=14000
.param alpha=4.5

VDD vdd 0 DC nom_vdd
VSS vss 0 DC 0

* input of the first inverter: starts at VDD, single falling edge with 5ps slew
V1 in vss PULSE(nom_vdd 0 100p 5p 5p 3n 6n)

* chain: stage i is alpha^i times the minimum inverter

X1 in out1 vdd vss INV K=k M=1
X2 out1 out2 vdd vss INV K=k M='pow(alpha,1)'
X3 out2 out3 vdd vss INV K=k M='pow(alpha,2)'
X4 out3 out4 vdd vss INV K=k M='pow(alpha,3)'
X5 out4 out5 vdd vss INV K=k M='pow(alpha,4)'
X6 out5 out6 vdd vss INV K=k M='pow(alpha,5)'
X7 out6 out7 vdd vss INV K=k M='pow(alpha,6)'

* 1pF load: one inverter 14000x the minimum
XLOAD out7 outload vdd vss INV K=k M='F'

.tran 0.1p 3n

* tpd: VDD/2 fall at the first inverter's input -> VDD/2 at the load's input
.measure tran tpd trig v(in) val='nom_vdd/2' fall=1 targ v(out7) val='nom_vdd/2' cross=1
.option post=2
.probe tran v(in) v(out7)
.end
