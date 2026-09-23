* Lab 5 -- tapered inverter chain driving a 1pF load (modelled as INV with M=F)
* N = 11 stages, alpha = F^(1/N) = 2.3819
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
.include "inv.sub"

.param nom_vdd=0.8
.param k=1.3
.param F=14000
.param alpha=2.381885

VDD vdd 0 DC nom_vdd
VSS vss 0 DC 0

* ideal pulse -> min-size shaping inverter, so stage 1 sees a realistic edge
V1 in0 vss PULSE(0 nom_vdd 100p 20p 20p 2n 4n)
XDRV in0 in vdd vss INV K=k

* chain: stage i is alpha^i times the minimum inverter

X1 in out1 vdd vss INV K=k M=1
X2 out1 out2 vdd vss INV K=k M='pow(alpha,1)'
X3 out2 out3 vdd vss INV K=k M='pow(alpha,2)'
X4 out3 out4 vdd vss INV K=k M='pow(alpha,3)'
X5 out4 out5 vdd vss INV K=k M='pow(alpha,4)'
X6 out5 out6 vdd vss INV K=k M='pow(alpha,5)'
X7 out6 out7 vdd vss INV K=k M='pow(alpha,6)'
X8 out7 out8 vdd vss INV K=k M='pow(alpha,7)'
X9 out8 out9 vdd vss INV K=k M='pow(alpha,8)'
X10 out9 out10 vdd vss INV K=k M='pow(alpha,9)'
X11 out10 out11 vdd vss INV K=k M='pow(alpha,10)'

* 1pF load: one inverter 14000x the minimum
XLOAD out11 outload vdd vss INV K=k M='F'

.tran 1p 4.1n

* tp1/tp2: chain input edge -> chain output (input of the load), 50% points
.measure tran tp1 trig v(in) val='nom_vdd/2' cross=1 targ v(out11) val='nom_vdd/2' cross=1
.measure tran tp2 trig v(in) val='nom_vdd/2' cross=2 targ v(out11) val='nom_vdd/2' cross=2
.measure tran tpd param='(tp1+tp2)/2'
.option post=2
.probe tran v(in) v(out11)
.end
