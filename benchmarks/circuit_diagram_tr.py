"""Circuit diagram for the TR quantum adder. Saved as PNG.

Run from the repo root:
    python benchmarks/circuit_diagram_tr.py
    python benchmarks/circuit_diagram_tr.py --n 3
"""

import argparse
import os
import sys
import tempfile

import cairosvg

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from psiqworkbench import QPU, QUInt
from psiqworkbench.filter_presets import BIT_DEFAULT
from src.qbk_tr import TRAdd


def draw_tr(n, save_dir=None, dpi=600):
    if save_dir is None:
        save_dir = os.path.dirname(os.path.abspath(__file__))

    # build circuit
    tr = TRAdd()
    qpu = QPU(num_qubits=2 * n + 2, filters=BIT_DEFAULT)
    lhs = QUInt(n, "lhs", qpu=qpu)
    rhs = QUInt(n, "rhs", qpu=qpu)
    tr.compute(lhs=lhs, rhs=rhs)

    # render: svg -> png
    out = os.path.join(save_dir, f"tr_circuit_n{n}.png")
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
        svg = tmp.name
    try:
        qpu.draw(filename=svg, show_qubricks=False)
        cairosvg.svg2png(url=svg, write_to=out, dpi=dpi)
    finally:
        os.unlink(svg)

    print(f"  saved  {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=2)
    parser.add_argument("--dpi", type=int, default=600)
    args = parser.parse_args()
    draw_tr(args.n, dpi=args.dpi)
