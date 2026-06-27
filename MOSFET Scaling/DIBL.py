import numpy as np
import matplotlib.pyplot as plt

# ==========================================================
# FILES
# ==========================================================

UNBIASED = "unbiased1.dat"
BIASED   = "biased1.dat"

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

x_u, Efn_u, Ev_u, Ec_u = read_energy_band(UNBIASED)
x_d, Efn_d, Ev_d, Ec_d = read_energy_band(BIASED)

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
# FIGURE 1
# Unbiased MOSFET
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
    'Unbiased MOSFET Energy Band Diagram',
    fontsize=16,
    weight='bold'
)

plt.ylim(
    auto_energy_limits(Ec_u, Ev_u, Efn_u)
)

plt.grid(True, alpha=0.3)

plt.legend(
    fontsize=11,
    loc='upper left'
)

plt.margins(x=0.01, y=0.03)

plt.tight_layout()

# ==========================================================
# FIGURE 2
# Biased MOSFET
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
    'Biased MOSFET Energy Band Diagram',
    fontsize=16,
    weight='bold'
)

plt.ylim(
    auto_energy_limits(Ec_d, Ev_d, Efn_d)
)

plt.grid(True, alpha=0.3)

plt.legend(
    fontsize=11,
    loc='upper left'
)

plt.margins(x=0.01, y=0.03)

plt.tight_layout()

# ==========================================================
# DISPLAY FIGURES
# ==========================================================

plt.show()