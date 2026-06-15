from psiqworkbench import QUInt
from psiqworkbench.qubricks.qubrick import Qubrick


def tr_add_engine(qbk, lhs, rhs, n):
    # bigA[i] = rhs[i] for i < n-1, bigA[n-1] = lhs[n-1]
    # Peres(A, B, C) = CCnot(A,B->C) then Cnot(A->B)
    # oldToffoli(A, B, C) = CCnot(A,B->C)

    if n == 1:
        lhs[0].x(rhs[0])
        return

    m = n - 1

    def bA(i):
        return rhs[i] if i < m else lhs[n - 1]

    # step 1
    for i in range(1, m):
        lhs[i].x(rhs[i])

    # step 2
    for i in range(m - 1, 0, -1):
        bA(i + 1).x(bA(i))

    # step 3: oldToffoli(B[i], bigA[i], bigA[i+1])
    for i in range(m - 1):
        bA(i + 1).x(lhs[i] | bA(i))           # CCnot

    # step 4: Peres(bigA[i], B[i], bigA[i+1])
    for i in range(m - 1, -1, -1):
        bA(i + 1).x(bA(i) | lhs[i])           # CCnot
        lhs[i].x(bA(i))                        # Cnot

    # step 5
    for i in range(1, m - 1):
        bA(i + 1).x(bA(i))

    # step 6
    for i in range(m - 1, 0, -1):
        lhs[i].x(rhs[i])

    lhs[n - 1].x(rhs[n - 1])


class TRAdd(Qubrick):

    """
    Implements the Thapliyal and Ranganathan (2013) in-place ripple-carry adder.
    This is an in-place adder. The form is lhs := (lhs + rhs) mod 2^n. The rhs
    register is restored to its original value after the computation. No ancilla
    qubits are required beyond the two n-qubit input registers.
    Follows the quant-arith-re adaptation of Methodology 1, which reuses lhs[n-1]
    as the carry register to avoid the carry-out garbage bit in the original paper.
    The Peres and Toffoli gates from the paper are expressed directly as CCNOT
    and CNOT, replacing the V-gate (Rx(pi/2)) decompositions used in the original.
    Ref: Thapliyal H, Ranganathan N (2013)
         Design of Efficient Reversible Logic-Based Binary and BCD Adder Circuits.
         ACM J. Emerg. Technol. Comput. Syst. 9(3). https://doi.org/10.1145/2491682
    """

    def __init__(self, add_engine=tr_add_engine, **kwargs):
        super().__init__(**kwargs)
        self.add_engine = add_engine

    def _compute(self, lhs, rhs, num_qubits=None):
        n = lhs.num_qubits if num_qubits is None else num_qubits
        assert rhs.num_qubits == n, "Register sizes must match"
        self.add_engine(self, lhs, rhs, n)
