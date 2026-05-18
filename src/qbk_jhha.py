from __future__ import annotations
from psiqworkbench import QUInt, Qubrick

class JHHAMultiplier(Qubrick):
    """
    Reversible JHHA-style n×n multiplier (add-and-rotate).

    API:
        mul = JHHAMultiplier()
        mul.compute(a=a, b=b, p=p, z=z)      # |a>|b>|0>|0> -> |a>|b>|a*b>|0>

    Registers:
        a: multiplicand (n qubits, preserved)
        b: multiplier (n qubits, preserved)
        p: product accumulator (2n qubits)
        z: carry bit (1 qubit, restored to 0)

    Complexity: O(n²) gates, 4n+1 qubits (no hidden ancilla)
    """

    @staticmethod
    def _xor_swap(q0, q1, condition=0) -> None:
        q0.x(q1 | condition)
        q1.x(q0 | condition)
        q0.x(q1 | condition)

    def _ttk_add(self, a: QUInt, b: QUInt, z: QUInt, ctrl=None) -> None:
        condition = 0 if ctrl is None else ctrl

        if a.num_qubits != b.num_qubits:
            raise ValueError("TTKAdd requires equal width")
        if z.num_qubits != 1:
            raise ValueError("TTKAdd requires z to be 1 qubit")

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

    def _controlled_ttk_add(self, sel, multiplicand: QUInt, target_window, carry, ctrl=None) -> None:
        condition = 0 if ctrl is None else ctrl
        local_ctrl = sel if condition == 0 else (sel | condition)
        self._ttk_add(a=multiplicand, b=target_window, z=carry, ctrl=local_ctrl)

    def _rotate_right(self, reg, steps: int = 1, ctrl=None) -> None:
        condition = 0 if ctrl is None else ctrl
        w = reg.num_qubits
        if w <= 1:
            return

        steps %= w
        for _ in range(steps):
            if w % 2 == 0:
                k1 = w // 2
                i, j = 0, w - 1
                while i < k1 and j >= k1:
                    self._xor_swap(reg[i], reg[j], condition=condition)
                    i += 1
                    j -= 1

                i, j = 0, w - 2
                while i < (k1 - 1) and j >= k1:
                    self._xor_swap(reg[i], reg[j], condition=condition)
                    i += 1
                    j -= 1
            else:
                k1 = w // 2
                i, j = 0, w - 1
                while i < k1 and j >= (k1 + 1):
                    self._xor_swap(reg[i], reg[j], condition=condition)
                    i += 1
                    j -= 1

                i, j = 0, w - 2
                while i < k1 and j >= k1:
                    self._xor_swap(reg[i], reg[j], condition=condition)
                    i += 1
                    j -= 1

    def _rotate_left(self, reg, steps: int = 1, ctrl=None) -> None:
        condition = 0 if ctrl is None else ctrl
        w = reg.num_qubits
        if w <= 1:
            return

        steps %= w
        for _ in range(steps):
            for i in range(w - 1, 0, -1):
                self._xor_swap(reg[i], reg[i - 1], condition=condition)

    def _carry_bridge(self, z: QUInt, p: QUInt, n: int, ctrl=None) -> None:
        condition = 0 if ctrl is None else ctrl
        if z.num_qubits != 1:
            raise ValueError("CarryBridge requires z to be 1 qubit")
        if p.num_qubits <= n:
            raise ValueError("CarryBridge requires p width > n")

        z0 = z[0]
        pn = p[n]
        z0.x(pn | condition)
        pn.x(z0 | condition)
        z0.x(pn | condition)

    def _compute(
        self, 
        a: QUInt, 
        b: QUInt, 
        p: QUInt, 
        z: QUInt, 
        ctrl = None
    ) -> None:
        condition = 0 if ctrl is None else ctrl

        if a.num_qubits != b.num_qubits:
            raise ValueError("a and b must have equal width")

        n = a.num_qubits
        if n == 0:
            return

        if p.num_qubits != 2 * n:
            raise ValueError("p must have width 2n")
        if z.num_qubits != 1:
            raise ValueError("z must be 1 qubit")

        # Paper Algorithm: for i=0..n-2: ADD/NOP + ROTATE
        for i in range(n - 1):
            self._carry_bridge(z=z, p=p, n=(2 * n - 1), ctrl=condition)
            self._controlled_ttk_add(
                sel=b[i],
                multiplicand=a,
                target_window=p[n - 1 : 2 * n - 1],
                carry=z,
                ctrl=condition,
            )
            self._carry_bridge(z=z, p=p, n=(2 * n - 1), ctrl=condition)
            self._rotate_right(reg=p, steps=1, ctrl=condition)

        # Final: i=n-1 (no rotation)
        self._carry_bridge(z=z, p=p, n=(2 * n - 1), ctrl=condition)
        self._controlled_ttk_add(
            sel=b[n - 1],
            multiplicand=a,
            target_window=p[n - 1 : 2 * n - 1],
            carry=z,
            ctrl=condition,
        )
        self._carry_bridge(z=z, p=p, n=(2 * n - 1), ctrl=condition)


def read_product(p: QUInt) -> int:
    """Read the product register as a Python integer."""
    return int(p.read())


__all__ = [
    "JHHAMultiplier",
    "read_product",
]