"""
Handlers de Telegram.

Maneja los diferentes tipos de mensajes y callbacks.
"""

import logging
from typing import Any, Dict, Optional

from application.dtos.routine_dto import RoutineDTO
from application.use_cases.generate_presentation import GeneratePresentationUseCase
from application.use_cases.parse_routine import ParseRoutineUseCase
from domain.exceptions import DomainException
from infrastructure.chatwoot.interface import ChatwootLoggerInterface
from infrastructure.telegram.bot import TelegramBot

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
# Mensajes
# ─────────────────────────────────────────────────────────

MSG_WELCOME = """👋 *¡Hola!* Soy tu asistente de rutinas de entrenamiento.

📝 *Cómo usarme:*
1. Envíame tu rutina de ejercicios
2. Revisa el preview de ejercicios detectados
3. Confirma para generar tu presentación

💡 *Comandos:*
/ayuda - Ver instrucciones detalladas
/cancelar - Cancelar rutina pendiente
/estado - Ver tu estado actual"""

MSG_HELP = """📖 *Instrucciones de Uso*

*Formato de rutina:*
Envía tus ejercicios en texto. Ejemplo:

```
Pull ups 4 series de 10 reps
Front lever touch 3 series
Muscle ups 5,6,7,8 reps
```

*Comandos:*
/start - Reiniciar
/cancelar - Cancelar rutina pendiente
/estado - Ver estado actual"""

MSG_NO_PENDING = "📭 No tienes ninguna rutina pendiente."
MSG_CANCELLED = "🚫 Rutina cancelada. Puedes enviarme una nueva cuando quieras."
MSG_PROCESSING = "⏳ Procesando tu rutina..."
MSG_CREATING = "⏳ Creando presentación en Google Slides..."
MSG_ERROR_PARSE = (
    "❌ *No pude procesar la rutina*\n\nVerifica el formato e intenta de nuevo."
)
MSG_ERROR_SLIDES = "❌ Error al crear la presentación. Intenta de nuevo más tarde."


