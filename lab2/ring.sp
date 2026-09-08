* Lab 1 -- sweep PMOS/NMOS width ratio K, measure tpHL/tpLH between out2 and out3
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
* HSPICE port of sweep_k.cir. The ngspice version needed a hand-rolled
* .control dowhile loop (alterparam + reset + tran) because ngspice-47 has no
* .step. HSPICE supports .step/.measure natively -- this does the same sweep
* in two top-level cards, and writes the per-K results to sweep_k.mt0 for you.
.include "inv.sub"

.param nom_vdd=0.8
.param X=5.7p
.param k=1.3
.param gnd_vss=0.0

*.step param k 0.5 4.0 0.1

VDD vdd 0 DC nom_vdd
VSS vss 0 DC gnd_vss

X0 in0 out0 vdd vss INV K=k
X1 out0 out1 vdd vss INV K=k
X2 out1 out2 vdd vss INV K=k
X3 out2 out3 vdd vss INV K=k
X4 out3 out4 vdd vss INV K=k
X5 out4 out5 vdd vss INV K=k
X6 out5 out6 vdd vss INV K=k
X7 out6 out7 vdd vss INV K=k
X8 out7 out8 vdd vss INV K=k
X9 out8 out9 vdd vss INV K=k
X10 out9 out10 vdd vss INV K=k
X11 out10 out11 vdd vss INV K=k
X12 out11 out12 vdd vss INV K=k
X13 out12 out13 vdd vss INV K=k
X14 out13 out14 vdd vss INV K=k
X15 out14 out15 vdd vss INV K=k
X16 out15 out16 vdd vss INV K=k
X17 out16 out17 vdd vss INV K=k
X18 out17 out18 vdd vss INV K=k
X19 out18 out19 vdd vss INV K=k
X20 out19 in0 vdd vss INV K=k


.option post=2
.probe tran v(in0) 

.tran 0.01p 3n * SWEEP gnd_vss LIN 41 0 4.0

* tpLH: out2 falling @0.4V -> out3 rising @0.4V
.measure tran tplh trig v(out2) val=0.4 fall=1 targ v(out3) val=0.4 rise=1
* tpHL: out2 rising @0.4V -> out3 falling @0.4V
.measure tran tphl trig v(out2) val=0.4 rise=1 targ v(out3) val=0.4 fall=1

.measure tran T trig v(in0) val=0.4 rise=10 targ v(in0) val=0.4 rise=11

.measure tran f param='1/T'
.measure tran tphl_42 param='tphl*42' 
.measure tran tplh_42 param='tplh*42' 

.end
