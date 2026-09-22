* Lab3 
* CMOS inverter subcircuit built from the 22nm PTM-HP BSIM4 model card
.include "../22nm_HP.pm"

.param nom_vdd=0.8
.param gnd_vss=0.0
.param X=5p
.param k=1.3
.param LPCH=22n
.param LNCH=22n
.param WN=44n
.param WP='k*WN'
.param vgate=0.2

VDD vdd 0 DC nom_vdd
VSS vss 0 DC gnd_vss
VGATE gate 0 DC vgate AC 0.001

*MP1 vdd gate vdd vdd pmos L=LPCH W=WP
MP2 vss gate vss vdd pmos L=LPCH W=WP
*MN1 vdd gate vdd vss nmos L=LNCH W=WN
*MN2 vss gate vss vss nmos L=LNCH W=WN


.option post=2
.option probe

.ac DEC 20 10 10g SWEEP vgate 0.2 0.8 0.2
.probe ac Ii(vgate) Ir(vgate) Vi(gate) Vr(gate)
.print ac ir(vgate) ii(vgate) vr(gate) vi(gate)

.end
