import sys
from datetime import date
from pathlib import Path
import unittest

_root = Path(__file__).resolve().parent.parent
for _p in (str(_root / "src"), str(_root)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config.settings import get_settings, Settings
from config.constants import OrderStatus, ReturnReason, SentimentLabel, CustomerSegment
from ecommerce_iq.utils.formatting import format_currency, format_percentage, format_delta_display
from ecommerce_iq.utils.validators import validate_date_range, clamp_limit, sanitize_identifier


class TestConfigAndUtils(unittest.TestCase):
    def test_settings_initialization(self):
        """Verify that application settings load with required default parameters."""
        settings = get_settings()
        self.assertEqual(settings.app_name, "E-Commerce IQ")
        self.assertIsNotNone(settings.database_url)
        self.assertIn("ecommerce_iq", settings.database_url)
        self.assertTrue(settings.project_root.exists())

    def test_constants_definitions(self):
        """Verify business constants and enumerations are correctly declared."""
        self.assertEqual(OrderStatus.COMPLETED.value, "completed")
        self.assertEqual(ReturnReason.DEFECTIVE.value, "Defective/Damaged")
        self.assertEqual(SentimentLabel.POSITIVE.value, "positive")
        self.assertEqual(CustomerSegment.VIP.value, "VIP High Value")

    def test_formatting_utilities(self):
        """Verify formatting utility functions format numbers properly."""
        self.assertEqual(format_currency(12500.5), "$12,500.50")
        self.assertEqual(format_percentage(12.345, include_sign=True), "+12.3%")
        self.assertEqual(format_percentage(-5.2, include_sign=True), "-5.2%")
        self.assertEqual(format_delta_display(4.5), "+4.5% vs previous period")

    def test_validators(self):
        """Verify validation helper routines."""
        # Valid date range
        valid, err = validate_date_range(date(2025, 1, 1), date(2025, 1, 31))
        self.assertTrue(valid)
        self.assertIsNone(err)

        # Invalid date range
        invalid, err = validate_date_range(date(2025, 2, 1), date(2025, 1, 1))
        self.assertFalse(invalid)
        self.assertIn("cannot be after", err or "")

        # Limit clamping
        self.assertEqual(clamp_limit(5), 5)
        self.assertEqual(clamp_limit(200, max_limit=100), 100)
        self.assertEqual(clamp_limit(-1, default=10), 10)

        # Identifier sanitization
        self.assertEqual(sanitize_identifier("orders_table_1"), "orders_table_1")
        self.assertEqual(sanitize_identifier("drop table;--"), "droptable")


if __name__ == "__main__":
    unittest.main()
