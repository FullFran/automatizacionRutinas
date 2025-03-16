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

# 🔹 ID de la plantilla de presentación y layout de rutinas
TEMPLATE_PRESENTATION_ID = os.getenv("TEMPLATE_PRESENTATION_ID")
ROUTINE_LAYOUT_ID = os.getenv("ROUTINE_LAYOUT_ID")  # ID del layout específico para rutinas

if not TEMPLATE_PRESENTATION_ID:
    raise ValueError("⚠ ERROR: No se encontró TEMPLATE_PRESENTATION_ID en las variables de entorno.")

if not ROUTINE_LAYOUT_ID:
    raise ValueError("⚠ ERROR: No se encontró ROUTINE_LAYOUT_ID en las variables de entorno.")

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

    # 🔹 Configuración de posiciones
    title_x, title_y = 50, 20  # Posición del título
    table_x, table_y = 80, 100  # Posición de la tabla (ajustable dinámicamente)

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
                    "layoutId": ROUTINE_LAYOUT_ID  # Usamos el layout específico para rutinas
                }
            }
        })

        # 🔹 Insertar título de la rutina
        title_id = f"title_{i}"
        requests.append({
            "createShape": {
                "objectId": title_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "height": {"magnitude": 50, "unit": "PT"},
                        "width": {"magnitude": 600, "unit": "PT"}  # Más ancho para centrado
                    },
                    "transform": {
                        "scaleX": 1, "scaleY": 1,
                        "translateX": title_x,
                        "translateY": title_y,
                        "unit": "PT"
                    }
                }
            }
        })
        requests.append({
            "insertText": {
                "objectId": title_id,
                "text": f"Día {i + 1}"
            }
        })
        requests.append({
            "updateTextStyle": {
                "objectId": title_id,
                "style": {
                    "bold": True,
                    "fontSize": {"magnitude": 24, "unit": "PT"},
                    "foregroundColor": {
                        "opaqueColor": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}  # Blanco
                    }
                },
                "fields": "bold,fontSize,foregroundColor"
            }
        })
        requests.append({
            "updateShapeProperties": {
                "objectId": title_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {
                            "color": {"rgbColor": {"red": 0.0, "green": 0.2, "blue": 0.8}}  # Azul oscuro
                        }
                    }
                },
                "fields": "shapeBackgroundFill.solidFill.color"
            }
        })

        # 🔹 Ajuste dinámico del tamaño de la tabla
        num_rows = len(rutina["rutina"]) + 1  # +1 para los encabezados
        num_cols = 3  # Columnas: Ejercicio, Series, Repeticiones

        table_width = 600 if num_rows <= 10 else 500  # Ajuste si hay muchas filas
        table_height = 250 if num_rows <= 10 else 350  # Ajuste dinámico de altura

        # 🔹 Insertar la tabla en la diapositiva
        table_id = f"table_{i}"
        requests.append({
            "createTable": {
                "objectId": table_id,
                "rows": num_rows,
                "columns": num_cols,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "height": {"magnitude": table_height, "unit": "PT"},
                        "width": {"magnitude": table_width, "unit": "PT"}
                    },
                    "transform": {
                        "scaleX": 1, "scaleY": 1,
                        "translateX": table_x,
                        "translateY": table_y,
                        "unit": "PT"
                    }
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

        # 🔹 Insertar datos en la tabla y aplicar colores alternos
        for row, exercise in enumerate(rutina["rutina"], start=1):
            row_color = {"red": 0.1, "green": 0.2, "blue": 0.5} if row % 2 == 0 else {"red": 0.2, "green": 0.4, "blue": 0.8}

            for col, text in enumerate([exercise["ejercicio"], exercise["series"], ", ".join(exercise["repeticiones"])]):
                requests.append({"insertText": {"objectId": table_id, "cellLocation": {"rowIndex": row, "columnIndex": col}, "text": text}})
                requests.append({
                    "updateTableCellProperties": {
                        "objectId": table_id,
                        "cellLocation": {"rowIndex": row, "columnIndex": col},
                        "tableCellProperties": {"tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": row_color}}}},
                        "fields": "tableCellBackgroundFill.solidFill.color"
                    }
                })

    slides_service.presentations().batchUpdate(presentationId=presentation_id, body={"requests": requests}).execute()
    set_permissions(presentation_id)
    return f"https://docs.google.com/presentation/d/{presentation_id}"
