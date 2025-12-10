"""
Caso de Uso: Parsear Rutina

Recibe texto crudo y devuelve una rutina estructurada.
"""

import logging

from application.dtos.routine_dto import RoutineDTO
from domain.exceptions import ParsingError
from domain.interfaces.routine_parser import RoutineParserInterface

logger = logging.getLogger(__name__)


class ParseRoutineUseCase:
    """
    Caso de uso para parsear texto de rutina.

    Recibe una implementación de RoutineParserInterface (ej: GeminiParser)
    y la usa para convertir texto a rutinas estructuradas.
    """

    def __init__(self, parser: RoutineParserInterface):
        self.parser = parser

    def execute(self, raw_text: str) -> RoutineDTO:
        """
        Ejecuta el caso de uso.

        Args:
            raw_text: Texto con la rutina del usuario

        Returns:
            RoutineDTO con la rutina estructurada

        Raises:
            ParsingError: Si no se puede parsear la rutina
        """
        if not raw_text or not raw_text.strip():
            raise ParsingError("El texto de la rutina está vacío")

        logger.info(f"Parseando rutina de {len(raw_text)} caracteres")

        try:
            routines = self.parser.parse(raw_text)

            if not routines:
                raise ParsingError("No se detectaron ejercicios en la rutina")

            dto = RoutineDTO.from_entities(routines)
            logger.info(
                f"Rutina parseada: {dto.total_exercises()} ejercicios en {len(dto.days)} días"
            )

            return dto

        except Exception as e:
            logger.error(f"Error parseando rutina: {e}")
            raise ParsingError(f"Error al procesar la rutina: {str(e)}")
