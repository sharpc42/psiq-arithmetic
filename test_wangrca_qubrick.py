import wangrca_qubrick
from psiqworkbench import QPU, Qubits

def test_add_one_bit():
    wrca = wangrca_qubrick.WangAdd()
    num_qubits = 4
    qpu = QPU(num_qubits=3*num_qubits+1)
    qpu.enable_qubit_allocation_debugging()
    a_val = 5
    b_val = 11
    a = Qubits(num_qubits + 1, "a", qpu=qpu)
    b = Qubits(num_qubits, "b", qpu=qpu)
    a.write(a_val << 1)  # shift left to make room for carry bit
    b.write(b_val)
    wrca.compute(lhs=a, rhs=b, num_qubits=num_qubits)
    result = a.read()
    assert result == a_val + b_val, f"Expected {a_val + b_val}, got {result}"