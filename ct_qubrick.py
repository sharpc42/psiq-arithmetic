"""
CT2002 Quantum Full Adder as psiqworkbench Qubrick.

Architecture follows AddBase pattern from:
  psiqworkbench/qubricks/qbk_gidney_arithmetic.py
"""

from psiqworkbench import QPU, QUInt
from psiqworkbench.qubricks.qubrick import Qubrick
from psiqworkbench.filter_presets import BIT_DEFAULT


def ct_add_engine(qbk, A, B, C, n):
    """CT2002 add: C ^= (A+B) mod 2^n. Within/apply inline.

    Gate order matches paper equations (3)-(6):
      gate 1: CCNOT(a_i, b_i,        carry_i)   eq(3)
      gate 2: CNOT (a_i,             b_i)        eq(4)
      gate 3: CCNOT(carry_{i-1}, b_i, carry_i)  eq(5)
      gate 4: CNOT (carry_{i-1},     b_i)        eq(6)
    Backward = same gates in reverse (all Hermitian).
    """
    carry = qbk.alloc_temp_qreg(n + 1, "carry")

    # WITHIN forward: QFA chain
    for i in range(n):
        carry[i+1].x(A[i] | B[i])      # gate 1
        B[i].x(A[i])                    # gate 2
        carry[i+1].x(carry[i] | B[i])  # gate 3
        B[i].x(carry[i])               # gate 4

    # APPLY: XOR sum bits into C
    for i in range(n):
        C[i].x(B[i])

    # WITHIN backward: QFA† chain
    for i in reversed(range(n)):
        B[i].x(carry[i])               # gate 4†
        carry[i+1].x(carry[i] | B[i]) # gate 3†
        B[i].x(A[i])                   # gate 2†
        carry[i+1].x(A[i] | B[i])     # gate 1†

    carry.release()


class CTAdd(Qubrick):
    """CT2002 out-of-place adder: C ^= (A + B) mod 2^n.

    A and B are restored after compute().
    carry ancilla allocated and released internally.

    Usage:
        adder = CTAdd()
        adder.compute(A=A, B=B, C=C)
    """

    def __init__(self, add_engine=ct_add_engine, **kwargs):
        super().__init__(**kwargs)
        self.add_engine = add_engine

    def _compute(self, A, B, C):
        n = A.num_qubits
        assert B.num_qubits == n and C.num_qubits == n, "Register sizes must match"
        self.add_engine(self, A, B, C, n)
        self.set_result_qreg(C)
