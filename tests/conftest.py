"""
Pytest Fixtures and Global Test Configuration.
"""

import sys
from pathlib import Path
import pytest

# Ensure project root and src/ are in sys.path
project_root = Path(__file__).resolve().parent.parent
src_dir = project_root / "src"

for directory in (project_root, src_dir):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))


@pytest.fixture
def mock_app_settings():
    """Return an instance of test application settings."""
    from config.settings import Settings
    return Settings()
