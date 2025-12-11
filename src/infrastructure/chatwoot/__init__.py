"""
Chatwoot integration for optional conversation logging.

This module provides:
- ChatwootLoggerInterface: Abstract interface
- ChatwootLogger: Real implementation that sends to Chatwoot API
- NullChatwootLogger: No-op implementation when Chatwoot is not configured
"""

from .interface import ChatwootLoggerInterface
from .logger import ChatwootLogger
from .null_logger import NullChatwootLogger

__all__ = ["ChatwootLoggerInterface", "ChatwootLogger", "NullChatwootLogger"]
