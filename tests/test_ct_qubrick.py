import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_ct import CTAdd
from tests.add_results import AddResultsOutOfPlace
from tests.add_consistency import ConsistencyAddOutOfPlace

# CTAdd is addition-only (no subtract_condition), so it uses the add and
# add-consistency bases but not the subtraction ones.
class TestCTAddResults(AddResultsOutOfPlace):
    adder = CTAdd()
class TestCTConsistency(ConsistencyAddOutOfPlace):
    adder = CTAdd()
