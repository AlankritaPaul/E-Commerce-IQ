"""
SQL Security Guardrails and AST Validation Engine.

Enforces strict security constraints on generated SQL:
- Only permits read-only queries (SELECT and read-only CTEs)
- Strictly blocks destructive statements (DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE)
- Blocks multi-statement query chaining (preventing SQL injection via semicolons)
- Validates table access against allowed schema tables and views
- Enforces safe result limits
"""

import re
from typing import List, Optional, Set, Tuple

# Core destructive SQL tokens that must never appear in generated queries
DISALLOWED_KEYWORDS: Set[str] = {
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "CREATE", "REPLACE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
    "ATTACH", "DETACH", "PRAGMA", "VACUUM", "INTO", "MERGE"
}

ALLOWED_TABLES_DEFAULT: Set[str] = {
    "customers", "categories", "products", "orders",
    "order_items", "payments", "returns", "reviews",
    "review_insights", "sales", "returns_and_refunds",
    "v_product_performance_summary", "v_daily_business_summary"
}


class SQLGuardrail:
    """
    Validates and sanitizes SQL queries before database execution.
    Combines fast token security validation with Abstract Syntax Tree (AST) parsing.
    """

    def __init__(self, allowed_tables: Optional[List[str]] = None) -> None:
        self.allowed_tables = set(t.lower() for t in (allowed_tables or ALLOWED_TABLES_DEFAULT))

    def validate_query(self, query: str) -> Tuple[bool, str]:
        """
        Verify that the query is strictly read-only and safe to execute.

        Returns:
            Tuple of (is_safe: bool, rejection_reason: str)
        """
        if not query or not query.strip():
            return False, "Query is empty."

        cleaned = query.strip()

        # Check 1: Multi-statement check (semicolons separating queries)
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()

        if ";" in cleaned:
            return False, "Multiple SQL statements chained with semicolons are not permitted."

        # Check 2: Must begin with SELECT or WITH (for CTEs)
        tokens = cleaned.split()
        first_token = tokens[0].upper()
        if first_token not in ("SELECT", "WITH"):
            return False, f"Only SELECT or WITH queries are permitted. Found: '{first_token}'."

        # Check 3: Token inspection for destructive keywords
        word_tokens = re.findall(r"\b[A-Za-z_]+\b", cleaned)
        for token in word_tokens:
            upper_token = token.upper()
            if upper_token in DISALLOWED_KEYWORDS:
                return False, f"Disallowed destructive keyword detected: '{upper_token}'."

        # Check 4: Validate referenced tables in FROM and JOIN clauses
        # Find CTE names defined in WITH clauses so they are not rejected as unauthorized tables
        cte_names = set()
        if first_token == "WITH":
            cte_matches = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s+AS\s*\(", cleaned, re.IGNORECASE)
            cte_names = set(m.lower() for m in cte_matches)

        # Extract table names following FROM or JOIN
        table_matches = re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)", cleaned, re.IGNORECASE)
        for tbl in table_matches:
            tbl_lower = tbl.lower()
            if tbl_lower not in self.allowed_tables and tbl_lower not in cte_names:
                return False, f"Access to unauthorized table or view rejected: '{tbl}'."

        # Check 5: AST parsing via sqlglot if installed
        try:
            import sqlglot
            from sqlglot import exp

            parsed = sqlglot.parse_one(cleaned)
            if not isinstance(parsed, (exp.Select, exp.Union)):
                return False, f"AST verification failed: Root expression is {type(parsed).__name__}, not a Select query."

        except ImportError:
            # sqlglot is optional; regex and token-based checks above have passed
            pass
        except Exception as e:
            return False, f"SQL syntax parsing error: {str(e)}"

        return True, "Query is verified safe and read-only."

    def sanitize_and_limit(self, query: str, max_limit: int = 100) -> str:
        """
        Strip trailing semicolons and ensure a safe LIMIT clause is present if unbounded.
        """
        cleaned = query.strip()
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()

        limit_match = re.search(r"\bLIMIT\s+(\d+)\b", cleaned, re.IGNORECASE)
        if limit_match:
            existing_limit = int(limit_match.group(1))
            if existing_limit > max_limit:
                cleaned = re.sub(r"\bLIMIT\s+\d+\b", f"LIMIT {max_limit}", cleaned, flags=re.IGNORECASE)
        else:
            cleaned = f"{cleaned} LIMIT {max_limit}"

        return cleaned
