# 🔵 domain/ - Capa de Dominio

**El corazón de la aplicación.** Aquí vive la lógica de negocio pura, sin dependencias externas.

---

## 🎯 ¿Qué es la Capa de Dominio?

Es la capa más interna de Clean Architecture. Contiene:

- **Entidades**: Objetos que representan conceptos del negocio (Rutina, Ejercicio)
- **Interfaces**: Contratos que definen QUÉ hacer, pero no CÓMO
- **Reglas de negocio**: Validaciones y lógica que siempre aplican
- **Excepciones**: Errores específicos del dominio

---

## 📂 Estructura

```
domain/
├── entities/           # Modelos de datos del negocio
│   ├── routine.py      # Entidad Rutina
│   └── exercise.py     # Entidad Ejercicio
│
├── interfaces/         # Contratos abstractos (ABC)
│   ├── routine_parser.py       # Interface para parsear rutinas
│   └── presentation_generator.py # Interface para generar presentaciones
│
└── exceptions.py       # Excepciones de dominio
```

---

## 🧩 Entidades

Las entidades son **objetos de negocio** con identidad propia. No saben nada de bases de datos, APIs, o frameworks.

```python
# entities/routine.py
from dataclasses import dataclass
from typing import List

@dataclass
class Exercise:
    name: str
    sets: int
    reps: List[str]

@dataclass
class Routine:
    day: int
    exercises: List[Exercise]

    def total_exercises(self) -> int:
        return len(self.exercises)
```

---

## 🔌 Interfaces (Puertos)

Las interfaces definen **contratos** que las capas externas deben implementar. Esto permite:

- Cambiar implementaciones sin tocar la lógica de negocio
- Testear con mocks fácilmente
- Desacoplar dependencias

```python
# interfaces/routine_parser.py
from abc import ABC, abstractmethod
from domain.entities.routine import Routine

class RoutineParserInterface(ABC):
    @abstractmethod
    def parse(self, text: str) -> List[Routine]:
        """Parsea texto y devuelve lista de rutinas."""
        pass
```

Luego en `infrastructure/ai/gemini_parser.py`:

```python
class GeminiParser(RoutineParserInterface):
    def parse(self, text: str) -> List[Routine]:
        # Implementación con Gemini
        ...
```

---

## ⚠️ Excepciones de Dominio

Errores específicos del negocio, no errores técnicos.

```python
# exceptions.py
class DomainException(Exception):
    """Base para excepciones de dominio."""
    pass

class InvalidRoutineError(DomainException):
    """La rutina no tiene un formato válido."""
    pass

class EmptyRoutineError(DomainException):
    """La rutina no contiene ejercicios."""
    pass
```

---

## ⚡ Regla de Oro

> **Esta carpeta NO debe importar NADA de las otras capas.**
>
> ❌ `from infrastructure.ai import GeminiParser`  
> ❌ `from api.schemas import RoutineRequest`  
> ❌ `import fastapi`  
> ❌ `import google.generativeai`
>
> ✅ Solo Python estándar y librerías de tipos (dataclasses, typing, abc)

---

## 🎓 Concepto Clave: Inversión de Dependencias

En lugar de que el dominio dependa de Gemini:

```
# ❌ MAL
domain/ → infrastructure/gemini
```

Hacemos que Gemini dependa del dominio:

```
# ✅ BIEN
infrastructure/gemini → domain/interfaces
```

Esto se logra con **interfaces abstractas**.
