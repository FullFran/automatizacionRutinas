"""
Endpoints de salud.
"""

from fastapi import APIRouter

from api.schemas.routine_schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="2.0.0")
