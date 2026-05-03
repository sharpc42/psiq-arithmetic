from psiqworkbench import QPU, Qubits
from psiqworkbench.filter_presets import BIT_DEFAULT

class AddResults:
    adder = None
    def test_adder_one_value(self, num_qubits=4, a_val=5, b_val=11):
        num_qubits = (a_val + b_val).bit_length()
        qpu = QPU(num_qubits=3*num_qubits+1, filters=BIT_DEFAULT)
        qpu.enable_qubit_allocation_debugging()
        a = Qubits(num_qubits, "a", qpu=qpu)
        b = Qubits(num_qubits, "b", qpu=qpu)
        a.write(a_val)
        b.write(b_val)
        with self.adder.computed(lhs=a, rhs=b, num_qubits=num_qubits) as result:
            assert result == a_val + b_val, f"Expected {a_val + b_val}, got {result}"
    def test_adder_many_values(self):
        for i in range(1,150):
            for j in range(0,150):
                print(f"Fifty vals - Testing {i=} and {j=}")
                num_qubits = max(i.bit_length(), j.bit_length(), (i+j).bit_length())
                self.test_adder_one_value(num_qubits=num_qubits, a_val=i, b_val=j)