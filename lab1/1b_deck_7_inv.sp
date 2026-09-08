* Lab 1 -- sweep PMOS/NMOS width ratio K, measure tpHL/tpLH between out2 and out3
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
* HSPICE port of sweep_k.cir. The ngspice version needed a hand-rolled
* .control dowhile loop (alterparam + reset + tran) because ngspice-47 has no
* .step. HSPICE supports .step/.measure natively -- this does the same sweep
* in two top-level cards, and writes the per-K results to sweep_k.mt0 for you.
.include "inv.sub"

.param nom_vdd=0.8
.param X=10p
.param k=0.5

*.step param k 0.5 4.0 0.1

VDD vdd 0 DC nom_vdd
VSS vss 0 DC 0

X0 in0 out0 vdd vss INV K=k
X1 out0 out1 vdd vss INV K=k
X2 out1 out2 vdd vss INV K=k
X3 out2 out3 vdd vss INV K=k
X4 out3 out4 vdd vss INV K=k
X5 out4 out5 vdd vss INV K=k
X6 out5 out6 vdd vss INV K=k

V1 in0 vss dc 0.8 PULSE (0.8 0 1n X X 1n 2n)

.option post=2
.probe tran v(in0) v(out2) v(out3)

.tran 0.01p 3n SWEEP k LIN 36 0.5 4.0

* tpHL: out2 falling @0.4V -> out3 rising @0.4V
.measure tran tphl trig v(out2) val=0.4 fall=1 targ v(out3) val=0.4 rise=1
* tpLH: out2 rising @0.4V -> out3 falling @0.4V
.measure tran tplh trig v(out2) val=0.4 rise=1 targ v(out3) val=0.4 fall=1

* rise time 10% of VDD -> 90% of VDD
* fall time 90% of VDD -> 10% of VDD
.measure tran tr trig v(out3) val=0.08 rise=1 targ v(out3) val=0.72 rise=1
.measure tran tf trig v(out3) val=0.72 fall=1 targ v(out3) val=0.08 fall=1

.end
