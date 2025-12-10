"""
Entidades de Dominio: Routine y Exercise

Estas son las entidades principales del negocio. Representan una rutina
de entrenamiento con sus ejercicios.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Exercise:
    """
    Representa un ejercicio de la rutina.

    Attributes:
        name: Nombre del ejercicio (ej: "Pull ups")
        sets: Número de series (ej: "4")
        reps: Lista de repeticiones por serie (ej: ["10", "8", "6"])
    """

    name: str
    sets: str
    reps: List[str] = field(default_factory=lambda: ["N/A"])

    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del ejercicio no puede estar vacío")
        if not self.sets:
            self.sets = "1"
        if not self.reps:
            self.reps = ["N/A"]


@dataclass
class Routine:
    """
    Representa una rutina de un día.

    Attributes:
        day_number: Número del día (1, 2, 3...)
        exercises: Lista de ejercicios del día
    """

    day_number: int
    exercises: List[Exercise] = field(default_factory=list)

    def total_exercises(self) -> int:
        """Devuelve el número total de ejercicios."""
        return len(self.exercises)

    def is_empty(self) -> bool:
        """Verifica si la rutina no tiene ejercicios."""
        return len(self.exercises) == 0

    def add_exercise(self, exercise: Exercise) -> None:
        """Añade un ejercicio a la rutina."""
        self.exercises.append(exercise)
