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
# limit=3 significa que solo rellenamos hasta 3 horas seguidas de huecos
# Si hay más de 3 horas seguidas sin datos, las dejamos como NaN
# para no inventar datos en periodos largos sin información

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

def rellenar_huecos(df):
    """
    Rellena los valores nulos con interpolación lineal.

    Interpolación lineal significa: si falta el valor de las 14:00
    y tenemos 100 a las 13:00 y 200 a las 15:00, ponemos 150 a las 14:00.
    Es una estimación sencilla y razonable para datos de energía.

    Parámetros:
        df: el DataFrame con posibles huecos

    Retorna:
        El DataFrame sin huecos
    """

    indice_completo = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq="h",
        tz="UTC"
    )

    df = df.reindex(indice_completo)

    df = df.interpolate(method="linear", limit=3)

    return df


def limpiar_flujos():
    """
    Loads, cleans and combines all physical flow files.
    TODO: implement by Margot
    """
    pass

def limpiar_capacidades():
    """
    Loads and cleans the interconnection capacity (NTC) files.
    TODO: implement by Margot
    """
    pass

def limpiar_precios():
    """
    Loads and cleans the day-ahead price files for each country.
    TODO: implement by Margot
    """
    pass

def limpiar_todo():
    """
    Runs the complete cleaning of all data.
    TODO: implement by Margot
    """
    pass