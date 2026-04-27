from psiqworkbench import QUInt
from psiqworkbench.qubricks.qubrick import Qubrick
from psiqworkbench.filter_presets import BIT_DEFAULT


def ct_add_engine(qbk, A, B, C, n):
    carry = qbk.alloc_temp_qreg(n + 1, "carry")

    # forward pass: compute sum bits into B, carry chain into carry
    for i in range(n):
        carry[i+1].x(A[i] | B[i])      # gate 1: CCnot
        B[i].x(A[i])                    # gate 2: Cnot
        carry[i+1].x(carry[i] | B[i])  # gate 3: CCnot
        B[i].x(carry[i])               # gate 4: Cnot

    # copy sum bits into output register
    for i in range(n):
        C[i].x(B[i])

    # reverse pass: restore B and carry to original values
    for i in reversed(range(n)):
        B[i].x(carry[i])
        carry[i+1].x(carry[i] | B[i])
        B[i].x(A[i])
        carry[i+1].x(A[i] | B[i])

    carry.release()


class CTAdd(Qubrick):

    """
    Implements the Cheng-Tseng (2002) quantum full adder. This is an
    out-of-place adder. The form is C ^= (A + B) mod 2^n. The result
    is stored in the C register, and the A and B registers are
    unmodified. For larger registers, use a QPU initialized with the
    BIT_DEFAULT filter preset to utilize the bit-vector simulator to
    enable simulation of more qubits.
    """

    def __init__(self, add_engine=ct_add_engine, **kwargs):
        super().__init__(**kwargs)
        self.add_engine = add_engine

    def _compute(self, A, B, C):
        n = A.num_qubits
        assert B.num_qubits == n and C.num_qubits == n, "Register sizes must match"
        self.add_engine(self, A, B, C, n)
        self.set_result_qreg(C)
