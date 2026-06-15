from psiqworkbench import QPU, Qubits
from psiqworkbench.filter_presets import BIT_DEFAULT

def _run_out_of_place(adder, a_val, b_val, subtract):
    """Run an out-of-place adder over a `computed` block and return the
    (lhs, rhs) values read back after automatic uncomputation."""
    num_qubits = (a_val + b_val).bit_length()
    qpu = QPU(num_qubits=4*num_qubits+2, filters=BIT_DEFAULT)
    qpu.enable_qubit_allocation_debugging()
    a = Qubits(num_qubits, "a", qpu=qpu)
    b = Qubits(num_qubits, "b", qpu=qpu)
    a.write(a_val)
    b.write(b_val)
    kwargs = dict(lhs=a, rhs=b, num_qubits=num_qubits)
    if subtract:
        kwargs["subtract_condition"] = True
    with adder.computed(**kwargs):
        pass
    return a.read(), b.read()


class ConsistencyAddOutOfPlace:
    """lhs and rhs must be restored after an out-of-place addition."""
    adder = None
    def test_lhs_add_consistency(self, a_val=11, b_val=5):
        a_result, _ = _run_out_of_place(self.adder, a_val, b_val, subtract=False)
        assert a_result == a_val, f"lhs was {a_val} before lhs + rhs, now it is {a_result}"
    def test_rhs_add_consistency(self, a_val=11, b_val=5):
        _, b_result = _run_out_of_place(self.adder, a_val, b_val, subtract=False)
        assert b_result == b_val, f"rhs was {b_val} before lhs + rhs, now it is {b_result}"


class ConsistencySubOutOfPlace:
    """lhs and rhs must be restored after an out-of-place subtraction.
    Only for adders that accept subtract_condition."""
    adder = None
    def test_lhs_sub_consistency(self, a_val=11, b_val=5):
        a_result, _ = _run_out_of_place(self.adder, a_val, b_val, subtract=True)
        assert a_result == a_val, f"lhs was {a_val} before lhs - rhs, now it is {a_result}"
    def test_rhs_sub_consistency(self, a_val=11, b_val=5):
        _, b_result = _run_out_of_place(self.adder, a_val, b_val, subtract=True)
        assert b_result == b_val, f"rhs was {b_val} before lhs - rhs, now it is {b_result}"

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
        self.adder.compute(rhs=a, lhs=b, num_qubits=num_qubits)
        a_result = a.read()
        assert a_result == a_val, f"a was {a_val} before b += a, now it is {a_result}"