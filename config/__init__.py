"""
Configuration package for E-Commerce IQ.
Provides environment-aware settings and application parameters.
"""

from config.settings import get_settings, Settings

__all__ = ["get_settings", "Settings"]
