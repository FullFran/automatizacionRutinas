# 🟠 infrastructure/ - Capa de Infraestructura

**Implementaciones concretas y detalles técnicos.** Aquí viven las integraciones con servicios externos.

---

## 🎯 ¿Qué es la Capa de Infraestructura?

Es la capa que implementa los **detalles técnicos** que el dominio y la aplicación no deben conocer:

- Integraciones con APIs externas (Gemini, Google Slides, Telegram)
- Configuración de la aplicación
- Bases de datos y repositorios
- Servicios de terceros

---

## 📂 Estructura

```
infrastructure/
├── ai/                     # Integraciones de IA
│   └── gemini_parser.py    # Implementa RoutineParserInterface
│
├── google/                 # Servicios de Google
│   ├── slides_generator.py # Implementa PresentationGeneratorInterface
│   └── drive_service.py    # Manejo de permisos en Drive
│
├── telegram/               # Bot de Telegram
│   ├── bot.py              # Funciones de envío de mensajes
│   └── handlers.py         # Manejadores de comandos/callbacks
│
└── config/                 # Configuración
    ├── settings.py         # Variables de entorno con Pydantic
    └── logging.py          # Configuración de logs
```

---

## 🔌 Implementando Interfaces

La infraestructura **implementa** las interfaces definidas en el dominio:

### Ejemplo: GeminiParser

```python
# infrastructure/ai/gemini_parser.py
from domain.interfaces.routine_parser import RoutineParserInterface
from domain.entities.routine import Routine, Exercise
import google.generativeai as genai

class GeminiParser(RoutineParserInterface):
    """Implementación concreta usando Gemini AI."""

    def __init__(self, api_key: str, model: str):
        genai.configure(api_key=api_key)
        self.model = model

    def parse(self, text: str) -> List[Routine]:
        # Lógica específica de Gemini
        response = self._call_gemini(text)
        return self._parse_response(response)

    def _call_gemini(self, text: str) -> str:
        # Llamada a la API de Gemini
        ...

    def _parse_response(self, response: str) -> List[Routine]:
        # Convertir JSON a entidades de dominio
        ...
```

### Ejemplo: GoogleSlidesGenerator

```python
# infrastructure/google/slides_generator.py
from domain.interfaces.presentation_generator import PresentationGeneratorInterface

class GoogleSlidesGenerator(PresentationGeneratorInterface):
    """Genera presentaciones en Google Slides."""

    def __init__(self, credentials, template_id: str):
        self.slides_service = build("slides", "v1", credentials=credentials)
        self.template_id = template_id

    def create(self, routine: Routine) -> str:
        """Crea presentación y devuelve ID."""
        # Copiar template
        # Crear slides
        # Insertar contenido
        return presentation_id
```

---

## ⚙️ Configuración con Pydantic Settings

```python
# infrastructure/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Telegram
    telegram_token: str
    webhook_url: str

    # Gemini
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    # Google
    google_credentials: str
    template_presentation_id: str
    routine_layout_id: str

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🤖 Telegram Handlers

```python
# infrastructure/telegram/handlers.py
from infrastructure.telegram.bot import send_message, send_typing

class TelegramHandler:
    def __init__(self, parse_routine_use_case, generate_presentation_use_case):
        self.parse = parse_routine_use_case
        self.generate = generate_presentation_use_case

    async def handle_message(self, chat_id: int, text: str):
        send_typing(chat_id)

        try:
            routine = self.parse.execute(text)
            # ...mostrar preview...
        except DomainException as e:
            send_message(chat_id, f"Error: {e}")
```

---

## 🔄 Patrón: Adaptador

La infraestructura actúa como **adaptador** entre el mundo exterior y la aplicación:

```
    Mundo Exterior              Infraestructura              Aplicación
    ─────────────              ───────────────              ──────────

    Gemini API      ←──────→   GeminiParser      ──────→   RoutineParserInterface

    Google Slides   ←──────→   SlidesGenerator   ──────→   PresentationGeneratorInterface

    Telegram API    ←──────→   TelegramHandler   ──────→   Use Cases
```

---

## ⚡ Reglas

1. ✅ Implementa interfaces de `domain/`
2. ✅ Puede importar de `domain/` y `application/`
3. ✅ Aquí SÍ vas librerías externas (google, langchain, requests)
4. ❌ NO debe ser importado por `domain/`
5. ❌ NO debe importar de `api/` (para evitar ciclos)
