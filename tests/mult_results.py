from psiqworkbench import QPU, Qubits, QUInt
from psiqworkbench.filter_presets import BIT_DEFAULT

class AddMultiplyResults:
    multiplier = None
    def test_multiply_one_value(
        self,
        a_val = 0,
        b_val = 5,
        c_val = 11,
    ) -> None:
        register_size = max(1, b_val.bit_length(), c_val.bit_length())
        accumulator_size = max(2 * register_size, (a_val + b_val * c_val).bit_length(), 1)
        qpu = QPU(num_qubits=2 * accumulator_size + 2 * register_size - 1, filters=BIT_DEFAULT)
        qpu.enable_qubit_allocation_debugging()
        a = Qubits(accumulator_size, "a", qpu=qpu)
        b = Qubits(register_size, "b", qpu=qpu)
        c = Qubits(register_size, "c", qpu=qpu)
        a.write(a_val)
        b.write(b_val)
        c.write(c_val)
        self.multiplier.compute(
            accumulator = a,
            factor1 = b,
            factor2 = c,
        )
        result = a.read()
        expected_result = a_val + (b_val * c_val)
        assert result == expected_result, f"Expected result {expected_result}, got {result} from a={a_val}, b={b_val}, c={c_val}"
    def test_multiply_many_values(self):
        for i in range(0,8):
            for j in range(0,8):
                for k in range(0,8):
                    self.test_multiply_one_value(a_val=i, b_val=j, c_val=k)

class AddMultiplyControlResults:
    multiplier = None
    def test_control_one_value(self, a_val=3, b_val=5, p_val=0, z_val=0):
        num_qubits = max(2, a_val.bit_length(), b_val.bit_length())
        qpu = QPU(num_qubits=(4*num_qubits + 1), filters=BIT_DEFAULT)
        a = QUInt(num_qubits, "a", qpu)
        b = QUInt(num_qubits, "b", qpu)
        p = QUInt(2*num_qubits, "p", qpu)
        z = QUInt(1, "z", qpu)
        a.write(a_val)
        b.write(b_val)
        p.write(p_val)
        z.write(z_val)
        self.multiplier.compute(a=a, b=b, p=p, z=z)
        product = p.read()  # 15 (3×5)
        assert product == a_val * b_val, f"Expected result {a_val * b_val}, got {product} from a={a_val} and b={b_val}"
    def test_control_many_values(self):
        # QUInt(4) can represent values 0..15, so limit the test ranges accordingly
        for i in range(0,8):
            for j in range(0,8):
                for k in range(0,8):
                    self.test_control_one_value(a_val=i, b_val=j, p_val=0, z_val=0)