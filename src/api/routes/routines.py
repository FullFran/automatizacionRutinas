"""
Endpoints REST para rutinas.

API pública para usar fuera de Telegram.
"""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import (
    get_generate_presentation_use_case,
    get_parse_routine_use_case,
)
from api.schemas.routine_schemas import (
    DaySchema,
    ExerciseSchema,
    GenerateSlidesRequest,
    ParseRoutineRequest,
    PresentationResponse,
    RoutineResponse,
)
from application.dtos.routine_dto import DayDTO, ExerciseDTO, RoutineDTO
from application.use_cases.generate_presentation import GeneratePresentationUseCase
from application.use_cases.parse_routine import ParseRoutineUseCase
from domain.exceptions import DomainException

router = APIRouter(prefix="/api/v1/routines", tags=["routines"])


@router.post("/parse", response_model=RoutineResponse)
async def parse_routine(
    request: ParseRoutineRequest,
    use_case: ParseRoutineUseCase = Depends(get_parse_routine_use_case),
):
    """
    Parsea texto de rutina con IA.

    Recibe texto con ejercicios y devuelve una rutina estructurada.
    """
    try:
        result = use_case.execute(request.text)

        # Convertir DTO a schema de respuesta
        days = [
            DaySchema(
                day_number=day.day_number,
                exercises=[
                    ExerciseSchema(name=ex.name, sets=ex.sets, reps=ex.reps)
                    for ex in day.exercises
                ],
                total_exercises=day.total_exercises,
            )
            for day in result.days
        ]

        return RoutineResponse(days=days, total_exercises=result.total_exercises())

    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.post("/generate-slides", response_model=PresentationResponse)
async def generate_slides(
    request: GenerateSlidesRequest,
    use_case: GeneratePresentationUseCase = Depends(get_generate_presentation_use_case),
):
    """
    Genera una presentación de Google Slides.

    Recibe una rutina estructurada y crea la presentación.
    """
    try:
        # Convertir schema a DTO
        routine_dto = RoutineDTO(
            days=[
                DayDTO(
                    day_number=day.day_number,
                    exercises=[
                        ExerciseDTO(name=ex.name, sets=ex.sets, reps=ex.reps)
                        for ex in day.exercises
                    ],
                    total_exercises=day.total_exercises,
                )
                for day in request.days
            ]
        )

        result = use_case.execute(routine_dto)

        return PresentationResponse(id=result.id, url=result.url)

    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")
