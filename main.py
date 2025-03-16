from fastapi import FastAPI, Request, HTTPException
from func.routine_parser import parse_routine
# from func.google_slides import create_presentation
from func.telegram_bot import send_telegram_message, set_webhook

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]

        # Procesar la rutina con Gemini y validar la estructura
        structured_routine = parse_routine(text)

        # Crear la presentación en Google Slides
  #      presentation_link = create_presentation(structured_routine)
        presentation_link = structured_routine
        # Enviar el enlace al usuario por Telegram
        send_telegram_message(chat_id, f"Tu rutina ha sido procesada. Aquí tienes la presentación: {presentation_link}")

        return {"status": "ok"}
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
