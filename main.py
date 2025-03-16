from fastapi import FastAPI, Request, HTTPException
from func.routine_parser import parse_routine
from func.google_slides import create_presentation
from func.telegram_bot import send_telegram_message, set_webhook, send_telegram_message_with_inline_keyboard

app = FastAPI()

# Diccionario para almacenar rutinas pendientes de confirmación
pending_routines = {}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()

        if "callback_query" in data:
            # Manejo de la respuesta del botón en línea
            callback_query = data["callback_query"]
            chat_id = callback_query["message"]["chat"]["id"]
            callback_data = callback_query["data"]

            if callback_data == "confirm":
                if chat_id in pending_routines:
                    structured_routine = pending_routines.pop(chat_id)  # Eliminar rutina pendiente
                    send_telegram_message(chat_id, "Creando presentación, esto podría tardar unos minutos...")
                    
                    # Generar la presentación en Google Slides
                    presentation_link = create_presentation(structured_routine)
                    
                    send_telegram_message(chat_id, f"✅ Rutina procesada. Aquí tienes la presentación: {presentation_link}")
                else:
                    send_telegram_message(chat_id, "⚠ No hay ninguna rutina pendiente para procesar.")

            elif callback_data == "cancel":
                pending_routines.pop(chat_id, None)  # Eliminar rutina sin procesar
                send_telegram_message(chat_id, "🚫 Entendido, no se procesará la rutina.")

            return {"status": "ok"}

        elif "message" in data:
            # Manejo de mensajes entrantes
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip().lower()

            if text in ["si", "sí"]:
                if chat_id in pending_routines:
                    structured_routine = pending_routines.pop(chat_id)  # Confirmar rutina pendiente
                    send_telegram_message(chat_id, "Creando presentación, esto podría tardar unos minutos...")

                    # Generar la presentación
                    presentation_link = create_presentation(structured_routine)

                    send_telegram_message(chat_id, f"✅ Rutina procesada. Aquí tienes la presentación: {presentation_link}")
                else:
                    send_telegram_message(chat_id, "⚠ No hay ninguna rutina pendiente para procesar.")
                return {"status": "confirmed"}

            elif text == "no":
                pending_routines.pop(chat_id, None)
                send_telegram_message(chat_id, "🚫 Entendido, no se procesará la rutina.")
                return {"status": "cancelled"}

            if chat_id not in pending_routines:
                send_telegram_message(chat_id, "Procesando tu rutina...")

                structured_routine = parse_routine(text)
                pending_routines[chat_id] = structured_routine

                send_telegram_message(chat_id, "✅ Rutina procesada correctamente.")

                # Enviar mensaje de confirmación con botones en línea
                send_telegram_message_with_inline_keyboard(
                    chat_id,
                    "¿Quieres generar la presentación?",
                    inline_keyboard=[
                        [{"text": "Sí", "callback_data": "confirm"}],
                        [{"text": "No", "callback_data": "cancel"}]
                    ]
                )
                return {"status": "waiting_for_confirmation"}
            else:
                send_telegram_message(chat_id, "⚠ Ya tienes una rutina pendiente de confirmación. Por favor, responde 'Sí' o 'No'.")
                return {"status": "already_pending"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/set_webhook")
def configure_webhook():
    """ Configura el webhook de Telegram. """
    return set_webhook()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


