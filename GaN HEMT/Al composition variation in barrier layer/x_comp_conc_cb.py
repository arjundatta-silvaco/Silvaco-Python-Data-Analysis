import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================================================
# SETTINGS
# =========================================================

# Composition numbering (same as the I-V / breakdown script):
#   1 -> Al composition x = 0.3
#   2 -> Al composition x = 0.45
#   3 -> Al composition x = 0.6

X_COMPOSITION = {
    1: 0.3,
    2: 0.45,
    3: 0.6,
}

# All .dat files should be in the same folder as this Python file.
DATA_DIR = Path(__file__).resolve().parent


# =========================================================
# FILE NAMES
# =========================================================

# Conduction band file columns:
#   x coordinate | Electron QFL | Conduction Band Energy
#
# Electron concentration file columns:
#   x coordinate | Electron Conc

CONDUCTION_BAND_FILES = {
    1: "x_comp_1_cb1.dat",
    2: "x_comp_2_cb1.dat",
    3: "x_comp_3_cb1.dat",
}

ELECTRON_CONC_FILES = {
    1: "x_comp_1_e_conc1.dat",
    2: "x_comp_2_e_conc1.dat",
    3: "x_comp_3_e_conc1.dat",
}


# =========================================================
# PROFILE SETTINGS
# =========================================================

# Silvaco exports 0 for every quantity in regions where it is
# undefined (the dielectric above the semiconductor). If True,
# those leading all-zero rows are removed so they don't appear
# as flat fake lines on the graphs.
TRIM_LEADING_ZEROS = False

# If True, the x axis is drawn as depth from the semiconductor
# surface (first point that has real data). This puts the band
# and concentration files on the same axis even when their
# coordinate origins differ, and lines up different compositions.
# If False, the raw Silvaco x coordinate is used.
ALIGN_TO_SURFACE = False

# Lower limit of the log-scale electron concentration plot
# (cm^-3). Set to None to autoscale to the full data range.
CONC_LOG_YMIN = 1e10


# =========================================================
# READ SILVACO CROSS-SECTION (.dat) FILE
# =========================================================

def read_cutline(filename):

    filepath = DATA_DIR / filename

    if not filepath.exists():
        raise FileNotFoundError(
            f"File not found:\n{filepath}\n\n"
            "Make sure the .dat files are in the same folder "
            "as this Python script."
        )

    with open(filepath, "r", errors="ignore") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Header format:
    #   line 0 : title (EXPORTED CROSS SECTION DATA)
    #   line 1 : <n_points> <n_columns> <n_columns>
    #   next n_columns lines : column names
    try:
        n_cols = int(lines[1].split()[1])
        names = lines[2:2 + n_cols]
    except (IndexError, ValueError):
        raise ValueError(
            f"{filename}: unexpected header, "
            "could not read the column names."
        )

    rows = []

    for line in lines[2 + n_cols:]:

        try:
            values = list(map(float, line.split()))
        except ValueError:
            continue

        if len(values) < n_cols:
            continue

        rows.append(values[:n_cols])

    if not rows:
        raise ValueError(f"{filename}: no numeric data found.")

    data = np.array(rows)

    return {
        name: data[:, i]
        for i, name in enumerate(names)
    }


def find_column(columns, keyword):

    keyword = keyword.lower()

    for name, values in columns.items():

        if keyword in name.lower():
            return values

    raise KeyError(
        f"No column containing '{keyword}'. "
        f"Columns found: {list(columns)}"
    )


def load_profile(filename):

    columns = read_cutline(filename)

    x_name = next(
        name for name in columns
        if "coordinate" in name.lower()
    )

    x = columns[x_name]

    quantities = {
        name: values
        for name, values in columns.items()
        if name != x_name
    }

    # First row where at least one quantity is not exactly 0.
    stacked = np.column_stack(list(quantities.values()))
    has_data = np.any(stacked != 0.0, axis=1)

    first = int(np.argmax(has_data)) if has_data.any() else 0
    x_surface = x[first]

    if TRIM_LEADING_ZEROS:
        x = x[first:]
        quantities = {
            name: values[first:]
            for name, values in quantities.items()
        }

    if ALIGN_TO_SURFACE:
        x = x - x_surface

    return x, quantities


def x_axis_label():

    if ALIGN_TO_SURFACE:
        return "Depth from Semiconductor Surface ($\\mu$m)"

    return "Position, x ($\\mu$m)"


# =========================================================
# ANALYSIS HELPERS
# =========================================================

def sheet_density(x_um, n_cm3):

    # n_s = integral of n dx  (trapezoid rule)
    # x in um, n in cm^-3  ->  1 um = 1e-4 cm  ->  cm^-2

    x_um = np.asarray(x_um, dtype=float)
    n_cm3 = np.asarray(n_cm3, dtype=float)

    if len(x_um) < 2:
        return None

    area = np.sum(
        0.5 * (n_cm3[1:] + n_cm3[:-1]) * np.diff(x_um)
    )

    return area * 1e-4


def sci_latex(value):

    mantissa, exponent = f"{value:.2e}".split("e")

    return f"{mantissa}\\times10^{{{int(exponent)}}}"


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
# CONDUCTION BAND COMPARISON
# =========================================================

