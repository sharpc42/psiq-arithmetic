"""Standalone PsiQuantum Workbench TTK in-place adder module.

This file contains the reusable TTK adder implementation without the
benchmarking, plotting, or end-to-end validation code from the larger script.
"""

from __future__ import annotations

from psiqworkbench import QUInt, Qubrick


class TTKAdd(Qubrick):
    """Custom no-ancilla TTK adder qubrick.

    Register semantics:
      |b>|a>|z> -> |(a + b) mod 2^n>|a>|z xor carry_out>
    """

    def _compute(self, a: QUInt, b: QUInt, z: QUInt, ctrl=None) -> None:
        condition = 0 if ctrl is None else ctrl

        if a.num_qubits != b.num_qubits:
            raise ValueError("TTKAdd requires a and b to have equal width")
        if z.num_qubits != 1:
            raise ValueError("TTKAdd requires z to be exactly 1 qubit")

        n = a.num_qubits
        if n == 0:
            return
        if n == 1:
            b[0].x(a[0] | condition)
            z[0].x(a[0] | b[0] | condition)
            return

        for i in range(1, n):
            b[i].x(a[i] | condition)

        for i in range(n - 1, 0, -1):
            target = z[0] if i == n - 1 else a[i + 1]
            target.x(a[i] | condition)

        for i in range(n):
            target = z[0] if i == n - 1 else a[i + 1]
            target.x(a[i] | b[i] | condition)

        for i in range(n - 1, 0, -1):
            b[i].x(a[i] | condition)
            a[i].x(a[i - 1] | b[i - 1] | condition)

        for i in range(1, n - 1):
            a[i + 1].x(a[i] | condition)

        for i in range(n):
            b[i].x(a[i] | condition)


__all__ = ["TTKAdd"]