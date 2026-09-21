"""
Streamlit Multi-Page: 5. Customer Analysis.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.ai.interpretation import AnalyticsInterpreter
from ui.views.customers_view import render_customers_page


def main() -> None:
    db = DatabaseManager()
    interpreter = AnalyticsInterpreter()
    render_customers_page(db, interpreter)


if __name__ == "__main__":
    main()
