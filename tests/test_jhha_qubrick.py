import sys
from pathlib import Path

# Add parent directory to path so imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qbk_jhha import JHHAMultiplier
from tests.mult_results import AddMultiplyControlResults

class TestJHHAMultiplyResults(AddMultiplyControlResults):
    multiplier = JHHAMultiplier()