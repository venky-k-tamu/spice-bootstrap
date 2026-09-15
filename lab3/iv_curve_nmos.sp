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
.param vgate=0.0
.param vdrain=0.0

VDD vdd 0 DC nom_vdd
VSS vss 0 DC gnd_vss
VGATE gate 0 DC vgate
VDRAIN drain 0 DC vdrain

*MP1 drain gate vdd vdd pmos L=LPCH W=WP
MN1 drain gate vss vss nmos L=LNCH W=WN


.option post=2
.option probe
.probe DC I(VDRAIN) I(vdd)

.dc vdrain start=0 stop=0.8 step=0.01 vgate start=0 stop=0.8 step=0.1

.end
