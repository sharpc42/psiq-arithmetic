from wangrca_qubrick import WangAdd
from add_results import AddResults
from add_consistency import ConsistencyResults

# can potentially add Wang-unique tests to both
class TestWangAddResults(AddResults):
    adder = WangAdd()
class TestWangAddConsistency(ConsistencyResults):
    adder = WangAdd()