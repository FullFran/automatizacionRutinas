"""
Automatización de Rutinas - Entry Point

Aplicación FastAPI con Clean Architecture.
"""

import logging
import sys
from pathlib import Path

# Añadir src al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, routines, telegram_webhook
from infrastructure.config.settings import settings

# ─────────────────────────────────────────────────────────
# Configuración de Logging
# ─────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────
# Aplicación FastAPI
# ─────────────────────────────────────────────────────────

app = FastAPI(
    title="Routine Bot API",
    description="""
    API para automatización de rutinas de entrenamiento.
    
    ## Funcionalidades
    
    - **Parsear rutinas**: Convierte texto a rutinas estructuradas con IA
    - **Generar slides**: Crea presentaciones de Google Slides
    - **Telegram Bot**: Webhook para el bot de Telegram
    
    ## Arquitectura
    
    Construido con Clean Architecture para máxima flexibilidad y testabilidad.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(routines.router)
app.include_router(telegram_webhook.router)


# ─────────────────────────────────────────────────────────
# Eventos
# ─────────────────────────────────────────────────────────


@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 {settings.app_name} v2.0.0 iniciando...")
    logger.info("📝 Docs disponibles en /docs")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Apagando aplicación...")


# ─────────────────────────────────────────────────────────
# Root endpoint
# ─────────────────────────────────────────────────────────


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ─────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
