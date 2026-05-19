# =============================================================
# analysis.py
# Módulo de análisis e indicadores
# Grupo 4 — Intercambios Internacionales
# =============================================================

import os
import pandas as pd
import numpy as np

# -------------------------------------------------------------
# CONFIGURACIÓN DE CARPETAS
# -------------------------------------------------------------

CARPETA_PROCESSED = os.path.join("data", "processed")
CARPETA_RESULTADOS = os.path.join("data", "processed", "resultados")

os.makedirs(CARPETA_RESULTADOS, exist_ok=True)


# -------------------------------------------------------------
# CARGA DE DATOS
# -------------------------------------------------------------

def cargar_datos_limpios():
    ruta = os.path.join(CARPETA_PROCESSED, "datos_limpios.csv")

    if not os.path.exists(ruta):
        print("✗ No se encontró datos_limpios.csv")
        print("  Ejecuta primero clean.py")
        return None

    df = pd.read_csv(ruta, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True)

    print(f"✓ Datos cargados: {len(df)} filas, periodo {df.index.min().date()} → {df.index.max().date()}")
    return df


# -------------------------------------------------------------
# INDICADOR 1: IMPORT / EXPORT
# -------------------------------------------------------------

def analizar_importexport(df):
    print("\n--- ANÁLISIS IMPORT/EXPORT ---")

    flujos_netos = df[["neto_ES_FR_MWh", "neto_FR_DE_MWh"]].copy()

    print("\nEstadísticas globales (MWh/hora):")
    print(flujos_netos.describe().round(1))

    resumen_mensual = flujos_netos.resample("ME").agg(
        media=("neto_ES_FR_MWh", "mean"),
        total_exportado=("neto_ES_FR_MWh", lambda x: x[x > 0].sum()),
        total_importado=("neto_ES_FR_MWh", lambda x: x[x < 0].sum()),
        horas_exportando=("neto_ES_FR_MWh", lambda x: (x > 0).sum()),
        horas_importando=("neto_ES_FR_MWh", lambda x: (x < 0).sum()),
    )

    print("\nResumen mensual ES→FR:")
    print(resumen_mensual.round(1))

    ruta = os.path.join(CARPETA_RESULTADOS, "importexport_mensual.csv")
    resumen_mensual.to_csv(ruta)
    print(f"\n✓ Guardado en {ruta}")

    return resumen_mensual


# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL (esqueleto — tus compañeras añadirán sus partes)
# -------------------------------------------------------------

def analizar_todo():
    print("=" * 50)
    print("INICIANDO ANÁLISIS — GRUPO 4")
    print("=" * 50)

    df = cargar_datos_limpios()
    if df is None:
        return

    analizar_importexport(df)

    print("\n" + "=" * 50)
    print("ANÁLISIS COMPLETADO")
    print("=" * 50)


if __name__ == "__main__":
    analizar_todo()