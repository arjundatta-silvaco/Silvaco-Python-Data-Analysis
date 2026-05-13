import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# FUNCTION: READ SILVACO Id-Vg DATA
# =========================================================

def read_idvg(filename):

    vg_list = []
    id_list = []

    with open(filename, "r") as f:

        for line in f:

            # Only use actual data rows
            if line.startswith("d"):

                parts = line.split()

                # Remove leading 'd'
                values = list(map(float, parts[1:]))

                # Your identified column format:
                # [Vg, Vg, Ig, Vd, Vd, Id, Vs, Vs, Is]

                vg = values[0]
                id_val = values[5]

                vg_list.append(vg)
                id_list.append(id_val)

    return np.array(vg_list), np.array(id_list)

# =========================================================
# FUNCTION: THRESHOLD VOLTAGE EXTRACTION
# =========================================================

def extract_Vt(vg, id_data):

    vg = np.array(vg)
    id_data = np.array(id_data)

    # Use absolute current
    id_abs = np.abs(id_data)

    # Remove zeros
    valid = id_abs > 0

    vg = vg[valid]
    id_abs = id_abs[valid]

    # If not enough points
    if len(vg) < 5:
        return None

    # -----------------------------------------------------
    # Use upper-current region for linear fitting
    # -----------------------------------------------------

    threshold_current = 0.1 * np.max(id_abs)

    mask = id_abs > threshold_current

    x = vg[mask]
    y = id_abs[mask]

    # Need enough points for fitting
    if len(x) < 3:
        return None

    # Linear fit
    m, c = np.polyfit(x, y, 1)

    # Avoid divide-by-zero
    if abs(m) < 1e-20:
        return None

    # Extrapolated threshold voltage
    Vt = -c / m

    return Vt

# =========================================================
# FILE LIST
# =========================================================

files = [
    "scl_1_vg_vd_5.dat",
    "scl_0.5_vg_vd_5.dat",
    "scl_0.25_vg_vd_5.dat",
    "scl_0.125_vg_vd_5.dat",
    "scl_0.0625_vg_vd_5.dat"
]

# =========================================================
# MAIN PROGRAM
# =========================================================

plt.figure(figsize=(8,6))

for file in files:

    # Read data
    vg, id_data = read_idvg(file)

    # Plot overlay
    plt.plot(vg, id_data, linewidth=2, label=file)

    # Extract threshold voltage
    Vt = extract_Vt(vg, id_data)

    # Print result
    if Vt is not None:
        print(f"{file} --> Vt = {Vt:.4f} V")
    else:
        print(f"{file} --> Vt extraction failed")

# =========================================================
# PLOT SETTINGS
# =========================================================

plt.xlabel("Gate Voltage Vg (V)")
plt.ylabel("Drain Current Id (A)")

plt.title("Overlay of Id-Vg Curves")

plt.grid(True)
plt.legend()

# Start Y-axis from zero
plt.ylim(bottom=0)

# =========================================================
# TRANSCONDUCTANCE PLOT
# =========================================================

plt.figure(figsize=(8,6))

for file in files:

    # Read data
    vg, id_data = read_idvg(file)

    # Numerical differentiation
    gm = np.gradient(id_data, vg)

    # Plot gm
    plt.plot(vg, gm, linewidth=2, label=file)

plt.xlabel("Gate Voltage Vg (V)")
plt.ylabel("Transconductance gm (S)")

plt.title("Transconductance (gm) vs Vg")

plt.grid(True)
plt.legend()

plt.show()