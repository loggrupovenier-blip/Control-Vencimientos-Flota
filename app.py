import os
import io
import mimetypes
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory

import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


# ============================================================
# CONFIGURACIÓN
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-secreta-cambiar")

SPREADSHEET_ID = "1qGR5-dTg4us73S9YcYzSiLO_NMFKbr5N8JpylQaP9D8"
DRIVE_FOLDER_ID = "1Q8wGdA3YMjCNIpXllxH4AYzNcuf07Vzf"

HOJAS = [
    "Camion T1",
    "Camion T2",
    "Autoelevadores",
    "Choferes y Ayudantes"
]

# Columnas que la aplicación agrega si no existen
COLUMNAS_APP = [
    "APP_ID",
    "APP_PATENTE",
    "APP_DOCUMENTO",
    "APP_FECHA_VENCIMIENTO",
    "APP_FOTO",
    "APP_FECHA_CARGA"
]

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "pdf"
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ============================================================
# GOOGLE
# ============================================================

def obtener_credenciales():
    """
    Las credenciales se obtienen desde la variable de entorno
    GOOGLE_CREDENTIALS de Render.

    La variable debe contener el JSON completo de la cuenta
    de servicio de Google.
    """

    credentials_json = os.environ.get("GOOGLE_CREDENTIALS")

    if not credentials_json:
        raise Exception(
            "No está configurada la variable GOOGLE_CREDENTIALS "
            "en Render."
        )

    import json

    info = json.loads(credentials_json)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        info,
        scopes=scopes
    )

    return credentials


def obtener_cliente_google():
    credentials = obtener_credenciales()

    cliente = gspread.authorize(credentials)

    return cliente


def obtener_drive():
    credentials = obtener_credenciales()

    return build(
        "drive",
        "v3",
        credentials=credentials
    )


# ============================================================
# GOOGLE SHEETS
# ============================================================

def obtener_hoja(nombre_hoja):
    cliente = obtener_cliente_google()

    spreadsheet = cliente.open_by_key(SPREADSHEET_ID)

    worksheet = spreadsheet.worksheet(nombre_hoja)

    return worksheet


def preparar_hoja(nombre_hoja):
    """
    Verifica que las columnas necesarias para la aplicación
    existan. Si no existen, las agrega al final.
    """

    worksheet = obtener_hoja(nombre_hoja)

    encabezados = worksheet.row_values(1)

    columnas_faltantes = []

    for columna in COLUMNAS_APP:
        if columna not in encabezados:
            columnas_faltantes.append(columna)

    if columnas_faltantes:

        ultima_columna = len(encabezados)

        nuevas_columnas = encabezados + columnas_faltantes

        worksheet.update(
            "A1",
            [nuevas_columnas]
        )

    return worksheet


def obtener_datos_hoja(nombre_hoja):

    worksheet = preparar_hoja(nombre_hoja)

    valores = worksheet.get_all_records()

    return valores


# ============================================================
# DRIVE
# ============================================================

def subir_archivo_drive(archivo, nombre_archivo):

    if not archivo:
        raise Exception("No se recibió ningún archivo.")

    contenido = archivo.read()

    if not contenido:
        raise Exception("El archivo está vacío.")

    if len(contenido) > MAX_FILE_SIZE:
        raise Exception(
            "La foto supera el tamaño máximo permitido de 10 MB."
        )

    mimetype = archivo.mimetype

    if not mimetype:
        mimetype = mimetypes.guess_type(
            nombre_archivo
        )[0]

    if not mimetype:
        mimetype = "application/octet-stream"

    drive = obtener_drive()

    metadata = {
        "name": nombre_archivo,
        "parents": [DRIVE_FOLDER_ID]
    }

    media = MediaIoBaseUpload(
        io.BytesIO(contenido),
        mimetype=mimetype,
        resumable=False
    )

    resultado = drive.files().create(
        body=metadata,
        media_body=media,
        fields="id,name,webViewLink"
    ).execute()

    archivo_id = resultado["id"]

    # Permitimos visualizar el archivo mediante el enlace.
    try:
        drive.permissions().create(
            fileId=archivo_id,
            body={
                "type": "anyone",
                "role": "reader"
            }
        ).execute()
    except Exception:
        pass

    link = resultado.get(
        "webViewLink",
        f"https://drive.google.com/file/d/{archivo_id}/view"
    )

    return archivo_id, link


