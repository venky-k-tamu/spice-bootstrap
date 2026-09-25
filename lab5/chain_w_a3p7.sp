* Lab 5 -- tapered inverter chain driving a 1pF load (modelled as INV of size F)
* sizing by W (WN = 44n * size, M = 1)
* alpha = 3.7, N = ceil(ln F / ln alpha) = 8 inverters before the load
* last stage fanout into the load = F / alpha^(N-1) = 1.475
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
.include "inv.sub"

.param nom_vdd=0.8
.param k=1.3
.param F=14000
.param alpha=3.7

VDD vdd 0 DC nom_vdd
VSS vss 0 DC 0

* input of the first inverter: starts at VDD, single falling edge with 5ps slew
V1 in vss PULSE(nom_vdd 0 100p 5p 5p 20n 40n)

* chain: stage i is alpha^i times the minimum inverter

X1 in out1 vdd vss INV K=k WN='44n*1'
X2 out1 out2 vdd vss INV K=k WN='44n*pow(alpha,1)'
X3 out2 out3 vdd vss INV K=k WN='44n*pow(alpha,2)'
X4 out3 out4 vdd vss INV K=k WN='44n*pow(alpha,3)'
X5 out4 out5 vdd vss INV K=k WN='44n*pow(alpha,4)'
X6 out5 out6 vdd vss INV K=k WN='44n*pow(alpha,5)'
X7 out6 out7 vdd vss INV K=k WN='44n*pow(alpha,6)'
X8 out7 out8 vdd vss INV K=k WN='44n*pow(alpha,7)'

* 1pF load: one inverter 14000x the minimum
XLOAD out8 outload vdd vss INV K=k WN='44n*F'

.tran 0.1p 20n

* tpd: VDD/2 fall at the first inverter's input -> VDD/2 at the load's input
.measure tran tpd trig v(in) val='nom_vdd/2' fall=1 targ v(out8) val='nom_vdd/2' cross=1
.option post=2
.probe tran v(in) v(out8)
.end
