print("\n-------------------------------------------------------\nOkay. 3, 2, 1, let's jam!\n-------------------------------------------------------\n")


'''----------------------------------------Notes----------------------------------------
'''
###		


'''----------------------------------------Imports----------------------------------------
'''

import sys
import numpy as np
import scipy.constants as const


'''----------------------------------------Main----------------------------------------
'''

#B = float(sys.argv[1])

#gamma = 0.761815 * const.value("electron gyromag. ratio over 2 pi") / 10
gamma = 0.761815 * const.value("proton gyromag. ratio over 2 pi") / 10

B_or_F = sys.argv[2].lower()

B, freq = (0 for i in range(2))

if B_or_F == 'khz':
	freq = float(sys.argv[1]) # in kHz
	B = freq / gamma
if B_or_F == 'g':
	B = float(sys.argv[1]) # in Gauss
	freq = gamma * B

print("Field at Larmor Frequency of " + str(np.round(freq, 3)) + " kHz is " + str(np.round(B, 3)) + " G")

print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")