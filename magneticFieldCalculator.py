print("\n-------------------------------------------------------\nOkay. 3, 2, 1, let's jam!\n-------------------------------------------------------\n")


'''----------------------------------------Notes----------------------------------------
'''
###		1) This program requires command line arguments
###			arg1:	Frequency in kHz (required)
###			arg2:	Top RMS voltage in mV (required)
###			arg3:	Bottom RMS voltage in mV (required)
###		2) If you use a different test coil than I use, you'll need to edit the information for the coil (under the heading "Test Coil Information")
###			Default Coils are:
###				Top: "Banging" Coil (should be taped to yardstick, N=5, d=6.7cm)
###				Bottom: "Large" Coil (should be the one connected to the "SIG. GEN" input on the A-Phi box, N=5, d=10cm)
###		3) To run from command prompt (windows, with examples below) or terminal (mac), go to the directory this program is in and type the following:
###			python magneticFieldCalculator.py [frequency] [top voltage] [bottom voltage]
###			ex. python magneticFieldCalculator.py 91 138 310
###		4) For small losses, need 50-100 mG in rotating frame
###


'''----------------------------------------Imports----------------------------------------
'''

import sys
import numpy as np
import scipy.constants as const


'''----------------------------------------Flags and Options----------------------------------------
'''

### Frequency (in kHz)
	### NMR (big coils) ~= 154
	### EPR (big coils) ~= 42
	### EPR (small coils) ~= 9550
f = float(sys.argv[1])

### Test Coil Information (verify before running)
	# -1 = Custom Coil (change custom_N and custom_d below)
	# 0 = Big Test Coil 		N=5, d=10cm
	# 1 = Little Test Coil 		N=9, d=3.5cm
	# 2 = Banging Test Coil 	N=5, d=6.7cm
coil_top = 0  		# Default 2
coil_bottom = 0 	# Default 0
custom_N = 5
custom_d = 3.81

'''----------------------------------------Flags and Options----------------------------------------
'''

# Notes "Field Calculation"
	# Purpose: Calculates the field based on the RMS voltage
	# Takes: testCoil (name of the coil being used), V (RMS voltage measurement), position (top/bottom for above/below the target)
	# Returns: Central Field (in mG)
def fieldCalc(testCoil, V, position):
	testCoilname = "BLANK"
	N = 0 	### Number of Turns
	d = 0	### diameter of test coil (cm)

	if (testCoil == -1):
		N = custom_N
		d = custom_d
		testCoilname = "CUSTOM Coil"
	elif (testCoil == 0):
		N = 5
		d = 10
		testCoilname = "Big Test Coil"
	elif (testCoil == 1):
		N = 9
		d = 3.5
		testCoilname = "Little Test Coil"
	elif (testCoil == 2):
		N = 5
		d = 6.7
		testCoilname = "Banging Test Coil"
	else:
		sys.exit("WARNING: Need Proper Test Coil Selected")

	r = d/200
	B = ( (np.sqrt(2)*V) / ( (N*np.pi*r*r)*w ) )

	### Find current in RF coils (in mA)
	I = 1000*((5/4)**(3/2))*R_RF/(N_RF*const.mu_0)*B 	# Formula from Wiki page for Helmholtz coils
	B = 1000*10000*B 	# Converts Tesla to milliGauss
	B_rf = B/2 			# Shifts field to rotating frame

	print(position + " RF Coil:\n\tMeasuring Coil: " + testCoilname + "\n\tRMS Voltage: " + str(np.round(1000*V, 3)) + " mV\n\tCntrl Field, Rotating Frame: " + str(np.round(B_rf, 3)) + " mG")
	print("\tEstimated current in RF coils: " + str(np.round(I, 3)) + " mA")

	return B_rf


'''----------------------------------------Main----------------------------------------
'''


### RF Coil information (verify before running)
N_RF = 16	### Number of turns for a single coil 
R_RF = 24	### Radius of 1 RF coil (in inches)

R_RF /= 39.3701		### Converts R_RF to meters (SI units)				
w = 2*np.pi*f*1000 	### Converts freq to angular freq

print("RF Frequency: " + str(f) + " kHz\n")

### RMS Voltage (mV)
V_top = float(sys.argv[2])/1000
V_bottom = float(sys.argv[3])/1000

### Calculate the Field from each coil
B_top = fieldCalc(coil_top, V_top, "Top")
B_bottom = fieldCalc(coil_bottom, V_bottom, "Bottom")


print("\nAverage RF Field: " + str( np.round((B_top + B_bottom)/2, 3)) + " mG")
## print( "\n\tNOTE: (50-100 mG in rotating frame for best results)" )
print("\n\n")

print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")