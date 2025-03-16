import json
import re
from pydantic import BaseModel, ValidationError
from typing import List, Dict
from func.config import GEMINI_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage
import google.generativeai as genai

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINI_API_KEY,
    credentials=None  # Evita que use ADC
)

class RoutineItem(BaseModel):
    ejercicio: str
    series: str
    repeticiones: List[str]

def split_routines(text: str) -> List[str]:
    """
    Separa el texto en diferentes rutinas cuando hay más de un salto de línea consecutivo.
    """
    routines = re.split(r'\n{2,}', text.strip())  # Divide cuando hay 2 o más saltos de línea
    return [routine.strip() for routine in routines if routine.strip()]  # Elimina espacios vacíos

def parse_routine(text: str) -> List[Dict[str, List[dict]]]:
    """
    Procesa el texto de entrada y lo estructura en formato JSON según el modelo RoutineItem.
    Devuelve una lista de rutinas, cada una con su lista de ejercicios.
    """
    routines = split_routines(text)
    structured_routines = []

    for routine_text in routines:
        prompt = f"""
            Estructura este texto en formato JSON con los campos:
            - "ejercicio": Nombre del ejercicio (string, obligatorio).
            - "series": Número de series (string, mínimo "1", no puede ser null).
            - "repeticiones": Lista de repeticiones (obligatorio, si hay una sola repetición, debe ir en una lista).

            Si un ejercicio no tiene repeticiones, coloca ["N/A"].
            Si un ejercicio no tiene número de series, coloca "1".

            Texto:
            {routine_text}

            Formato de respuesta:
            [
                {{"ejercicio": "Pull ups", "series": "4", "repeticiones": ["3", "4", "5", "6"]}},
                {{"ejercicio": "Front touch", "series": "3", "repeticiones": ["3seg", "4 pull ups"]}}
            ]

            Notas:
            - Normalmente tras un ejercicio y sus series y repeticiones hay un salto de línea.
            - Por ejemplo esto son 5 ejercicios: 
               "front a 3touch, front a 4touch, front a 5touch, front a 6touch 4series     # un ejercicio 4 series N/A reps
                Front 2pull + touch, 3pull + touch, 4pull + touch, 5pull+ touch 4series de  # un ejercicio 4 series N/A reps
                Touch + pull + touch suma, las reps de pull suman desde 2,3,4,5              # un ejercicio 4 series 2,3,4,5 reps
                2pull completas + touch sube reps de pull en 1, 3series                         # un ejercicio 3 series N/A reps
                Front touch 3seg, 5seg, 8seg, 10seg, negativa de front completa 4series"     # un ejercicio 4 series 3seg, 5seg, 8seg, 10seg reps
            - Por lo general una rutina tiene menos de 10 ejercicios.
            """

        response = llm.invoke([
            SystemMessage(content="Eres un asistente que estructura rutinas de entrenamiento."),
            HumanMessage(content=prompt)
        ])

        try:
            # 🔹 Limpiar triple comillas y etiquetas de código
            cleaned_content = re.sub(r"```json\n|\n```", "", response.content).strip()

            # 🔹 Decodificar JSON
            routine_data = json.loads(cleaned_content)

            # Validar cada elemento usando el modelo RoutineItem
            validated_data = [RoutineItem(**item).dict() for item in routine_data]

            # Guardar la rutina en una estructura organizada
            structured_routines.append({"rutina": validated_data})

        except json.JSONDecodeError as e:
            print("❌ JSON inválido recibido:")
            print(cleaned_content)
            raise ValueError("La respuesta de Gemini no es un JSON válido.") from e
        except ValidationError as e:
            raise ValueError("La estructura de la rutina no coincide con el modelo esperado.") from e

    return structured_routines
