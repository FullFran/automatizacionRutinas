"""
Generador de presentaciones en Google Slides.

Implementa PresentationGeneratorInterface del dominio.
"""

import json
import logging
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

from domain.entities.routine import Routine
from domain.interfaces.presentation_generator import PresentationGeneratorInterface

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/presentations",
]


class GoogleSlidesGenerator(PresentationGeneratorInterface):
    """
    Generador de presentaciones usando Google Slides API.

    Implementa PresentationGeneratorInterface del dominio.
    """

    def __init__(self, credentials_json: str, template_id: str, layout_id: str):
        """
        Inicializa el generador con credenciales.

        Args:
            credentials_json: JSON string con las credenciales de service account
            template_id: ID de la plantilla de presentación
            layout_id: ID del layout para rutinas
        """
        # Manejar caracteres de escape en el JSON (común en vars de entorno)
        try:
            credentials_info = json.loads(credentials_json)
        except json.JSONDecodeError:
            # Intentar escapar newlines literales
            fixed_json = credentials_json.replace("\\n", "\n")
            credentials_info = json.loads(fixed_json)

        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=SCOPES
        )

        self.slides_service = build("slides", "v1", credentials=credentials)
        self.drive_service = build("drive", "v3", credentials=credentials)
        self.template_id = template_id
        self.layout_id = layout_id

        logger.info("GoogleSlidesGenerator inicializado")

    def create(self, routines: List[Routine]) -> str:
        """
        Crea una presentación a partir de las rutinas.

        Args:
            routines: Lista de rutinas (una por día)

        Returns:
            ID de la presentación creada
        """
        # Copiar plantilla
        copy = (
            self.drive_service.files()
            .copy(fileId=self.template_id, body={"name": "Rutina de Entrenamiento"})
            .execute()
        )
        presentation_id = copy["id"]
        logger.info(f"Presentación copiada: {presentation_id}")

        # Obtener slides existentes
        presentation = (
            self.slides_service.presentations()
            .get(presentationId=presentation_id)
            .execute()
        )
        num_existing = len(presentation.get("slides", []))

        # Generar requests
        requests_content = []
        requests_format = []

        for i, routine in enumerate(routines):
            slide_id = f"slide_{i + num_existing}"

            # Crear slide
            requests_content.append(
                {
                    "createSlide": {
                        "objectId": slide_id,
                        "insertionIndex": str(i + num_existing),
                        "slideLayoutReference": {"layoutId": self.layout_id},
                    }
                }
            )

            # Crear título
            title_id = f"title_{i}"
            requests_content.extend(
                self._create_title(slide_id, title_id, routine.day_number)
            )
            requests_format.extend(self._format_title(title_id))

            # Crear tabla
            table_id = f"table_{i}"
            requests_content.extend(self._create_table(slide_id, table_id, routine))
            requests_format.extend(self._format_table(table_id, routine))

        # Ejecutar requests
        if requests_content:
            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id, body={"requests": requests_content}
            ).execute()
            logger.info("Contenido insertado")

        if requests_format:
            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id, body={"requests": requests_format}
            ).execute()
            logger.info("Formato aplicado")

        return presentation_id

    def set_permissions(self, presentation_id: str) -> None:
        """Configura permisos públicos."""
        self.drive_service.permissions().create(
            fileId=presentation_id, body={"type": "anyone", "role": "writer"}
        ).execute()
        logger.info("Permisos configurados")

    # ─────────────────────────────────────────────────────────
    # Métodos privados para construir slides
    # ─────────────────────────────────────────────────────────

    def _create_title(self, slide_id: str, title_id: str, day: int) -> List[dict]:
        return [
            {
                "createShape": {
                    "objectId": title_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "height": {"magnitude": 50, "unit": "PT"},
                            "width": {"magnitude": 600, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 50,
                            "translateY": 10,
                            "unit": "PT",
                        },
                    },
                }
            },
            {"insertText": {"objectId": title_id, "text": f"Día {day}"}},
        ]

    def _format_title(self, title_id: str) -> List[dict]:
        return [
            {
                "updateTextStyle": {
                    "objectId": title_id,
                    "style": {
                        "bold": True,
                        "fontSize": {"magnitude": 24, "unit": "PT"},
                        "foregroundColor": {
                            "opaqueColor": {
                                "rgbColor": {"red": 1, "green": 1, "blue": 1}
                            }
                        },
                    },
                    "fields": "bold,fontSize,foregroundColor",
                }
            },
            {
                "updateShapeProperties": {
                    "objectId": title_id,
                    "shapeProperties": {
                        "shapeBackgroundFill": {
                            "solidFill": {
                                "color": {
                                    "rgbColor": {"red": 0.0, "green": 0.2, "blue": 0.8}
                                }
                            }
                        }
                    },
                    "fields": "shapeBackgroundFill.solidFill.color",
                }
            },
        ]

    def _create_table(
        self, slide_id: str, table_id: str, routine: Routine
    ) -> List[dict]:
        num_rows = len(routine.exercises) + 1
        requests = [
            {
                "createTable": {
                    "objectId": table_id,
                    "rows": num_rows,
                    "columns": 3,
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {
                            "height": {"magnitude": 250, "unit": "PT"},
                            "width": {"magnitude": 600, "unit": "PT"},
                        },
                        "transform": {
                            "scaleX": 1,
                            "scaleY": 1,
                            "translateX": 50,
                            "translateY": 80,
                            "unit": "PT",
                        },
                    },
                }
            }
        ]

        # Encabezados
        headers = ["Ejercicio", "Series", "Repeticiones"]
        for col, text in enumerate(headers):
            requests.append(
                {
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": 0, "columnIndex": col},
                        "text": text,
                    }
                }
            )

        # Datos
        for row, ex in enumerate(routine.exercises, start=1):
            requests.append(
                {
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": row, "columnIndex": 0},
                        "text": ex.name,
                    }
                }
            )
            requests.append(
                {
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": row, "columnIndex": 1},
                        "text": ex.sets,
                    }
                }
            )
            requests.append(
                {
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": row, "columnIndex": 2},
                        "text": ", ".join(ex.reps),
                    }
                }
            )

        return requests

    def _format_table(self, table_id: str, routine: Routine) -> List[dict]:
        requests = []

        # Estilo encabezados (blanco + bold)
        for col in range(3):
            requests.append(
                {
                    "updateTextStyle": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": 0, "columnIndex": col},
                        "style": {
                            "bold": True,
                            "foregroundColor": {
                                "opaqueColor": {
                                    "rgbColor": {"red": 1, "green": 1, "blue": 1}
                                }
                            },
                        },
                        "fields": "bold,foregroundColor",
                    }
                }
            )

        # Estilo datos (blanco + fondo alternado)
        for row in range(1, len(routine.exercises) + 1):
            bg_color = (
                {"red": 0.2, "green": 0.2, "blue": 0.2}
                if row % 2 == 0
                else {"red": 0.27, "green": 0.27, "blue": 0.27}
            )

            for col in range(3):
                # Texto blanco
                requests.append(
                    {
                        "updateTextStyle": {
                            "objectId": table_id,
                            "cellLocation": {"rowIndex": row, "columnIndex": col},
                            "style": {
                                "foregroundColor": {
                                    "opaqueColor": {
                                        "rgbColor": {"red": 1, "green": 1, "blue": 1}
                                    }
                                }
                            },
                            "fields": "foregroundColor",
                        }
                    }
                )
                # Fondo
                requests.append(
                    {
                        "updateTableCellProperties": {
                            "objectId": table_id,
                            "tableRange": {
                                "location": {"rowIndex": row, "columnIndex": col},
                                "rowSpan": 1,
                                "columnSpan": 1,
                            },
                            "tableCellProperties": {
                                "tableCellBackgroundFill": {
                                    "solidFill": {"color": {"rgbColor": bg_color}}
                                }
                            },
                            "fields": "tableCellBackgroundFill.solidFill.color",
                        }
                    }
                )

        return requests
