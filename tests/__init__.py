"""
Test suite package for E-Commerce IQ.
"""

import sys
from pathlib import Path

# Add project root and src directory to sys.path so tests run seamlessly
_root = Path(__file__).resolve().parent.parent
_src = _root / "src"

for _p in (str(_root), str(_src)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
