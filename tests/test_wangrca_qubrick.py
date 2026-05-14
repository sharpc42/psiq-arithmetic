import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_wangrca import WangAdd
from tests.add_results import AddResultsOutOfPlace
from tests.add_consistency import ConsistencyResultsOutOfPlace

# can potentially add Wang-unique tests to both
class TestWangAddResults(AddResultsOutOfPlace):
    adder = WangAdd()
class TestWangAddConsistency(ConsistencyResultsOutOfPlace):
    adder = WangAdd()