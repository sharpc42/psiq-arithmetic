from src.qbk_gayathri import GayathriAdd
from psiqworkbench import QPU, QUInt
from psiqworkbench.filter_presets import BIT_DEFAULT


def test_adder_one_value(num_qubits=4, a_val=5, b_val=6):
    gayathri = GayathriAdd()
    qpu = QPU(num_qubits=3 * num_qubits + 1, filters=BIT_DEFAULT)
    qpu.enable_qubit_allocation_debugging()
    a = QUInt(num_qubits, "a", qpu=qpu)
    b = QUInt(num_qubits, "b", qpu=qpu)
    c = QUInt(num_qubits, "c", qpu=qpu)
    a.write(a_val)
    b.write(b_val)
    gayathri.compute(lhs=a, rhs=b, sum=c)
    result = c.read()
    expected = (a_val + b_val) % (1 << num_qubits)
    assert result == expected, f"Expected {expected}, got {result}"
    assert a.read() == a_val, f"A not restored: expected {a_val}, got {a.read()}"
    assert b.read() == b_val, f"B not restored: expected {b_val}, got {b.read()}"


def test_adder_fifty_values():
    for i in range(1, 50):
        for j in range(1, 50):
            num_qubits = max(i.bit_length(), j.bit_length())
            test_adder_one_value(num_qubits=num_qubits, a_val=i, b_val=j)
