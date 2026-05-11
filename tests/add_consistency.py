from psiqworkbench import QPU, Qubits
from psiqworkbench.filter_presets import BIT_DEFAULT

class ConsistencyResultsOutOfPlace:
    adder = None
    def test_rhs_consistency(self, num_qubits=4, a_val=5, b_val=11):
        num_qubits = (a_val + b_val).bit_length()
        qpu = QPU(num_qubits=3*num_qubits+1, filters=BIT_DEFAULT)
        qpu.enable_qubit_allocation_debugging()
        a = Qubits(num_qubits, "a", qpu=qpu)
        b = Qubits(num_qubits, "b", qpu=qpu)
        a.write(a_val)
        b.write(b_val)
        with self.adder.computed(lhs=a, rhs=b, num_qubits=num_qubits) as result:
            pass
        b_result = b.read()
        assert b_result == b_val, f"rhs was {b_val} before sum = lhs + rhs, now it is {b_result}"
    def test_lhs_consistency(self, num_qubits=4, a_val=5, b_val=11):
        num_qubits = (a_val + b_val).bit_length()
        qpu = QPU(num_qubits=3*num_qubits+1, filters=BIT_DEFAULT)
        qpu.enable_qubit_allocation_debugging()
        a = Qubits(num_qubits, "a", qpu=qpu)
        b = Qubits(num_qubits, "b", qpu=qpu)
        a.write(a_val)
        b.write(b_val)
        with self.adder.computed(lhs=a, rhs=b, num_qubits=num_qubits) as result:
            pass
        a_result = a.read()
        assert a_result == a_val, f"lhs was {a_val} before lhs += rhs, now it is {a_result}"

class ConsistencyResultsInPlace:
    adder = None
    def test_a_consistency(self, num_qubits=4, a_val=5, b_val=11):
        num_qubits = (a_val + b_val).bit_length()
        qpu = QPU(num_qubits=2*num_qubits+1, filters=BIT_DEFAULT)
        qpu.enable_qubit_allocation_debugging()
        a = Qubits(num_qubits, "a", qpu=qpu)
        b = Qubits(num_qubits + 1, "b", qpu=qpu)
        # z = Qubits(1, "z", qpu=qpu)
        a.write(a_val)
        b.write(b_val)
        # z.write(z_val)
        self.adder.compute(a=a, b=b)
        a_result = a.read()
        assert a_result == a_val, f"a was {a_val} before b += a, now it is {a_result}"