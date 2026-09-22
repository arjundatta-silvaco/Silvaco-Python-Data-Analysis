import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================================================
# SETTINGS
# =========================================================

# File numbering:
#   1 -> Al composition x = 0.3
#   2 -> Al composition x = 0.4
#   3 -> Al composition x = 0.5

X_COMPOSITION = {
    1: 0.3,
    2: 0.4,
    3: 0.5,
}

# All .log files should be in the same folder as this Python file.
DATA_DIR = Path(__file__).resolve().parent


# =========================================================
# FILE NAMES
# =========================================================

IDVG_FILES = {
    1: "x_comp_idvg_1.log",
    2: "x_comp_idvg_2.log",
    3: "x_comp_idvg_3.log",
}

IDVD_FILES = {
    1: {
        1: "x_comp_1_vg1v.log",
        3: "x_comp_1_vg3v.log",
        5: "x_comp_1_vg5v.log",
    },

    2: {
        1: "x_comp_2_vg1v.log",
        3: "x_comp_2_vg3v.log",
        5: "x_comp_2_vg5v.log",
    },

    3: {
        1: "x_comp_3_vg1v.log",
        3: "x_comp_3_vg3v.log",
        5: "x_comp_3_vg5v.log",
    },
}


# =========================================================
# READ SILVACO IDVG FILE
# =========================================================

def read_idvg(filename):

    vg_list = []
    id_list = []

    filepath = DATA_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"File not found:\n{filepath}\n\n"
            "Make sure the .log files are in the same folder "
            "as this Python script."
        )

    with open(filepath, "r", errors="ignore") as f:

        for line in f:

            if line.startswith("d"):

                parts = line.split()

                try:
                    values = list(map(float, parts[1:]))
                except ValueError:
                    continue

                # Format:
                # [Vg, Vg, Ig, Vs, Vs, Is , Vd, Vd, Id,]

                if len(values) < 9:
                    continue

                vg = values[1]
                id_val = values[8]

                vg_list.append(vg)
                id_list.append(id_val)

    return np.array(vg_list), np.array(id_list)


# =========================================================
# READ SILVACO IDVD FILE
# =========================================================

def read_idvd(filename):

    vd_list = []
    id_list = []

    filepath = DATA_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"File not found:\n{filepath}\n\n"
            "Make sure the .log files are in the same folder "
            "as this Python script."
        )

    with open(filepath, "r", errors="ignore") as f:

        for line in f:

            if line.startswith("d"):

                parts = line.split()

                try:
                    values = list(map(float, parts[1:]))
                except ValueError:
                    continue

                # Format:
                # [Vg, Vg, Ig, Vs, Vs, Is , Vd, Vd, Id,]

                if len(values) < 9:
                    continue

                vd = values[6]
                id_val = values[8]

                vd_list.append(vd)
                id_list.append(id_val)

    return np.array(vd_list), np.array(id_list)


# =========================================================
# READ SILVACO GATE CURRENT
# =========================================================

def read_gate_current(filename):

    vg_list = []
    ig_list = []

    filepath = DATA_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(f"File not found:\n{filepath}")

    with open(filepath, "r", errors="ignore") as f:

        for line in f:

            if line.startswith("d"):

                parts = line.split()

                try:
                    values = list(map(float, parts[1:]))
                except ValueError:
                    continue

                if len(values) < 9:
                    continue

                # [Vg, Vg, Ig, Vs, Vs, Is , Vd, Vd, Id,]

                vg = values[1]
                ig = values[2]

                vg_list.append(vg)
                ig_list.append(ig)

    return np.array(vg_list), np.array(ig_list)


# =========================================================
# THRESHOLD VOLTAGE EXTRACTION
# Constant Current Method
# =========================================================

