"""
Caso de Uso: Generar Presentación

Crea una presentación de Google Slides a partir de una rutina.
"""

import logging

from application.dtos.routine_dto import PresentationDTO, RoutineDTO
from domain.exceptions import PresentationError
from domain.interfaces.presentation_generator import PresentationGeneratorInterface

logger = logging.getLogger(__name__)


class GeneratePresentationUseCase:
    """
    Caso de uso para generar presentaciones.

    Recibe una implementación de PresentationGeneratorInterface
    y la usa para crear slides.
    """

    def __init__(self, generator: PresentationGeneratorInterface):
        self.generator = generator

    def execute(self, routine: RoutineDTO) -> PresentationDTO:
        """
        Genera una presentación a partir de la rutina.

        Args:
            routine: RoutineDTO con los datos de la rutina

        Returns:
            PresentationDTO con el ID y URL de la presentación

        Raises:
            PresentationError: Si falla la generación
        """
        if not routine.days:
            raise PresentationError("La rutina no tiene días para generar")

        logger.info(f"Generando presentación para {len(routine.days)} días")

        try:
            # Convertir DTO a entidades
            entities = routine.to_entities()

            # Generar presentación
            presentation_id = self.generator.create(entities)

            # Configurar permisos
            self.generator.set_permissions(presentation_id)

            url = f"https://docs.google.com/presentation/d/{presentation_id}"
            logger.info(f"Presentación creada: {url}")

            return PresentationDTO(id=presentation_id, url=url)

        except Exception as e:
            logger.error(f"Error generando presentación: {e}")
            raise PresentationError(f"Error al crear la presentación: {str(e)}")
