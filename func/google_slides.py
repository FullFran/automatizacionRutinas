import os
import time
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

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

if not TEMPLATE_PRESENTATION_ID:
    raise ValueError("⚠ ERROR: No se encontró TEMPLATE_PRESENTATION_ID en las variables de entorno.")


def create_presentation(routine_data):
    """
    Crea una presentación en Google Slides basada en una plantilla con diseño profesional y robusto.
    """
    print("🚀 Creando una nueva presentación desde la plantilla...")

    try:
        copy = drive_service.files().copy(
            fileId=TEMPLATE_PRESENTATION_ID,
            body={"name": "Rutina de Entrenamiento Generada"}
        ).execute()
        presentation_id = copy.get("id")

        if not presentation_id:
            print("❌ ERROR: No se pudo obtener el ID de la nueva presentación.")
            return None

        print(f"✅ Presentación creada: {presentation_id}")

    except Exception as e:
        print(f"❌ ERROR al copiar la plantilla: {str(e)}")
        return None

    requests_text = []
    requests_format = []

    try:
        for i, rutina in enumerate(routine_data):
            slide_id = f"slide_{i}"
            title_id = f"title_{i}"
            table_id = f"table_{i}"

            # 🔹 Crear una nueva diapositiva basada en una plantilla
            requests_text.append({"createSlide": {}})

            # 🔹 Cambiar fondo a negro (se usa "pageBackgroundFill" dentro de updatePageProperties correctamente)
            requests_text.append({
                "updatePageProperties": {
                    "objectId": slide_id,
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

            # 🔹 Crear cuadro de texto para el título
            requests_text.append({
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
                            "scaleX": 1, "scaleY": 1, "translateX": 50, "translateY": 20, "unit": "PT"
                        }
                    }
                }
            })

            # 🔹 Insertar título
            requests_text.append({
                "insertText": {
                    "objectId": title_id,
                    "text": f"Rutina {i + 1}"
                }
            })

            # 🔹 Crear tabla para ejercicios
            num_rows = len(rutina["rutina"]) + 1
            num_cols = 3

            requests_text.append({
                "createTable": {
                    "objectId": table_id,
                    "rows": num_rows,
                    "columns": num_cols,
                    "elementProperties": {
                        "pageObjectId": slide_id
                    }
                }
            })

            # 🔹 Insertar títulos de columna
            headers = ["Ejercicio", "Series", "Repeticiones"]
            for col, text in enumerate(headers):
                requests_text.append(_insert_table_text(table_id, 0, col, text))
                requests_format.append(_format_table_cell(table_id, 0, col, "#444444"))  # Color gris oscuro

            # 🔹 Insertar datos en la tabla
            for row, exercise in enumerate(rutina["rutina"], start=1):
                color = "#222222" if row % 2 == 0 else "#333333"  # Alternar colores de fila
                requests_text.append(_insert_table_text(table_id, row, 0, exercise["ejercicio"]))
                requests_text.append(_insert_table_text(table_id, row, 1, exercise["series"]))
                requests_text.append(_insert_table_text(table_id, row, 2, ", ".join(exercise["repeticiones"])))

                requests_format.append(_format_table_cell(table_id, row, 0, color))
                requests_format.append(_format_table_cell(table_id, row, 1, color))
                requests_format.append(_format_table_cell(table_id, row, 2, color))

        # 🔹 Ejecutar batchUpdate para insertar texto y estructura
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests_text}
        ).execute()

        # 🔹 Ejecutar batchUpdate para aplicar formatos
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests_format}
        ).execute()

        print("✅ Presentación generada con éxito.")

    except Exception as e:
        print(f"❌ ERROR al generar la presentación: {str(e)}")
        return None

    # 🔹 Configurar permisos de edición
    set_permissions(presentation_id)

    return f"https://docs.google.com/presentation/d/{presentation_id}"


def set_permissions(file_id):
    """
    Da permisos de edición a cualquier persona con el enlace en Google Drive.
    """
    try:
        drive_service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "writer"}
        ).execute()
        print(f"✅ Permisos públicos agregados para el archivo {file_id}")
    except Exception as e:
        print(f"❌ ERROR al configurar permisos: {str(e)}")


def _hex_to_rgb(hex_color):
    """
    Convierte un color HEX a formato RGB para la API de Google Slides.
    """
    hex_color = hex_color.lstrip("#")
    return {"red": int(hex_color[0:2], 16) / 255, "green": int(hex_color[2:4], 16) / 255, "blue": int(hex_color[4:6], 16) / 255}


def _insert_table_text(table_id, row, col, text):
    """
    Inserta texto en una celda de tabla.
    """
    return {
        "insertText": {
            "objectId": table_id,
            "cellLocation": {"rowIndex": row, "columnIndex": col},
            "text": text
        }
    }


def _format_table_cell(table_id, row, col, background_color):
    """
    Aplica color de fondo a una celda de tabla.
    """
    return {
        "updateTableCellProperties": {
            "objectId": table_id,
            "tableRange": {
                "location": {"rowIndex": row, "columnIndex": col},
                "rowSpan": 1,
                "columnSpan": 1
            },
            "tableCellProperties": {
                "backgroundFill": {
                    "solidFill": {"color": {"rgbColor": _hex_to_rgb(background_color)}}
                }
            },
            "fields": "tableCellProperties.backgroundFill.solidFill.color"
        }
    }

