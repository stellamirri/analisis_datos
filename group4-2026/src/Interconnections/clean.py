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