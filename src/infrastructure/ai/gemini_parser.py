"""
Implementación del parser de rutinas usando Gemini AI.

Implementa RoutineParserInterface del dominio.
"""

import json
import logging
import re
from typing import List

import google.generativeai as genai
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from domain.entities.routine import Exercise, Routine
from domain.exceptions import ParsingError
from domain.interfaces.routine_parser import RoutineParserInterface

logger = logging.getLogger(__name__)


class GeminiParser(RoutineParserInterface):
    """
    Parser de rutinas usando Google Gemini.

    Implementa la interface RoutineParserInterface del dominio.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        """
        Inicializa el parser con las credenciales.

        Args:
            api_key: API key de Gemini
            model: Nombre del modelo a usar
        """
        genai.configure(api_key=api_key)
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            credentials=None,
        )
        logger.info(f"GeminiParser inicializado con modelo {model}")

    def parse(self, text: str) -> List[Routine]:
        """
        Parsea texto de rutina y devuelve lista de Routine.

        Args:
            text: Texto crudo con la rutina

        Returns:
            Lista de Routine, una por cada bloque/día
        """
        routines_text = self._split_routines(text)
        result = []

        for i, routine_text in enumerate(routines_text, start=1):
            exercises = self._parse_single_routine(routine_text)
            routine = Routine(day_number=i, exercises=exercises)
            result.append(routine)

        return result

    def _split_routines(self, text: str) -> List[str]:
        """Separa el texto en bloques de rutina."""
        routines = re.split(r"\n{2,}", text.strip())
        return [r.strip() for r in routines if r.strip()]

    def _parse_single_routine(self, text: str) -> List[Exercise]:
        """Parsea un solo bloque de rutina con Gemini."""
        prompt = f"""
        Estructura este texto en formato JSON con los campos:
        - "ejercicio": Nombre del ejercicio (string, obligatorio).
        - "series": Número de series (string, mínimo "1", no puede ser null).
        - "repeticiones": Lista de repeticiones (obligatorio, si hay una sola repetición, debe ir en una lista).

        Si un ejercicio no tiene repeticiones, coloca ["N/A"].
        Si un ejercicio no tiene número de series, coloca "1".

        Texto:
        {text}

        Formato de respuesta:
        [
            {{"ejercicio": "Pull ups", "series": "4", "repeticiones": ["10"]}},
            {{"ejercicio": "Front touch", "series": "3", "repeticiones": ["N/A"]}}
        ]
        
        SOLO devuelve el JSON, sin explicaciones ni markdown.
        """

        try:
            response = self.llm.invoke(
                [
                    SystemMessage(
                        content="Eres un asistente que estructura rutinas de entrenamiento en JSON."
                    ),
                    HumanMessage(content=prompt),
                ]
            )

            # Limpiar respuesta
            cleaned = re.sub(r"```json\n|```|\n```", "", response.content).strip()
            data = json.loads(cleaned)

            # Convertir a entidades
            exercises = []
            for item in data:
                exercise = Exercise(
                    name=item.get("ejercicio", "Ejercicio"),
                    sets=item.get("series", "1"),
                    reps=item.get("repeticiones", ["N/A"]),
                )
                exercises.append(exercise)

            return exercises

        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de Gemini: {e}")
            raise ParsingError("La respuesta de la IA no es un JSON válido")
        except Exception as e:
            logger.error(f"Error en Gemini: {e}")
            raise ParsingError(f"Error al procesar con IA: {str(e)}")
