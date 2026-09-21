"""
E-Commerce IQ - Streamlit Cloud & Root Application Entrypoint.

Delegates execution to ui.app.main() with automated path resolution
and database initialization for seamless 1-click cloud deployment.
"""

import sys
from pathlib import Path

# Add project root and src/ to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ui.app import main

if __name__ == "__main__":
    main()
