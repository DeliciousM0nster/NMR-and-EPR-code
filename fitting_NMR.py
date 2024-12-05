print("\n-------------------------------------------------------\nOkay. 3, 2, 1, let's jam!\n-------------------------------------------------------\n")

'''----------------------------------------Notes----------------------------------------
'''
###		1) Files for analysis should be in the following form: [Cell]_[MeasurementType]_[PC/TC]_[TimeInterval]_[AdditionalNotes]
###			Ex. "Wayne_spindown_PC_1hr_dT20C_FITAMP_20191105_224302"
###			Note: "FITAMP" and the time stamp are added automatically by the analysis vi
###		2) This program requires command line arguments
###			arg1:	First file to analyze, usually pumping chamber (required)
###			arg2:	Second file to analyze, usually target chamber (optional)
###		3) To run from command prompt (windows, with examples below) or terminal (mac), go to the directory this program is in and type the following:
###			python fitting_NMR.py [path.file1] [path.file2]
###			ex. python fitting_NMR.py "C:\Users\Christopher\Documents\Wayne\Wayne_spindown_PC_1hr_dT20C_FITAMP_20191105_224302.txt"
###			ex. python fitting_NMR.py Wayne_spindown_PC_1hr_dT20C_FITAMP_20191105_224302.txt
###			ex. python fitting_NMR.py ./data/Wayne_spindown_PC_1hr_dT20C_FITAMP_20191105_224302.txt
###			ex. python fitting_NMR.py Wayne_spindown_PC_1hr_dT20C_FITAMP_20191105_224302.txt Wayne_spindown_TC_1hr_dT20C_FITAMP_20191105_224601.txt
###
###

'''----------------------------------------Imports----------------------------------------
'''

import sys, re, math, os
import numpy as np
from matplotlib import gridspec
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.optimize import curve_fit
from pathlib import Path

###    

'''----------------------------------------Flags and Options----------------------------------------
'''

### Position of annotation on graph (-99 for default position)
xpos = -99
ypos = -99

### Calibration Constants (for Spin Up)
ovenTemp_calibration = 235
ovenTemp_data = 235
allCalConsts = [0.7949, 0.7522] # ex. [3.22, 3.32, 3.29]; [0] for no calibration constants 
constantsSource = "Ukraine" # Name of the cell (cellName taken from file name) must match this exactly to apply calibration constants

# If data is upside down, set to -1. Normal, set to 1
flipData_PC = 1 
flipData_TC = 1

### modifier for TC signal if too small ("1" for no boost)
boost = 1.5

### How thin (smaller number) or thick (larger number) the fitted line should be
### (it's plotted as many points, not a line)
fitResolution = 1000
attemptsToFit = 50000

### To cut a few points on the end of the data (-1 for no cuts)
frontEndCut = -1

### Initial guess at time constant
tau_initial = 10		# spindown time const. hours or minutes, depending on rate
g_sc_initial = 0.1705	# spinup time const. in hours

### Add Extra Notation to Title ("" for no additional annotation)
extraNote = ""


'''----------------------------------------Functions----------------------------------------
'''

# Notes "3-Parameter Fit"
	# Purpose: Fit the data to equation 39 from the Hybrid paper
	# Takes: t (time), P_0 (initial polarization), P_inf (asymtotic polarization), g_sc (spinup rate)
	# Returns: Point t for fit
def threeParamSpinUp(t, P_0, P_inf, g_sc):
	return ((P_0 - P_inf)*np.exp(-1.0*g_sc*t) + P_inf)

# Notes "5-Parameter Fit"
	# Purpose: Fit the data to equation 41/42 from the Hybrid paper (DOES NOT WORK? NOT SURE WHY.)
	# Takes: t (time), C (constant), g_fast (fast time const), g_slow (slow time const), P_0 (initial polarization), P_inf (asymtotic polarization)
	# Returns: Point t for fit
def fiveParamSpinUp(t, P_0, P_inf, g_fast, g_slow, C):
	return (C*np.exp(-1*g_fast*t) + (P_0 - P_inf - C)*np.exp(-1.0*g_slow*t) + P_inf)

# Notes "Spin Down Fit"
	# Purpose: Fit the data to a simple, decaying exponential
	# Takes: t (time), A (amplitude), tau (time constant)
	# Returns: Point t for fit
def decayingExp(t, A, tau):
	return (A*np.exp(-1.0*t/tau))	

def pathChecker(pList):
	for i, p in enumerate(pList):
		try:
			os.makedirs(p)
		except:
			pass

'''----------------------------------------Main----------------------------------------
'''

