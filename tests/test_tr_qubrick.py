import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_tr import TRAdd
from psiqworkbench import QPU, QUInt
from psiqworkbench.filter_presets import BIT_DEFAULT


def test_adder_one_value(num_qubits=4, lhs_val=5, rhs_val=6):
    tr = TRAdd()
    qpu = QPU(num_qubits=4 * num_qubits + 2, filters=BIT_DEFAULT)
    qpu.enable_qubit_allocation_debugging()
    lhs = QUInt(num_qubits, "lhs", qpu=qpu)
    rhs = QUInt(num_qubits, "rhs", qpu=qpu)
    lhs.write(lhs_val)
    rhs.write(rhs_val)
    tr.compute(lhs=lhs, rhs=rhs)
    result = lhs.read()
    expected = (lhs_val + rhs_val) % (1 << num_qubits)
    assert result == expected, f"Expected {expected}, got {result}"
    assert rhs.read() == rhs_val, f"rhs not restored: expected {rhs_val}, got {rhs.read()}"


def test_adder_fifty_values():
    for i in range(1, 50):
        for j in range(1, 50):
            num_qubits = max(i.bit_length(), j.bit_length())
            test_adder_one_value(num_qubits=num_qubits, lhs_val=i, rhs_val=j)