# ============================================================
# UTILIDADES
# ============================================================

def extension_permitida(nombre):

    if "." not in nombre:
        return False

    extension = nombre.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def limpiar_nombre(nombre):

    caracteres_no_permitidos = [
        "/", "\\", ":", "*", "?",
        '"', "<", ">", "|"
    ]

    for caracter in caracteres_no_permitidos:
        nombre = nombre.replace(caracter, "-")

    return nombre.strip()


def convertir_fecha(fecha_texto):

    if not fecha_texto:
        return None

    try:
        return datetime.strptime(
            fecha_texto,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return None


def estado_vencimiento(fecha_vencimiento):

    if not fecha_vencimiento:
        return "SIN FECHA"

    try:

        if isinstance(fecha_vencimiento, date):
            fecha = fecha_vencimiento

        else:
            fecha = datetime.strptime(
                str(fecha_vencimiento),
                "%Y-%m-%d"
            ).date()

        hoy = date.today()

        dias = (fecha - hoy).days

        if dias < 0:
            return "VENCIDO"

        if dias <= 30:
            return "POR VENCER"

        return "VIGENTE"

    except Exception:

        return "SIN FECHA"


def obtener_columna_indice(encabezados, nombre):

    try:
        return encabezados.index(nombre) + 1

    except ValueError:
        return None


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def index():

    resumen = []

    total_vencidos = 0
    total_por_vencer = 0
    total_vigentes = 0

    for hoja in HOJAS:

        try:

            datos = obtener_datos_hoja(hoja)

            vencidos = 0
            por_vencer = 0
            vigentes = 0

            for fila in datos:

                fecha = fila.get(
                    "APP_FECHA_VENCIMIENTO"
                )

                estado = estado_vencimiento(fecha)

                if estado == "VENCIDO":
                    vencidos += 1

                elif estado == "POR VENCER":
                    por_vencer += 1

                elif estado == "VIGENTE":
                    vigentes += 1

            total_vencidos += vencidos
            total_por_vencer += por_vencer
            total_vigentes += vigentes

            resumen.append({
                "nombre": hoja,
                "vencidos": vencidos,
                "por_vencer": por_vencer,
                "vigentes": vigentes
            })

        except Exception as e:

            resumen.append({
                "nombre": hoja,
                "vencidos": 0,
                "por_vencer": 0,
                "vigentes": 0,
                "error": str(e)
            })

    return render_template(
        "index.html",
        resumen=resumen,
        total_vencidos=total_vencidos,
        total_por_vencer=total_por_vencer,
        total_vigentes=total_vigentes
    )


# ============================================================
# LISTADO
# ============================================================

@app.route("/documentacion/<nombre_hoja>")
def documentacion(nombre_hoja):

    if nombre_hoja not in HOJAS:
        return "Hoja no válida", 404

    try:

        datos = obtener_datos_hoja(nombre_hoja)

        registros = []

        for fila in datos:

            patente = fila.get(
                "APP_PATENTE",
                ""
            )

            documento = fila.get(
                "APP_DOCUMENTO",
                ""
            )

            fecha = fila.get(
                "APP_FECHA_VENCIMIENTO",
                ""
            )

            foto = fila.get(
                "APP_FOTO",
                ""
            )

            estado = estado_vencimiento(fecha)

            registros.append({
                "patente": patente,
                "documento": documento,
                "fecha": fecha,
                "foto": foto,
                "estado": estado
            })

        return render_template(
            "documentacion.html",
            nombre_hoja=nombre_hoja,
            registros=registros
        )

    except Exception as e:

        flash(
            f"Error al cargar la información: {e}",
            "danger"
        )

        return redirect(url_for("index"))


# ============================================================
# FORMULARIO DE CARGA
# ============================================================

@app.route("/cargar")
def cargar():

    return render_template(
        "cargar.html",
        hojas=HOJAS
    )


# ============================================================
# GUARDAR DOCUMENTACIÓN
# ============================================================

@app.route("/guardar", methods=["POST"])
def guardar():

    nombre_hoja = request.form.get(
        "hoja",
        ""
    ).strip()

    patente = request.form.get(
        "patente",
        ""
    ).strip()

    documento = request.form.get(
        "documento",
        ""
    ).strip()

    fecha_vencimiento = request.form.get(
        "fecha_vencimiento",
        ""
    ).strip()

    archivo = request.files.get(
        "foto"
    )

    # --------------------------------------------------------
    # VALIDACIONES OBLIGATORIAS
    # --------------------------------------------------------

    if nombre_hoja not in HOJAS:

        flash(
            "Debe seleccionar una categoría válida.",
            "danger"
        )

        return redirect(url_for("cargar"))

    if not patente:

        flash(
            "La patente es obligatoria.",
            "danger"
        )

        return redirect(url_for("cargar"))

    if not documento:

        flash(
            "El documento es obligatorio.",
            "danger"
        )

        return redirect(url_for("cargar"))

    if not fecha_vencimiento:

        flash(
            "La fecha de vencimiento es obligatoria.",
            "danger"
        )

        return redirect(url_for("cargar"))

    if not archivo or not archivo.filename:

        flash(
            "La foto del documento es obligatoria.",
            "danger"
        )

        return redirect(url_for("cargar"))

    if not extension_permitida(
        archivo.filename
    ):

        flash(
            "Formato de archivo no permitido. "
            "Utilice JPG, JPEG, PNG, WEBP o PDF.",
            "danger"
        )

        return redirect(url_for("cargar"))

    fecha = convertir_fecha(
        fecha_vencimiento
    )

    if not fecha:

        flash(
            "La fecha de vencimiento no es válida.",
            "danger"
        )

        return redirect(url_for("cargar"))

    # --------------------------------------------------------
    # NOMBRE DEL ARCHIVO
    # --------------------------------------------------------

    extension = archivo.filename.rsplit(
        ".",
        1
    )[1].lower()

    nombre_archivo = (
        f"{patente} - {documento}.{extension}"
    )

    nombre_archivo = limpiar_nombre(
        nombre_archivo
    )

    try:

        # ----------------------------------------------------
        # SUBIR FOTO A DRIVE
        # ----------------------------------------------------

        archivo_id, link = subir_archivo_drive(
            archivo,
            nombre_archivo
        )

        # ----------------------------------------------------
        # GOOGLE SHEETS
        # ----------------------------------------------------

        worksheet = preparar_hoja(
            nombre_hoja
        )

        encabezados = worksheet.row_values(
            1
        )

        # ----------------------------------------------------
        # GENERAR ID
        # ----------------------------------------------------

        import uuid

        app_id = str(
            uuid.uuid4()
        )

        fecha_carga = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        # ----------------------------------------------------
        # BUSCAR PRIMERA FILA VACÍA
        # ----------------------------------------------------

        siguiente_fila = (
            len(
                worksheet.get_all_values()
            ) + 1
        )

        # ----------------------------------------------------
        # CREAR FILA
        # ----------------------------------------------------

        nueva_fila = [
            ""
            for _ in encabezados
        ]

        valores = {
            "APP_ID": app_id,
            "APP_PATENTE": patente,
            "APP_DOCUMENTO": documento,
            "APP_FECHA_VENCIMIENTO":
                fecha.strftime("%Y-%m-%d"),
            "APP_FOTO": link,
            "APP_FECHA_CARGA": fecha_carga
        }

        for columna, valor in valores.items():

            indice = obtener_columna_indice(
                encabezados,
                columna
            )

            if indice:

                nueva_fila[indice - 1] = valor

        worksheet.insert_row(
            nueva_fila,
            siguiente_fila
        )

        flash(
            "Documentación cargada correctamente.",
            "success"
        )

        return redirect(
            url_for(
                "documentacion",
                nombre_hoja=nombre_hoja
            )
        )

    except Exception as e:

        flash(
            f"Error al guardar la documentación: {e}",
            "danger"
        )

        return redirect(
            url_for("cargar")
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# EJECUCIÓN LOCAL
# ============================================================

if __name__ == "__main__":

    puerto = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=puerto,
        debug=False
    )