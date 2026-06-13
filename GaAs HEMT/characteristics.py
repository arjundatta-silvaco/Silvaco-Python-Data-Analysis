import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# READ SILVACO IDVG FILE
# =========================================================

def read_idvg(filename):

    vg_list = []
    id_list = []

    with open(filename, "r") as f:

        for line in f:

            if line.startswith("d"):

                parts = line.split()
                values = list(map(float, parts[1:]))

                # Format:
                # [Vd, Vd, Id, Vg, Vg, Ig, Vs, Vs, Is]

                vg = values[3]
                id_val = values[2]

                vg_list.append(vg)
                id_list.append(id_val)

    return np.array(vg_list), np.array(id_list)


# =========================================================
# READ SILVACO IDVD FILE
# =========================================================

def read_idvd(filename):

    vd_list = []
    id_list = []

    with open(filename, "r") as f:

        for line in f:

            if line.startswith("d"):

                parts = line.split()
                values = list(map(float, parts[1:]))

                # Format:
                # [Vd, Vd, Id, Vg, Vg, Ig, Vs, Vs, Is]

                vd = values[0]
                id_val = values[2]

                vd_list.append(vd)
                id_list.append(id_val)

    return np.array(vd_list), np.array(id_list)


# =========================================================
# THRESHOLD VOLTAGE EXTRACTION
# Constant Current Method
# =========================================================

def extract_vth(vg, id_data):

    Ith = 1e-5  # A

    vg = np.array(vg)
    id_abs = np.abs(id_data)

    if np.max(id_abs) < Ith:
        return None

    # Sort in case data isn't ordered
    idx = np.argsort(vg)

    vg = vg[idx]
    id_abs = id_abs[idx]

    # Find first crossing of Ith
    for i in range(1, len(vg)):

        if id_abs[i-1] < Ith and id_abs[i] >= Ith:

            x1 = vg[i-1]
            x2 = vg[i]

            y1 = id_abs[i-1]
            y2 = id_abs[i]

            # Linear interpolation
            vth = x1 + (Ith - y1) * (x2 - x1) / (y2 - y1)

            return vth

    return None


# =========================================================
# FILES
# =========================================================

idvd_files = [
    "mod_idvd_1.dat",
    "mod_idvd_2.dat"
]

idvg_files = [
    "mod_idvg_02_1.dat",
    "mod_idvg_02_2.dat"
]

# =========================================================
# CREATE FIGURE
# =========================================================

fig, (ax1, ax2) = plt.subplots(
    1,
    2,
    figsize=(14, 6)
)

# =========================================================
# ID-VD PLOTS
# =========================================================

for file in idvd_files:

    try:

        vd, id_data = read_idvd(file)

        ax1.plot(
            vd,
            np.abs(id_data),
            linewidth=2,
            label=file
        )

    except Exception as e:

        print(f"Error reading {file}: {e}")

ax1.set_title("ID-VD Characteristics")
ax1.set_xlabel("Drain Voltage (V)")
ax1.set_ylabel("Drain Current (A)")
ax1.grid(True)
ax1.legend()

# =========================================================
# ID-VG PLOTS
# =========================================================

for file in idvg_files:

    try:

        vg, id_data = read_idvg(file)

        ax2.plot(
            vg,
            np.abs(id_data),
            linewidth=2,
            label=file
        )

        # Threshold voltage extraction
        vth = extract_vth(vg, id_data)

        if vth is not None:

            print(f"{file} --> Vth = {vth:.4f} V")

        else:

            print(f"{file} --> DEVICE OFF")

    except Exception as e:

        print(f"Error reading {file}: {e}")

ax2.set_title("ID-VG Characteristics")
ax2.set_xlabel("Gate Voltage (V)")
ax2.set_ylabel("Drain Current (A)")
ax2.grid(True)
ax2.legend()

# =========================================================
# FINALIZE
# =========================================================

plt.tight_layout()
plt.show()