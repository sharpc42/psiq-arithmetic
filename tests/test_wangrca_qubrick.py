import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_wangrca import WangAdd
from tests.add_results import AddResultsOutOfPlace, SubtractResultsOutOfPlace
from tests.add_consistency import ConsistencyAddOutOfPlace, ConsistencySubOutOfPlace

# can potentially add Wang-unique tests to both
class TestWangAddResults(AddResultsOutOfPlace):
    adder = WangAdd()
class TestWangSubtractResults(SubtractResultsOutOfPlace):
    adder = WangAdd()
class TestWangConsistency(ConsistencyAddOutOfPlace, ConsistencySubOutOfPlace):
    adder = WangAdd()