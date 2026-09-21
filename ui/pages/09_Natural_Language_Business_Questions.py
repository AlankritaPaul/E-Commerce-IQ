"""
Streamlit Multi-Page: 9. Natural-language business questions.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine
from ui.views.copilot_view import render_copilot_page


def main() -> None:
    db = DatabaseManager()
    engine = NaturalLanguageQueryEngine(db_manager=db)
    render_copilot_page(engine)


if __name__ == "__main__":
    main()
