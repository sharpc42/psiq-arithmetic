import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_ttk import TTKAdd
from src.qbk_ttkmult import TTKAddMultiply
from tests.add_results import AddResultsInPlace
from tests.add_consistency import ConsistencyResultsInPlace
from tests.mult_results import AddMultiplyResults

# can potentially add TTK-unique tests to both
class TestTTKAddResults(AddResultsInPlace):
    adder = TTKAdd()
class TestWangAddConsistency(ConsistencyResultsInPlace):
    adder = TTKAdd()
class TestTTKMultiplyResults(AddMultiplyResults):
    multiplier = TTKAddMultiply()