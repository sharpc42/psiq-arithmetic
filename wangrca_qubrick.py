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
        super().__init__(name, **kwargs)

    def _compute(
            self, 
            lhs : Qubits, 
            rhs : int | Qubits, 
            num_qubits : int = 1
        ) -> None:
        # initialize auxiliary qubits
        aux = self.alloc_temp_qreg(
            num_qubits, 
            "aux",
            release_after_compute=True,
        )
        c_0 = lhs[0]
        # initial s1 layer
        aux[0].x(cond=rhs[0])
        rhs[0].x(cond=lhs[1])
        c_0.x(cond=lhs[1])
        lhs[1].x(cond=rhs[0] | c_0)        # a_0 -> c_1
        # iterate through layers
        for idx in range(num_qubits - 1):  
            lhs[idx].x(cond=aux[idx])      # c_j -> s_j
            rhs[idx].x(cond=aux[idx])      # b_j -> a_j
            # s1 layer
            aux[idx+1].x(cond=rhs[idx+1])
            rhs[idx+1].x(cond=lhs[idx+2])
            lhs[idx+1].x(cond=lhs[idx+2])
            lhs[idx+2].x(cond=lhs[idx+1] | rhs[idx+1])
        # final s2 layer
        lhs[-2].x(cond=aux[-1])
        rhs[-1].x(cond=aux[-1])
        # uncompute auxiliary qubits
        aux.read()
        c_0.read()