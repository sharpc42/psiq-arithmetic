from src.qbk_wangrca import WangAdd
from tests.add_results import AddResults
from tests.add_consistency import ConsistencyResults

# can potentially add Wang-unique tests to both
class TestWangAddResults(AddResults):
    adder = WangAdd()
class TestWangAddConsistency(ConsistencyResults):
    adder = WangAdd()