def plot_conduction_band(tab):

    clear_tab(tab)

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    files_found = False
    qfl_drawn = False

    for number in sorted(CONDUCTION_BAND_FILES):

        filename = CONDUCTION_BAND_FILES[number]
        xcomp = X_COMPOSITION[number]
        filepath = DATA_DIR / filename

        if not filepath.exists():
            print(f"x = {xcomp:g}: {filename} not found, skipped.")
            continue

        files_found = True

        try:

            depth, columns = load_profile(filename)

            ec = find_column(columns, "conduction")

            line, = ax.plot(
                depth,
                ec,
                linewidth=2,
                marker="o",
                markersize=3,
                label=f"Al composition x = {xcomp:g}"
            )

            # Electron quasi-Fermi level, same colour, dashed.
            try:
                qfl = find_column(columns, "qfl")
            except KeyError:
                qfl = None

            if qfl is not None:

                ax.plot(
                    depth,
                    qfl,
                    linestyle="--",
                    linewidth=1.2,
                    color=line.get_color(),
                    alpha=0.7
                )

                qfl_drawn = True

            i_min = int(np.argmin(ec))

            print(
                f"Conduction band: x = {xcomp:g} | "
                f"Ec(surface) = {ec[0]:.4f} eV | "
                f"min Ec = {ec[i_min]:.4f} eV "
                f"at {depth[i_min]:.4f} um"
            )

        except Exception as e:

            messagebox.showerror(
                "Conduction Band Error",
                f"{filename}\n\n{e}"
            )

            plt.close(fig)
            return

    if not files_found:

        ax.text(
            0.5,
            0.5,
            "No conduction band files found",
            ha="center",
            va="center",
            transform=ax.transAxes
        )

    if qfl_drawn:

        # One legend entry explaining the dashed lines.
        ax.plot(
            [],
            [],
            linestyle="--",
            linewidth=1.2,
            color="black",
            label="Electron QFL"
        )

    ax.set_title(
        "Conduction Band Energy Profile"
    )

    ax.set_xlabel(
        x_axis_label()
    )

    ax.set_ylabel(
        "Energy (eV)"
    )

    if files_found:
        ax.legend()

    add_grid(ax)

    fig.tight_layout()

    make_canvas(
        tab,
        fig
    )


# =========================================================
# TAB 2
# ELECTRON CONCENTRATION COMPARISON (LOG SCALE)
# =========================================================

def plot_electron_concentration(tab):

    clear_tab(tab)

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    files_found = False

    for number in sorted(ELECTRON_CONC_FILES):

        filename = ELECTRON_CONC_FILES[number]
        xcomp = X_COMPOSITION[number]
        filepath = DATA_DIR / filename

        if not filepath.exists():
            print(f"x = {xcomp:g}: {filename} not found, skipped.")
            continue

        files_found = True

        try:

            depth, columns = load_profile(filename)

            conc = find_column(columns, "conc")

            ns = sheet_density(depth, conc)

            label = f"Al composition x = {xcomp:g}"

            if ns is not None:
                label += (
                    f", $n_s$ = ${sci_latex(ns)}$ cm$^{{-2}}$"
                )

            # A log axis cannot show zero or negative values.
            positive = conc > 0

            ax.plot(
                depth[positive],
                conc[positive],
                linewidth=2,
                marker="o",
                markersize=3,
                label=label
            )

            i_peak = int(np.argmax(conc))

            print(
                f"Electron conc: x = {xcomp:g} | "
                f"peak = {conc[i_peak]:.4e} cm^-3 "
                f"at {depth[i_peak]:.4f} um | "
                f"n_s = {ns:.4e} cm^-2"
            )

        except Exception as e:

            messagebox.showerror(
                "Electron Concentration Error",
                f"{filename}\n\n{e}"
            )

            plt.close(fig)
            return

    if not files_found:

        ax.text(
            0.5,
            0.5,
            "No electron concentration files found",
            ha="center",
            va="center",
            transform=ax.transAxes
        )

    ax.set_yscale("log")

    if files_found and CONC_LOG_YMIN is not None:
        ax.set_ylim(bottom=CONC_LOG_YMIN)

    ax.set_title(
        "Electron Concentration Profile"
    )

    ax.set_xlabel(
        x_axis_label()
    )

    ax.set_ylabel(
        "Electron Concentration (cm$^{-3}$)"
    )

    if files_found:
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
        "AlGaN/GaN HEMT Band / Carrier Profile Plotter"
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
    # TAB 1: CONDUCTION BAND
    # -----------------------------------------------------

    tab_band = ttk.Frame(
        notebook
    )

    notebook.add(
        tab_band,
        text="Conduction Band Comparison"
    )

    # -----------------------------------------------------
    # TAB 2: ELECTRON CONCENTRATION
    # -----------------------------------------------------

    tab_conc = ttk.Frame(
        notebook
    )

    notebook.add(
        tab_conc,
        text="Electron Concentration Comparison"
    )

    # -----------------------------------------------------
    # CREATE PLOTS
    # -----------------------------------------------------

    plot_conduction_band(
        tab_band
    )

    plot_electron_concentration(
        tab_conc
    )

    root.mainloop()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()