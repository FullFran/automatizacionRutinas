"""
Interface: RoutineParserInterface

Define el contrato para cualquier servicio que parsee rutinas de texto.
Esto permite cambiar la implementación (Gemini, OpenAI, etc.) sin
modificar el resto de la aplicación.
"""

from abc import ABC, abstractmethod
from typing import List

from domain.entities.routine import Routine


class RoutineParserInterface(ABC):
    """
    Interface abstracta para parsear texto de rutinas.

    Cualquier implementación debe heredar de esta clase e implementar
    el método `parse`.
    """

    @abstractmethod
    def parse(self, text: str) -> List[Routine]:
        """
        Parsea texto de entrada y devuelve lista de rutinas estructuradas.

        Args:
            text: Texto crudo con la rutina del usuario

        Returns:
            Lista de Routine, una por cada día/bloque detectado

        Raises:
            ParsingError: Si el texto no puede ser parseado
        """
        pass
