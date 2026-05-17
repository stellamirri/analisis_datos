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
    Carga, limpia y combina todos los archivos de flujos físicos.

    Los flujos entre dos países vienen en dos archivos : uno de ida y uno de vuelta.
    Este programa les combina en un solo DataFrame y calcula el flujo neto.

    Ejemplo:
    Flujo neto ES→FR = flujo ES→FR - flujo FR→ES
    Si es positivo: España exporta a Francia
    Si es negativo: España importa de Francia

    Retorna:
        Un DataFrame con todos los flujos limpios y el flujo neto
    """

    print("\nLimpiando flujos físicos...")

    # Carga los 4 archivos de datos
    flujo_es_fr = cargar_csv("flujos_ES_FR.csv")
    flujo_fr_es = cargar_csv("flujos_FR_ES.csv")
    flujo_fr_de = cargar_csv("flujos_FR_DE.csv")
    flujo_de_fr = cargar_csv("flujos_DE_FR.csv")

    # Comproba que se cargaron bien
    archivos = {
        "ES→FR": flujo_es_fr,
        "FR→ES": flujo_fr_es,
        "FR→DE": flujo_fr_de,
        "DE→FR": flujo_de_fr
    }

    for nombre, df in archivos.items():
        if df is not None:
            detectar_huecos(df, nombre)
    
    # Rellena huecos en cada archivo
    flujo_es_fr = rellenar_huecos(flujo_es_fr) if flujo_es_fr is not None else None
    flujo_fr_es = rellenar_huecos(flujo_fr_es) if flujo_fr_es is not None else None
    flujo_fr_de = rellenar_huecos(flujo_fr_de) if flujo_fr_de is not None else None
    flujo_de_fr = rellenar_huecos(flujo_de_fr) if flujo_de_fr is not None else None

    # Combina todo en un solo DataFrame : cada columna es un flujo diferente
    df_flujos = pd.DataFrame({
        "flujo_ES_FR_MWh": flujo_es_fr.iloc[:, 0] if flujo_es_fr is not None else None,
        "flujo_FR_ES_MWh": flujo_fr_es.iloc[:, 0] if flujo_fr_es is not None else None,
        "flujo_FR_DE_MWh": flujo_fr_de.iloc[:, 0] if flujo_fr_de is not None else None,
        "flujo_DE_FR_MWh": flujo_de_fr.iloc[:, 0] if flujo_de_fr is not None else None,
    })

    # Calcula flujos netos (exportación neta de cada país hacia el vecino) : àositivo = exporta, Negativo = importa
    df_flujos["neto_ES_FR_MWh"] = df_flujos["flujo_ES_FR_MWh"] - df_flujos["flujo_FR_ES_MWh"]
    df_flujos["neto_FR_DE_MWh"] = df_flujos["flujo_FR_DE_MWh"] - df_flujos["flujo_DE_FR_MWh"]

    print(f"  ✓ Flujos combinados: {len(df_flujos)} filas, {len(df_flujos.columns)} columnas")
    return df_flujos


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