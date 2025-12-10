"""
Bot de Telegram para automatización de rutinas de entrenamiento.
Genera presentaciones de Google Slides a partir de rutinas enviadas por el usuario.
"""

import logging

from fastapi import FastAPI, Request

from func.google_slides import create_presentation
from func.routine_parser import parse_routine
from func.telegram_bot import (
    answer_callback_query,
    edit_message_reply_markup,
    send_telegram_message,
    send_telegram_message_with_inline_keyboard,
    send_typing_action,
    set_webhook,
)

# -------------------------
# Configuración
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Estado de usuarios (chat_id -> datos)
user_states = {}

# -------------------------
# Mensajes
# -------------------------
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

*El bot detectará:*
• Nombre del ejercicio
• Número de series
• Repeticiones por serie

Una vez procesado, podrás revisar el preview y confirmar para generar la presentación en Google Slides.

*Comandos:*
/start - Reiniciar
/cancelar - Cancelar rutina pendiente
/estado - Ver estado actual"""

MSG_NO_PENDING = "📭 No tienes ninguna rutina pendiente."

MSG_CANCELLED = "🚫 Rutina cancelada. Puedes enviarme una nueva cuando quieras."

MSG_PROCESSING = "⏳ Procesando tu rutina..."

MSG_CREATING_SLIDES = (
    "⏳ Creando presentación en Google Slides...\nEsto puede tardar unos segundos."
)

MSG_ERROR_PARSING = """❌ *No pude procesar la rutina*

Verifica el formato e intenta de nuevo. Ejemplo:
```
Pull ups 4 series de 10 reps
Front touch 3 series
```

Escribe /ayuda para más detalles."""

MSG_ERROR_SLIDES = (
    "❌ Error al crear la presentación. Por favor, intenta de nuevo más tarde."
)


# -------------------------
# Funciones auxiliares
# -------------------------


def format_routine_preview(structured_routine: list) -> str:
    """Genera un preview legible de la rutina estructurada."""
    lines = ["📋 *Rutina Detectada*\n"]

    for i, day in enumerate(structured_routine, 1):
        exercises = day.get("rutina", [])
        lines.append(f"*Día {i}* ({len(exercises)} ejercicios)")

        for ex in exercises[:5]:  # Mostrar máximo 5 por día
            name = ex.get("ejercicio", "?")
            series = ex.get("series", "?")
            reps = ", ".join(ex.get("repeticiones", ["N/A"]))
            lines.append(f"• {name} - {series}x ({reps})")

        if len(exercises) > 5:
            lines.append(f"  _...y {len(exercises) - 5} más_")
        lines.append("")

    lines.append("¿Generar la presentación?")
    return "\n".join(lines)


def handle_command(chat_id: int, command: str) -> dict:
    """Maneja los comandos del bot."""

    if command in ["/start", "/inicio"]:
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id, MSG_WELCOME)
        return {"status": "welcome"}

    elif command in ["/ayuda", "/help"]:
        send_telegram_message(chat_id, MSG_HELP)
        return {"status": "help"}

    elif command in ["/cancelar", "/cancel"]:
        if chat_id in user_states:
            user_states.pop(chat_id)
            send_telegram_message(chat_id, MSG_CANCELLED)
        else:
            send_telegram_message(chat_id, MSG_NO_PENDING)
        return {"status": "cancelled"}

    elif command == "/estado":
        if chat_id in user_states:
            send_telegram_message(
                chat_id,
                "📌 Tienes una rutina pendiente de confirmación.\nUsa /cancelar para descartarla.",
            )
        else:
            send_telegram_message(chat_id, MSG_NO_PENDING)
        return {"status": "status"}

    return None  # No es un comando reconocido


def handle_routine_message(chat_id: int, text: str) -> dict:
    """Procesa un mensaje de rutina del usuario."""

    # Si ya tiene rutina pendiente
    if chat_id in user_states:
        send_telegram_message(
            chat_id,
            "⚠️ Ya tienes una rutina pendiente.\nUsa los botones para confirmar o escribe /cancelar.",
        )
        return {"status": "already_pending"}

    # Indicar que estamos procesando
    send_typing_action(chat_id)
    send_telegram_message(chat_id, MSG_PROCESSING)

    try:
        # Parsear la rutina
        structured_routine = parse_routine(text)

        # Guardar estado
        user_states[chat_id] = {"routine": structured_routine}

        # Mostrar preview con botones
        preview = format_routine_preview(structured_routine)
        send_telegram_message_with_inline_keyboard(
            chat_id,
            preview,
            inline_keyboard=[
                [
                    {"text": "✅ Crear Presentación", "callback_data": "confirm"},
                    {"text": "❌ Cancelar", "callback_data": "cancel"},
                ]
            ],
        )
        return {"status": "awaiting_confirmation"}

    except Exception as e:
        logger.error(f"Error parsing routine: {e}", exc_info=True)
        send_telegram_message(chat_id, MSG_ERROR_PARSING)
        return {"status": "parsing_error"}


def handle_callback(callback_query: dict) -> dict:
    """Maneja los callbacks de botones inline."""

    callback_id = callback_query.get("id")
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    action = callback_query.get("data")

    # Responder al callback inmediatamente (quita el loading)
    answer_callback_query(callback_id)

    # Eliminar botones del mensaje
    edit_message_reply_markup(chat_id, message_id, None)

    if action == "confirm":
        if chat_id not in user_states:
            send_telegram_message(chat_id, MSG_NO_PENDING)
            return {"status": "no_pending"}

        structured_routine = user_states.pop(chat_id).get("routine")

        # Indicar que estamos creando
        send_typing_action(chat_id)
        send_telegram_message(chat_id, MSG_CREATING_SLIDES)

        try:
            presentation_link = create_presentation(structured_routine)
            send_telegram_message(
                chat_id,
                f"✅ *¡Presentación creada!*\n\n🔗 [Abrir presentación]({presentation_link})",
            )
            return {"status": "success"}

        except Exception as e:
            logger.error(f"Error creating presentation: {e}", exc_info=True)
            send_telegram_message(chat_id, MSG_ERROR_SLIDES)
            return {"status": "slides_error"}

    elif action == "cancel":
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id, MSG_CANCELLED)
        return {"status": "cancelled"}

    return {"status": "unknown_callback"}


# -------------------------
# Webhook Endpoint
# -------------------------


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Endpoint principal del webhook de Telegram."""
    try:
        data = await request.json()

        # Manejar callbacks de botones
        if "callback_query" in data:
            return handle_callback(data["callback_query"])

        # Manejar mensajes
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()

            if not text:
                return {"status": "empty_message"}

            # Verificar si es un comando
            if text.startswith("/"):
                result = handle_command(chat_id, text.lower())
                if result:
                    return result

            # Es un mensaje de rutina
            return handle_routine_message(chat_id, text)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"status": "error"}


@app.get("/set_webhook")
def configure_webhook():
    """Configura el webhook de Telegram."""
    return set_webhook()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
