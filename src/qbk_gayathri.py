from psiqworkbench import QUInt
from psiqworkbench.qubricks.qubrick import Qubrick
from psiqworkbench.filter_presets import BIT_DEFAULT


def gayathri_add_engine(qbk, A, B, C, n):
    # forward pass: compute sum bits into C[0..n-2], carry into C[n-1]
    for i in range(n - 1):
        A[i].x(C[n-1])             # gate 1: Cnot
        C[i].x(B[i])               # gate 2: Cnot
        C[i].x(A[i])               # gate 3: Cnot
        B[i].x(C[n-1])             # gate 4: Cnot
        C[n-1].x(A[i] | B[i])     # gate 5: CCnot
        B[i].x(C[i])               # gate 6: Cnot
        A[i].x(C[i])               # gate 7: Cnot

    # unswap A and B to restore original values
    for i in range(n - 1):
        A[i].x(B[i])
        B[i].x(A[i])
        A[i].x(B[i])

    # add MSB into C[n-1] which holds the carry-out from bit n-2
    C[n-1].x(A[n-1])
    C[n-1].x(B[n-1])


class GayathriAdd(Qubrick):

    """
    Implements the Gayathri et al. (2021) quantum full adder. This is an
    out-of-place adder. The form is C = (A + B) mod 2^n. The C register
    must be prepared in the zero state on entry; C[n-1] is used as the
    ripple-carry register internally and must start at |0>. The A and B
    registers are restored to their original values after the computation.
    For larger registers, use a QPU initialized with the BIT_DEFAULT filter
    preset to utilize the bit-vector simulator to enable simulation
    of more qubits.
    """

    def __init__(self, add_engine=gayathri_add_engine, **kwargs):
        super().__init__(**kwargs)
        self.add_engine = add_engine

    # def _compute(self, A, B, C):
    #     n = A.num_qubits
    #     assert B.num_qubits == n and C.num_qubits == n, "Register sizes must match"
    #     self.add_engine(self, A, B, C, n)
    #     self.set_result_qreg(C)
    
    def _compute(self, lhs, rhs, sum=None, num_qubits=None):
        n = lhs.num_qubits if num_qubits is None else num_qubits
        if sum is None:
            sum = self.alloc_temp_qreg(rhs.num_qubits, "sum")
        assert rhs.num_qubits == n and sum.num_qubits == n, "Register sizes must match"
        self.add_engine(self, lhs, rhs, sum, n)
        self.set_result_qreg(sum)
