"""
Interface para logging de mensajes a Chatwoot.

Define el contrato que implementan tanto el logger real como el null logger.
"""

from abc import ABC, abstractmethod


class ChatwootLoggerInterface(ABC):
    """Interface para logging de mensajes a Chatwoot."""

    @abstractmethod
    def log_incoming_message(self, source_id: str, user_name: str, content: str) -> None:
        """Registra un mensaje entrante del usuario."""
        pass

    @abstractmethod
    def log_outgoing_message(self, source_id: str, content: str) -> None:
        """Registra un mensaje saliente del bot."""
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """Indica si el logging está habilitado."""
        pass
