print("\n-------------------------------------------------------\nOkay. 3, 2, 1, let's jam!\n-------------------------------------------------------\n")

'''----------------------------------------Imports----------------------------------------
'''

import sys
import numpy as np
import math
import scipy.constants as const
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib import gridspec
import scipy.stats as stats

xpos = -99
ypos = -99


'''----------------------------------------Functions----------------------------------------
'''

# Notes "Quick Description"
	# Purpose: 
	# Takes: 
	# Returns: 
def Qcurve(v, v0, A, Q):
	return (A*v)/( np.sqrt( ( (v/v0)**2 - 1 )**2 + (1/Q)**2 ) )

# Notes "Quick Description"
	# Purpose: 
	# Takes: 
	# Returns: 
def gain(v0, Q):
	return 1/( np.sqrt( ( (154/v0)**2 - 1 )**2 + (1/Q)**2 ) )

# Notes "Calculating R^2 for a Fit"
	# Purpose: Find R^2
	# Takes: y (the data), res (the residuals from the fit)
	# Returns: R^2
def calcR2(y, res):
	ss_res = np.sum((res)**2)
	ss_tot = np.sum((y - np.mean(y))**2)
	return 1 - (ss_res/ss_tot)

'''----------------------------------------Main----------------------------------------
'''
file = sys.argv[1]
data = np.loadtxt( file )

freq = np.asarray(data[ 0,: ])
ampl = np.asarray(data[ 1,: ])

init_vals = [154, 1, 20] # [v0, A, Q]
best_vals, covar = curve_fit(Qcurve, freq, ampl, p0=init_vals)
yFit = Qcurve(freq, best_vals[0], best_vals[1], best_vals[2])
resid = ampl - yFit

g = gain(best_vals[0], best_vals[2])

# Statistics
r2 = calcR2(ampl, resid)
chi2, chi2_pVal = stats.chisquare(ampl, f_exp=yFit)
chi2 = abs(chi2)
statArray = [r2,chi2,chi2_pVal]


plt.figure("Q Curve")

# Plot Data and Fit
gs = gridspec.GridSpec(2,1, height_ratios=[4,1])
ax0 = plt.subplot(gs[0])

ax0.plot(freq, ampl, 'ro', label="Data")
ax0.plot(freq, yFit, color="b", label="Fit")


if(xpos == -99):
	xpos = freq[0]
if(ypos == -99):
	ypos = 0.6*max(ampl)

s = "Q-value = " + str( np.round(best_vals[2], 3) ) + " +/- " + str( np.round( np.sqrt(abs(covar[2][2])) ) ) + "\nGain at 154 kHz = " + str( np.round(g, 3) )

print(s)
print("\t(Q > 20 is good!)")
print("\nFit Stats:")
print("\tR^2\t= " + str( np.round(statArray[0],3 )))
print("\tChi^2\t= " + str( np.round(statArray[1],3 )))
print("\tP-Val\t= " + str( np.round(statArray[2],3 )))


ax0.legend()
ax0.annotate(s, (xpos, ypos))
ax0.set_ylabel("Amplitude (mV)")

# Plot Residuals
ax1 = plt.subplot(gs[1])
ax1.plot( freq, resid, color='salmon', marker='.', ls='' )
ax1.set_ylabel("Residuals")

# Set title and shared x label, then show plots
plt.xlabel( "Frequency (kHz)" )
# plt.suptitle(cell + " " + target + " Thickness")



plt.show()

print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")