from psiqworkbench import Qubrick, Qubits
from psiqworkbench.qubricks import GidneyAdd

class WangAdd(Qubrick):

    """
    Implements the Wang ripple-carry adder. This is an
    out-of-place adder. The form is sum = lhs + rhs. The 
    result is returned by calling get_result_qreg() after 
    compute(). An uncompute() step is required after. The 
    QPU must have at least 3N+1 qubits for N-bit addition.
    The lhs and rhs are left unmodified. For larger registers,
    use a QPU initialized with the BIT_DEFAULT filter preset 
    for the lhs and rhs registers to utilize the bit-vector 
    simulator to enable simulation of more qubits. The lhs
    and rhs registers are required to be Qubits type.
    """

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

    def _compute(
            self, 
            lhs : Qubits, 
            rhs : Qubits, 
            num_qubits : int = 1
        ) -> None:
        if type(lhs) != Qubits or type(rhs) != Qubits:
            raise TypeError("lhs and rhs must be of type Qubits")
        
        # initialize carry qubit
        c_0 = self.alloc_temp_qreg(1, "carry")[0]
        self.set_result_qreg(lhs)
        # initialize auxiliary qubits
        aux = self.alloc_temp_qreg(
            num_qubits, 
            "aux",
        )
        # initial s1 layer
        aux[0].x(cond=rhs[0])
        rhs[0].x(cond=lhs[0])
        c_0.x(cond=lhs[0])
        lhs[0].x(cond=rhs[0] | c_0)        # a_0 -> c_1
        # iterate through layers
        for idx in range(num_qubits - 1):  
            lhs[idx].x(cond=aux[idx])      # c_j -> s_j
            rhs[idx].x(cond=aux[idx])      # b_j -> a_j
            # s1 layer
            aux[idx+1].x(cond=rhs[idx+1])
            rhs[idx+1].x(cond=lhs[idx+1])
            lhs[idx].x(cond=lhs[idx+1])
            lhs[idx+1].x(cond=lhs[idx] | rhs[idx+1])
        # final s2 layer
        lhs[num_qubits - 2].x(cond=aux[-1])
        rhs[-1].x(cond=aux[-1])