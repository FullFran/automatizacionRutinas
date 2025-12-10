# 🔴 api/ - Capa de Presentación

**La cara pública de la aplicación.** Aquí se exponen los endpoints HTTP y se manejan las peticiones.

---

## 🎯 ¿Qué es la Capa de Presentación?

Es la capa más externa que:

- Recibe peticiones HTTP (REST API)
- Valida datos de entrada
- Llama a los casos de uso
- Formatea respuestas
- Maneja errores HTTP

---

## 📂 Estructura

```
api/
├── routes/                 # Endpoints organizados por recurso
│   ├── health.py           # GET /health
│   ├── routines.py         # /api/v1/routines/*
│   └── telegram_webhook.py # POST /api/v1/telegram/webhook
│
├── schemas/                # Schemas de request/response (Pydantic)
│   └── routine_schemas.py  # RoutineRequest, RoutineResponse
│
└── dependencies.py         # Inyección de dependencias FastAPI
```

---

## 🛣️ Endpoints Propuestos

### Health Check

```
GET /health
Response: {"status": "healthy", "version": "1.0.0"}
```

### Rutinas API

```
POST /api/v1/routines/parse
Body: {"text": "Pull ups 4 series..."}
Response: {"days": [...], "total_exercises": 5}

POST /api/v1/routines/generate-slides
Body: {"routine": {...}}
Response: {"url": "https://docs.google.com/..."}
```

### Telegram Webhook

```
POST /api/v1/telegram/webhook
Body: {telegram update object}
Response: {"status": "ok"}
```

---

## 📋 Schemas (Validación)

Los schemas validan datos de entrada y estructuran respuestas:

```python
# api/schemas/routine_schemas.py
from pydantic import BaseModel, Field
from typing import List

class ParseRoutineRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Texto de la rutina")

class ExerciseResponse(BaseModel):
    name: str
    sets: str
    reps: List[str]

class DayResponse(BaseModel):
    day_number: int
    exercises: List[ExerciseResponse]

class RoutineResponse(BaseModel):
    days: List[DayResponse]
    total_exercises: int

class GenerateSlidesRequest(BaseModel):
    routine: RoutineResponse

class PresentationResponse(BaseModel):
    id: str
    url: str
```

---

## 🛣️ Routes (Endpoints)

```python
# api/routes/routines.py
from fastapi import APIRouter, Depends, HTTPException
from api.schemas.routine_schemas import (
    ParseRoutineRequest,
    RoutineResponse,
    GenerateSlidesRequest,
    PresentationResponse
)
from api.dependencies import get_parse_routine_use_case

router = APIRouter(prefix="/api/v1/routines", tags=["routines"])

@router.post("/parse", response_model=RoutineResponse)
async def parse_routine(
    request: ParseRoutineRequest,
    use_case = Depends(get_parse_routine_use_case)
):
    """Parsea texto de rutina con IA."""
    try:
        result = use_case.execute(request.text)
        return result
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate-slides", response_model=PresentationResponse)
async def generate_slides(
    request: GenerateSlidesRequest,
    use_case = Depends(get_generate_presentation_use_case)
):
    """Genera presentación de Google Slides."""
    result = use_case.execute(request.routine)
    return result
```

---

## 💉 Inyección de Dependencias

FastAPI usa `Depends` para inyección de dependencias:

```python
# api/dependencies.py
from functools import lru_cache
from infrastructure.ai.gemini_parser import GeminiParser
from infrastructure.config.settings import settings
from application.use_cases.parse_routine import ParseRoutineUseCase

@lru_cache()
def get_parser() -> GeminiParser:
    return GeminiParser(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model
    )

def get_parse_routine_use_case() -> ParseRoutineUseCase:
    return ParseRoutineUseCase(parser=get_parser())
```

---

## 🔄 Flujo de una Petición

```
         HTTP Request
              │
              ▼
    ┌─────────────────┐
    │   Route Handler │  Valida request con Schema
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   Dependencies  │  Inyecta use case configurado
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │    Use Case     │  Ejecuta lógica de aplicación
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   DTO/Schema    │  Formatea respuesta
    └────────┬────────┘
             │
             ▼
         HTTP Response
```

---

## ⚡ Reglas

1. ✅ Puede importar de todas las otras capas
2. ✅ Aquí vive FastAPI y todo lo relacionado con HTTP
3. ✅ Maneja errores y los convierte a HTTP status codes
4. ❌ NO debe contener lógica de negocio
5. ❌ Los schemas NO son las entidades del dominio
