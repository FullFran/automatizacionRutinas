"""
Webhook de Telegram.
"""

import logging

from fastapi import APIRouter, Depends, Request

from api.dependencies import get_telegram_bot, get_telegram_handler
from infrastructure.telegram.bot import TelegramBot
from infrastructure.telegram.handlers import TelegramHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(
    request: Request, handler: TelegramHandler = Depends(get_telegram_handler)
):
    """
    Webhook para recibir updates de Telegram.

    Procesa mensajes, comandos y callbacks del bot.
    """
    try:
        data = await request.json()
        result = handler.handle_update(data)
        return result
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"status": "error"}


@router.get("/set-webhook")
async def set_webhook(bot: TelegramBot = Depends(get_telegram_bot)):
    """
    Configura el webhook de Telegram.

    Llamar este endpoint para registrar la URL del webhook.
    """
    return bot.set_webhook()
