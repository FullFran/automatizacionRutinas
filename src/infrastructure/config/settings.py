"""
Configuración de la aplicación usando Pydantic Settings.

Carga variables de entorno desde .env y las valida con tipos.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación.

    Todas las variables de entorno se cargan aquí y se validan.
    Usa `settings.variable` para acceder a los valores.
    """

    # ─────────────────────────────────────────────────────────
    # Telegram
    # ─────────────────────────────────────────────────────────
    telegram_token: str = Field(
        ..., alias="TELEGRAM_BOT_TOKEN", description="Token del bot de Telegram"
    )
    webhook_url: str = Field(..., description="URL del webhook para Telegram")

    # ─────────────────────────────────────────────────────────
    # Gemini AI
    # ─────────────────────────────────────────────────────────
    gemini_api_key: str = Field(..., description="API Key de Google Gemini")
    gemini_model: str = Field(
        default="gemini-2.5-flash", description="Modelo de Gemini a usar"
    )

    # ─────────────────────────────────────────────────────────
    # Google Services
    # ─────────────────────────────────────────────────────────
    google_credentials: str = Field(
        ..., description="JSON de credenciales de service account"
    )
    template_presentation_id: str = Field(
        ..., description="ID de la plantilla de Google Slides"
    )
    routine_layout_id: str = Field(..., description="ID del layout para rutinas")

    # ─────────────────────────────────────────────────────────
    # Aplicación
    # ─────────────────────────────────────────────────────────
    app_name: str = Field(default="Routine Bot", description="Nombre de la app")
    debug: bool = Field(default=False, description="Modo debug")
    log_level: str = Field(default="INFO", description="Nivel de logging")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Devuelve la instancia de configuración (singleton).

    Usa @lru_cache para crear una única instancia.
    """
    return Settings()


# Instancia global para importar fácilmente
settings = get_settings()
