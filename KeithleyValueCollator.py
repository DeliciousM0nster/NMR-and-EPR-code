print("\n-------------------------------------------------------\nOkay. 3, 2, 1, let's jam!\n-------------------------------------------------------\n")

'''----------------------------------------Imports----------------------------------------
'''

import sys
import os
import numpy as np
from matplotlib import gridspec
import matplotlib.pyplot as plt


'''----------------------------------------Functions----------------------------------------
'''


'''----------------------------------------Main----------------------------------------
'''

path = sys.argv[1]

timeStamps = []
time = []
voltages = []
count = 0
timeUnit = 1

for idx, val in enumerate(path.split("_")):
	if "minute" in val:
		timeUnit = float(val.split("minute")[0])/60.0
	if "hr" in val:
		timeUnit = float(val.split("hr")[0])

for filename in os.listdir(path):
	file = path + filename

	timeStamps.append(filename.split("Keithley_")[1])
	time.append(count)
	voltages.append(np.loadtxt( file ))

	count += timeUnit

for i in range(len(timeStamps)):
	print(str(timeStamps[i]) + "\t" + str(voltages[i]))

plt.figure("Keithley")   
gs = gridspec.GridSpec(1,1)
ax0 = plt.subplot(gs[0])

ax0.plot( time, voltages, color='0.6', marker='o', ls='', label='Keithley Values' )
plt.show()



print("\n-------------------------------------------------------\nSee you, Space Cowboy...\n-------------------------------------------------------\n")