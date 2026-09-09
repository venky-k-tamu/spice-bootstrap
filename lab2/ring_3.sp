* Lab2 
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
X2 out1 in0 vdd vss INV K=k

.ic v(out0)=0.8

.option post=2
.probe tran v(in0) 

.tran 0.01p 10n SWEEP gnd_vss LIN 41 0 0.4 

* tpLH: out2 falling @0.4V -> out3 rising @0.4V
.measure tran tplh trig v(out0) val=0.4 fall=10 targ v(out1) val=0.4 rise=10
* tpHL: out2 rising @0.4V -> out3 falling @0.4V
.measure tran tphl trig v(out0) val=0.4 rise=10 targ v(out1) val=0.4 fall=10

.measure tran T trig v(in0) val=0.4 rise=10 targ v(in0) val=0.4 rise=11

.measure tran f param='1/T'
.measure tran tphl_6 param='tphl*6' 
.measure tran tplh_6 param='tplh*6' 

.end
