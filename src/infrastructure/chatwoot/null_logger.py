"""
Null Object implementation for Chatwoot logging.

Used when Chatwoot is not configured - all methods are no-ops.
"""

from .interface import ChatwootLoggerInterface


class NullChatwootLogger(ChatwootLoggerInterface):
    """Logger que no hace nada. Usado cuando Chatwoot no está configurado."""

    def is_enabled(self) -> bool:
        return False

    def log_incoming_message(
        self, source_id: str, user_name: str, content: str
    ) -> None:
        pass

    def log_outgoing_message(self, source_id: str, content: str) -> None:
        pass
