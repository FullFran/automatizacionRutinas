"""
Interface: PresentationGeneratorInterface

Define el contrato para generar presentaciones de rutinas.
Permite cambiar de Google Slides a PowerPoint u otro sin modificar la lógica.
"""

from abc import ABC, abstractmethod
from typing import List

from domain.entities.routine import Routine


class PresentationGeneratorInterface(ABC):
    """
    Interface abstracta para generar presentaciones.
    """

    @abstractmethod
    def create(self, routines: List[Routine]) -> str:
        """
        Crea una presentación a partir de las rutinas.

        Args:
            routines: Lista de rutinas a incluir en la presentación

        Returns:
            ID o URL de la presentación generada

        Raises:
            PresentationError: Si falla la creación
        """
        pass

    @abstractmethod
    def set_permissions(self, presentation_id: str) -> None:
        """
        Configura permisos de la presentación (público, compartido, etc.)

        Args:
            presentation_id: ID de la presentación
        """
        pass
