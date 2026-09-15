* Lab3 
* CMOS inverter subcircuit built from the 22nm PTM-HP BSIM4 model card
.include "../22nm_HP.pm"

.param nom_vdd=0.8
.param X=5p
.param k=0.5
.param gnd_vss=0.0
.param LPCH=22n
.param LNCH=22n
.param WN=44n
.param WP=44n

*.step param k 0.5 4.0 0.1

VDD vdd 0 DC nom_vdd
VSS vss 0 DC gnd_vss

MP1 vdd in vdd vdd pmos L=LPCH W=WP
MP2 vss in vss vdd pmos L=LPCH W=WP
MN1 vdd in vdd vss nmos L=LNCH W=WN
MN1 vss in vss vss nmos L=LNCH W=WN

.ic v(out0)=0.8

.option post=2
.probe tran v(in0) 

.dc k start=0.1 stop=10 step=0.1

.end
