# src/domain/interfaces/__init__.py
"""Interfaces (contratos) del dominio."""

from .presentation_generator import PresentationGeneratorInterface
from .routine_parser import RoutineParserInterface

__all__ = ["RoutineParserInterface", "PresentationGeneratorInterface"]
