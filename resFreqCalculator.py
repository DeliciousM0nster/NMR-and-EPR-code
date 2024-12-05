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
	sys.argv[1] is coil (L) inductance in uH
	sys.argv[2] is coil (C) capacitance in nF
	sys.argv[3] is coil (R) resistance in Ohms

'''

L = float(sys.argv[1])*(10**-6)
C = float(sys.argv[2])*(10**-9)
R = float(sys.argv[3])

f = (1000/(2*np.pi))*( np.sqrt( (1/(L*C)) - (R/L)**2 )) 	# Freq in Hz

print("Res Freq of Coil:\n\t" + str(np.round(f, 3)) + " Hz\n\t" + str(np.round(f/1000, 3)) + " kHz\n\t" + str(np.round(f/1000000, 3)) + " MHz\n\t")



print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")