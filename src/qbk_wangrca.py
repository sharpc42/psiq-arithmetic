from psiqworkbench import Qubrick, Qubits, QUInt

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

    def _add(
            self,
            lhs : QUInt | Qubits,
            rhs : QUInt | Qubits,
            num_qubits : int = 1,
            subtract_condition : bool = False,
            result_is_sum_not_carry : bool = True,
        ) -> None:

        # initialize carry qubit
        c_0 = self.alloc_temp_qreg(1, "carry")[0]
        if result_is_sum_not_carry:
            self.set_result_qreg(lhs | c_0)
        else:
            self.set_result_qreg(c_0)

        if num_qubits == 1:
            if not result_is_sum_not_carry:
                c_0.x(cond=lhs[0] | rhs[0])
            lhs[0].x(cond=rhs[0])
            return

        # initialize auxiliary qubits
        aux = self.alloc_temp_qreg(
            num_qubits,
            "aux",
        )

        # initial s1 layer
        aux[0].x(cond=rhs[0])
        rhs[0].x(cond=lhs[0])
        if subtract_condition:
            c_0.x()
            rhs.x()
        c_0.x(cond=lhs[0])
        lhs[0].x(cond=rhs[0] | c_0)        # a_0 -> c_1
        # iterate through layers
        for idx in range(num_qubits - 1):  
            if idx == 0:
                c_0.x(cond=aux[0])             # c_0 -> s_0
            else:
                lhs[idx - 1].x(cond=aux[idx])  # c_j -> s_j
            rhs[idx].x(cond=aux[idx])          # b_j -> a_j
            # s1 layer
            aux[idx+1].x(cond=rhs[idx+1])
            rhs[idx+1].x(cond=lhs[idx+1])
            lhs[idx].x(cond=lhs[idx+1])
            lhs[idx+1].x(cond=lhs[idx] | rhs[idx+1])
        # final s2 layer
        lhs[num_qubits - 2].x(cond=aux[-1])
        rhs[-1].x(cond=aux[-1])
        for idx in range(num_qubits):
            c_0.swap(lhs[idx])

    def _compute(
            self, 
            lhs : QUInt | Qubits, 
            rhs : QUInt | Qubits,
            num_qubits : int = 1,
            subtract_condition : bool = False,
        ) -> None:

        if not isinstance(lhs, (Qubits, QUInt)) or not isinstance(rhs, (Qubits, QUInt)):
            raise TypeError("lhs and rhs must be of type QUInt or Qubits")
        required_qubits = len(lhs) + len(rhs) + num_qubits + 1 
        if lhs.qpu.num_qubits < required_qubits:
            raise ValueError(f"QPU has insufficient qubits for WangAdd."
                             f"Need at least {required_qubits} total qubits."
                             f"Got {lhs.qpu.num_qubits}.")
        if lhs.num_qubits != rhs.num_qubits:
            raise ValueError("WangAdd requires lhs and rhs to have same number of qubits.")
        
        self._add(
            lhs=lhs, 
            rhs=rhs, 
            num_qubits=num_qubits,
            subtract_condition=subtract_condition,
        )