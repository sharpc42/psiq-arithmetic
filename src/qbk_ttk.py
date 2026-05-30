"""Standalone PsiQuantum Workbench TTK in-place adder module.

This file contains the reusable TTK adder implementation without the
benchmarking, plotting, or end-to-end validation code from the larger script.
"""

from __future__ import annotations

from psiqworkbench import QUInt, Qubits, Qubrick


class TTKAdd(Qubrick):
    """Custom no-ancilla TTK adder qubrick.

    Register semantics:
      |b>|a>|z> -> |(a + b) mod 2^n>|a>|z xor carry_out>

    Requires b.num_qubits = a.num_qubits + 1 for carry
    """

    def _compute(
            self, 
            rhs: QUInt | Qubits, 
            lhs: QUInt | Qubits,
            num_qubits: int | None = None,
            ctrl=None
        ) -> None:
        condition = 0 if ctrl is None else ctrl

        num_qubits = rhs.num_qubits if num_qubits is None else num_qubits
        z = lhs[num_qubits]
        if num_qubits == 0:
            return
        if num_qubits == 1:
            z[0].x(rhs[0] | lhs[0] | condition)
            lhs[0].x(rhs[0] | condition)
            return

        for i in range(1, num_qubits):
            lhs[i].x(rhs[i] | condition)

        for i in range(num_qubits - 1, 0, -1):
            target = z[0] if i == num_qubits - 1 else rhs[i + 1]
            target.x(rhs[i] | condition)

        for i in range(num_qubits):
            target = z[0] if i == num_qubits - 1 else rhs[i + 1]
            target.x(rhs[i] | lhs[i] | condition)

        for i in range(num_qubits - 1, 0,-1):
            lhs[i].x(rhs[i] | condition)
            rhs[i].x(rhs[i - 1] | lhs[i - 1] | condition)

        for i in range(1, num_qubits - 1):
            rhs[i + 1].x(rhs[i] | condition)

        for i in range(num_qubits):
            lhs[i].x(rhs[i] | condition)

__all__ = ["TTKAdd"]