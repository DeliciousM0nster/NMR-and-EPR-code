print("\n-------------------------------------------------------\nOkay. 3, 2, 1, let's jam!\n-------------------------------------------------------\n")

'''----------------------------------------Imports----------------------------------------
'''

import sys
import numpy as np


'''---------------------------------------Notes-------------------------------------------
'''

### Details for different circuits here (including drawings) on page 88 of personal logbook

'''----------------------------------------Main----------------------------------------
'''

'''
COMMAND LINE INPUTS:
	sys.argv[1] is p, s, or l for parallel, series, or L-network resonant circuit (L-network is traditional "matchbox")
	sys.argv[2] is RF frequency in kHz
	sys.argv[3] is coil inductance in mH
	sys.argv[4] is coil capacitance in pF
	sys.argv[5] is coil resistance in Ohms

'''

L = float(sys.argv[3])*(10**-3)		### input in mH (converted to Henry)
R_0 = float(sys.argv[5])			### input in Ohms
R_load = 50							### input in Ohms (50 Ohms for RF Agilent)

f = float(sys.argv[2])				### RF freq in kHz (154 for NMR, 42 for EPR big coils, 9550 for EPR small coils, 91 for A1n setup)
w = 2.0*np.pi*f*1000				### RF ang freq in Hz

### 1, 2, or 3 (see below for descriptions) 
coilModel = 1
### Impedence for the Coil
### Z_coil = A + jB
A = 0
B = 0

X0 = np.inf

if coilModel == 1:
	### Model coil as inductor and resistor in series
	### DOUBLE CHECKED MATH - It's right, Chris
	A = R_0
	B = w*L
elif coilModel == 2:
	### Model coil as capacitor running parallel to series of inductor and resistor
	### DOUBLE CHECKED MATH - It's right, Chris
	X0 = -1/(w*float(sys.argv[4])*(10**-6))
	A = (R_0*X0*X0) / (R_0**2 + ( X0 + w*L )**2 )
	B = 1.0*( X0*((R_0**2) + ((w*L)**2) + (X0*w*L)) ) / (R_0**2 + ( X0 + w*L )**2 )
elif coilModel == 3:
	### Model coil as capacitor and inductor in parallel followed by a resistor in series
	X0 = -1/(w*float(sys.argv[4])*(10**-6))
	A = R_0
	B = (X0*w*L)/(X0 + w*L)

### L-Network circuit (two capacitors, one in series, one in parallel)
if sys.argv[1].lower() == "l":

	C1 = 1000000000/(w*( B - np.sqrt(A*(R_load-A))) )		### C1 in nF
	C2 = 1000000000/(w*R_load*np.sqrt( A/(R_load-A) ))		### C2 in nF

	print("For " + str(f) + " kHz L-Network circuit:")
	print("\tC1 = " + str(np.round(C1, 3)) + " nF")
	print("\tC2 = " + str(np.round(C2, 3)) + " nF")

### For a series resonant circuit
elif sys.argv[1].lower() == "s":

	C = 1/(w*B)
	R = R_load - A

	print("For " + str(f) + " kHz series resonance circuit:")
	print("\tC = " + str(np.round(1000000000000*C, 3)) + " pF")
	print("\tR = " + str(np.round(R, 3)) + " \u03A9")

### For a parallel resonance circuit
elif sys.argv[1].lower() == "p":

	X_L = w*L
	X_C = (-1/X_L)*( (R_0**2) + (X_L**2) )

	C = -1/(w*X_C)

	a = R_load*( (R_0**2) + ((X_L + X_C)**2) ) - (X_C**2)*R_0
	b = (X_C**2)*( 2*R_0*R_load - (X_L**2) - (R_0**2) )
	c = (X_C**2)*R_load*( (X_L**2) + (R_0**2) )

	R_pos = (1/(2*a)) * (-1*b + np.sqrt( (b**2) - 4*a*c ) )
	R_neg = (1/(2*a)) * (-1*b - np.sqrt( (b**2) - 4*a*c ) )

	check = True
	print("For " + str(f) + " kHz parallel resonance circuit:")
	if R_pos > 0:
		check = False
		print("\tC = " + str(np.round(1000000000000*C, 3)) + " pF")
		print("\tR = " + str(np.round(R_pos, 3)) + " \u03A9")
	if R_neg > 0:
		check = False
		print("\tC = " + str(np.round(1000000000000*C, 3)) + " pF")
		print("\tR = " + str(np.round(R_neg, 3)) + " \u03A9")
	if check:
		print("\tNo Result Valid...")
		print("\tR_pos = " + str(np.round(R_pos, 3)) + " \u03A9")
		print("\tR_neg = " + str(np.round(R_neg, 3)) + " \u03A9")

else:

	print("Circuit type not recognized. Please input \"p\" for parallel resonance, \"s\" for series resonance, or \"m\" for \"mixed\" or what was traditionally used as a two capacitor matchbox.")


print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")