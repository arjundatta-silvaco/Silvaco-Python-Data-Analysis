import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# FILES
# ==========================================================

UNDOPED_FILE = "undoped_energy_band1.dat"
DOPED_FILE   = "doped_energy_band1.dat"

# ==========================================================
# READ SILVACO ENERGY BAND FILE
# ==========================================================

def read_energy_band(filename):

    data = np.loadtxt(filename, skiprows=6)

    x   = data[:, 0]
    Efn = data[:, 1]      # Electron Quasi-Fermi Level
    Ev  = data[:, 2]      # Valence Band Energy
    Ec  = data[:, 3]      # Conduction Band Energy

    return x, Efn, Ev, Ec

# ==========================================================
# REMOVE LEADING ZERO PADDING
# ==========================================================

def trim_padding(x, Efn, Ev, Ec):

    valid = np.where(np.abs(Ec) > 1e-8)[0]

    if len(valid) == 0:
        return x, Efn, Ev, Ec

    start = valid[0]

    return (
        x[start:],
        Efn[start:],
        Ev[start:],
        Ec[start:]
    )

# ==========================================================
# AUTOMATIC ENERGY LIMITS
# ==========================================================

def auto_energy_limits(*arrays, padding_fraction=0.05):

    ymin = min(np.min(arr) for arr in arrays)
    ymax = max(np.max(arr) for arr in arrays)

    padding = padding_fraction * (ymax - ymin)

    return ymin - padding, ymax + padding

# ==========================================================
# LOAD DATA
# ==========================================================

x_u, Efn_u, Ev_u, Ec_u = read_energy_band(UNDOPED_FILE)
x_d, Efn_d, Ev_d, Ec_d = read_energy_band(DOPED_FILE)

# ==========================================================
# REMOVE LEADING ZERO REGIONS
# ==========================================================

x_u, Efn_u, Ev_u, Ec_u = trim_padding(
    x_u, Efn_u, Ev_u, Ec_u
)

x_d, Efn_d, Ev_d, Ec_d = trim_padding(
    x_d, Efn_d, Ev_d, Ec_d
)

# ==========================================================
# CONVERT POSITION TO nm
# ==========================================================

x_u = x_u * 1000
x_d = x_d * 1000

# ==========================================================
# FIGURE 1
# UNDOPED HEMT
# ==========================================================

plt.figure(figsize=(10,6))

plt.plot(
    x_u,
    Ec_u,
    linewidth=3,
    label='Conduction Band $E_C$'
)

plt.plot(
    x_u,
    Ev_u,
    linewidth=3,
    label='Valence Band $E_V$'
)

plt.plot(
    x_u,
    Efn_u,
    'k--',
    linewidth=2.5,
    label='Electron Quasi-Fermi Level'
)

plt.xlabel('Distance (nm)', fontsize=13)
plt.ylabel('Energy (eV)', fontsize=13)

plt.title(
    'Undoped AlGaN/GaN HEMT Energy Band Diagram',
    fontsize=16,
    weight='bold'
)

plt.ylim(
    auto_energy_limits(Ec_u, Ev_u, Efn_u)
)

plt.grid(True, alpha=0.3)

plt.legend(
    fontsize=11,
    loc='upper right'
)

plt.margins(x=0.01, y=0.03)

plt.tight_layout()

# ==========================================================
# FIGURE 2
# MODULATION-DOPED HEMT
# ==========================================================

plt.figure(figsize=(10,6))

plt.plot(
    x_d,
    Ec_d,
    linewidth=3,
    label='Conduction Band $E_C$'
)

plt.plot(
    x_d,
    Ev_d,
    linewidth=3,
    label='Valence Band $E_V$'
)

plt.plot(
    x_d,
    Efn_d,
    'k--',
    linewidth=2.5,
    label='Electron Quasi-Fermi Level'
)

plt.xlabel('Distance (nm)', fontsize=13)
plt.ylabel('Energy (eV)', fontsize=13)

plt.title(
    'Modulation-Doped AlGaN/GaN HEMT Energy Band Diagram',
    fontsize=16,
    weight='bold'
)

plt.ylim(
    auto_energy_limits(Ec_d, Ev_d, Efn_d)
)

plt.grid(True, alpha=0.3)

plt.legend(
    fontsize=11,
    loc='upper right'
)

plt.margins(x=0.01, y=0.03)

plt.tight_layout()

# ==========================================================
# FIGURE 3
# CONDUCTION BAND COMPARISON
# ==========================================================

plt.figure(figsize=(10,6))

plt.plot(
    x_u,
    Ec_u,
    linewidth=3,
    color='crimson',
    label='Undoped Barrier'
)

plt.plot(
    x_d,
    Ec_d,
    linewidth=3,
    color='green',
    label='Modulation-Doped Barrier'
)

# Single Fermi level curve

plt.plot(
    x_u,
    Efn_u,
    'k--',
    linewidth=2.5,
    label='Electron Quasi-Fermi Level'
)

plt.xlabel('Distance (nm)', fontsize=13)
plt.ylabel('Energy (eV)', fontsize=13)

plt.title(
    'Conduction Band Comparison',
    fontsize=16,
    weight='bold'
)

plt.ylim(
    auto_energy_limits(Ec_u, Ec_d, Efn_u)
)

plt.grid(True, alpha=0.3)

plt.legend(
    fontsize=11,
    loc='upper right'
)

plt.margins(x=0.01, y=0.03)

plt.tight_layout()

# ==========================================================
# DISPLAY FIGURES
# ==========================================================

plt.show()