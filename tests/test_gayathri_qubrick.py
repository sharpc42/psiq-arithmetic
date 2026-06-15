import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_gayathri import GayathriAdd
from tests.add_results import AddResultsOutOfPlace
from tests.add_consistency import ConsistencyAddOutOfPlace

# GayathriAdd is addition-only (no subtract_condition), so it uses the add and
# add-consistency bases but not the subtraction ones.
class TestGayathriAddResults(AddResultsOutOfPlace):
    adder = GayathriAdd()
class TestGayathriConsistency(ConsistencyAddOutOfPlace):
    adder = GayathriAdd()
