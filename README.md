# NMR-and-EPR-code
Python code related to the NMR/EPR system I rebuilt during my PhD, including data analysis programs. This system was fairly well understood and the code is, in my opinion, not overly complicated as a result; the data was collected in a reliable way with only small variations in data quality and a very high signal to noise ratio. More details can be found in my thesis (available [here](https://doi.org/10.18130/p44g-5b82) in chapter 3.

Overview: The system used during my PhD work partly consisted of the following parts:
 - A ceramic oven (about 8.5" cubed) in which a glass target could be heated through forced air convection
 - 2 large "Holding Field" coils (diameter ~7 ft), magnetic field coils along the z-axis in a Helmholtz configuration creating a constant, homogeanous magnetic field
 - 2 medium "RF Field" coils (diameter ~4ft), magnetic field coils along the y axis creating an oscillating magnetic field, constant in a rotating reference frame
 - 2 small "Pickup Coils" (diameter ~6in), coils with magnet wire used to pick up changing magnetic field signals

### circuitSolver, circuitSolver_companion
The RF coils needed to resonant at a specific freqency, so we used a matching circuit (called an "L-network", consisting of 2 capacitors) to tune the RF coil circuit to said resonant frequency given the inductance (L), capacitance (C), and resistance (R) of the coils themselves. **circuitSolver** can use these values (measured using a multimeter) along with the desired resonant frequency and solve for the capacitance required for each capacitor in the L-Network. **C1** is the capacitor in series with the wire, **C2** is the capacitor that bridges the positive and negative wires. **circuitSolver_companion** was abandoned at some point. I don't think it was ever finished.

### fitting_NMR, fitting_threePoint, fitting_Qcurve, KeithleyValueCollator
These are the data analysis programs:
 - **fitting_NMR** fits polarization over time and was used when either "pumping" the polarization of the target (increasing polarization) or letting it decay naturally over time. While the equation for decay is a simple exponential decay, the equation for increased polarization over time is more complex and includes a calibration constant (or group of them) used to convert mV of signal to percent polarization.
 - **fitting_threePoint** fits several "spindowns", where polarization is measured as it decreases over time. These are fit to a linear fit and the corrected mean lifetime is extracted.
 - **fitting_Qcurve** was used to monitor the signal to noise ratio, which was pretty consistent, so it wasn't used often.
 - **KeithleyValueCollator** was a niche program used ONLY in pNMR measurements, converting raw data output to something that could be plotted. I very rarely did pulsed NMR.

### EPR_RF_field_calc, larmorFreqToField, magneticFieldCalculator, resFreqCalculator
These were helper programs I wrote to do quick calculations that I repeated often (and got tired of punching into a calculator):
 - **EPR_RF_field_calc** was used to calculate the RF field strength for the EPR RF coils to ensure the field was strong enough.
 - **larmorFreqToField** was used to convert a larmor frequency (for protons or electrons) to the strength of the magnetic field inducing it or vice-versa
 - **magneticFieldCalculator** took one or two voltages measured by small coils in the RF field and converted those voltages to magnetic field strength. I had to do this calculation a LOT, so this saved me a ton of time.
 - **resFreqCalculator** used to find natural resonant frequency of a circuit given known inductance, resistance, and capacitance. This was used to test circuits including magnetic field coils to ensure their resonant frequency matched the frequency we were driving them at. resonant frequency for hte circuit could be adjusted using a matching circuit (described above under **circuitSolver**).