# Load the Data in from the file, simplify file name
file = sys.argv[1]
data = np.loadtxt( file )

homePath = Path.cwd()
plotPath = Path(Path(file).parent, "plots")

file = file.split("\\")[len(file.split("\\")) - 1]
file = file.split("/")[len(file.split("/")) - 1]

pathChecker([plotPath, homePath])

if (len(sys.argv) > 2):
	file2 = sys.argv[2] 

# Check if valid file (exit if not), determine spin up or down
spinup = False
pNMR = False
valsColumn = 0
if "spinup" in file.split("_"):
	spinup = True
	scan = "Spin Up"
elif "spindown" in file.split("_"):
	scan = "Spin Down"
	allCalConsts = [0]
else:
	sys.exit("\n\nInvalid File. Try again.\n\n")
if "pNMR" in file.split("_"):
	pNMR = True
	valsColumn = 2
else:
	valsColumn = 1

scanRate = "(No Time Specified)"
scanRateNum = 0
for idx, val in enumerate(file.split("_FITAMP_")[0].split("_")):
	val = val.lower()
	if "hr" in val or "hour" in val or "hours" in val or "hrs" in val:
		scanRate = val
		scanRateUnit = "Hours"
		scanRateNum = val.split("h")[0]
	if "min" in val or "minute" in val or "mins" in val or "minutes" in val:
		scanRate = val
		scanRateUnit = "Minutes"
		scanRateNum = val.split("m")[0]
	if "sec" in val or "second" in val or "secs" in val or "seconds" in val:
		scanRate = val
		scanRateUnit = "Seconds"
		scanRateNum = val.split("s")[0]


# Get cell name and get date/time
cellName = file.split("_")[0]
stamp_date, stamp_time = (0 for i in range(2))

if pNMR:
	stamp_date = str(file.split("_")[len(file.split("_")) - 2]) + "-" + str(file.split("_")[len(file.split("_")) - 1]) + "-" + str(file.split("_")[len(file.split("_")) - 3])
	stamp_date = re.sub('D', '', stamp_date)
	stamp_date = re.sub('.txt', '', stamp_date)
else:
	stamp_date = file.split("_")[len(file.split("_")) - 2]
	stamp_date = str(stamp_date[:4] + "-" + stamp_date[4:6] + "-" + stamp_date[6:])
	stamp_time = file.split("_")[len(file.split("_")) - 1]
	stamp_time = str(stamp_time[:2] + ":" + stamp_time[2:4] + ":" + stamp_time[4:])
	stamp_time = re.sub('.txt', '', stamp_time)

titleAnnotation = cellName + ": " + scanRateNum + "-" + re.sub('s', '', scanRateUnit) + " " + scan + extraNote
if cellName == constantsSource:
	calConst = np.mean(allCalConsts)*((ovenTemp_calibration + 20)/(ovenTemp_data + 20))
else:
	calConst = 0


# Create x data (time in hours)
time = []
for idx, val in enumerate(data[ :,0 ]):
	if idx > frontEndCut:
		if pNMR:
			time.append((val-1)*float(scanRateNum))
		else:
			x_val = val - data[ :,0 ][0]
			if scanRateUnit == "Minutes":
				x_val = x_val*60.0
			elif scanRateUnit == "Seconds":
				x_val = x_val*3600
			time.append(x_val)
			
time = np.asarray(time)


# create y data (amplitudes either in mV or %)
sweep_up, sweep_dn = ([] for i in range(2))
sweeps = []
for idx, val in enumerate(data[ :,valsColumn ]):
	if idx > frontEndCut:
		if pNMR:
			sweeps.append(abs(val))
		else:
			# Gather and average y data (sweep magnitudes in volts)
			sign = math.copysign(1.0, data[:,1][idx])
			sweep_up.append(flipData_PC * sign * np.sqrt( (data[:,1][idx])**2 + (data[:,2][idx])**2 ) )
			sweep_dn.append(flipData_PC * sign * np.sqrt( (data[:,3][idx])**2 + (data[:,4][idx])**2 ) )
if not pNMR:
	#sweeps = [( sign * (g + h)) / 2.0 for g, h in zip(sweep_up, sweep_dn)]
	sweeps = [( (g + h)) / 2.0 for g, h in zip(sweep_up, sweep_dn)]
sweeps = np.asarray(sweeps)

# Create special x data for a smoother, fitted line
time_steps = (time[ len(time)-1 ] - time[0])/(fitResolution - 1)
time_yFitLine = []
i = time[0]
while (i < time[ len(time)-1 ]):
	if i > frontEndCut:
		time_yFitLine.append(i)
	i += time_steps