def extract_vth(vg, id_data):

    Ith = 1e-2  # A

    vg = np.array(vg)
    id_abs = np.abs(id_data)

    if len(vg) == 0:
        return None

    if np.max(id_abs) < Ith:
        return None

    # Sort in case data isn't ordered
    idx = np.argsort(vg)

    vg = vg[idx]
    id_abs = id_abs[idx]

    # Find first crossing of Ith
    for i in range(1, len(vg)):

        if id_abs[i - 1] < Ith and id_abs[i] >= Ith:

            x1 = vg[i - 1]
            x2 = vg[i]

            y1 = id_abs[i - 1]
            y2 = id_abs[i]

            if y2 == y1:
                return x1

            # Linear interpolation
            vth = x1 + (Ith - y1) * (x2 - x1) / (y2 - y1)

            return vth

    return None

# =========================================================
# =========================================================
# PLOTTING HELPERS
# =========================================================

def add_grid(ax):

    ax.grid(
        True,
        which="major",
        alpha=0.3
    )

    ax.grid(
        True,
        which="minor",
        alpha=0.15
    )

    ax.minorticks_on()


def clear_tab(tab):

    for widget in tab.winfo_children():
        widget.destroy()


def make_canvas(parent, figure):

    canvas = FigureCanvasTkAgg(
        figure,
        master=parent
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill=tk.BOTH,
        expand=True
    )

    return canvas


# =========================================================
# TAB 1
# ID-VG COMPARISON
# =========================================================

def plot_idvg(tab):

    clear_tab(tab)

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    for number in sorted(IDVG_FILES):

        filename = IDVG_FILES[number]
        xcomp = X_COMPOSITION[number]

        try:

            vg, idrain = read_idvg(filename)

            ax.plot(
                vg,
                idrain,
                linewidth=2,
                label=f"Al composition x = {xcomp:.1f}"
            )

            # Extract Vth
            vth = extract_vth(
                vg,
                idrain
            )

            if vth is not None:

                print(
                    f"x = {xcomp:.1f}: "
                    f"Vth = {vth:.4f} V"
                )

        except Exception as e:

            messagebox.showerror(
                "ID-VG Error",
                str(e)
            )

            plt.close(fig)
            return

    ax.set_title(
        "ID-VG Comparison for Different AlGaN Compositions"
    )

    ax.set_xlabel(
        "Gate Voltage, $V_G$ (V)"
    )

    ax.set_ylabel(
        "Drain Current, $I_D$ (A)"
    )

    ax.legend()

    add_grid(ax)

    fig.tight_layout()

    make_canvas(
        tab,
        fig
    )


# =========================================================
# TAB 2
# ID-VD FOR EACH ALGAN COMPOSITION
# =========================================================

def plot_all_idvd(tab):

    clear_tab(tab)

    # One graph for each Al composition.
    # Each graph contains VG = 1, 3 and 5 V.
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(15, 5),
        sharey=False
    )

    gate_voltages = [1, 3, 5]

    for col, number in enumerate(sorted(IDVD_FILES)):

        ax = axes[col]
        xcomp = X_COMPOSITION[number]

        for vg in gate_voltages:

            filename = IDVD_FILES[number][vg]

            try:

                vd, idrain = read_idvd(
                    filename
                )

                ax.plot(
                    vd,
                    idrain,
                    linewidth=2,
                    label=f"$V_G$ = {vg} V"
                )

            except Exception as e:

                ax.text(
                    0.5,
                    0.5,
                    f"ERROR\\n{filename}",
                    ha="center",
                    va="center",
                    transform=ax.transAxes
                )

                continue

        ax.set_title(
            f"AlGaN $x$ = {xcomp:.1f}"
        )

        ax.set_xlabel(
            "$V_D$ (V)"
        )

        ax.set_ylabel(
            "$I_D$ (A)"
        )

        ax.legend()

        add_grid(ax)

    fig.suptitle(
        "ID-VD Characteristics for Each AlGaN Composition",
        fontsize=15
    )

    fig.tight_layout(
        rect=[0, 0, 1, 0.94]
    )

    make_canvas(
        tab,
        fig
    )


# =========================================================
# TAB 3
# ID-VD COMPARISON BETWEEN COMPOSITIONS
# =========================================================

