"""
DTOs para rutinas.

Data Transfer Objects que se usan para transferir datos entre capas.
"""

from typing import List

from pydantic import BaseModel, Field

from domain.entities.routine import Exercise, Routine


class ExerciseDTO(BaseModel):
    """DTO para un ejercicio."""

    name: str = Field(..., description="Nombre del ejercicio")
    sets: str = Field(..., description="Número de series")
    reps: List[str] = Field(default_factory=list, description="Repeticiones")

    @classmethod
    def from_entity(cls, exercise: Exercise) -> "ExerciseDTO":
        return cls(name=exercise.name, sets=exercise.sets, reps=exercise.reps)

    def to_entity(self) -> Exercise:
        return Exercise(name=self.name, sets=self.sets, reps=self.reps)


class DayDTO(BaseModel):
    """DTO para un día de rutina."""

    day_number: int = Field(..., description="Número del día")
    exercises: List[ExerciseDTO] = Field(default_factory=list)
    total_exercises: int = Field(0, description="Total de ejercicios")

    @classmethod
    def from_entity(cls, routine: Routine) -> "DayDTO":
        exercises = [ExerciseDTO.from_entity(ex) for ex in routine.exercises]
        return cls(
            day_number=routine.day_number,
            exercises=exercises,
            total_exercises=len(exercises),
        )

    def to_entity(self) -> Routine:
        return Routine(
            day_number=self.day_number,
            exercises=[ex.to_entity() for ex in self.exercises],
        )


class RoutineDTO(BaseModel):
    """DTO para una rutina completa (múltiples días)."""

    days: List[DayDTO] = Field(default_factory=list)

    @classmethod
    def from_entities(cls, routines: List[Routine]) -> "RoutineDTO":
        days = [DayDTO.from_entity(r) for r in routines]
        return cls(days=days)

    def to_entities(self) -> List[Routine]:
        return [day.to_entity() for day in self.days]

    def total_exercises(self) -> int:
        return sum(day.total_exercises for day in self.days)


class PresentationDTO(BaseModel):
    """DTO para una presentación generada."""

    id: str = Field(..., description="ID de la presentación")
    url: str = Field(..., description="URL de la presentación")
