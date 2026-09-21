"""
Streamlit Multi-Page: Natural-Language AI Query Copilot.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ecommerce_iq.database.connection import DatabaseManager
from ui.pages.copilot_view import render_copilot_page


def main() -> None:
    db = DatabaseManager()
    render_copilot_page(db)


if __name__ == "__main__":
    main()
