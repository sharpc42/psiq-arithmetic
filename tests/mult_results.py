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
        for i in range(0,20):
            for j in range(0,20):
                for k in range(0,20):
                    self.test_multiply_one_value(a_val=i, b_val=j, c_val=k)