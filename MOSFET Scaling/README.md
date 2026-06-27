Scaling down MOSFET from 1 micron to 62.5 nm.

# Silvaco Simulations

This folder contains ATHENA and ATLAS simulations for MOSFET scaling studies.

Some simulations show nearly resistive ID-VD behavior due to high electric fields and aggressive scaling.

# Cutline dat files
1) Open str file in TonyPlot
2) Take a cutline of required area
3) Do to file and click export
4) Select displayed only and tonyplot user data
5) Change the name of the file from the default 'export' to a desired name
6) Put the name of file in energy_band.py python code

# Python Data Analysis

Scripts for plotting and analyzing Silvaco simulation outputs.

plot_and_threshold_voltage_extraction.py --> transfer characteristics (Id-Vg)

output_characteristics.py --> Id-Vd

## Features

- Linear and log IV plots
- Threshold voltage extraction in terminal
- Multi-gate voltage comparison in output characteristics