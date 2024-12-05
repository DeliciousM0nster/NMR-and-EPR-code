# NMR-and-EPR-code
Python code used in the building, running, and maintenance of the NMR/EPR system I built during my PhD. Also includes Python code to analyze my data.

The system used during my PhD work partly consisted of the following parts:
 - A ceramic oven (about 8.5" cubed) in which a glass target could be heated through forced air convection
 - 2 large "Holding Field" coils (diameter ~7 ft), magnetic field coils along the z-axis in a Helmholtz configuration creating a constant, homogeanous magnetic field
 - 2 medium "RF Field" coils (diameter ~4ft), magnetic field coils along the y axis creating an oscillating magnetic field, constant in a rotating reference frame
 - 2 small "Pickup Coils" (diameter ~6in), coils with magnet wire used to pick up changing magnetic field signals

The RF coils needed to resonant at a specific freqency, so we used a matching circuit (called an "L-network", consisting of 2 capacitors) to tune the RF coil circuit to said resonant frequency given the inductance (L), capacitance (C), and resistance (R) of the coils themselves. **circuitSolver.py** can use these values (measured using a multimeter) along with the desired resonant frequency and solve for the capacitance required for each capacitor in the L-Network. **C1** is the capacitor in series with the wire, **C2** is the capacitor that bridges the positive and negative wires.

Further discriptions of programs coming soon. --Chris (05Dec2024)
