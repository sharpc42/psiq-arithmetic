import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_wangrca import WangAdd
from src.qbk_ct import CTAdd
from src.qbk_ttk import TTKAdd
from src.qbk_gayathri import GayathriAdd
from psiqworkbench.qubricks.qbk_gidney_arithmetic import GidneyAdd, CuccaroAdd, NaiveAdd
from src.qbk_jhha import JHHAMultiplier
from src.qbk_ttkmult import TTKMultiplyAdd
from psiqworkbench.qubricks.qbk_gidney_arithmetic import GidneyMultiplyAdd, CuccaroMultiplyAdd, NaiveMultiplyAdd
from psiqworkbench.qubricks.qbk_gidney_arithmetic import OptimizedGidneyMultiplyAdd, OptimizedNaiveMultiplyAdd

from psiqworkbench import QPU, Qubits
from psiqworkbench.resource_estimation.qre import resource_estimator
import matplotlib.pyplot as plt
import numpy as np

def create_joint_plots_outofplace_adder(
    a=1, 
    b=1, 
    max_qubits = 100,
    plot_only = True,
) -> None:
    qubits_arr = []
    toffs_arr  = []
    t_gate_arr = []
    actvol_arr = []
    rhs_val = 1
    adders = [
        "Wang",
        "CT",
        "Gayathri",
        "Gidney",
        "Cuccaro",
        "Naive",
    ]
    adder = None
    if not plot_only:
        for adder_name in adders:
            drawn_circuit = False
            this_qubits_arr = []
            this_toffs_arr = []
            this_t_gate_arr = []
            this_actvol_arr = []
            if adder_name == "Wang":
                adder = WangAdd()
            elif adder_name == "CT":
                adder = CTAdd()
            elif adder_name == "Gayathri":
                adder = GayathriAdd()
            elif adder_name == "Gidney":
                adder = GidneyAdd()
            elif adder_name == "Cuccaro":
                adder = CuccaroAdd()
            elif adder_name == "Naive":
                adder = NaiveAdd()
            for n in range(1,max_qubits):
                lhs_val = int(2**n) - 2
                # num_qubits = max(a_val.bit_length(), b_val.bit_length(), (a_val + b_val).bit_length())
                qpu = QPU(
                    num_qubits = 4*n + 10,
                    filters=[
                        ">>buffer>>", 
                        ">>bit-sim>>", 
                        ">>toffoli-filter>>",
                    ])
                qpu.enable_qubit_allocation_debugging()
                lhs = Qubits(n, "lhs", qpu=qpu)
                rhs = Qubits(n, "rhs", qpu=qpu)
                lhs.write(lhs_val)
                rhs.write(rhs_val)
                if adder_name == "Gidney" or adder_name == "Cuccaro" or adder_name == "Naive":
                    adder.compute(lhs=lhs, rhs=rhs, alloc_result=True)
                else:
                    adder.compute(lhs=lhs, rhs=rhs, num_qubits=n)
                resources = resource_estimator(qpu).resources()
                this_qubits_arr.append(resources["qubit_highwater"])
                this_toffs_arr.append(resources["toffs"] + resources["gidney_lelbows"])
                this_t_gate_arr.append(
                    resources["t_gates"] + 4*resources["toffs"] + 4*resources["gidney_lelbows"]
                )
                this_actvol_arr.append(resources["active_volume"])
                if n == 3 and drawn_circuit == False:
                    if adder_name == "Wang" or adder_name == "CT":
                        qpu.draw(
                            filename=f"benchmarks/images/{adder_name}_adder_circuit.svg", 
                            format="svg",
                            show_qubricks=True,
                        )
                        drawn_circuit = True
                adder.uncompute()
            qubits_arr.append(this_qubits_arr)
            toffs_arr.append(this_toffs_arr)
            t_gate_arr.append(this_t_gate_arr)
            actvol_arr.append(this_actvol_arr)
        print(f"Writing arrays...")
        qubits = [n for n in range(1, max_qubits)]
        np.save("benchmarks/data/qubits_arr.npy", np.asarray(qubits_arr))
        np.save("benchmarks/data/toffs_arr.npy", np.asarray(toffs_arr))
        np.save("benchmarks/data/t_gate_arr.npy", np.asarray(t_gate_arr))
        np.save("benchmarks/data/actvol_arr.npy", np.asarray(actvol_arr))

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams["legend.frameon"] = True

    if plot_only:
        print(f"Reading arrays...")
        qubits = [n for n in range(1, max_qubits)]
        qubits_arr = np.load("benchmarks/data/qubits_arr.npy")
        toffs_arr = np.load("benchmarks/data/toffs_arr.npy")
        t_gate_arr = np.load("benchmarks/data/t_gate_arr.npy")
        actvol_arr = np.load("benchmarks/data/actvol_arr.npy")

    print(f"Printing Plots...")

    fig, ax = plt.subplots()
    for i, adder_name in enumerate(adders):
        if adder_name == "Cuccaro":
            ax.plot(
                qubits, 
                # np.asarray(qubits_arr[i])*1.09,
                qubits_arr[i], 
                label=f"{adder_name}",
                color="purple",
                linewidth=2.5,
            )   
        elif adder_name == "Wang":
            ax.plot(
                qubits, 
                np.asarray(qubits_arr[i]), 
                label=f"{adder_name}",
                color="red",
                linewidth=5,
                linestyle=":",
                alpha=0.7
            )   
        elif adder_name == "Gayathri":
            ax.plot(
                qubits, 
                np.asarray(qubits_arr[i]), 
                label=f"{adder_name}",
                color="cyan",
                linewidth=5,
                linestyle="--",
                alpha=0.5,
            )
        elif adder_name == "Naive":
            ax.plot(
                qubits, 
                np.asarray(qubits_arr[i]), 
                label=f"{adder_name}",
                color="orange",
                linewidth=5,
                linestyle="-.",
                alpha=0.5,
            )      
        elif adder_name == "Gidney":
            ax.plot(
                qubits, 
                qubits_arr[i], 
                label=f"{adder_name}",
                color="blue",
                linewidth=2.5,
            )
        elif adder_name == "CT":
            ax.plot(
                qubits, 
                np.asarray(qubits_arr[i]), 
                label=f"{adder_name}",
                linewidth=5,
                linestyle="--",
                alpha=0.5,
            )
        else:
            ax.plot(
                qubits, 
                qubits_arr[i], 
                label=f"{adder_name}"
            )
    ax.set_title("Logical Qubit Count vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Logical Qubits")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.xticks(np.arange(0, 101, 5))
    plt.savefig(f"benchmarks/images/test_joint_outofplace_qubits.png")
    plt.close()

    fig, ax = plt.subplots()
    for i, adder_name in enumerate(adders):
        if adder_name == "Wang":
            ax.plot(
                qubits, 
                # np.asarray(toffs_arr[i])*1.08, 
                toffs_arr[i],
                label=f"{adder_name}",
                color="red",
                linestyle=":",
                linewidth=5,
                alpha=0.7
            )  
        elif adder_name == "Gayathri":
            ax.plot(
                qubits, 
                # np.asarray(toffs_arr[i])*1.03, 
                toffs_arr[i],
                label=f"{adder_name}",
                color="cyan",
                linestyle="--",
                linewidth=5,
                alpha=0.5,
            )
        elif adder_name == "Gidney":
            ax.plot(
                qubits, 
                # np.asarray(toffs_arr[i])*0.97,
                toffs_arr[i], 
                label=f"{adder_name}",
                color="blue",
                linewidth=2.5,
            )
        elif adder_name == "Cuccaro":
            ax.plot(
                qubits, 
                np.asarray(toffs_arr[i]), 
                label=f"{adder_name}",
                color="purple",
            )
        else:
            ax.plot(
                qubits, 
                toffs_arr[i], 
                label=f"{adder_name}"
            )
    ax.set_title("Toffoli Count vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Toffoli Gates")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.savefig(f"benchmarks/images/test_joint_outofplace_toffs.png")
    plt.close()

    fig, ax = plt.subplots()
    for i, adder_name in enumerate(adders):
        if adder_name == "Wang":
            ax.plot(
                qubits, 
                # np.asarray(t_gate_arr[i])*1.08,
                t_gate_arr[i], 
                label=f"{adder_name}",
                color="red",
                linestyle=":",
                linewidth=5,
                alpha=0.7,
            )
        elif adder_name == "Gayathri":
            ax.plot(
                qubits, 
                # np.asarray(t_gate_arr[i])*1.03, 
                t_gate_arr[i],
                label=f"{adder_name}",
                color="cyan",
                linestyle="--",
                linewidth=5,
                alpha=0.5,
            )
        elif adder_name == "Gidney":
            ax.plot(
                qubits, 
                # np.asarray(t_gate_arr[i])*0.97, 
                t_gate_arr[i],
                label=f"{adder_name}",
                color="blue",
                linewidth=2.5,
            )
        elif adder_name == "Cuccaro":
            ax.plot(
                qubits, 
                np.asarray(t_gate_arr[i]), 
                label=f"{adder_name}",
                color="purple",
            )
        else: 
            ax.plot(
                qubits, 
                t_gate_arr[i], 
                label=f"{adder_name}"
            )
    ax.set_title("T-Gate Count vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("T-Gates")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.savefig(f"benchmarks/images/test_joint_outofplace_tgates.png")
    plt.close()

    fig, ax = plt.subplots()
    for i, adder_name in enumerate(adders):
        if adder_name == "Gayathri":
            ax.plot(
                qubits, 
                actvol_arr[i], 
                label=f"{adder_name}",
                color="cyan",
                linestyle="--",
                linewidth=5,
                alpha=0.5,
            )
        elif adder_name == "Wang":
            ax.plot(
                qubits, 
                actvol_arr[i], 
                label=f"{adder_name}",
                color="red",
                linestyle=":",
                linewidth=5,
                alpha=0.7,
            )
        elif adder_name == "Gidney":
            ax.plot(
                qubits, 
                actvol_arr[i], 
                label=f"{adder_name}",
                color="blue",
                linewidth=2.5,
            )
        elif adder_name == "Cuccaro":
            ax.plot(
                qubits, 
                actvol_arr[i], 
                label=f"{adder_name}",
                color="purple",
            )
        else:
            ax.plot(
                qubits, 
                actvol_arr[i], 
                label=f"{adder_name}"
            )
    ax.set_title("Active Volume vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Active Volume")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.savefig(f"benchmarks/images/test_joint_outofplace_actvol.png")
    plt.close()

def create_joint_plots_inplace_adder(
    a=3, 
    b=1,
    max_qubits = 100,
    plot_only = True,
) -> None:
    qubits_arr = []
    toffs_arr  = []
    t_gate_arr = []
    actvol_arr = []
    rhs_val = 1
    adders = [
        "TTK",
        "Gidney",
        "Cuccaro",
        "Naive"
    ]
    adder = None
    if not plot_only:
        for adder_name in adders:
            drawn_circuit = False
            this_qubits_arr = []
            this_toffs_arr = []
            this_t_gate_arr = []
            this_actvol_arr = []
            if adder_name == "TTK":
                adder = TTKAdd()
            elif adder_name == "Gidney":
                adder = GidneyAdd()
            elif adder_name == "Cuccaro":
                adder = CuccaroAdd()
            elif adder_name == "Naive":
                adder = NaiveAdd()
            for n in range(1,max_qubits):
                lhs_val = int(2**n) - 2
                # num_qubits = max(a_val.bit_length(), b_val.bit_length(), (a_val + b_val).bit_length())
                qpu = QPU(
                    num_qubits = 4*n + 10,
                    filters=[
                        ">>buffer>>", 
                        ">>bit-sim>>", 
                        ">>toffoli-filter>>",
                    ])
                qpu.enable_qubit_allocation_debugging()
                lhs = Qubits(n + 1, "lhs", qpu=qpu)
                rhs = Qubits(n, "rhs", qpu=qpu)
                lhs.write(lhs_val)
                rhs.write(rhs_val)
                adder.compute(lhs=lhs, rhs=rhs)
                resources = resource_estimator(qpu).resources()
                this_qubits_arr.append(resources["qubit_highwater"])
                this_toffs_arr.append(resources["toffs"] + resources["gidney_lelbows"])
                this_t_gate_arr.append(
                    resources["t_gates"] + 4*resources["toffs"] + 4*resources["gidney_lelbows"]
                )
                this_actvol_arr.append(resources["active_volume"])
                if n == 3 and drawn_circuit == False:
                    if adder_name == "TTK":
                        qpu.draw(
                            filename=f"benchmarks/images/{adder_name}_adder_circuit.svg", 
                            format="svg",
                            show_qubricks=True,
                        )
                        drawn_circuit = True
                adder.uncompute()
            qubits_arr.append(this_qubits_arr)
            toffs_arr.append(this_toffs_arr)
            t_gate_arr.append(this_t_gate_arr)
            actvol_arr.append(this_actvol_arr)
        print(f"Writing arrays...")
        qubits = [n for n in range(1, max_qubits)]
        np.save("benchmarks/data/qubits_arr.npy", np.asarray(qubits_arr))
        np.save("benchmarks/data/toffs_arr.npy", np.asarray(toffs_arr))
        np.save("benchmarks/data/t_gate_arr.npy", np.asarray(t_gate_arr))
        np.save("benchmarks/data/actvol_arr.npy", np.asarray(actvol_arr))

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams["legend.frameon"] = True

    if plot_only:
        print(f"Reading arrays...")
        qubits = [n for n in range(1, max_qubits)]
        qubits_arr = np.load("benchmarks/data/qubits_arr.npy")
        toffs_arr = np.load("benchmarks/data/toffs_arr.npy")
        t_gate_arr = np.load("benchmarks/data/t_gate_arr.npy")
        actvol_arr = np.load("benchmarks/data/actvol_arr.npy")

    print(f"Printing Plots...")

    fig, ax = plt.subplots()
    for i, adder_name in enumerate(adders):
        if adder_name == "Naive":
            ax.plot(
                qubits,
                # np.asarray(qubits_arr[i])*1.08,
                qubits_arr[i],
                label=f"{adder_name}",
                alpha=0.5,
                color="red",
                linestyle=":",
                linewidth=5,
            )
        elif adder_name == "Cuccaro":
            ax.plot(
                qubits,
                # np.asarray(qubits_arr[i])*1.04, 
                qubits_arr[i],
                label=f"{adder_name}",
                # alpha=0.5,
                linewidth=2.5,
                alpha=0.7,
            )
        elif adder_name == "TTK":
            ax.plot(
                qubits, 
                qubits_arr[i], 
                label=f"{adder_name}",
                linestyle="--",
                linewidth=5,
                # alpha=0.7,
            )
        else:
            ax.plot(
                qubits, 
                qubits_arr[i], 
                label=f"{adder_name}",
                linestyle='-',
            )
    ax.set_title("Logical Qubit Count vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Logical Qubits")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.xticks(np.arange(0, 101, 5))
    plt.savefig(f"benchmarks/images/test_joint_inplace_qubits.png")
    plt.close()

    fig, ax = plt.subplots()
    for i, adder_name in enumerate(adders):
        if adder_name == "Cuccaro":
            ax.plot(
                qubits, 
                # np.asarray(toffs_arr[i])*1.08,
                toffs_arr[i],
                label=f"{adder_name}",
                linewidth=2.5,
                alpha=0.7,
            )  
        elif adder_name == "TTK":
            ax.plot(
                qubits, 
                # np.asarray(toffs_arr[i])*1.08,
                toffs_arr[i],
                label=f"{adder_name}",
                linewidth=5,
                linestyle="--",
                # alpha=0.7,
            )   
        else:
            ax.plot(
                qubits, 
                toffs_arr[i], 
                label=f"{adder_name}"
            )
    ax.set_title("Toffoli Count vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Toffoli Gates")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.savefig(f"benchmarks/images/test_joint_inplace_toffs.png")
    plt.close()

    fig, ax = plt.subplots()
    for i, adder_name in enumerate(adders):
        if adder_name == "Cuccaro":
            ax.plot(
                qubits, 
                # np.asarray(t_gate_arr[i])*1.08,
                t_gate_arr[i], 
                label=f"{adder_name}",
                linewidth=2.5,
                alpha=0.7,
            )   
        elif adder_name == "TTK":
            ax.plot(
                qubits, 
                # np.asarray(t_gate_arr[i])*1.08,
                t_gate_arr[i], 
                label=f"{adder_name}",
                linewidth=5,
                linestyle="--",
                # alpha=0.7,
            )   
        else:
            ax.plot(
                qubits, 
                t_gate_arr[i], 
                label=f"{adder_name}"
            )
    ax.set_title("T-Gate Count vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("T-Gates")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.savefig(f"benchmarks/images/test_joint_inplace_tgates.png")
    plt.close()

    fig, ax = plt.subplots()
    for i, adder_name in enumerate(adders):
        if adder_name == "Cuccaro":
            ax.plot(
                qubits, 
                # np.asarray(actvol_arr[i])*1.08,
                actvol_arr[i], 
                label=f"{adder_name}",
                linewidth=2.5,
                alpha=0.7,
            ) 
        elif adder_name == "TTK":
            ax.plot(
                qubits, 
                # np.asarray(actvol_arr[i])*1.08,
                actvol_arr[i], 
                label=f"{adder_name}",
                linewidth=5,
                linestyle="--",
                # alpha=0.7,
            )   
        else:
            ax.plot(
                qubits, 
                actvol_arr[i], 
                label=f"{adder_name}"
            )
    ax.set_title("Active Volume vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Active Volume")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.savefig(f"benchmarks/images/test_joint_inplace_actvol.png")
    plt.close()

def create_joint_plots_multiplier(
    a=1, 
    b=1, 
    max_qubits = 100,
    plot_only = True,
) -> None:
    qubits_arr = []
    toffs_arr  = []
    t_gate_arr = []
    actvol_arr = []
    rhs_val = 1
    multipliers = [
        "TTK",
        "JHHA",
        "Cuccaro",
        "Gidney",
        "Naive",
        "OptimizedGidney",
        "OptimizedNaive",
    ]
    if not plot_only:
        for multiplier_name in multipliers:
            print(f"Multiplier: {multiplier_name}")
            drawn_circuit = False
            this_qubits_arr = []
            this_toffs_arr = []
            this_t_gate_arr = []
            this_actvol_arr = []
            if multiplier_name == "TTK":
                multiplier = TTKMultiplyAdd()
            elif multiplier_name == "JHHA":
                multiplier = JHHAMultiplier()
            elif multiplier_name == "Cuccaro":
                multiplier = CuccaroMultiplyAdd()
            elif multiplier_name == "Gidney":
                multiplier = GidneyMultiplyAdd()
            elif multiplier_name == "Naive":
                multiplier = NaiveMultiplyAdd()
            elif multiplier_name == "OptimizedGidney":
                multiplier = OptimizedGidneyMultiplyAdd()
            elif multiplier_name == "OptimizedNaive":
                multiplier = OptimizedNaiveMultiplyAdd()
            for n in range(1, max_qubits):
                lhs_val = int(2**n) - 2
                qpu = QPU(
                    num_qubits = 6*n + 10,
                    filters=[">>buffer>>", ">>bit-sim>>", ">>toffoli-filter>>"])
                qpu.enable_qubit_allocation_debugging()
                lhs = Qubits(n, "lhs", qpu=qpu)
                rhs = Qubits(n, "rhs", qpu=qpu)
                lhs.write(lhs_val)
                rhs.write(rhs_val)

                if multiplier_name == "TTK":
                    accumulator = Qubits(2 * n, "acc", qpu=qpu)
                    accumulator.write(0)
                    multiplier.compute(
                        accumulator=accumulator,
                        factor1=lhs,
                        factor2=rhs,
                    )
                elif multiplier_name == "JHHA":
                    p = Qubits(2 * n, "p", qpu=qpu)
                    z = Qubits(1, "z", qpu=qpu)
                    p.write(0)
                    z.write(0)
                    multiplier.compute(
                        a=lhs,
                        b=rhs,
                        p=p,
                        z=z,
                    )
                else:
                    multiplier.compute(dst=None, lhs=lhs, rhs=rhs)

                resources = resource_estimator(qpu).resources()
                this_qubits_arr.append(resources["qubit_highwater"])
                this_toffs_arr.append(resources["toffs"] + resources["gidney_lelbows"])
                this_t_gate_arr.append(
                    resources["t_gates"] + 4*resources["toffs"] + 4*resources["gidney_lelbows"]
                )
                this_actvol_arr.append(resources["active_volume"])
                if n == 3 and drawn_circuit == False:
                    if multiplier_name == "TTK" or multiplier_name == "JHHA":
                        qpu.draw(
                            filename=f"benchmarks/images/{multiplier_name}_multiplier_circuit.svg", 
                            format="svg",
                            show_qubricks=True,
                        )
                        drawn_circuit = True
                multiplier.uncompute()
            qubits_arr.append(this_qubits_arr)
            toffs_arr.append(this_toffs_arr)
            t_gate_arr.append(this_t_gate_arr)
            actvol_arr.append(this_actvol_arr)
        print("Writing arrays...")
        qubits = [n for n in range(1, max_qubits)]
        np.save("benchmarks/data/qubits_arr.npy", np.asarray(qubits_arr))
        np.save("benchmarks/data/toffs_arr.npy", np.asarray(toffs_arr))
        np.save("benchmarks/data/t_gate_arr.npy", np.asarray(t_gate_arr))
        np.save("benchmarks/data/actvol_arr.npy", np.asarray(actvol_arr))

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams["legend.frameon"] = True

    if plot_only:
        print(f"Reading arrays...")
        qubits = [n for n in range(1, max_qubits)]
        qubits_arr = np.load("benchmarks/data/qubits_arr.npy")
        toffs_arr = np.load("benchmarks/data/toffs_arr.npy")
        t_gate_arr = np.load("benchmarks/data/t_gate_arr.npy")
        actvol_arr = np.load("benchmarks/data/actvol_arr.npy")

    print(f"Printing Plots...")

    fig, ax = plt.subplots()
    for i, multiplier_name in enumerate(multipliers):
        print(f"***{multiplier_name} max qubits*** {max(qubits_arr[i])}")
        if multiplier_name == "Naive":
            ax.plot(
                qubits, 
                # np.asarray(qubits_arr[i])*0.96, 
                qubits_arr[i],
                label=f"{multiplier_name}",
                linestyle=":",
                linewidth=5,
                alpha=0.7
            )
        elif multiplier_name == "OptimizedNaive":
            ax.plot(
                qubits, 
                qubits_arr[i],
                label=f"{multiplier_name}",
                linestyle="--",
                linewidth=5,
                alpha=0.5,
            )
        elif multiplier_name == "Gidney":
            ax.plot(
                qubits, 
                # np.asarray(qubits_arr[i])*0.96, 
                qubits_arr[i],
                label=f"{multiplier_name}",
                linestyle=":",
                linewidth=5,
                alpha=0.7
            )
        elif multiplier_name == "OptimizedGidney":
            ax.plot(
                qubits, 
                # np.asarray(qubits_arr[i])*1.04, 
                qubits_arr[i],
                label=f"{multiplier_name}",
                linestyle="--",
                linewidth=5,
                alpha=0.5,
            )
        elif multiplier_name == "JHHA":
            ax.plot(
                qubits, 
                # np.asarray(qubits_arr[i])*1.04, 
                qubits_arr[i],
                label=f"{multiplier_name}",
                linewidth=2.5,
            )
        elif multiplier_name == "TTK":
            ax.plot(
                qubits, 
                # np.asarray(qubits_arr[i])*0.96, 
                qubits_arr[i],
                label=f"{multiplier_name}",
                linewidth=2.5,
            )
        else:
            ax.plot(
                qubits, 
                qubits_arr[i], 
                label=f"{multiplier_name}"
            )
    ax.set_title("Logical Qubit Count vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Logical Qubits")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.xticks(np.arange(0, 101, 5))
    plt.savefig(f"benchmarks/images/test_joint_multiplier_qubits.png")
    plt.close()

    fig, ax = plt.subplots()
    for i, multiplier_name in enumerate(multipliers):
        if multiplier_name == "Gidney":
            ax.plot(
                qubits, 
                np.asarray(toffs_arr[i]), 
                label=f"{multiplier_name}"
            )
        else:
            ax.plot(
                qubits, 
                toffs_arr[i], 
                label=f"{multiplier_name}"
            )
    ax.set_title("Toffoli Count vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Toffoli Gates")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.savefig(f"benchmarks/images/test_joint_multiplier_toffs.png")
    plt.close()

    fig, ax = plt.subplots()
    for i, multiplier_name in enumerate(multipliers):
        ax.plot(
            qubits, 
            t_gate_arr[i], 
            label=f"{multiplier_name}"
        )
    ax.set_title("T-Gate Count vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("T-Gates")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.savefig(f"benchmarks/images/test_joint_multiplier_tgates.png")
    plt.close()

    fig, ax = plt.subplots()
    for i, multiplier_name in enumerate(multipliers):
        ax.plot(
            qubits, 
            actvol_arr[i], 
            label=f"{multiplier_name}"
        )
    ax.set_title("Active Volume vs n")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Active Volume")
    ax.legend(
        loc="upper left", 
        facecolor="white",
        edgecolor="lightgray",
        framealpha=1.0,
        fancybox=True,
    )
    plt.yscale("log")
    plt.savefig(f"benchmarks/images/test_joint_multiplier_actvol.png")
    plt.close()

create_joint_plots_outofplace_adder()
create_joint_plots_inplace_adder()
create_joint_plots_multiplier()