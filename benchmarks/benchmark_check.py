from psiqworkbench import QPU, Qubits
from psiqworkbench.filter_presets import BIT_DEFAULT
from psiqworkbench.resource_estimation.qre import resource_estimator
import matplotlib.pyplot as plt

class BenchmarkResults:
    adder = None
    adder_name = ""
    def create_individual_plots(
        self, 
        a=None, 
        b=None, 
        c=None, 
        d=None, 
        in_place=False,
        max_qubits = 50,
    ) -> None:
        qubits_arr    = []
        toffs_arr     = []
        qubits_theory = []
        toffs_theory  = []
        rhs_val = 1
        for n in range(1,max_qubits):
            lhs_val = int(2**n) - 2
            # num_qubits = max(a_val.bit_length(), b_val.bit_length(), (a_val + b_val).bit_length())
            if a is not None and b is not None:
                qpu = QPU(num_qubits = a*n + b, filters=BIT_DEFAULT)
            else:
                qpu = QPU(
                    num_qubits = max(
                        lhs_val.bit_length(),
                        (a + b).bit_length(),
                        2*lhs_val.bit_length() + 1,
                        2,
                    ), 
                    filters=BIT_DEFAULT)
            qpu.enable_qubit_allocation_debugging()
            if not in_place:
                lhs = Qubits(n, "lhs", qpu=qpu)
            else:
                lhs = Qubits(n + 1, "lhs", qpu=qpu)
            rhs = Qubits(n, "rhs", qpu=qpu)
            lhs.write(lhs_val)
            rhs.write(rhs_val)
            self.adder.compute(lhs=lhs, rhs=rhs, num_qubits=n)
            resources = resource_estimator(qpu).resources()
            qubits_arr.append(resources["qubit_highwater"])
            toffs_arr.append(resources["toffs"])
            if a is not None or b is not None:
                qubits_theory.append(a*n + b)
            if c is not None or d is not None:
                toffs_theory.append(c*n + d)
            self.adder.uncompute()
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
        if len(qubits_theory) > 0:
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
        plt.savefig(f"benchmarks/images/test_{self.adder_name}_qubit.png")
        plt.close()

        fig, ax = plt.subplots()
        ax.scatter(qubits, toffs_arr, label=f"{self.adder_name} (measured)")
        if len(toffs_theory) > 0:
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
        plt.savefig(f"benchmarks/images/test_{self.adder_name}_toffs.png")
        plt.close()