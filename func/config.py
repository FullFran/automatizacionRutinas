import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env (opcional)
load_dotenv()

# Configuración de tokens y claves
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://tu-dominio.com/webhook")

# Verifica si la variable con las credenciales está definida
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credenciales.json")

# Otros parámetros
GOOGLE_SLIDES_SCOPES = ["https://www.googleapis.com/auth/presentations"]
