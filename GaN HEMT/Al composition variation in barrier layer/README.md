Analyzing the change brought by varying the Al composition in the barrier layer

# Silvaco Simulations

This folder contains ATLAS simulations for GaN HEMT

Al composition was changed using the variable list given on top and near the l.end statement

# Cutline dat files
1) Open str file in TonyPlot
2) Take a cutline of required area
3) Go to file and click export
4) Select displayed only and tonyplot user data
5) Change the name of the file from the default 'export' to a desired name
6) Put the name of file in x_comp_conc_cb.py python code

# Python Data Analysis

Scripts for plotting and analyzing Silvaco simulation outputs.

x_comp_characteristics.py --> Both output, transfer characteristics, gate current, and breakdown graphs are included in one Python file. Threshold voltage and breakdown voltage is printed in output window.

x_comp_conc_cb.py --> Electron concentration and conduction band energy differences are included in one Python file. 