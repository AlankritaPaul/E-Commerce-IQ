"""
Interactive E-Commerce IQ Copilot CLI.

Allows business operators to ask plain-English questions directly from Python
and receive verified, deterministic data, executed SQL, and executive briefings.
"""

import sys
from pathlib import Path

# Force UTF-8 stream handling for Windows PowerShell / CMD
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root and src/ to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ecommerce_iq.database.connection import DatabaseManager
from ecommerce_iq.ai.query_engine import NaturalLanguageQueryEngine


def print_banner() -> None:
    print("=" * 72)
    print("       [E-COMMERCE IQ] CONVERSATIONAL AI & SQL COPILOT          ")
    print("=" * 72)
    print("Ask any business question in plain English (e.g., revenue, products,")
    print("customer behavior, returns, or sentiment).")
    print("Type 'exit' or 'quit' to close the session.\n")
    print("Sample Questions to try:")
    print("  1. What was our total sales revenue and order volume?")
    print("  2. What are our top 5 best selling products?")
    print("  3. Which products have the highest return rate?")
    print("  4. What is our revenue breakdown by category?")
    print("  5. How many customers are repeat buyers?")
    print("-" * 72)


def run_cli() -> None:
    print_banner()

    try:
        db = DatabaseManager()
        copilot = NaturalLanguageQueryEngine(db_manager=db)
        print("Connected to database: OK [data/ecommerce_iq.db]\n")
    except Exception as e:
        print(f"Error initializing Copilot database engine: {e}")
        return

    while True:
        try:
            query = input("\nYour Question > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break

        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            print("\nExiting E-Commerce IQ Copilot. Goodbye!")
            break

        print("\nAnalyzing question and running deterministic SQL query...")
        response = copilot.ask(query)

        if not response.is_safe:
            print("\n[SECURITY GUARDRAIL INTERCEPTION]")
            print(f"Status: BLOCKED ({response.execution_time_ms:.1f}ms)")
            print(f"Reason: {response.error_message}")
            continue

        print(f"\n[VERIFIED SAFE SQL] ({response.execution_time_ms:.1f}ms)")
        print(f"Query: {response.generated_sql}")

        print("\n[EXECUTIVE ANSWER]")
        print(response.executive_summary)

        if response.data and len(response.data) > 0:
            print("\n[DATA PREVIEW] (First 5 records):")
            for idx, row in enumerate(response.data[:5], 1):
                print(f"  {idx}. {row}")


if __name__ == "__main__":
    run_cli()