time_yFitLine.append(time[ len(time)-1 ])
time_yFitLine = np.asarray(time_yFitLine)


# If we have a calibration constant, adjust accordingly here
units = ""
if (calConst != 0 and cellName == constantsSource):
	for inx, val in enumerate(sweeps):
		sweeps[inx] = calConst*val
	units = "%"
else:
	if pNMR:
		units = "V"
	else:
		units = "mV"

# Fit y data
if (spinup): ### ----Spin Up---- ###
	### ----Three Parameter Fit---- ###
	init_vals = [sweeps[0], sweeps[ len(sweeps)-1 ], g_sc_initial] # [P_0, P_inf, g_sc]
	best_vals, covar = curve_fit(threeParamSpinUp, time, sweeps, maxfev=attemptsToFit, p0=init_vals)
	yFit = threeParamSpinUp(time, best_vals[0], best_vals[1], best_vals[2])
	yFitLine = threeParamSpinUp(time_yFitLine, best_vals[0], best_vals[1], best_vals[2])

	# Print Results from fit (rates converted to time constants)
	P_0 = str(np.round(best_vals[0], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[0][0])), 3)) + " " + units
	P_inf = str(np.round(best_vals[1], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[1][1])), 3)) + " " + units
	T_sc = str(np.round(1.0/best_vals[2], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[2][2]))/( best_vals[2]*best_vals[2] ), 3)) + " " + scanRateUnit
	s = "P_inf (PC) = " + str(P_inf) + "\nT_sc (PC) = " + T_sc
	s_printable = f"{best_vals[1]}\n{np.sqrt(covar[1][1])}\n{1.0/best_vals[2]}\n{np.sqrt(covar[2][2])/(best_vals[2]**2)}"
	str(best_vals[1]) + "\n" + str(1.0/best_vals[2])
	
else: ### ----Spin Down---- ###
	init_vals = [sweeps[0], tau_initial] # [A, tau]
	best_vals, covar = curve_fit(decayingExp, time, sweeps, maxfev=attemptsToFit,  p0=init_vals)
	yFit = decayingExp(time, best_vals[0], best_vals[1])
	yFitLine = decayingExp(time_yFitLine, best_vals[0], best_vals[1])

	# Print Results from fit (rates converted to time constants)
	A = str(np.round(best_vals[0], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[0][0])), 3))
	Tau = str(np.round(best_vals[1], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[1][1])), 3))
	s = "Mean Lifetime (PC) = " + Tau + " " + scanRateUnit
	s_printable = f"{best_vals[1]}\n{np.sqrt(covar[1][1])}"

# Calculate Residuals
residuals = sweeps - yFit

### Plots...
figureName = cellName + "_" + scanRate + "_" + scan.split(" ")[0] + scan.split(" ")[1] + "_"
if "prelim" in list(map(lambda x: x.lower(), file.split("_"))):
	figureName += "PRELIMINARY_"  + stamp_date
else:
	figureName += stamp_date
	if "pNMR" not in file.split("_"):
		figureName += "_" + re.sub('.txt', '', file.split("_")[len(file.split("_")) - 1])
plt.figure(figureName)   
gs = gridspec.GridSpec(2,1, height_ratios=[4,1])
ax0 = plt.subplot(gs[0])
if (calConst != 0 and cellName == constantsSource):
	ax0.set_ylabel("% Polarization")
else:
	ax0.set_ylabel("Signal (" + units + ")")

# Now plot it....
ax0.plot( time, sweeps, color='b', marker='o', ls='', label='PC Data' )
ax0.plot( time_yFitLine, yFitLine, color='b', marker='o', ms="0.5",ls='', label='PC Fit' )

if (xpos == -99):
	xpos = time[(len(time)-1)]/4.0
if (ypos == -99):
	if spinup:
		ypos = sweeps[0]
	else:
		ypos = (sweeps[1] + sweeps[0])/2.0


