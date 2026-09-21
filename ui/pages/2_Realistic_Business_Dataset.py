"""
Streamlit Multi-Page: 2. Realistic Business Dataset.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ecommerce_iq.database.connection import DatabaseManager
from ui.pages.dataset_view import render_dataset_page


def main() -> None:
    db = DatabaseManager()
    render_dataset_page(db)


if __name__ == "__main__":
    main()
