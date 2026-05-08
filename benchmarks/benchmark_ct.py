"""Resource estimation benchmark for the CT quantum adder.

Plots logical qubit count, active volume (runtime proxy), and Toffoli count
versus register width n, each with an ideal line.

Ideal values from the CT circuit structure (forward + copy + reverse):
  - Logical qubits : 4n + 1
  - Toffoli count  : 4n   (2n CCnot forward + 2n CCnot reverse)
  - Active volume  : 208n (4n * 47 AV/CCnot + 5n * 4 AV/CNOT)

Run from the repo root:
    python benchmarks/benchmark_ct.py
"""

import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from psiqworkbench import QPU, QUInt
from psiqworkbench.filter_presets import NO_SIM_DEFAULT
from src.qbk_ct import CTAdd


def _run_one(ct, n):
    qpu = QPU(num_qubits=4 * n + 2, filters=NO_SIM_DEFAULT)
    a = QUInt(n, "a", qpu=qpu)
    b = QUInt(n, "b", qpu=qpu)
    c = QUInt(n, "c", qpu=qpu)
    ct.compute(A=a, B=b, C=c)

    w = qpu.witness
    m = w.get_all_metrics()
    return {
        "qubit_highwater": w.qubit_highwater,
        "active_volume":   m["active_volume"],
        "toffs":           int(m["toffs"]),
    }


def run_benchmark(n_values):
    ct = CTAdd()
    return {n: _run_one(ct, n) for n in n_values}


def _make_plot(ax, n_arr, measured, ideal, title, ylabel, ideal_label):
    ax.plot(n_arr, measured, "o-", color="steelblue", linewidth=2.5,
            markersize=7, label="CT (measured)")
    ax.plot(n_arr, ideal,    "--", color="darkorange", linewidth=2.5,
            label=f"Ideal: {ideal_label}")
    ax.set_title(title, fontsize=20)
    ax.set_xlabel("n (register width in bits)", fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.legend(fontsize=14)
    ax.tick_params(axis="both", labelsize=14)
    ax.grid(True, alpha=0.3)


def plot_benchmarks(n_values, results, save_dir=None):
    if save_dir is None:
        save_dir = os.path.dirname(os.path.abspath(__file__))

    n_arr = np.array(n_values)

    measured_qubits = np.array([results[n]["qubit_highwater"] for n in n_values])
    measured_av     = np.array([results[n]["active_volume"]   for n in n_values])
    measured_toffs  = np.array([results[n]["toffs"]           for n in n_values])

    ideal_qubits = 4 * n_arr + 1
    ideal_toffs  = 4 * n_arr
    ideal_av     = 208 * n_arr  # 4n * 47 (Toffoli AV) + 5n * 4 (CNOT AV)

    specs = [
        ("ct_qubit",  measured_qubits, ideal_qubits,
         "Logical Qubit Count vs n",           "Logical Qubits", "4n + 1"),
        ("ct_av",     measured_av,     ideal_av,
         "Active Volume (Runtime Proxy) vs n", "Active Volume",  "208n"),
        ("ct_toffs",  measured_toffs,  ideal_toffs,
         "Toffoli Count vs n",                 "Toffoli Gates",  "4n"),
    ]

    for fname, measured, ideal, title, ylabel, ideal_label in specs:
        fig, ax = plt.subplots(figsize=(6, 6))
        _make_plot(ax, n_arr, measured, ideal, title, ylabel, ideal_label)
        plt.tight_layout()
        out = os.path.join(save_dir, f"{fname}.png")
        plt.savefig(out, dpi=600, bbox_inches="tight")
        plt.close(fig)
        print(f"  saved  {out}")


if __name__ == "__main__":
    n_values = list(range(2, 51))
    print(f"Running CT benchmark for n = {n_values[0]} ... {n_values[-1]}")
    results = run_benchmark(n_values)
    print("Plotting ...")
    plot_benchmarks(n_values, results)
    print("Done.")
