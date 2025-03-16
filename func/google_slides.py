import os
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json


# 🔹 Configuración de credenciales
SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/presentations"]

# Cargar credenciales desde la variable de entorno
credentials_json = os.getenv("GOOGLE_CREDENTIALS")

if not credentials_json:
    raise ValueError("⚠ ERROR: No se encontraron las credenciales de Google en las variables de entorno.")

try:
    print("🔍 Cargando credenciales desde GOOGLE_CREDENTIALS...")
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


def _hex_to_rgb(hex_color):
    """Convierte un color HEX a RGB para la API de Google Slides."""
    hex_color = hex_color.lstrip('#')
    return {
        "red": int(hex_color[0:2], 16) / 255.0,
        "green": int(hex_color[2:4], 16) / 255.0,
        "blue": int(hex_color[4:6], 16) / 255.0
    }


def create_presentation(routine_data):
    """
    Crea una presentación en Google Slides a partir de una plantilla y formatea el contenido con tablas.
    """
    print("🚀 Creando una nueva presentación desde la plantilla...")
    
    # Copiar la plantilla en una nueva presentación
    copy = drive_service.files().copy(
        fileId=TEMPLATE_PRESENTATION_ID,
        body={"name": "Rutina de Entrenamiento Generada"}
    ).execute()
    presentation_id = copy["id"]
    print(f"✅ Presentación creada: {presentation_id}")

    requests = []

    # 🔹 Configurar fondo negro para toda la presentación
    requests.append({
        "updatePageProperties": {
            "objectId": "p",
            "pageProperties": {
                "pageBackgroundFill": {
                    "solidFill": {
                        "color": {"rgbColor": _hex_to_rgb("#000000")}
                    }
                }
            },
            "fields": "pageBackgroundFill.solidFill.color"
        }
    })

    # 🔹 Crear diapositivas para cada rutina
    for i, rutina in enumerate(routine_data):
        slide_id = f"slide_{i}"
        
        # Agregar diapositiva
        requests.append({
            "createSlide": {
                "objectId": slide_id,
                "insertionIndex": str(i),
            }
        })

        # Agregar título
        title_id = f"title_{i}"
        requests.append({
            "createShape": {
                "objectId": title_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "height": {"magnitude": 50, "unit": "PT"},
                        "width": {"magnitude": 400, "unit": "PT"}
                    },
                    "transform": {
                        "scaleX": 1, "scaleY": 1, "translateX": 50, "translateY": 50, "unit": "PT"
                    }
                }
            }
        })
        requests.append({
            "insertText": {
                "objectId": title_id,
                "text": f"Rutina {i + 1}"
            }
        })

        # 🔹 Insertar tabla de ejercicios
        num_rows = len(rutina["rutina"]) + 1  # +1 para los encabezados
        num_cols = 3  # Columnas: Ejercicio, Series, Repeticiones
        table_id = f"table_{i}"
        
        requests.append({
            "createTable": {
                "objectId": table_id,
                "rows": num_rows,
                "columns": num_cols,
                "elementProperties": {
                    "pageObjectId": slide_id
                }
            }
        })

        # Insertar títulos de las columnas
        headers = ["Ejercicio", "Series", "Repeticiones"]
        for col, text in enumerate(headers):
            requests.append({
                "insertText": {
                    "objectId": table_id,
                    "cellLocation": {"rowIndex": 0, "columnIndex": col},
                    "text": text
                }
            })

        # Insertar datos en la tabla y aplicar formato a las celdas
        for row, exercise in enumerate(rutina["rutina"], start=1):
            requests.append({
                "insertText": {
                    "objectId": table_id,
                    "cellLocation": {"rowIndex": row, "columnIndex": 0},
                    "text": exercise["ejercicio"]
                }
            })
            requests.append({
                "insertText": {
                    "objectId": table_id,
                    "cellLocation": {"rowIndex": row, "columnIndex": 1},
                    "text": exercise["series"]
                }
            })
            requests.append({
                "insertText": {
                    "objectId": table_id,
                    "cellLocation": {"rowIndex": row, "columnIndex": 2},
                    "text": ", ".join(exercise["repeticiones"])
                }
            })

            # Aplicar color de fondo alterno en las filas
            background_color = "#333333" if row % 2 == 0 else "#444444"
            requests.append({
                "updateTableCellProperties": {
                    "objectId": table_id,
                    "tableRange": {
                        "location": {"rowIndex": row, "columnIndex": 0},
                        "rowSpan": 1,
                        "columnSpan": num_cols
                    },
                    "tableCellProperties": {
                        "tableCellBackgroundFill": {
                            "solidFill": {"color": {"rgbColor": _hex_to_rgb(background_color)}}
                        }
                    },
                    "fields": "tableCellBackgroundFill.solidFill.color"
                }
            })

    # 🔹 Enviar todas las solicitudes a la API
    try:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests}
        ).execute()
        print("✅ Presentación generada exitosamente.")
    except Exception as e:
        print(f"❌ ERROR al generar la presentación: {e}")
        return None

    # 🔹 Hacer la presentación pública y editable
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

