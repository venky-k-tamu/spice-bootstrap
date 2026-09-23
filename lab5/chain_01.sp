* Lab 5 -- tapered inverter chain driving a 1pF load (modelled as INV with M=F)
* N = 1 stages, alpha = F^(1/N) = 14000.0000
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
.include "inv.sub"

.param nom_vdd=0.8
.param k=1.3
.param F=14000
.param alpha=14000.000000

VDD vdd 0 DC nom_vdd
VSS vss 0 DC 0

* ideal pulse -> min-size shaping inverter, so stage 1 sees a realistic edge
V1 in0 vss PULSE(0 nom_vdd 100p 20p 20p 60n 120n)
XDRV in0 in vdd vss INV K=k

* chain: stage i is alpha^i times the minimum inverter

X1 in out1 vdd vss INV K=k M=1

* 1pF load: one inverter 14000x the minimum
XLOAD out1 outload vdd vss INV K=k M='F'

.tran 1p 120.1n

* tp1/tp2: chain input edge -> chain output (input of the load), 50% points
.measure tran tp1 trig v(in) val='nom_vdd/2' cross=1 targ v(out1) val='nom_vdd/2' cross=1
.measure tran tp2 trig v(in) val='nom_vdd/2' cross=2 targ v(out1) val='nom_vdd/2' cross=2
.measure tran tpd param='(tp1+tp2)/2'
.option post=2
.probe tran v(in) v(out1)
.end
