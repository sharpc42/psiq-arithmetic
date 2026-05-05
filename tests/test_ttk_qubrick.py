from src.qbk_ttk import TTKAdd
from tests.add_results import AddResultsInPlace
from tests.add_consistency import ConsistencyResultsInPlace

# can potentially add TTK-unique tests to both
class TestTTKAddResults(AddResultsInPlace):
    adder = TTKAdd()
class TestWangAddConsistency(ConsistencyResultsInPlace):
    adder = TTKAdd()