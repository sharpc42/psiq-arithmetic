import wangrca_qubrick
from psiqworkbench import QPU, Qubits
from psiqworkbench.filter_presets import BIT_DEFAULT

def test_adder_one_value(num_qubits=4, a_val=5, b_val=11):
    wrca = wangrca_qubrick.WangAdd()
    qpu = QPU(num_qubits=3*num_qubits+1, filters=BIT_DEFAULT)
    qpu.enable_qubit_allocation_debugging()
    a = Qubits(num_qubits + 1, "a", qpu=qpu)
    b = Qubits(num_qubits, "b", qpu=qpu)
    a.write(a_val << 1)  # shift left to make room for carry bit
    b.write(b_val)
    wrca.compute(lhs=a, rhs=b, num_qubits=num_qubits)
    result = wrca.get_result_qreg()
    wrca.uncompute()
    assert result == a_val + b_val, f"Expected {a_val + b_val}, got {result}"

def test_adder_fifty_values():
    for i in range(1,50):
        for j in range(1,50):
            num_qubits = max(i.bit_length(), j.bit_length())
            test_adder_one_value(num_qubits=num_qubits, a_val=i, b_val=j)

def test_rhs_consistency(num_qubits=4, a_val=5, b_val=11):
    wrca = wangrca_qubrick.WangAdd()
    qpu = QPU(num_qubits=3*num_qubits+1, filters=BIT_DEFAULT)
    qpu.enable_qubit_allocation_debugging()
    a = Qubits(num_qubits + 1, "a", qpu=qpu)
    b = Qubits(num_qubits, "b", qpu=qpu)
    a.write(a_val << 1)  # shift left to make room for carry bit
    b.write(b_val)
    wrca.compute(lhs=a, rhs=b, num_qubits=num_qubits)
    wrca.uncompute()
    b_result = b.read()
    assert b_result == b_val, f"rhs was {b_val} before sum = lhs + rhs, now it is {b_result}"