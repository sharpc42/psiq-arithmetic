from psiqworkbench import Qubrick, Qubits, QUInt
from .qbk_ttk import TTKAdd

class TTKAddMultiply(Qubrick):

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

    def _compute(
            self, 
            accumulator : QUInt | Qubits, 
            factor1 : QUInt | Qubits,
            factor2 : QUInt | Qubits,
        ) -> None:
        """
        Computes accumulator += factor1 * factor2
        """

        if factor1.num_qubits < factor2.num_qubits:
            factor1, factor2 = factor2, factor1
        adder = TTKAdd()
        max_aux = accumulator.num_qubits - 1
        aux = self.alloc_temp_qreg(
            max_aux, 
            "aux", 
            release_after_compute=True
        )
        for k in range(factor1.num_qubits):
            aux.write(0)
            for i in range(factor2.num_qubits):
                aux[i].x(factor2[i])
            # update accumulator slice
            adder.compute(
                lhs=accumulator[k:],
                rhs=aux,
                num_qubits=accumulator[k:].num_qubits - 1,
                ctrl=factor1[k],
            )
            # uncompute step
            for i in range(factor2.num_qubits):
                aux[i].x(factor2[i])