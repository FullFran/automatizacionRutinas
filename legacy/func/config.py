import os

from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env (opcional)
load_dotenv()

# Configuración de tokens y claves
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://tu-dominio.com/webhook")

# si en el entorno no hay un archivo de credenciales, se creará a partir de las variables de entorno
# a partir de GOOGLE_CREDENTIALS que está en .env y contiene el json creamos el archivo a partir de la variable de entorno
if os.getenv("GOOGLE_CREDENTIALS") and not os.path.exists("credenciales.json"):
    with open("credenciales.json", "w") as file:
        file.write(os.getenv("GOOGLE_CREDENTIALS"))

# Verifica si la variable con las credenciales está definida
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "credenciales.json")

# Otros parámetros
GOOGLE_SLIDES_SCOPES = ["https://www.googleapis.com/auth/presentations"]
