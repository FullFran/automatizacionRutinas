mport os
import time
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

# -------------------------
# Configuración de Credenciales
# -------------------------
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/presentations"
]

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

# -------------------------
# Variables de la plantilla
# -------------------------
TEMPLATE_PRESENTATION_ID = os.getenv("TEMPLATE_PRESENTATION_ID")
ROUTINE_LAYOUT_ID = os.getenv("ROUTINE_LAYOUT_ID")  # ID del layout específico para rutinas

if not TEMPLATE_PRESENTATION_ID:
    raise ValueError("⚠ ERROR: No se encontró TEMPLATE_PRESENTATION_ID en las variables de entorno.")
if not ROUTINE_LAYOUT_ID:
    raise ValueError("⚠ ERROR: No se encontró ROUTINE_LAYOUT_ID en las variables de entorno.")

# -------------------------
# Funciones Auxiliares
# -------------------------
def _hex_to_rgb(hex_color):
    """Convierte un color HEX a formato RGB para la API de Google Slides."""
    hex_color = hex_color.lstrip("#")
    return {
        "red": int(hex_color[0:2], 16) / 255.0,
        "green": int(hex_color[2:4], 16) / 255.0,
        "blue": int(hex_color[4:6], 16) / 255.0
    }

def _insert_table_text(table_id, row, col, text):
    """Genera la solicitud para insertar texto en una celda."""
    return {
        "insertText": {
            "objectId": table_id,
            "cellLocation": {"rowIndex": row, "columnIndex": col},
            "text": text
        }
    }

def _format_table_cell(table_id, row, col, background_color):
    """Genera la solicitud para actualizar el fondo de una celda."""
    return {
        "updateTableCellProperties": {
            "objectId": table_id,
            "tableRange": {
                "location": {"rowIndex": row, "columnIndex": col},
                "rowSpan": 1,
                "columnSpan": 1
            },
            "tableCellProperties": {
                "tableCellBackgroundFill": {
                    "solidFill": {
                        "color": {"rgbColor": _hex_to_rgb(background_color)}
                    }
                }
            },
            "fields": "tableCellBackgroundFill.solidFill.color"
        }
    }

def set_permissions(file_id):
    """Configura permisos públicos para la presentación."""
    permission = {
        "type": "anyone",
        "role": "writer"
    }
    drive_service.permissions().create(
        fileId=file_id,
        body=permission
    ).execute()
    print("✅ Permisos de edición configurados.")

# -------------------------
# Función principal: crear presentación
# -------------------------
def create_presentation(routine_data):
    """
    Crea una presentación en Google Slides basada en una plantilla,
    utilizando un layout predefinido y aplicando estilos profesionales.
    """
    print("🚀 Creando una nueva presentación desde la plantilla...")

    # Copiar la plantilla
    copy = drive_service.files().copy(
        fileId=TEMPLATE_PRESENTATION_ID,
        body={"name": "Rutina de Entrenamiento Generada"}
    ).execute()
    presentation_id = copy["id"]
    print(f"✅ Presentación creada: {presentation_id}")

    # Obtener las diapositivas existentes
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation.get('slides', [])
    num_existing_slides = len(slides)

    # Definir posiciones fijas (márgenes)
    title_x, title_y = 50, 10     # El título estará muy arriba
    table_x, table_y = 50, 80     # La tabla estará debajo del título, centrada horizontalmente

    # Variables para ajustar tamaño de la tabla (se pueden ajustar dinámicamente)
    default_table_width = 600
    default_table_height = 250

    requests_text = []  # Para insertar contenido (crear diapositivas, insertar textos, crear tablas)
    requests_format = []  # Para aplicar estilos (colores, fuentes)

    for i, rutina in enumerate(routine_data):
        # Crear nueva diapositiva usando el layout predefinido
        slide_id = f"slide_{i + num_existing_slides}"
        requests_text.append({
            "createSlide": {
                "objectId": slide_id,
                "insertionIndex": str(i + num_existing_slides),
                "slideLayoutReference": {
                    "layoutId": ROUTINE_LAYOUT_ID
                }
            }
        })

        # Insertar título en la diapositiva: "Día 1", "Día 2", etc.
        title_id = f"title_{i}"
        requests_text.append({
            "createShape": {
                "objectId": title_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "height": {"magnitude": 50, "unit": "PT"},
                        "width": {"magnitude": 600, "unit": "PT"}
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
        requests_text.append({
            "insertText": {
                "objectId": title_id,
                "text": f"Día {i + 1}"
            }
        })
        requests_format.append({
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
        requests_format.append({
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

        # Insertar tabla en la diapositiva
        num_rows = len(rutina["rutina"]) + 1  # Encabezado + filas de datos
        num_cols = 3
        table_id = f"table_{i}"
        # Ajustar tamaño de la tabla (se puede modificar según necesidad)
        table_width = default_table_width
        table_height = default_table_height

        requests_text.append({
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

        # Insertar encabezados de la tabla
        headers = ["Ejercicio", "Series", "Repeticiones"]
        for col, header_text in enumerate(headers):
            requests_text.append(_insert_table_text(table_id, 0, col, header_text))
            requests_format.append({
                "updateTextStyle": {
                    "objectId": table_id,
                    "cellLocation": {"rowIndex": 0, "columnIndex": col},
                    "style": {
                        "bold": True,
                        "foregroundColor": {
                            "opaqueColor": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}
                        }
                    },
                    "fields": "bold,foregroundColor"
                }
            })

        # Insertar datos en la tabla y aplicar colores alternos
        for row, exercise in enumerate(rutina["rutina"], start=1):
            requests_text.append(_insert_table_text(table_id, row, 0, exercise["ejercicio"]))
            requests_text.append(_insert_table_text(table_id, row, 1, exercise["series"]))
            requests_text.append(_insert_table_text(table_id, row, 2, ", ".join(exercise["repeticiones"])))
            # Definir color de fondo alternado: tonos de gris
            row_color = "#333333" if row % 2 == 0 else "#444444"
            for col in range(num_cols):
                requests_format.append(_format_table_cell(table_id, row, col, row_color))

    # Enviar primero las solicitudes de contenido
    try:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests_text}
        ).execute()
        print("✅ Contenido insertado exitosamente.")
    except Exception as e:
        print(f"❌ ERROR al insertar contenido: {e}")
        return None

    # Enviar luego las solicitudes de formato
    try:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests_format}
        ).execute()
        print("✅ Formato aplicado exitosamente.")
    except Exception as e:
        print(f"❌ ERROR al aplicar formato: {e}")
        return None

    set_permissions(presentation_id)
    print("✅ Presentación generada exitosamente.")
    return f"https://docs.google.com/presentation/d/{presentation_id}"


