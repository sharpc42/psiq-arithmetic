from psiqworkbench import Qubrick, Qubits, QUInt

class WangAdd(Qubrick):

    """
    Implements the Wang ripple-carry adder (Wang et al. 2016).

    Out-of-place reversible adder. The result is written into the
    (n+1)-qubit register ``lhs | c_0``: the low n bits hold the sum and
    the top bit holds the carry-out. Use the context manager and read
    the value off the result register, e.g.::

        with WangAdd().computed(lhs=a, rhs=b, num_qubits=n) as result:
            value = result.read()

    ``compute()`` runs the addition; ``uncompute()`` (invoked
    automatically on exit of the ``computed`` block) restores ``lhs``
    and ``rhs`` to their original values.

    Pass ``subtract_condition=True`` to compute ``lhs - rhs`` instead,
    via two's complement.

    The QPU must have at least 3N+1 qubits for N-bit operands. For
    larger registers, initialize the QPU with the BIT_DEFAULT filter
    preset to use the bit-vector simulator. The lhs and rhs registers
    are required to be Qubits (or QUInt) type.
    """

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

    def _add(
            self,
            lhs : QUInt | Qubits,
            rhs : QUInt | Qubits,
            num_qubits : int = 1,
            subtract_condition : bool = False,
        ) -> None:

        # initialize carry qubit
        c_0 = self.alloc_temp_qreg(1, "carry")[0]
        # result is the (n+1)-qubit register lhs|c_0: low n bits hold the sum,
        # the top bit (c_0) holds the carry-out.
        self.set_result_qreg(lhs | c_0)

        if num_qubits == 1:
            c_0.x(cond=lhs[0] | rhs[0])   # carry-out = a0 & b0  (top bit of lhs|c_0)
            lhs[0].x(cond=rhs[0])         # sum bit = a0 ^ b0
            return

        # initialize auxiliary qubits
        aux = self.alloc_temp_qreg(
            num_qubits,
            "aux",
        )
        if subtract_condition:
            # two's complement: lhs - rhs = lhs + ~rhs + 1
            c_0.x()
            rhs.x()
        # initial s1 layer
        aux[0].x(cond=rhs[0])
        rhs[0].x(cond=lhs[0])
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
        # Sum bit s_j is written one index low (s_0 into c_0, s_j into lhs[j-1]);
        # this cyclic rotation of [lhs[0..n-1], c_0] by one realigns them so that
        # the result register lhs|c_0 reads out correctly.
        for idx in range(num_qubits):
            c_0.swap(lhs[idx])
        # uncompute the two's-complement input transform to restore rhs
        if subtract_condition:
            rhs.x()
            c_0.x()

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