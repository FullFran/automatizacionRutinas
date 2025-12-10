"""
Schemas para la API de rutinas.

Define los modelos de request/response para los endpoints.
"""

from typing import List

from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────────────────


class ParseRoutineRequest(BaseModel):
    """Request para parsear una rutina."""

    text: str = Field(
        ..., min_length=5, description="Texto con la rutina de ejercicios"
    )

    class Config:
        json_schema_extra = {
            "example": {"text": "Pull ups 4 series de 10 reps\nFront lever 3 series"}
        }


class GenerateSlidesRequest(BaseModel):
    """Request para generar presentación."""

    days: List["DaySchema"] = Field(..., description="Días de la rutina")


# ─────────────────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────────────────


class ExerciseSchema(BaseModel):
    """Schema de un ejercicio."""

    name: str = Field(..., description="Nombre del ejercicio")
    sets: str = Field(..., description="Número de series")
    reps: List[str] = Field(default_factory=list, description="Repeticiones")


class DaySchema(BaseModel):
    """Schema de un día de rutina."""

    day_number: int = Field(..., description="Número del día")
    exercises: List[ExerciseSchema] = Field(default_factory=list)
    total_exercises: int = Field(0, description="Total de ejercicios")


class RoutineResponse(BaseModel):
    """Response con la rutina parseada."""

    days: List[DaySchema]
    total_exercises: int = Field(0, description="Total de ejercicios")

    class Config:
        json_schema_extra = {
            "example": {
                "days": [
                    {
                        "day_number": 1,
                        "exercises": [
                            {"name": "Pull ups", "sets": "4", "reps": ["10"]}
                        ],
                        "total_exercises": 1,
                    }
                ],
                "total_exercises": 1,
            }
        }


class PresentationResponse(BaseModel):
    """Response con la presentación generada."""

    id: str = Field(..., description="ID de la presentación")
    url: str = Field(..., description="URL de la presentación")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "1abc123xyz",
                "url": "https://docs.google.com/presentation/d/1abc123xyz",
            }
        }


class HealthResponse(BaseModel):
    """Response del health check."""

    status: str = Field(default="healthy")
    version: str = Field(default="2.0.0")


class ErrorResponse(BaseModel):
    """Response de error."""

    detail: str = Field(..., description="Mensaje de error")


# Actualizar forward references
GenerateSlidesRequest.model_rebuild()
