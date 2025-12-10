"""
Cliente de Telegram Bot API.

Funciones para enviar mensajes y manejar la API de Telegram.
"""

import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class TelegramBot:
    """Cliente para la API de Telegram Bot."""

    def __init__(self, token: str, webhook_url: str):
        self.token = token
        self.webhook_url = webhook_url
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(
        self, chat_id: int, text: str, parse_mode: str = "Markdown"
    ) -> Dict[str, Any]:
        """Envía un mensaje de texto."""
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        response = requests.post(url, json=payload)
        return response.json()

    def send_typing_action(self, chat_id: int) -> None:
        """Envía indicador de 'escribiendo...'."""
        url = f"{self.base_url}/sendChatAction"
        requests.post(url, json={"chat_id": chat_id, "action": "typing"})

    def send_message_with_keyboard(
        self, chat_id: int, text: str, keyboard: List[List[Dict[str, str]]]
    ) -> Dict[str, Any]:
        """Envía mensaje con teclado inline."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": keyboard},
        }
        response = requests.post(url, json=payload)
        return response.json()

    def answer_callback(
        self, callback_id: str, text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Responde a un callback query."""
        url = f"{self.base_url}/answerCallbackQuery"
        payload = {"callback_query_id": callback_id}
        if text:
            payload["text"] = text
        response = requests.post(url, json=payload)
        return response.json()

    def edit_message_markup(
        self, chat_id: int, message_id: int, keyboard: Optional[List] = None
    ) -> Dict[str, Any]:
        """Edita el teclado de un mensaje."""
        url = f"{self.base_url}/editMessageReplyMarkup"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": {"inline_keyboard": keyboard or []},
        }
        response = requests.post(url, json=payload)
        return response.json()

    def set_webhook(self) -> Dict[str, Any]:
        """Configura el webhook."""
        url = f"{self.base_url}/setWebhook?url={self.webhook_url}"
        response = requests.get(url)
        return response.json()
