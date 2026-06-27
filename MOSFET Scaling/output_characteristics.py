import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# FUNCTION: READ SILVACO Id-Vd DATA
# =========================================================

def read_idvd(filename):

    vd_list = []
    id_list = []

    with open(filename, "r") as f:

        for line in f:

            if line.startswith("d"):

                parts = line.split()

                values = list(map(float, parts[1:]))

                # [Vg, Vg, Ig, Vd, Vd, Id, Vs, Vs, Is]

                vd = values[4]
                id_val = values[5]

                vd_list.append(vd)
                id_list.append(id_val)

    return np.array(vd_list), np.array(id_list)


# =========================================================
# FILE GROUPS
# =========================================================

mosfet1_files = [
    "scl_1_vd_out_at_vg_00V.dat",
    "scl_1_vd_out_at_vg_05V.dat",
    "scl_1_vd_out_at_vg_10V.dat",
    "scl_1_vd_out_at_vg_15V.dat",
    "scl_1_vd_out_at_vg_20V.dat"
]

mosfet2_files = [
    "scl_0.5_vd_out_at_vg_00V.dat",
    "scl_0.5_vd_out_at_vg_05V.dat",
    "scl_0.5_vd_out_at_vg_10V.dat",
    "scl_0.5_vd_out_at_vg_15V.dat",
    "scl_0.5_vd_out_at_vg_20V.dat"
]

mosfet3_files = [
    "scl_0.25_vd_out_at_vg_00V.dat",
    "scl_0.25_vd_out_at_vg_05V.dat",
    "scl_0.25_vd_out_at_vg_10V.dat",
    "scl_0.25_vd_out_at_vg_15V.dat",
    "scl_0.25_vd_out_at_vg_20V.dat"
]

mosfet4_files = [
    "scl_0.125_vd_out_at_vg_00V.dat",
    "scl_0.125_vd_out_at_vg_05V.dat",
    "scl_0.125_vd_out_at_vg_10V.dat",
    "scl_0.125_vd_out_at_vg_15V.dat",
    "scl_0.125_vd_out_at_vg_20V.dat"
]

mosfet5_files = [
    "scl_0.0625_vd_out_at_vg_00V.dat",
    "scl_0.0625_vd_out_at_vg_05V.dat",
    "scl_0.0625_vd_out_at_vg_10V.dat",
    "scl_0.0625_vd_out_at_vg_15V.dat",
    "scl_0.0625_vd_out_at_vg_20V.dat"
]


# =========================================================
# GROUP EVERYTHING
# =========================================================

all_mosfets = {
    "1 um": mosfet1_files,
    "0.5 um": mosfet2_files,
    "0.25 um": mosfet3_files,
    "0.125 um": mosfet4_files,
    "0.0625 um": mosfet5_files
}


# =========================================================
# GATE VOLTAGE LABELS
# =========================================================

gate_labels = [
    "Vg = 0 V",
    "Vg = 0.5 V",
    "Vg = 1.0 V",
    "Vg = 1.5 V",
    "Vg = 2.0 V"
]


# =========================================================
# FIGURE 1 : LINEAR SCALE
# =========================================================

fig1, axes1 = plt.subplots(2, 3, figsize=(15,10))

axes1 = axes1.flatten()

for ax, (mosfet_name, file_list) in zip(axes1, all_mosfets.items()):

    for file, label in zip(file_list, gate_labels):

        vd, id_data = read_idvd(file)

        ax.plot(
            vd,
            id_data,
            marker='o',
            linewidth=2,
            markersize=4,
            label=label
        )

    ax.set_title(f"{mosfet_name} (Linear Scale)")

    ax.set_xlabel("Drain Voltage Vd (V)")
    ax.set_ylabel("Drain Current Id (A)")

    ax.grid(True)
    ax.legend()

# Remove empty subplot
fig1.delaxes(axes1[-1])


# =========================================================
# FIGURE 2 : LOG SCALE
# =========================================================

fig2, axes2 = plt.subplots(2, 3, figsize=(15,10))

axes2 = axes2.flatten()

for ax, (mosfet_name, file_list) in zip(axes2, all_mosfets.items()):

    for file, label in zip(file_list, gate_labels):

        vd, id_data = read_idvd(file)

        ax.semilogy(
            vd,
            np.abs(id_data),
            marker='o',
            linewidth=2,
            markersize=4,
            label=label
        )

    ax.set_title(f"{mosfet_name} (Log Scale)")

    ax.set_xlabel("Drain Voltage Vd (V)")
    ax.set_ylabel("Drain Current Id (A)")

    ax.grid(True)
    ax.legend()

# Remove empty subplot
fig2.delaxes(axes2[-1])


# =========================================================
# SHOW BOTH FIGURES TOGETHER
# =========================================================

plt.tight_layout()

plt.show()