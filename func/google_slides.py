import os
import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json


# 🔹 Configuración de credenciales
SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/presentations"]
# Asegúrate de que este archivo es correcto
SERVICE_ACCOUNT_FILE = "credenciales.json"


# 🔹 Cargar credenciales desde la variable de entorno
credentials_json = os.getenv("GOOGLE_CREDENTIALS")

if not credentials_json:
    raise ValueError(
        "⚠ ERROR: No se encontraron las credenciales de Google en las variables de entorno.")

try:
    # 🔹 Verifica que el JSON se está cargando correctamente
    print("🔍 Cargando credenciales desde GCP_CREDENTIALS...")
    credentials_info = json.loads(credentials_json)

    # 🔹 Usa las credenciales correctamente
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info)

    # 🔹 Configurar Google Slides API
    slides_service = build("slides", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)

    print("✅ Credenciales cargadas con éxito.")

except json.JSONDecodeError as e:
    raise ValueError(
        f"❌ ERROR: No se pudo decodificar el JSON de credenciales. {str(e)}")
except Exception as e:
    raise ValueError(f"❌ ERROR en la autenticación con Google: {str(e)}")


# credentials = service_account.Credentials.from_service_account_file(
#    SERVICE_ACCOUNT_FILE, scopes=SCOPES
# )
# slides_service = build("slides", "v1", credentials=credentials)
# drive_service = build("drive", "v3", credentials=credentials)

# 🔹 ID de la plantilla de presentación
# Cambia esto por el ID correcto
TEMPLATE_PRESENTATION_ID = "1D4IDgelJUvbQQdkc3tF-K9k11THf7Au_ZYmuRYvxExM"


def create_presentation(routine_data):
    """
    Crea una presentación en Google Slides a partir de una plantilla y formatea el contenido con tablas.
    """
    # 🔹 Copiar la plantilla en una nueva presentación
    copy = drive_service.files().copy(
        fileId=TEMPLATE_PRESENTATION_ID,
        body={"name": "Rutina de Entrenamiento Generada"}
    ).execute()
    presentation_id = copy["id"]

    for i, rutina in enumerate(routine_data):
        slide_id = f"slide_{i}"

        # 🔹 Crear una nueva diapositiva basada en la plantilla
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": [{"createSlide": {"objectId": slide_id}}]}
        ).execute()
        time.sleep(1)

        # 🔹 Crear una caja de texto para el título
        title_id = f"title_{i}"
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": [{
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
            }]}
        ).execute()
        time.sleep(1)

        # 🔹 Insertar el título en la caja de texto
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": [{
                "insertText": {
                    "objectId": title_id,
                    "text": f"Rutina {i + 1}"
                }
            }]}
        ).execute()
        time.sleep(1)

        # 🔹 Insertar una tabla bien estructurada para los ejercicios
        # Agregar una fila extra para los títulos
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

        # 🔹 Insertar títulos de las columnas
        headers = ["Ejercicio", "Series", "Repeticiones"]
        for col, text in enumerate(headers):
            slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": [{
                    "insertText": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": 0, "columnIndex": col},
                        "text": text
                    }
                }]}
            ).execute()
            time.sleep(1)

        # 🔹 Insertar datos en la tabla
        for row, exercise in enumerate(rutina["rutina"], start=1):
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
                }]}
            ).execute()
            time.sleep(1)

    # 🔹 Hacer la presentación pública y editable
    set_permissions(presentation_id)

    return f"https://docs.google.com/presentation/d/{presentation_id}"


def set_permissions(file_id):
    """
    Da permisos de edición a cualquier persona con el enlace en Google Drive.
    """
    permission = {
        "type": "anyone",
        "role": "writer"  # "writer" permite edición, "reader" solo visualización
    }

    drive_service.permissions().create(
        fileId=file_id,
        body=permission
    ).execute()
