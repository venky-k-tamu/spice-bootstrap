* Lab2 
.include "inv.sub"

.param nom_vdd=0.8
.param X=5.7p
.param k=0.5
.param gnd_vss=0.0

*.step param k 0.5 4.0 0.1

VDD vdd 0 DC nom_vdd
VSS vss 0 DC gnd_vss

X0 in0 in0 vdd vss INV K=k

.ic v(out0)=0.8

.option post=2
.probe tran v(in0) 

.dc k start=0.1 stop=10 step=0.1

.end
