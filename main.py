from fastapi import FastAPI, Request, HTTPException
from func.routine_parser import parse_routine
from func.google_slides import create_presentation
from func.telegram_bot import send_telegram_message, set_webhook

app = FastAPI()

# Diccionario temporal para almacenar la rutina antes de la confirmación
pending_routines = {}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        # Si el usuario aún no ha confirmado y envía una rutina
        if chat_id not in pending_routines:
            send_telegram_message(chat_id, "Procesando tu rutina...")
            structured_routine = parse_routine(text)  # Convierte la rutina
            pending_routines[chat_id] = structured_routine  # Almacena la rutina temporalmente
            send_telegram_message(chat_id, "Rutina procesada correctamente.")
            
            # Enviar mensaje de confirmación con botones
            send_telegram_message(chat_id, "¿Quieres generar la presentación?", reply_markup={
                "keyboard": [["Sí"], ["No"]],
                "one_time_keyboard": True,
                "resize_keyboard": True
            })
            return {"status": "waiting_for_confirmation"}

        # Si el usuario responde "No", cancelamos la operación
        if text.lower() in ["no"]:
            send_telegram_message(chat_id, "Entendido, no se procesará la rutina.")
            pending_routines.pop(chat_id, None)  # Eliminar rutina temporal
            return {"status": "cancelled"}

        # Si el usuario responde "Sí", generamos la presentación
        if text.lower() in ["sí", "si"]:
            send_telegram_message(chat_id, "Creando presentación, esto podría tardar unos minutos...")
            structured_routine = pending_routines.pop(chat_id, None)  # Recupera la rutina almacenada

            if not structured_routine:
                send_telegram_message(chat_id, "No hay ninguna rutina pendiente para procesar.")
                return {"status": "error", "message": "No pending routine"}

            presentation_link = create_presentation(structured_routine)
            send_telegram_message(chat_id, f"Tu rutina ha sido procesada. Aquí tienes la presentación: {presentation_link}")
            return {"status": "ok"}

        return {"status": "invalid_input"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/set_webhook")
def configure_webhook():
    """
    Endpoint para configurar el webhook de Telegram.
    """
    return set_webhook()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
