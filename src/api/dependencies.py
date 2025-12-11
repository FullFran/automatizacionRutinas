"""
Inyección de dependencias para FastAPI.

Configura y proporciona las instancias de los servicios.
"""

import logging
from functools import lru_cache

from application.use_cases.generate_presentation import GeneratePresentationUseCase
from application.use_cases.parse_routine import ParseRoutineUseCase
from infrastructure.ai.gemini_parser import GeminiParser
from infrastructure.chatwoot import ChatwootLogger, NullChatwootLogger
from infrastructure.chatwoot.interface import ChatwootLoggerInterface
from infrastructure.config.settings import settings
from infrastructure.google.slides_generator import GoogleSlidesGenerator
from infrastructure.telegram.bot import TelegramBot
from infrastructure.telegram.handlers import TelegramHandler

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
# Singletons (se crean una vez y se reutilizan)
# ─────────────────────────────────────────────────────────


@lru_cache()
def get_gemini_parser() -> GeminiParser:
    """Devuelve instancia singleton del parser."""
    return GeminiParser(api_key=settings.gemini_api_key, model=settings.gemini_model)


@lru_cache()
def get_slides_generator() -> GoogleSlidesGenerator:
    """Devuelve instancia singleton del generador de slides."""
    return GoogleSlidesGenerator(
        credentials_json=settings.google_credentials,
        template_id=settings.template_presentation_id,
        layout_id=settings.routine_layout_id,
    )


@lru_cache()
def get_telegram_bot() -> TelegramBot:
    """Devuelve instancia singleton del bot de Telegram."""
    return TelegramBot(token=settings.telegram_token, webhook_url=settings.webhook_url)


@lru_cache()
def get_chatwoot_logger() -> ChatwootLoggerInterface:
    """
    Devuelve logger de Chatwoot si está configurado, o NullChatwootLogger si no.

    Las variables de entorno requeridas son:
    - CHATWOOT_BASE_URL
    - CHATWOOT_ACCOUNT_ID
    - CHATWOOT_INBOX_ID
    - CHATWOOT_API_ACCESS_TOKEN
    """
    if settings.chatwoot_enabled:
        logger.info("✅ Chatwoot logging habilitado")
        return ChatwootLogger(
            base_url=settings.chatwoot_base_url,
            account_id=settings.chatwoot_account_id,
            inbox_id=settings.chatwoot_inbox_id,
            api_token=settings.chatwoot_api_token,
        )
    logger.info("ℹ️ Chatwoot logging deshabilitado (variables no configuradas)")
    return NullChatwootLogger()


# ─────────────────────────────────────────────────────────
# Use Cases (nuevas instancias, pero con dependencias singleton)
# ─────────────────────────────────────────────────────────


def get_parse_routine_use_case() -> ParseRoutineUseCase:
    """Devuelve caso de uso para parsear rutinas."""
    return ParseRoutineUseCase(parser=get_gemini_parser())


def get_generate_presentation_use_case() -> GeneratePresentationUseCase:
    """Devuelve caso de uso para generar presentaciones."""
    return GeneratePresentationUseCase(generator=get_slides_generator())


# ─────────────────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────────────────


@lru_cache()
def get_telegram_handler() -> TelegramHandler:
    """Devuelve handler de Telegram con todas las dependencias."""
    return TelegramHandler(
        bot=get_telegram_bot(),
        parse_use_case=get_parse_routine_use_case(),
        generate_use_case=get_generate_presentation_use_case(),
        chatwoot_logger=get_chatwoot_logger(),
    )
