from psiqworkbench import Qubrick

class WangRCA(Qubrick):

    def __init__(self, name=None, **kwargs):
        super().__init__(name, never_uncompute=True, **kwargs)

    def _compute(self, a, b, num_qubits=1):

        # initialize auxiliary qubits
        aux = self.alloc_temp_qreg(
            num_qubits, 
            "aux",
            release_after_compute=True,
        )
        c_0 = self.alloc_temp_qreg(
            1,
            "c_0",
            release_after_compute=True,
        )

        # initial s1 layer
        aux[0].x(cond=a[0] | b[0])
        c_0.x(cond=a[0])
        a[0].x(cond=aux[0] ^ c_0)        # a_0 -> c_1
        aux[0].write(0)
        # iterate through layers
        for idx in range(num_qubits):
            # s2 layer
            a[idx].x(cond=aux[idx])    # c_j -> s_j
            b[idx].x(cond=aux[idx])    # b_j -> a_j
            # s1 layer
            aux[idx+1].x(cond=b[idx+1])
            a[idx].x(cond=a[idx+1])
            b[idx+1].x(cond=a[idx+1])
            a[idx+1].x(cond=a[idx] | b[idx+1])
        # final s2 layer
        a[-1].x(cond=aux[-1])
        b[-1].x(cond=aux[-1])