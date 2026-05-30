import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_ttk import TTKAdd
from benchmark_check import BenchmarkResults

class BenchmarkTTKPlots(BenchmarkResults):
    def __init__(self):
        self.adder = TTKAdd()
        self.adder_name = "ttk"

if __name__ == "__main__":
    bwp = BenchmarkTTKPlots()
    bwp.create_individual_plots(a=2, b=1, c=2, d=-1, in_place=True)