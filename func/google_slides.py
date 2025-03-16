import os
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json


# 🔹 Configuración de credenciales
SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/presentations"]

# 🔹 Cargar credenciales desde la variable de entorno
credentials_json = os.getenv("GOOGLE_CREDENTIALS")

if not credentials_json:
    raise ValueError("⚠ ERROR: No se encontraron las credenciales de Google en las variables de entorno.")

try:
    print("🔍 Cargando credenciales desde GCP_CREDENTIALS...")
    credentials_info = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    slides_service = build("slides", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)
    print("✅ Credenciales cargadas con éxito.")
except json.JSONDecodeError as e:
    raise ValueError(f"❌ ERROR: No se pudo decodificar el JSON de credenciales. {str(e)}")
except Exception as e:
    raise ValueError(f"❌ ERROR en la autenticación con Google: {str(e)}")


# 🔹 ID de la plantilla de presentación
TEMPLATE_PRESENTATION_ID = os.getenv("TEMPLATE_PRESENTATION_ID")


def create_presentation(routine_data):
    """
    Crea una presentación en Google Slides con un diseño moderno.
    """
    copy = drive_service.files().copy(
        fileId=TEMPLATE_PRESENTATION_ID,
        body={"name": "Rutina de Entrenamiento Generada"}
    ).execute()
    presentation_id = copy["id"]

    for i, rutina in enumerate(routine_data):
        slide_id = f"slide_{i}"

        # 🔹 Crear una nueva diapositiva con fondo negro
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": [{
                "createSlide": {
                    "objectId": slide_id
                }
            }, {
                "updatePageProperties": {
                    "objectId": slide_id,
                    "pageProperties": {
                        "pageBackgroundFill": {
                            "solidFill": {
                                "color": {
                                    "rgbColor": {"red": 0, "green": 0, "blue": 0}  # Fondo negro
                                }
                            }
                        }
                    }
                }
            }]}
        ).execute()
        time.sleep(1)

        # 🔹 Crear un título con texto blanco
        title_id = f"title_{i}"
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": [{
                "createShape": {
                    "objectId": title_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"height": {"magnitude": 50, "unit": "PT"},
                                 "width": {"magnitude": 400, "unit": "PT"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 50, "translateY": 50, "unit": "PT"}
                    }
                }
            }, {
                "insertText": {
                    "objectId": title_id,
                    "text": f"Rutina {i + 1}",
                    "textStyle": {
                        "foregroundColor": {"opaqueColor": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}},  # Blanco
                        "fontSize": {"magnitude": 24, "unit": "PT"},
                        "bold": True
                    }
                }
            }]}
        ).execute()
        time.sleep(1)

        # 🔹 Insertar una tabla bien estructurada
        num_rows = len(rutina["rutina"]) + 1
        num_cols = 3  # Columnas: Ejercicio, Series, Repeticiones
        table_id = f"table_{i}"

        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": [{
                "createTable": {
                    "objectId": table_id,
                    "rows": num_rows,
                    "columns": num_cols,
                    "elementProperties": {
                        "pageObjectId": slide_id
                    }
                }
            }]}
        ).execute()
        time.sleep(1)

        # 🔹 Insertar títulos de las columnas con fondo gris oscuro
        headers = ["Ejercicio", "Series", "Repeticiones"]
        for col, text in enumerate(headers):
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": [{
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": 0, "columnIndex": col},
                        "text": text,
                        "textStyle": {
                            "foregroundColor": {"opaqueColor": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}},  # Blanco
                            "fontSize": {"magnitude": 18, "unit": "PT"},
                            "bold": True
                        }
                    }
                }, {
                    "updateTableCellProperties": {
                        "objectId": table_id,
                        "tableRange": {
                            "location": {"rowIndex": 0, "columnIndex": col},
                            "rowSpan": 1,
                            "columnSpan": 1
                        },
                        "tableCellProperties": {
                            "backgroundFill": {
                                "solidFill": {
                                    "color": {
                                        "rgbColor": {"red": 0.2, "green": 0.2, "blue": 0.2}  # Gris oscuro
                                    }
                                }
                            }
                        }
                    }
                }]}
            ).execute()
            time.sleep(1)

        # 🔹 Insertar datos con alternancia de colores en las filas
        for row, exercise in enumerate(rutina["rutina"], start=1):
            row_color = {"red": 0.3, "green": 0.3, "blue": 0.3} if row % 2 == 0 else {"red": 0.1, "green": 0.1, "blue": 0.1}

            slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": [{
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": row, "columnIndex": 0},
                        "text": exercise["ejercicio"]
                    }
                }, {
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": row, "columnIndex": 1},
                        "text": exercise["series"]
                    }
                }, {
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": row, "columnIndex": 2},
                        "text": ", ".join(exercise["repeticiones"])
                    }
                }, {
                    "updateTableCellProperties": {
                        "objectId": table_id,
                        "tableRange": {
                            "location": {"rowIndex": row, "columnIndex": 0},
                            "rowSpan": 1,
                            "columnSpan": 3
                        },
                        "tableCellProperties": {
                            "backgroundFill": {
                                "solidFill": {
                                    "color": {"rgbColor": row_color}  # Alternar colores
                                }
                            }
                        }
                    }
                }]}
            ).execute()
            time.sleep(1)

    set_permissions(presentation_id)

    return f"https://docs.google.com/presentation/d/{presentation_id}"


def set_permissions(file_id):
    """
    Da permisos de edición a cualquier persona con el enlace en Google Drive.
    """
    permission = {
        "type": "anyone",
        "role": "writer"
    }

    drive_service.permissions().create(
        fileId=file_id,
        body=permission
    ).execute()
