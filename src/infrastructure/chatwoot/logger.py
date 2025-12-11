"""
Implementación de logging a Chatwoot.

Envía mensajes entrantes y salientes a la API de Chatwoot.
"""

import logging
from typing import Dict

import httpx

from .interface import ChatwootLoggerInterface

logger = logging.getLogger(__name__)


class ChatwootLogger(ChatwootLoggerInterface):
    """Implementación de logging a Chatwoot."""

    def __init__(
        self,
        base_url: str,
        account_id: str,
        inbox_id: str,
        api_token: str,
    ):
        self.base_url = base_url.rstrip("/")
        self.account_id = account_id
        self.inbox_id = inbox_id
        self.api_token = api_token
        self._conversations: Dict[str, int] = {}  # source_id -> conversation_id
        self._contacts: Dict[str, int] = {}  # source_id -> contact_id

    def is_enabled(self) -> bool:
        return True

    def log_incoming_message(
        self, source_id: str, user_name: str, content: str
    ) -> None:
        """Registra mensaje entrante."""
        try:
            conv_id = self._get_or_create_conversation(source_id, user_name)
            self._create_message(conv_id, content, "incoming")
        except Exception as e:
            logger.warning(f"Error logging to Chatwoot: {e}")

    def log_outgoing_message(self, source_id: str, content: str) -> None:
        """Registra mensaje saliente."""
        try:
            conv_id = self._conversations.get(source_id)
            if conv_id:
                self._create_message(conv_id, content, "outgoing")
        except Exception as e:
            logger.warning(f"Error logging to Chatwoot: {e}")

    def _get_or_create_conversation(self, source_id: str, user_name: str) -> int:
        """Obtiene o crea una conversación para el source_id."""
        if source_id in self._conversations:
            return self._conversations[source_id]

        contact_id = self._get_or_create_contact(source_id, user_name)

        # Crear conversación
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations"
        response = httpx.post(
            url,
            headers=self._headers(),
            json={
                "source_id": source_id,
                "inbox_id": int(self.inbox_id),
                "contact_id": contact_id,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        conv_id = response.json()["id"]
        self._conversations[source_id] = conv_id
        return conv_id

    def _get_or_create_contact(self, source_id: str, user_name: str) -> int:
        """Obtiene o crea un contacto para el source_id."""
        if source_id in self._contacts:
            return self._contacts[source_id]

        identifier = f"telegram_{source_id}"

        # Primero intentar buscar si ya existe el contacto
        search_url = (
            f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts/search"
        )
        try:
            search_resp = httpx.get(
                search_url,
                headers=self._headers(),
                params={"q": identifier},
                timeout=10.0,
            )
            if search_resp.status_code == 200:
                contacts = search_resp.json().get("payload", [])
                for contact in contacts:
                    if contact.get("identifier") == identifier:
                        contact_id = contact["id"]
                        self._contacts[source_id] = contact_id
                        logger.debug(f"Contacto existente encontrado: {contact_id}")
                        return contact_id
        except Exception as e:
            logger.debug(f"Error buscando contacto: {e}")

        # Crear nuevo contacto (sin inbox_id)
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/contacts"
        response = httpx.post(
            url,
            headers=self._headers(),
            json={
                "name": user_name,
                "identifier": identifier,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        # La respuesta puede variar según la versión de Chatwoot
        contact_id = data.get("id") or data.get("payload", {}).get("contact", {}).get(
            "id"
        )
        if contact_id:
            self._contacts[source_id] = contact_id
            logger.debug(f"Contacto creado: {contact_id}")
        return contact_id

    def _create_message(self, conv_id: int, content: str, msg_type: str) -> None:
        """Crea un mensaje en la conversación."""
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conv_id}/messages"
        httpx.post(
            url,
            headers=self._headers(),
            json={
                "content": content,
                "message_type": msg_type,
                "private": False,
            },
            timeout=10.0,
        )

    def _headers(self) -> dict:
        """Headers comunes para las peticiones."""
        return {
            "Content-Type": "application/json",
            "api_access_token": self.api_token,
        }
