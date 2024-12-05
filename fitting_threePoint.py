print("\n-------------------------------------------------------\nOkay. 3, 2, 1, let's jam!\n-------------------------------------------------------\n")

'''----------------------------------------Notes----------------------------------------
'''
###		1) Files for analysis should be in the following form: [Cell]_[MeasurementType]_[PC/TC]_[TimeInterval]_[AdditionalNotes]
###			Ex. "Wayne_spindown_PC_1hr_dT20C_FITAMP_20191105_224302"
###			Note: "FITAMP" and the time stamp are added automatically by the analysis vi
###		2) This program requires command line arguments
###			arg1:	First file to analyze (required)
###			arg2:	Second file to analyze (required)
###			arg#:	The #th file to analyze (optional, just add as many as you want after 2)
###		3) To run from command prompt (windows, with examples below) or terminal (mac), go to the directory this program is in and type the following:
###			python fitting_threePoint.py [path.file1] [path.file2] [path.file3].......
###			ex. python fitting_threePoint.py Wayne_spindown_PC_1hr_dT20C_FITAMP_20191105_224302.txt Wayne_spindown_TC_1hr_dT20C_FITAMP_20191105_224601.txt
###
###



'''----------------------------------------Imports----------------------------------------
'''

import sys
import numpy as np
import math
from matplotlib import gridspec
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import datetime


'''----------------------------------------Flags and Options----------------------------------------
'''

### Sets a specific location for the analysis on the graph (-99 for default location)
xpos = -99
ypos = 0.055

### Adds an additional data point (-99 for not adding a point)
x_point = -99 # 1.0/6.0
y_point = -99 # 1.0/9.097

### To cut a few points on the end of the data (-1 for no cuts)
frontEndCut = -1

'''----------------------------------------Functions----------------------------------------
'''
# Notes "Quick Description"
	# Purpose: 
	# Takes: 
	# Returns: 
def threePoint(n, G_0, G_afp):
	return ((G_afp)*(n) + G_0)

# Notes "Spin Down Fit"
	# Purpose: Fit the data to a simple, decaying exponential
	# Takes: t (time), A (amplitude), tau (time constant)
	# Returns: Point t for fit
def decayingExp(t, A, tau):
	return (A*np.exp(-1.0*t/tau))	

'''----------------------------------------Main----------------------------------------
'''

n, t = ([] for i in range(2))

for idx, val in enumerate(sys.argv):
	if (idx != 0):
		file = sys.argv[idx]
		data = np.loadtxt( file )
		file = file.split("\\")[len(file.split("\\")) - 1]
		file = file.split("/")[len(file.split("/")) - 1]
		cellName = file.split("_")[0]

		pNMR = False
		valsColumn = 1
		if "pNMR" in file.split("_"):
			pNMR = True
			valsColumn = 2

		# Create x data (time in hours)
		time = []
		scanRate = 0
		for i in file.split("_"):
			i = i.lower()
			if "hour" in i or "hr" in i:
				scanRate = float(i.split("h")[0])
			if "min" in i or "minute" in i:
				scanRate = float(i.split("m")[0])/60.0
			if "sec" in i or "second" in i:
				scanRate = float(i.split("s")[0])/3600.0
		n.append(1.0/scanRate)

		for inx, value in enumerate(data[ :,0 ]):
			if inx > frontEndCut:
				if pNMR:
					time.append((value-1)*scanRate)
				else:
					time.append(value - data[ :,0 ][0])
		time = np.asarray(time)

		sweep_up, sweep_dn = ([] for i in range(2))
		sweeps = []
		# Gather and average y data (sweep magnitudes in volts)
		for inx, val in enumerate(data[ :,valsColumn ]):
			if inx > frontEndCut:
				if pNMR:
					sweeps.append(abs(val))
				else:
					sign = math.copysign(1.0, data[:,1][inx])
					sweep_up.append(sign * np.sqrt( (data[:,1][inx])**2 + (data[:,2][inx])**2 ) )
					sweep_dn.append(sign * np.sqrt( (data[:,3][inx])**2 + (data[:,4][inx])**2 ) )
		if not pNMR:
			sweeps = [( sign * (g + h)) / 2.0 for g, h in zip(sweep_up, sweep_dn)]

		init_vals = [sweeps[0], 24.0] # [A, tau]
		best_vals, covar = curve_fit(decayingExp, time, sweeps, p0=init_vals)

		t.append(1.0/best_vals[1])

# Sort into ascending order of n
check = 1
while (check==1):
	check = 0
	lastVal = 0
	lastIdx = 0
	for idx, val in enumerate(n):
		if(val < lastVal):
			n[idx], n[lastIdx] = n[lastIdx], n[idx]
			t[idx], t[lastIdx] = t[lastIdx], t[idx]
			check = 1
		lastIdx = idx
		lastVal = val

init_vals = [ t[len(t)-1], 0.0 ]
best_vals, covar = curve_fit(threePoint, n, t, p0=init_vals)
yFit = threePoint(np.asarray(n), best_vals[0], best_vals[1])
residuals = t - yFit


s = ("Adjusted Lifetime: " + str(np.round(1.0/best_vals[0], 3)))
if (len(sys.argv) > 3):
	s += (" +/- " + str(np.round(np.sqrt(abs(covar[0][0]))/( best_vals[0]*best_vals[0] ), 3)))
s += (" hours\nLosses per scan: " + str(np.round(100*(1.0-np.exp(-1.0*best_vals[1])), 3)))
if (len(sys.argv) > 3):
	s += (" +/- " + str(np.round(100*np.sqrt(abs(best_vals[1]*best_vals[1]*covar[1][1]*covar[1][1])), 3)))
s += " %\n"




plt.figure(cellName + "_ThreePointPlot" + "_" + str(datetime.date.today()))
gs = gridspec.GridSpec(2,1, height_ratios=[4,1])
ax0 = plt.subplot(gs[0])
ax0.plot( n, t, color='0.6', marker='o', ls='' )
ax0.plot( n, yFit, color='r', marker=',', ls=':' )
if (x_point != -99 or y_point != -99):
	ax0.plot( x_point, y_point, color='g', marker='x', ls='' )
ax0.set_ylabel("1/t for Mean Lifetime 't'")

if (xpos == -99):
	xpos = n[0] + 0.3*(n[len(n)-1]-n[0])
if (ypos == -99):
	ypos = t[0]

ax0.annotate(s, (xpos, ypos))

ax1 = plt.subplot(gs[1], sharex=ax0)
ax1.plot( n, residuals, color='b', marker='o', ls='' )
ax1.set_ylabel("Residuals")

plt.xlabel("1/n for Scan Rate 'n'")
plt.suptitle("Three Point Plot: " + cellName)
print(s)


print("\n----------- Raw Data -----------\n1 / interval:\t" + str(np.asarray(n)) + "\n1 / lifetime:\t" + str(np.asarray(t)))

print("\nCopy/Paste (lifetime, err):\n" + str(1.0/best_vals[0]) + "\n" + str(np.sqrt(abs(covar[0][0]))/( best_vals[0]*best_vals[0] )))
ax0.set_ylim([0.055, 0.14])
plt.show()



print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")