# Plot the Target Chamber too....
if (len(sys.argv) > 2):
	file2 = sys.argv[2]
	data2 = np.loadtxt( file2 )

	sweep_up2, sweep_dn2 = ([] for i in range(2))
	# Gather and average y data (sweep magnitudes in volts)
	for idx, val in enumerate(data2[ :,1 ]):
		if idx > frontEndCut:
			sign = math.copysign(1.0, data2[:,1][idx])
			sweep_up2.append(flipData_TC * sign * np.sqrt( (data2[:,1][idx])**2 + (data2[:,2][idx])**2 ) )
			sweep_dn2.append(flipData_TC * sign * np.sqrt( (data2[:,3][idx])**2 + (data2[:,4][idx])**2 ) )
	sweeps2 = [(boost * (g + h)) / 2.0 for g, h in zip(sweep_up2, sweep_dn2)]
	if (calConst != 0 and cellName == constantsSource):
		for inx, val in enumerate(sweeps2):
			sweeps2[inx] = calConst*val

	if (spinup): ### ----Spin Up---- ###
		### ----Three Parameter Fit---- ###
		init_vals = [sweeps2[0], sweeps2[ len(sweeps2)-1 ], g_sc_initial] # [P_0, P_inf, g_sc]
		best_vals, covar = curve_fit(threeParamSpinUp, time, sweeps2, maxfev=attemptsToFit,  p0=init_vals)
		yFit = threeParamSpinUp(time, best_vals[0], best_vals[1], best_vals[2])
		yFitLine = threeParamSpinUp(time_yFitLine, best_vals[0], best_vals[1], best_vals[2])

		# Print Results from fit (rates converted to time constants)
		P_0 = str(np.round(best_vals[0], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[0][0])), 3)) + " " + units
		P_inf = str(np.round(best_vals[1], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[1][1])), 3)) + " " + units
		T_sc = str(np.round(1.0/best_vals[2], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[2][2]))/( best_vals[2]*best_vals[2] ), 3)) + " " + scanRateUnit
		s += "\nT_sc (TC) = " + T_sc
		s_printable += f"\n{1.0/best_vals[2]}\n{np.sqrt(covar[2][2])/(best_vals[2]**2)}"
		
	else: ### ----Spin Down---- ###
		init_vals = [sweeps2[0], tau_initial] # [A, tau]
		best_vals, covar = curve_fit(decayingExp, time, sweeps2, maxfev=attemptsToFit,  p0=init_vals)
		yFit = decayingExp(time, best_vals[0], best_vals[1])
		yFitLine = decayingExp(time_yFitLine, best_vals[0], best_vals[1])

		# Print Results from fit (rates converted to time constants)
		A = str(np.round(best_vals[0], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[0][0])), 3))
		Tau = str(np.round(best_vals[1], 3)) + " +/- " + str(np.round(np.sqrt(abs(covar[1][1])), 3))
		s += "\nMean Lifetime (TC) = " + Tau + " " + scanRateUnit
		s_printable += f"\n{best_vals[1]}\n{np.sqrt(covar[1][1])}"

	# Now plot it....
	ax0.plot( time, sweeps2, color='r', marker='o', ls='', label='TC Data' )
	ax0.plot( time_yFitLine, yFitLine, color='r', marker='o', ms="0.5", ls='', label='TC Fit' )

	# Calculate Residuals
	residuals2 = sweeps2 - yFit

# Add number of calibration constants to plot
if (calConst != 0 and cellName == constantsSource):
	s += ("\nNum. Calibrations = " + str(len(allCalConsts)))

ax0.annotate(s, (xpos, ypos))
ax0.legend()

# Plot Residuals
ax1 = plt.subplot(gs[1])
ax1.plot( time, residuals, color='DodgerBlue', marker='o', ls='', label='PC' )
if (len(sys.argv) > 2):
	ax1.plot( time, residuals2, color='tomato', marker='o', ls='', label='TC' )
ax1.set_ylabel("Residuals")
ax1.legend()


# Set title and shared x label, then show plots
plt.xlabel( "Time (" + scanRateUnit + ")")
suptitleName = titleAnnotation + "\n"
if "prelim" in list(map(lambda x: x.lower(), file.split("_"))):
	suptitleName += "PRELIMINARY RESULTS (" + stamp_date + ")"
else:
	suptitleName += "Date: " + stamp_date
	if not pNMR:
		suptitleName += "      Time: " + stamp_time
plt.suptitle(suptitleName)

# Print Results
print("\n------------------  " + file + "  ------------------\n")
print(s)
print("\n----------- Raw Data -----------\nTime (" + scanRateUnit + ") = " + str(np.asarray(time)))
print("PC Polarization ("+ units +") = " + str(np.asarray(sweeps)))
if (len(sys.argv) > 2):
	print("TC Polarization ("+ units +") = " + str(np.asarray(sweeps2)))

print("\n" + s_printable)

plt.gcf().canvas.manager.set_window_title(file)

plt.gcf().set_size_inches(12, 8)

os.chdir(plotPath)
plt.savefig(file + ".png", dpi=600)
os.chdir(homePath)

#plt.show()
plt.close()

print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")



