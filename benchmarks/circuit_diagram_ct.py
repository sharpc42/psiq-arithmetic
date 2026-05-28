"""Circuit diagram for the CT quantum adder. Saved as PNG.

Run from the repo root:
    python benchmarks/circuit_diagram_ct.py
    python benchmarks/circuit_diagram_ct.py --n 3
"""

import argparse
import os
import sys
import tempfile

import cairosvg

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from psiqworkbench import QPU, QUInt
from psiqworkbench.filter_presets import BIT_DEFAULT
from src.qbk_ct import CTAdd


def draw_ct(n, save_dir=None, dpi=600):
    if save_dir is None:
        save_dir = os.path.dirname(os.path.abspath(__file__))

    # build circuit
    ct = CTAdd()
    qpu = QPU(num_qubits=4 * n + 2, filters=BIT_DEFAULT)
    a = QUInt(n, "a", qpu=qpu)
    b = QUInt(n, "b", qpu=qpu)
    c = QUInt(n, "c", qpu=qpu)
    ct.compute(A=a, B=b, C=c)

    # render: svg -> png
    out = os.path.join(save_dir, f"ct_circuit_n{n}.png")
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
    draw_ct(args.n, dpi=args.dpi)