def plot_idvd_comparisons(tab):

    clear_tab(tab)

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(15, 5)
    )

    gate_voltages = [1, 3, 5]

    for col, vg in enumerate(
        gate_voltages
    ):

        ax = axes[col]

        for number in sorted(IDVD_FILES):

            xcomp = X_COMPOSITION[number]

            filename = IDVD_FILES[number][vg]

            try:

                vd, idrain = read_idvd(
                    filename
                )

                ax.plot(
                    vd,
                    idrain,
                    linewidth=2,
                    label=f"x = {xcomp:.1f}"
                )

            except Exception as e:

                ax.text(
                    0.5,
                    0.5,
                    f"ERROR\n{filename}",
                    ha="center",
                    va="center",
                    transform=ax.transAxes
                )

                continue

        ax.set_title(
            f"$V_G$ = {vg} V"
        )

        ax.set_xlabel(
            "$V_D$ (V)"
        )

        ax.set_ylabel(
            "$I_D$ (A)"
        )

        ax.legend()

        add_grid(ax)

    fig.suptitle(
        "ID-VD Comparison Between AlGaN Compositions",
        fontsize=15
    )

    fig.tight_layout(
        rect=[0, 0, 1, 0.94]
    )

    make_canvas(
        tab,
        fig
    )

# =========================================================
# TAB 4
# GATE CURRENT
# =========================================================

def plot_gate_current(tab):

    clear_tab(tab)

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    for number in sorted(IDVG_FILES):

        filename = IDVG_FILES[number]
        xcomp = X_COMPOSITION[number]

        try:

            vg, ig = read_gate_current(
                filename
            )

            ax.plot(
                vg,
                ig,
                linewidth=2,
                label=f"Al composition x = {xcomp:.1f}"
            )

        except Exception as e:

            messagebox.showerror(
                "Gate Current Error",
                str(e)
            )

            plt.close(fig)
            return

    ax.set_title(
        "Gate Current vs Gate Voltage"
    )

    ax.set_xlabel(
        "Gate Voltage, $V_G$ (V)"
    )

    ax.set_ylabel(
        "Gate Current, $I_G$ (A)"
    )

    ax.legend()

    add_grid(ax)

    fig.tight_layout()

    make_canvas(
        tab,
        fig
    )


# =========================================================
# MAIN GUI
# =========================================================

def main():

    root = tk.Tk()

    root.title(
        "AlGaN/GaN HEMT TCAD Plotter"
    )

    root.geometry(
        "1400x900"
    )

    notebook = ttk.Notebook(
        root
    )

    notebook.pack(
        fill=tk.BOTH,
        expand=True
    )

    # -----------------------------------------------------
    # TAB 1: ID-VG
    # -----------------------------------------------------

    tab_idvg = ttk.Frame(
        notebook
    )

    notebook.add(
        tab_idvg,
        text="ID-VG Comparison"
    )

    # -----------------------------------------------------
    # TAB 2: ALL ID-VD
    # -----------------------------------------------------

    tab_all_idvd = ttk.Frame(
        notebook
    )

    notebook.add(
        tab_all_idvd,
        text="All ID-VD Curves"
    )

    # -----------------------------------------------------
    # TAB 3: ID-VD COMPARISON
    # -----------------------------------------------------

    tab_compare_idvd = ttk.Frame(
        notebook
    )

    notebook.add(
        tab_compare_idvd,
        text="ID-VD Composition Comparison"
    )

    # -----------------------------------------------------
    # TAB 4: GATE CURRENT
    # -----------------------------------------------------

    tab_gate_current = ttk.Frame(
        notebook
    )

    notebook.add(
        tab_gate_current,
        text="Gate Current"
    )

    # -----------------------------------------------------
    # CREATE PLOTS
    # -----------------------------------------------------

    plot_idvg(
        tab_idvg
    )

    plot_all_idvd(
        tab_all_idvd
    )

    plot_idvd_comparisons(
        tab_compare_idvd
    )

    plot_gate_current(
        tab_gate_current
    )

    root.mainloop()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()