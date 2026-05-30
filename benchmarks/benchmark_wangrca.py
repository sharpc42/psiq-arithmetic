import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_wangrca import WangAdd
from benchmark_check import BenchmarkResults

class BenchmarkWangPlots(BenchmarkResults):
    def __init__(self):
        self.adder = WangAdd()
        self.adder_name = "wang"

if __name__ == "__main__":
    bwp = BenchmarkWangPlots()
    bwp.create_individual_plots(a=3, b=1, c=1, d=0)