from psiqworkbench import Qubrick, Qubits
from psiqworkbench.qubricks import GidneyAdd

class WangAdd(Qubrick):

    """
    Implements the Wang ripple-carry adder. This is an
    out-of-place adder. The form is lhs += rhs. The result 
    is stored in the lhs register with a carry qubit, and 
    the rhs register is unmodified. For larger registers,
    use a QPU initialized with the BIT_DEFAULT filter preset 
    for the lhs and rhs registers to utilize the bit-vector 
    simulator to enable simulation of more qubits. The lhs
    register is required to be Qubits type.
    """

    def __init__(self, name=None, **kwargs):
        super().__init__(name, never_uncompute=True, **kwargs)

    def _compute(
            self, 
            lhs : Qubits, 
            rhs : int | Qubits, 
            num_qubits : int = 1
        ) -> None:
        lhs_q = lhs
        if isinstance(rhs, int):
            rhs_q = self.alloc_temp_qreg(
                num_qubits, 
                "rhs", 
                release_after_compute=True,
            )
        else:
            rhs_q = rhs
        # initialize auxiliary qubits
        aux = self.alloc_temp_qreg(
            num_qubits, 
            "aux",
            release_after_compute=True,
        )
        c_0 = lhs_q[0]
        # initial s1 layer
        aux[0].x(cond=rhs_q[0])
        rhs_q[0].x(cond=lhs_q[1])
        c_0.x(cond=lhs_q[1])
        lhs_q[1].x(cond=rhs_q[0] | c_0)        # a_0 -> c_1
        # iterate through layers
        for idx in range(num_qubits - 1):  
            lhs_q[idx].x(cond=aux[idx])      # c_j -> s_j
            rhs_q[idx].x(cond=aux[idx])      # b_j -> a_j
            # s1 layer
            aux[idx+1].x(cond=rhs_q[idx+1])
            rhs_q[idx+1].x(cond=lhs_q[idx+2])
            lhs_q[idx+1].x(cond=lhs_q[idx+2])
            lhs_q[idx+2].x(cond=lhs_q[idx+1] | rhs_q[idx+1])
        # final s2 layer
        lhs_q[-2].x(cond=aux[-1])
        rhs_q[-1].x(cond=aux[-1])
        # uncompute auxiliary qubits
        aux.read()
        c_0.read()
        if isinstance(rhs, int):
            rhs_q.read()