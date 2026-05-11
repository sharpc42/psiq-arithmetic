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
            ctrl=None
        ) -> None:
        condition = 0 if ctrl is None else ctrl

        n = lhs.num_qubits
        z = rhs[n]
        if n == 0:
            return
        if n == 1:
            z[0].x(lhs[0] | rhs[0] | condition)
            rhs[0].x(lhs[0] | condition)
            return

        for i in range(1, n):
            rhs[i].x(lhs[i] | condition)

        for i in range(n - 1, 0, -1):
            target = z[0] if i == n - 1 else lhs[i + 1]
            target.x(lhs[i] | condition)

        for i in range(n):
            target = z[0] if i == n - 1 else lhs[i + 1]
            target.x(lhs[i] | rhs[i] | condition)

        for i in range(n - 1, 0, -1):
            rhs[i].x(lhs[i] | condition)
            lhs[i].x(lhs[i - 1] | rhs[i - 1] | condition)

        for i in range(1, n - 1):
            lhs[i + 1].x(lhs[i] | condition)

        for i in range(n):
            rhs[i].x(lhs[i] | condition)

__all__ = ["TTKAdd"]