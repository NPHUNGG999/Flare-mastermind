"""
============================================
 FLARE AI - Bot Package
============================================
Core bot functionality
============================================
"""

from .client import FlareBot
from .events import setup_events

__all__ = ["FlareBot", "setup_events"]
