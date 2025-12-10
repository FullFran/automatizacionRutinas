import requests

from func.config import TELEGRAM_TOKEN, WEBHOOK_URL

# -------------------------
# Funciones básicas
# -------------------------


def send_telegram_message(
    chat_id: int, text: str, parse_mode: str = "Markdown"
) -> dict:
    """Envía un mensaje a un chat de Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    response = requests.post(url, json=payload)
    return response.json()


def send_typing_action(chat_id: int) -> None:
    """Envía indicador de 'escribiendo...' al chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction"
    payload = {"chat_id": chat_id, "action": "typing"}
    requests.post(url, json=payload)


def send_telegram_message_with_inline_keyboard(
    chat_id: int, text: str, inline_keyboard: list
) -> dict:
    """Envía un mensaje con teclado inline."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {"inline_keyboard": inline_keyboard},
    }
    response = requests.post(url, json=payload)
    return response.json()


def answer_callback_query(callback_query_id: str, text: str = None) -> dict:
    """Responde a un callback query (elimina el 'loading' del botón)."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    response = requests.post(url, json=payload)
    return response.json()


def edit_message_text(chat_id: int, message_id: int, text: str) -> dict:
    """Edita un mensaje existente."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    response = requests.post(url, json=payload)
    return response.json()


def edit_message_reply_markup(
    chat_id: int, message_id: int, inline_keyboard: list = None
) -> dict:
    """Edita los botones de un mensaje (o los elimina si inline_keyboard es None)."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageReplyMarkup"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
    }
    if inline_keyboard:
        payload["reply_markup"] = {"inline_keyboard": inline_keyboard}
    else:
        payload["reply_markup"] = {"inline_keyboard": []}
    response = requests.post(url, json=payload)
    return response.json()


# -------------------------
# Webhook
# -------------------------


def set_webhook() -> dict:
    """Configura el webhook de Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    response = requests.get(url)
    return response.json()
