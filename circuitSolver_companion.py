print("\n-------------------------------------------------------\nOkay. 3, 2, 1, let's jam!\n-------------------------------------------------------\n")


'''----------------------------------------Notes----------------------------------------
'''

###		CURRENTLY DOESN'T WORK (08Dec2021)

###		1) This program requires command line arguments
###			arg1:	File to analyze, x-values (kHz) in first column, y-values (arb. units) in second column
###			arg2:	Sign (+ or -) to tell the program to try fitting increasing or decreasing exponential curve
###

'''----------------------------------------Imports----------------------------------------
'''

import sys
import re
import numpy as np
import math
from scipy.optimize import curve_fit
from matplotlib import gridspec
import matplotlib.pyplot as plt


###    

'''----------------------------------------Flags and Options----------------------------------------
'''

### Initial guess at time constant and amplitude
tau_in = 30
A_in = 1200
sign = sys.argv[2]
targetFreq = 154		# Target Freq in kHz
fitResolution = 10000
XvalModifier = 1		# Convert frequencies to other metric prefixes (1000 changes to Hz)
YvalModifier = 1		# Convert y values to other metric prefixes
base = math.e


'''----------------------------------------Functions----------------------------------------
'''

# Notes "Increasing Exponential Fit"
	# Purpose: Fit the data to a simple exponential
	# Takes: x, A (amplitude), tau (time constant)
	# Returns: Point x for fit
def growingExp(x, A, tau):
	return (A*(base**(1.0*x/tau)))

# Notes "Decaying Exponential Fit"
	# Purpose: Fit the data to a simple exponential
	# Takes: x, A (amplitude), tau (time constant)
	# Returns: Point x for fit
def decayingExp(x, A, tau):
	return (A*(base**(-1.0*x/tau)))

'''----------------------------------------Main----------------------------------------
'''

# Load the Data in from the file, sort into x and y vals
# File should be x-values in one column, y-values in the next, each val seperated by a tab 
file = sys.argv[1]
data = np.loadtxt( file )

# x-values in kHz, y-values arbitrary
x = []
y = []
for idx, val in enumerate(data[ :,0 ]):
	x.append(val*XvalModifier)
for idx, val in enumerate(data[ :,1 ]):
	y.append(val*YvalModifier)
x = np.asarray(x)
y = np.asarray(y)

print(x)
print(y)

x_steps = (x[ len(x)-1 ] - x[0])/(fitResolution - 1)
x_yFitLine = []
i = x[0]
while (i < x[ len(x)-1 ]):
	x_yFitLine.append(i)
	i += x_steps

x_yFitLine.append(x[ len(x)-1 ])
x_yFitLine = np.asarray(x_yFitLine)

init_vals = [A_in, tau_in]
targetFreq_val = 0
if sign == "+":
	best_vals, covar = curve_fit(growingExp, x, y, p0=init_vals)
	yFit = growingExp(x, best_vals[0], best_vals[1])
	yFitLine = growingExp(x_yFitLine, best_vals[0], best_vals[1])
	targetFreq_val = growingExp(targetFreq, best_vals[0], best_vals[1])
elif sign == "-":
	best_vals, covar = curve_fit(decayingExp, x, y, p0=init_vals)
	yFit = decayingExp(x, best_vals[0], best_vals[1])
	yFitLine = decayingExp(x_yFitLine, best_vals[0], best_vals[1])
	targetFreq_val = decayingExp(targetFreq, best_vals[0], best_vals[1])
else:
	print("Invalid sign")

print(best_vals)


### Plots...
plt.plot( x, y, color='r', marker='o', ls='', label='Data' )
plt.plot( x_yFitLine, yFitLine, color='r', marker=',',ls='', label='Fit' )
plt.plot( targetFreq, targetFreq_val, color='b', marker='o', label='Target Value' )
plt.xscale('log')

print("Value at target freq of " + str(targetFreq) + " kHz is " + str(targetFreq_val))

plt.legend()
plt.show()

print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")