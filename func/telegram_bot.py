import requests
from func.config import TELEGRAM_TOKEN, WEBHOOK_URL

def send_telegram_message(chat_id: int, text: str) -> None:
    """
    Envía un mensaje a un chat de Telegram usando la API.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def set_webhook() -> dict:
    """
    Configura el webhook de Telegram.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    response = requests.get(url)
    return response.json()

def send_telegram_message_with_inline_keyboard(chat_id, text, inline_keyboard):
    """
    Envía un mensaje con un teclado en línea en Telegram.
    
    :param chat_id: ID del chat de Telegram
    :param text: Texto del mensaje
    :param inline_keyboard: Lista de listas con los botones del teclado en línea
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": inline_keyboard
        }
    }
    response = requests.post(url, json=payload)
    return response.json()