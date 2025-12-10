# 🟢 application/ - Capa de Aplicación

**Orquestador de la lógica de negocio.** Contiene los casos de uso que coordinan las operaciones.

---

## 🎯 ¿Qué es la Capa de Aplicación?

Es el intermediario entre la capa de presentación (API) y el dominio. Aquí se definen:

- **Casos de Uso (Use Cases)**: Acciones que el usuario puede realizar
- **DTOs**: Objetos para transferir datos entre capas
- **Application Services**: Servicios que orquestan múltiples operaciones

---

## 📂 Estructura

```
application/
├── use_cases/              # Casos de uso
│   ├── parse_routine.py    # Parsear texto a rutina estructurada
│   └── generate_presentation.py  # Generar slides de una rutina
│
└── dtos/                   # Data Transfer Objects
    ├── routine_dto.py      # DTO para rutinas
    └── presentation_dto.py # DTO para presentaciones
```

---

## 🎬 Casos de Uso

Un caso de uso representa **una acción específica** que el usuario quiere realizar. Es un único punto de entrada para una funcionalidad.

### Ejemplo: ParseRoutineUseCase

```python
# use_cases/parse_routine.py
from domain.interfaces.routine_parser import RoutineParserInterface
from domain.entities.routine import Routine
from application.dtos.routine_dto import RoutineDTO

class ParseRoutineUseCase:
    def __init__(self, parser: RoutineParserInterface):
        # Recibe la interface, no la implementación concreta
        self.parser = parser

    def execute(self, raw_text: str) -> RoutineDTO:
        """
        Parsea texto de rutina y devuelve DTO.

        Args:
            raw_text: Texto con la rutina del usuario

        Returns:
            RoutineDTO con la rutina estructurada
        """
        # 1. Usar el parser (puede ser Gemini, OpenAI, o mock)
        routines = self.parser.parse(raw_text)

        # 2. Convertir entidades a DTO para la respuesta
        return RoutineDTO.from_entities(routines)
```

### Ejemplo: GeneratePresentationUseCase

```python
# use_cases/generate_presentation.py
class GeneratePresentationUseCase:
    def __init__(
        self,
        generator: PresentationGeneratorInterface,
        drive: DriveServiceInterface
    ):
        self.generator = generator
        self.drive = drive

    def execute(self, routine: RoutineDTO) -> PresentationDTO:
        """Genera presentación y devuelve el link."""
        # 1. Generar slides
        presentation_id = self.generator.create(routine.to_entity())

        # 2. Configurar permisos
        self.drive.set_public_permissions(presentation_id)

        # 3. Devolver DTO con el link
        return PresentationDTO(
            id=presentation_id,
            url=f"https://docs.google.com/presentation/d/{presentation_id}"
        )
```

---

## 📦 DTOs (Data Transfer Objects)

Los DTOs son objetos simples para **transferir datos** entre capas. Ventajas:

- Desacoplan la API de las entidades internas
- Permiten versionar la API sin cambiar el dominio
- Pueden incluir campos calculados o transformados

```python
# dtos/routine_dto.py
from pydantic import BaseModel
from typing import List

class ExerciseDTO(BaseModel):
    name: str
    sets: str
    reps: List[str]

class DayDTO(BaseModel):
    day_number: int
    exercises: List[ExerciseDTO]
    total_exercises: int

class RoutineDTO(BaseModel):
    days: List[DayDTO]

    @classmethod
    def from_entities(cls, routines: List[Routine]) -> "RoutineDTO":
        """Convierte entidades de dominio a DTO."""
        days = [
            DayDTO(
                day_number=i+1,
                exercises=[...],
                total_exercises=len(r.exercises)
            )
            for i, r in enumerate(routines)
        ]
        return cls(days=days)
```

---

## 🔄 Flujo Típico

```
    API (Controller)
           │
           │  request_data
           ▼
    ┌──────────────────┐
    │    Use Case      │  ← Orquesta la operación
    │  (application/)  │
    └────────┬─────────┘
             │
    ┌────────┴─────────┐
    │                  │
    ▼                  ▼
 Domain            Infrastructure
(entities)         (Gemini, Google)
    │                  │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │       DTO        │  ← Respuesta estructurada
    └──────────────────┘
```

---

## ⚡ Reglas

1. ✅ Puede importar de `domain/`
2. ✅ Usa interfaces, no implementaciones concretas
3. ❌ NO debe importar de `api/` o `infrastructure/`
4. ❌ NO debe conocer FastAPI, Telegram, Gemini directamente
