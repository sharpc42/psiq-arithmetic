from src.qbk_wangrca import WangAdd
from tests.add_results import AddResultsOutOfPlace
from tests.add_consistency import ConsistencyResultsOutOfPlace

# can potentially add Wang-unique tests to both
class TestWangAddResults(AddResultsOutOfPlace):
    adder = WangAdd()
class TestWangAddConsistency(ConsistencyResultsOutOfPlace):
    adder = WangAdd()