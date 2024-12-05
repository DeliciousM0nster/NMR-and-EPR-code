print("\n-------------------------------------------------------\nOkay. 3, 2, 1, let's jam!\n-------------------------------------------------------\n")

'''----------------------------------------Imports----------------------------------------
'''

import sys
import numpy as np
import scipy.constants as const

'''----------------------------------------Functions----------------------------------------
'''
# Notes "Quick Description"
	# Purpose: 
	# Takes: 
	# Returns: 
def example():
	pass

'''----------------------------------------Main----------------------------------------
'''

r = 0.0889
N = 2
Vpp = 8
w = 2*np.pi*9500000

B = (1/4)*(Vpp/(w*N*np.pi*r*r))*10000000

print("Estimated Field Strength for 9.5 MHz RF field at 8 Vpp: " + str(np.round(B, 3)) + " mG")

print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")