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
.param vdrain=0.0
.param vgs=0.8

.step param vdrain 0.0 0.8 0.01
.step param vgs 0.8 0.2 -0.1

VDD vdd 0 DC nom_vdd
VSS vss 0 DC gnd_vss
VGS in 0 DC nom_vdd
VDRAIN drain 0 DC vdrain

MP1 drain in vdd vdd pmos L=LPCH W=WP
*MN1 drain in vss vss nmos L=LNCH W=WN


.option post=2
.probe DC ID(MP1) IS(MP1)
.measure DC VDS = 'V(drain) - nom_vdd'


.dc 

.end
