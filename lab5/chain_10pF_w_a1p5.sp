* Lab 5 -- tapered inverter chain driving a 10pF load (modelled as INV of size F)
* sizing by W (WN = 44n * size, M = 1)
* alpha = 1.5, N = ceil(ln F / ln alpha) = 30 inverters before the load
* last stage fanout into the load = F / alpha^(N-1) = 1.095
* Technology: PTM 22nm HP, BSIM4 (level=54), nominal VDD = 0.8V
.include "inv.sub"

.param nom_vdd=0.8
.param k=1.3
.param F=140000
.param alpha=1.5

VDD vdd 0 DC nom_vdd
VSS vss 0 DC 0

* input of the first inverter: starts at VDD, single falling edge with 5ps slew
V1 in vss PULSE(nom_vdd 0 100p 5p 5p 2000n 4000n)

* chain: stage i is alpha^i times the minimum inverter

X1 in out1 vdd vss INV K=k WN='44n*1'
X2 out1 out2 vdd vss INV K=k WN='44n*pow(alpha,1)'
X3 out2 out3 vdd vss INV K=k WN='44n*pow(alpha,2)'
X4 out3 out4 vdd vss INV K=k WN='44n*pow(alpha,3)'
X5 out4 out5 vdd vss INV K=k WN='44n*pow(alpha,4)'
X6 out5 out6 vdd vss INV K=k WN='44n*pow(alpha,5)'
X7 out6 out7 vdd vss INV K=k WN='44n*pow(alpha,6)'
X8 out7 out8 vdd vss INV K=k WN='44n*pow(alpha,7)'
X9 out8 out9 vdd vss INV K=k WN='44n*pow(alpha,8)'
X10 out9 out10 vdd vss INV K=k WN='44n*pow(alpha,9)'
X11 out10 out11 vdd vss INV K=k WN='44n*pow(alpha,10)'
X12 out11 out12 vdd vss INV K=k WN='44n*pow(alpha,11)'
X13 out12 out13 vdd vss INV K=k WN='44n*pow(alpha,12)'
X14 out13 out14 vdd vss INV K=k WN='44n*pow(alpha,13)'
X15 out14 out15 vdd vss INV K=k WN='44n*pow(alpha,14)'
X16 out15 out16 vdd vss INV K=k WN='44n*pow(alpha,15)'
X17 out16 out17 vdd vss INV K=k WN='44n*pow(alpha,16)'
X18 out17 out18 vdd vss INV K=k WN='44n*pow(alpha,17)'
X19 out18 out19 vdd vss INV K=k WN='44n*pow(alpha,18)'
X20 out19 out20 vdd vss INV K=k WN='44n*pow(alpha,19)'
X21 out20 out21 vdd vss INV K=k WN='44n*pow(alpha,20)'
X22 out21 out22 vdd vss INV K=k WN='44n*pow(alpha,21)'
X23 out22 out23 vdd vss INV K=k WN='44n*pow(alpha,22)'
X24 out23 out24 vdd vss INV K=k WN='44n*pow(alpha,23)'
X25 out24 out25 vdd vss INV K=k WN='44n*pow(alpha,24)'
X26 out25 out26 vdd vss INV K=k WN='44n*pow(alpha,25)'
X27 out26 out27 vdd vss INV K=k WN='44n*pow(alpha,26)'
X28 out27 out28 vdd vss INV K=k WN='44n*pow(alpha,27)'
X29 out28 out29 vdd vss INV K=k WN='44n*pow(alpha,28)'
X30 out29 out30 vdd vss INV K=k WN='44n*pow(alpha,29)'

* 10pF load: one inverter 140000x the minimum
XLOAD out30 outload vdd vss INV K=k WN='44n*F'

.tran 0.1p 2000n

* tpd: VDD/2 fall at the first inverter's input -> VDD/2 at the load's input
.measure tran tpd trig v(in) val='nom_vdd/2' fall=1 targ v(out30) val='nom_vdd/2' cross=1
.option post=2
.probe tran v(in) v(out30)
.end
