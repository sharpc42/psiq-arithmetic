from psiqworkbench import QPU, Qubits
from psiqworkbench.filter_presets import BIT_DEFAULT
from psiqworkbench.resource_estimation.qre import resource_estimator
import matplotlib.pyplot as plt

class BenchmarkResults:
    adder = None
    adder_name = ""
    def create_benchmark_plots(self):
        qubits_arr    = []
        toffs_arr     = []
        qubits_theory = []
        toffs_theory  = []
        b_val = 1
        max_qubits = 50
        for n in range(1,max_qubits):
            a_val = int(2**n) - 2
            # num_qubits = max(a_val.bit_length(), b_val.bit_length(), (a_val + b_val).bit_length())
            qpu = QPU(num_qubits=3*n+1, filters=BIT_DEFAULT)
            qpu.enable_qubit_allocation_debugging()
            a = Qubits(n, "a", qpu=qpu)
            b = Qubits(n, "b", qpu=qpu)
            a.write(a_val)
            b.write(b_val)
            self.adder.compute(lhs=a, rhs=b, num_qubits=n)
            resources = resource_estimator(qpu).resources()
            qubits_arr.append(resources["qubit_highwater"])
            toffs_arr.append(resources["toffs"])
            qubits_theory.append(3*n + 1)
            toffs_theory.append(n)
        qubits = [n for n in range(1, max_qubits)]
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams["legend.frameon"] = True

        print(f"Printing Plots...")

        fig, ax = plt.subplots()
        ax.scatter(
            qubits, 
            qubits_arr, 
            label=f"{self.adder_name.capitalize()} (measured)"
        )
        ax.plot(qubits, qubits_theory, ls="-", color="orange", label="Ideal: 3n + 1")
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
        plt.savefig(f"{self.adder_name}_qubit.png")
        plt.close()

        fig, ax = plt.subplots()
        ax.scatter(qubits, toffs_arr, label=f"{self.adder_name} (measured)")
        ax.plot(qubits, toffs_theory, ls="-", color="orange", label="Ideal: n")
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
        plt.savefig(f"{self.adder_name}_toffs.png")
        plt.close()