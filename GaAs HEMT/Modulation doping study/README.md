Comparative study of presence versus absence of modulation doping in GaAs HEMT

# Silvaco Simulations

This folder contains ATHENA and ATLAS simulations for GaAs HEMT

Absence of modulation doping shows drain current of the magnitude 1E-17, only noise.

# Cutline dat files
1) Open str file in TonyPlot
2) Take a cutline of required area
3) Do to file and click export
4) Select displayed only and tonyplot user data
5) Change the name of the file from the default 'export' to a desired name
6) Put the name of file in energy_band.py python code

# Electron concentration Origin Plot
Use origin for the file 'gaas_hemt_mod_doping.opju'

# Python Data Analysis

Scripts for plotting and analyzing Silvaco simulation outputs.

characteristics.py --> Both output and transfer characteristics are included in one python file. Threshold voltage is printed in output window.

energy_band.py --> Code for getting the energy band plots from doped_energy_band1.dat and undoped_energy_band1.dat