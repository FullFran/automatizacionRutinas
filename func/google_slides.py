import os
import time
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

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
ROUTINE_LAYOUT_ID = os.getenv("ROUTINE_LAYOUT_ID")  # ID del layout específico para rutinas

def create_presentation(routine_data):
    """
    Crea una presentación en Google Slides basada en una plantilla, aplicando estilos profesionales.
    """
    print("🚀 Creando una nueva presentación desde la plantilla...")

    # Copiar la plantilla en una nueva presentación
    copy = drive_service.files().copy(
        fileId=TEMPLATE_PRESENTATION_ID,
        body={"name": "Rutina de Entrenamiento Generada"}
    ).execute()
    presentation_id = copy["id"]
    print(f"✅ Presentación creada: {presentation_id}")

    # 🔹 Obtener las diapositivas existentes
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation.get('slides', [])
    num_existing_slides = len(slides)

    # 🔹 Crear diapositivas para cada rutina usando el layout predefinido
    requests = []
    for i, rutina in enumerate(routine_data):
        slide_id = f"slide_{i + num_existing_slides}"  # Evitamos sobrescribir IDs existentes

        # Crear una nueva diapositiva con el layout personalizado
        requests.append({
            "createSlide": {
                "objectId": slide_id,
                "insertionIndex": str(i + num_existing_slides),
                "slideLayoutReference": {
                    "objectId": ROUTINE_LAYOUT_ID  # Usamos el layout específico para rutinas
                }
            }
        })

        # 🔹 Insertar la tabla en la diapositiva
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

        # 🔹 Insertar títulos de las columnas
        headers = ["Ejercicio", "Series", "Repeticiones"]
        for col, text in enumerate(headers):
            requests.append({
                "insertText": {
                    "objectId": table_id,
                    "cellLocation": {"rowIndex": 0, "columnIndex": col},
                    "text": text
                }
            })
            # Aplicar estilo a los encabezados (blanco y negrita)
            requests.append({
                "updateTextStyle": {
                    "objectId": table_id,
                    "cellLocation": {"rowIndex": 0, "columnIndex": col},
                    "style": {
                        "bold": True,
                        "foregroundColor": {
                            "opaqueColor": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}  # Blanco
                        }
                    },
                    "fields": "bold,foregroundColor"
                }
            })

        # 🔹 Insertar datos en la tabla y aplicar formato
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

            # Aplicar color de fondo alterno a las filas de la tabla
            row_color = {"red": 0.1, "green": 0.2, "blue": 0.5} if row % 2 == 0 else {"red": 0.2, "green": 0.4, "blue": 0.8}

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
                            "solidFill": {
                                "color": {"rgbColor": row_color}
                            }
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
    print("✅ Permisos de edición configurados.")
