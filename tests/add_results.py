from psiqworkbench import QPU, Qubits, QUInt
from psiqworkbench.filter_presets import BIT_DEFAULT

class AddResultsOutOfPlace:
    adder = None
    def test_adder_one_value(self, a_val=5, b_val=11):
        num_qubits = max(a_val.bit_length(), b_val.bit_length(), (a_val + b_val).bit_length())
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
                self.test_adder_one_value(a_val=i, b_val=j)

class AddResultsInPlace:
    adder = None
    def test_adder_one_value(self, a_val=5, b_val=11, z_val=0):
        num_qubits = max(a_val.bit_length(), b_val.bit_length(), (a_val + b_val).bit_length())
        qpu = QPU(num_qubits=2*num_qubits+1, filters=BIT_DEFAULT)
        qpu.enable_qubit_allocation_debugging()
        a = QUInt(num_qubits, "a", qpu=qpu)
        b = QUInt(num_qubits, "b", qpu=qpu)
        z = QUInt(1, "z", qpu=qpu)
        a.write(a_val)
        b.write(b_val)
        z.write(0)
        self.adder.compute(a=a, b=b, z=z)
        b_result = b.read()
        expected_sum = (a_val + b_val) % (1 << num_qubits)
        assert b_result == expected_sum, f"Expected sum {expected_sum}, got {b_result}"
    def test_adder_many_values(self, z_val=0):
        for i in range(1,150):
            for j in range(0,150):
                print(f"Fifty vals - Testing {i=} and {j=}")
                self.test_adder_one_value(a_val=i, b_val=j, z_val=z_val)