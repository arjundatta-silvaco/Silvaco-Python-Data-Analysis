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
#   2 -> Al composition x = 0.45
#   3 -> Al composition x = 0.6

X_COMPOSITION = {
    1: 0.3,
    2: 0.45,
    3: 0.6,
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
# BREAKDOWN FILES AND FIT SETTINGS
# =========================================================

BREAKDOWN_FILES = {
    1: "x_comp_breakdown_1.log",
    2: "x_comp_breakdown_2.log",
    3: "x_comp_breakdown_3.log",
}

# Fit settings, one entry per breakdown curve (same keys as
# BREAKDOWN_FILES). Each curve has its own steep region, so tune
# them independently.
#
#   "low", "high" : the steep region is the part of the curve where
#                   |I_D| lies between these fractions of that
#                   curve's maximum |I_D|.
#   "vd_min",     : optional. Also restrict the fit to this drain
#   "vd_max"        voltage window (V). Use None for no limit.
#                   Handy if the pre-breakdown leakage or the
#                   compliance plateau sneaks into the fit.

BREAKDOWN_FIT_SETTINGS = {
    1: {"low": 0.20, "high": 0.60, "vd_min": None, "vd_max": None},  # x = 0.3
    2: {"low": 0.15, "high": 0.20, "vd_min": None, "vd_max": None},  # x = 0.45
    3: {"low": 0.20, "high": 0.50, "vd_min": None, "vd_max": None},  # x = 0.6
}

# Used for any curve that has no entry in BREAKDOWN_FIT_SETTINGS.
DEFAULT_BREAKDOWN_FIT = {
    "low": 0.20,
    "high": 0.60,
    "vd_min": None,
    "vd_max": None,
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
# READ SILVACO BREAKDOWN FILE
# =========================================================

def read_breakdown(filename):

    vd_list = []
    id_list = []

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

                # Breakdown log format:
                # [Vg, Vg, Ig, Vs, Vs, Is, Vd, Vd, Id, ...]

                if len(values) < 9:
                    continue

                vd = values[6]
                id_val = values[8]

                vd_list.append(vd)
                id_list.append(id_val)

    return np.array(vd_list), np.array(id_list)


# =========================================================
# THRESHOLD VOLTAGE EXTRACTION
# Constant Current Method
# =========================================================

def extract_vth(vg, id_data):

    Ith = 5e-3  # A

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

    # Side-by-side comparison:
    #   left  = normal linear scale
    #   right = logarithmic |Ig| scale

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(15, 6)
    )

    for number in sorted(IDVG_FILES):

        filename = IDVG_FILES[number]
        xcomp = X_COMPOSITION[number]

        try:

            vg, ig = read_gate_current(
                filename
            )

            label = f"Al composition x = {xcomp:g}"

            axes[0].plot(
                vg,
                ig,
                linewidth=2,
                label=label
            )

            # Absolute value is used because log(Ig) is undefined
            # when Ig is zero or negative.
            axes[1].semilogy(
                vg,
                np.maximum(np.abs(ig), 1e-30),
                linewidth=2,
                label=label
            )

        except Exception as e:

            messagebox.showerror(
                "Gate Current Error",
                str(e)
            )

            plt.close(fig)
            return

    axes[0].set_title(
        "Gate Current vs Gate Voltage"
    )

    axes[0].set_xlabel(
        "Gate Voltage, $V_G$ (V)"
    )

    axes[0].set_ylabel(
        "Gate Current, $I_G$ (A)"
    )

    axes[0].legend()
    add_grid(axes[0])

    axes[1].set_title(
        "Gate Current vs Gate Voltage (Log Scale)"
    )

    axes[1].set_xlabel(
        "Gate Voltage, $V_G$ (V)"
    )

    axes[1].set_ylabel(
        "$|I_G|$ (A)"
    )

    axes[1].legend()
    add_grid(axes[1])

    fig.suptitle(
        "Gate Current Comparison",
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
# TAB 5
# BREAKDOWN CHARACTERISTICS
# =========================================================

def extract_breakdown_voltage(
    vd,
    id_data,
    low=0.20,
    high=0.60,
    vd_min=None,
    vd_max=None
):

    vd = np.asarray(vd, dtype=float)
    current = np.abs(np.asarray(id_data, dtype=float))

    if len(vd) < 5:
        return None

    # Sort by drain voltage.
    idx = np.argsort(vd)
    vd = vd[idx]
    current = current[idx]

    max_current = np.max(current)

    if max_current <= 0:
        return None

    # Select the steep increasing region for this curve.
    low_current = low * max_current
    high_current = high * max_current

    mask = (
        (current >= low_current) &
        (current <= high_current)
    )

    # Optional drain-voltage window.
    if vd_min is not None:
        mask &= (vd >= vd_min)

    if vd_max is not None:
        mask &= (vd <= vd_max)

    fit_vd = vd[mask]
    fit_current = current[mask]

    if len(fit_vd) < 3:
        return None

    # Fit:
    #
    # I_D = m V_D + b
    #
    # x-intercept:
    #
    # V_BR = -b/m

    m, b = np.polyfit(
        fit_vd,
        fit_current,
        1
    )

    if m <= 0:
        return None

    vbr = -b / m

    predicted = m * fit_vd + b

    ss_res = np.sum(
        (fit_current - predicted) ** 2
    )

    ss_tot = np.sum(
        (fit_current - np.mean(fit_current)) ** 2
    )

    r_squared = (
        1 - ss_res / ss_tot
        if ss_tot > 0
        else 0.0
    )

    return {
        "vbr": vbr,
        "slope": m,
        "intercept": b,
        "r_squared": r_squared,
        "fit_vd": fit_vd,
        "fit_current": fit_current,
    }


def plot_breakdown(tab):

    clear_tab(tab)

    fig, ax = plt.subplots(
        figsize=(11, 7)
    )

    files_found = False

    for number in sorted(BREAKDOWN_FILES):

        filename = BREAKDOWN_FILES[number]
        xcomp = X_COMPOSITION[number]
        filepath = DATA_DIR / filename

        if not filepath.exists():
            continue

        files_found = True

        try:

            vd, idrain = read_breakdown(
                filename
            )

            if len(vd) < 5:
                continue

            idx = np.argsort(vd)
            vd = vd[idx]
            idrain = idrain[idx]

            label = f"Al composition x = {xcomp:g}"

            # Original simulated breakdown curve.
            ax.plot(
                vd,
                idrain,
                linewidth=2,
                label=label
            )

            # Fit settings specific to this curve.
            fit_cfg = BREAKDOWN_FIT_SETTINGS.get(
                number,
                DEFAULT_BREAKDOWN_FIT
            )

            result = extract_breakdown_voltage(
                vd,
                idrain,
                low=fit_cfg["low"],
                high=fit_cfg["high"],
                vd_min=fit_cfg.get("vd_min"),
                vd_max=fit_cfg.get("vd_max")
            )

            if result is None:
                print(
                    f"x = {xcomp:g}: "
                    "breakdown fit could not be extracted "
                    f"with settings {fit_cfg}. "
                    "Adjust BREAKDOWN_FIT_SETTINGS for this curve."
                )
                continue

            vbr = result["vbr"]
            slope = result["slope"]
            intercept = result["intercept"]
            fit_vd = result["fit_vd"]
            r_squared = result["r_squared"]

            # Draw the fitted steep-region line and extend it
            # leftward until it reaches the x-axis.
            line_start = min(
                vbr,
                np.min(fit_vd)
            )

            line_end = np.max(fit_vd)

            line_vd = np.linspace(
                line_start,
                line_end,
                100
            )

            line_id = (
                slope * line_vd
                + intercept
            )

            ax.plot(
                line_vd,
                line_id,
                linestyle="--",
                linewidth=1.8,
                label=(
                    f"Fit x = {xcomp:g}, "
                    f"$V_{{BR}}$ = {vbr:.2f} V"
                )
            )

            # Mark the extrapolated x-intercept.
            ax.plot(
                vbr,
                0,
                marker="o",
                markersize=7
            )

            print(
                f"Breakdown: x = {xcomp:g} | "
                f"V_BR = {vbr:.4f} V | "
                f"slope = {slope:.6e} A/V | "
                f"R^2 = {r_squared:.5f} | "
                f"fit window = {fit_cfg['low']:g}-"
                f"{fit_cfg['high']:g} of Imax | "
                f"fit range = "
                f"{np.min(fit_vd):.4f} to "
                f"{np.max(fit_vd):.4f} V"
            )

        except Exception as e:

            messagebox.showerror(
                "Breakdown Error",
                f"{filename}\n\n{e}"
            )

            plt.close(fig)
            return

    if not files_found:

        ax.text(
            0.5,
            0.5,
            "No breakdown log files found",
            ha="center",
            va="center",
            transform=ax.transAxes
        )

    ax.axhline(
        0,
        linewidth=1
    )

    ax.set_title(
        "HEMT Breakdown Characteristics"
    )

    ax.set_xlabel(
        "Drain Voltage, $V_D$ (V)"
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
    # TAB 5: BREAKDOWN
    # -----------------------------------------------------

    tab_breakdown = ttk.Frame(
        notebook
    )

    notebook.add(
        tab_breakdown,
        text="Breakdown"
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

    plot_breakdown(
        tab_breakdown
    )

    root.mainloop()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()