class TelegramHandler:
    """Maneja mensajes y callbacks de Telegram."""

    def __init__(
        self,
        bot: TelegramBot,
        parse_use_case: ParseRoutineUseCase,
        generate_use_case: GeneratePresentationUseCase,
        chatwoot_logger: Optional[ChatwootLoggerInterface] = None,
    ):
        self.bot = bot
        self.parse_use_case = parse_use_case
        self.generate_use_case = generate_use_case
        self.chatwoot_logger = chatwoot_logger
        self.user_states: Dict[int, RoutineDTO] = {}

    def handle_update(self, update: Dict[str, Any]) -> Dict[str, str]:
        """Punto de entrada para procesar un update de Telegram."""

        if "callback_query" in update:
            return self._handle_callback(update["callback_query"])

        if "message" in update:
            return self._handle_message(update["message"])

        return {"status": "ok"}

    def _handle_message(self, message: Dict[str, Any]) -> Dict[str, str]:
        """Procesa un mensaje de texto."""
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()
        user_name = message.get("from", {}).get("first_name", "Usuario")

        if not text:
            return {"status": "empty"}

        # Log incoming message to Chatwoot
        self._log_incoming(chat_id, user_name, text)

        # Comandos
        if text.startswith("/"):
            return self._handle_command(chat_id, text.lower(), user_name)

        # Rutina
        return self._handle_routine(chat_id, text, user_name)

    def _handle_command(
        self, chat_id: int, command: str, user_name: str = "Usuario"
    ) -> Dict[str, str]:
        """Procesa comandos."""

        if command in ["/start", "/inicio"]:
            self.user_states.pop(chat_id, None)
            self._send_and_log(chat_id, MSG_WELCOME)
            return {"status": "welcome"}

        if command in ["/ayuda", "/help"]:
            self._send_and_log(chat_id, MSG_HELP)
            return {"status": "help"}

        if command in ["/cancelar", "/cancel"]:
            if chat_id in self.user_states:
                self.user_states.pop(chat_id)
                self._send_and_log(chat_id, MSG_CANCELLED)
            else:
                self._send_and_log(chat_id, MSG_NO_PENDING)
            return {"status": "cancelled"}

        if command == "/estado":
            if chat_id in self.user_states:
                self._send_and_log(
                    chat_id,
                    "📌 Tienes una rutina pendiente.\nUsa /cancelar para descartarla.",
                )
            else:
                self._send_and_log(chat_id, MSG_NO_PENDING)
            return {"status": "state"}

        return {"status": "unknown_command"}

    def _handle_routine(
        self, chat_id: int, text: str, user_name: str = "Usuario"
    ) -> Dict[str, str]:
        """Procesa texto de rutina."""

        if chat_id in self.user_states:
            self._send_and_log(
                chat_id,
                "⚠️ Ya tienes una rutina pendiente.\nUsa /cancelar para descartarla.",
            )
            return {"status": "pending"}

        self.bot.send_typing_action(chat_id)
        self._send_and_log(chat_id, MSG_PROCESSING)

        try:
            routine = self.parse_use_case.execute(text)
            self.user_states[chat_id] = routine

            preview = self._format_preview(routine)
            self.bot.send_message_with_keyboard(
                chat_id,
                preview,
                [
                    [
                        {"text": "✅ Crear Presentación", "callback_data": "confirm"},
                        {"text": "❌ Cancelar", "callback_data": "cancel"},
                    ]
                ],
            )
            self._log_outgoing(chat_id, preview)
            return {"status": "awaiting"}

        except DomainException as e:
            logger.error(f"Error parsing: {e}")
            self._send_and_log(chat_id, MSG_ERROR_PARSE)
            return {"status": "error"}

    def _handle_callback(self, callback: Dict[str, Any]) -> Dict[str, str]:
        """Procesa callbacks de botones."""
        callback_id = callback.get("id")
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        action = callback.get("data")

        self.bot.answer_callback(callback_id)
        self.bot.edit_message_markup(chat_id, message_id, None)

        if action == "confirm":
            return self._confirm_presentation(chat_id)

        if action == "cancel":
            self.user_states.pop(chat_id, None)
            self._send_and_log(chat_id, MSG_CANCELLED)
            return {"status": "cancelled"}

        return {"status": "unknown_callback"}

    def _confirm_presentation(self, chat_id: int) -> Dict[str, str]:
        """Genera la presentación."""
        if chat_id not in self.user_states:
            self._send_and_log(chat_id, MSG_NO_PENDING)
            return {"status": "no_pending"}

        routine = self.user_states.pop(chat_id)

        self.bot.send_typing_action(chat_id)
        self._send_and_log(chat_id, MSG_CREATING)

        try:
            result = self.generate_use_case.execute(routine)
            success_msg = (
                f"✅ *¡Presentación creada!*\n\n🔗 [Abrir presentación]({result.url})"
            )
            self._send_and_log(chat_id, success_msg)
            return {"status": "success"}

        except DomainException as e:
            logger.error(f"Error generating: {e}")
            self._send_and_log(chat_id, MSG_ERROR_SLIDES)
            return {"status": "error"}

    def _format_preview(self, routine: RoutineDTO) -> str:
        """Formatea el preview de la rutina."""
        lines = ["📋 *Rutina Detectada*\n"]

        for day in routine.days:
            lines.append(f"*Día {day.day_number}* ({day.total_exercises} ejercicios)")
            for ex in day.exercises[:5]:
                lines.append(f"• {ex.name} - {ex.sets}x")
            if day.total_exercises > 5:
                lines.append(f"  _...y {day.total_exercises - 5} más_")
            lines.append("")

        lines.append("¿Generar la presentación?")
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────
    # Chatwoot Logging Helpers
    # ─────────────────────────────────────────────────────────

    def _send_and_log(self, chat_id: int, message: str) -> None:
        """Envía mensaje al usuario y lo loguea en Chatwoot."""
        self.bot.send_message(chat_id, message)
        self._log_outgoing(chat_id, message)

    def _log_incoming(self, chat_id: int, user_name: str, content: str) -> None:
        """Loguea mensaje entrante en Chatwoot si está habilitado."""
        if self.chatwoot_logger:
            self.chatwoot_logger.log_incoming_message(
                source_id=str(chat_id),
                user_name=user_name,
                content=content,
            )

    def _log_outgoing(self, chat_id: int, content: str) -> None:
        """Loguea mensaje saliente en Chatwoot si está habilitado."""
        if self.chatwoot_logger:
            self.chatwoot_logger.log_outgoing_message(
                source_id=str(chat_id),
                content=content,
            )
