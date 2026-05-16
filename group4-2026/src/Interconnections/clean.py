# =============================================================
# clean.py
# Módulo de limpieza y procesado de datos
# Grupo 4 — Intercambios Internacionales
# =============================================================
# Este archivo toma los datos en bruto de data/raw/ y los limpia:
#   - Corrige el formato de fechas
#   - Detecta y rellena huecos en los datos
#   - Unifica la zona horaria
#   - Combina todos los archivos en uno solo
#   - Guarda el resultado en data/processed/
# =============================================================

import os
import pandas as pd

# -------------------------------------------------------------
# CONFIGURACIÓN DE CARPETAS
# -------------------------------------------------------------

CARPETA_RAW = os.path.join("data", "raw")
CARPETA_PROCESSED = os.path.join("data", "processed")
os.makedirs(CARPETA_PROCESSED, exist_ok=True)

# -------------------------------------------------------------
# FUNCIONES DE AYUDA
# -------------------------------------------------------------

def cargar_csv(nombre_archivo):
    """
    Carga un archivo CSV de la carpeta data/raw/ y prepara
    el índice de fechas para que Python lo entienda bien.

    Parámetros:
        nombre_archivo: nombre del archivo (ej: "flujos_ES_FR.csv")

    Retorna:
        Un DataFrame con el índice como fechas, o None si hay error
    """

    ruta = os.path.join(CARPETA_RAW, nombre_archivo)

    if not os.path.exists(ruta):
        print(f"  ✗ Archivo no encontrado: {ruta}")
        return None

    try:
        df = pd.read_csv(ruta, index_col=0, parse_dates=True)

        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")

        return df

    except Exception as error:
        print(f"  ✗ Error leyendo {nombre_archivo}: {error}")
        return None


def detectar_huecos(df, nombre):
    """
    Comprueba si faltan horas en los datos.
    Los datos de ENTSO-E deberían tener un valor por cada hora.

    Parámetros:
        df    : el DataFrame a comprobar
        nombre: nombre descriptivo para mostrar en pantalla
    """

    nulos = df.isnull().sum().sum()

    if nulos > 0:
        print(f"  ⚠ {nombre}: {nulos} valores nulos encontrados")
    else:
        print(f"  ✓ {nombre}: sin valores nulos")

    indice_completo = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq="h",
        tz="UTC"
    )

    horas_que_faltan = indice_completo.difference(df.index)

    if len(horas_que_faltan) > 0:
        print(f"  ⚠ {nombre}: faltan {len(horas_que_faltan)} horas en el índice")
    else:
        print(f"  ✓ {nombre}: índice de fechas completo")

