# Este archivo genera gráficas a partir de los resultados
# calculados por analysis.py
# =============================================================

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------------------

CARPETA_PROCESSED  = os.path.join("data", "processed")
CARPETA_RESULTADOS = os.path.join("data", "processed", "resultados")
CARPETA_FIGURAS    = os.path.join("figures")

# Creamos la carpeta figures si no existe
os.makedirs(CARPETA_FIGURAS, exist_ok=True)

# Colores por país
COLORES = {
    "ES": "#E63946",
    "FR": "#2196F3",
    "DE": "#4CAF50",
}


# -------------------------------------------------------------
# FUNCIÓN DE AYUDA
# -------------------------------------------------------------

def guardar_figura(nombre_archivo):
    """
    Guarda la figura actual en la carpeta figures/
    """
    ruta = os.path.join(CARPETA_FIGURAS, nombre_archivo)
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ Guardada: {ruta}")


# -------------------------------------------------------------
# GRÁFICA 1: HEATMAP DE CONGESTIONES
# -------------------------------------------------------------

def grafica_heatmap_congestiones():
    """
    Genera un mapa de calor que muestra el porcentaje de uso
    de la interconexión ES-FR por hora del día y mes.

    Esto nos permite ver en qué momentos hay más congestión.
    """

    print("\nGenerando heatmap de congestiones...")

    # Cargamos los datos limpios
    ruta = os.path.join(CARPETA_PROCESSED, "datos_limpios.csv")
    if not os.path.exists(ruta):
        print("  ✗ No encontrado datos_limpios.csv — ejecuta clean.py primero")
        return

    df = pd.read_csv(ruta, index_col=0, parse_dates=True)
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")

    # Calculamos el porcentaje de uso
    df["uso_ES_FR_pct"] = (
        df["flujo_ES_FR_MWh"].abs() / df["ntc_ES_FR_MW"] * 100
    ).round(1)

    # Añadimos columnas de hora y mes
    df["hora"] = df.index.hour
    df["mes"]  = df.index.strftime("%b")

    # Tabla pivote: filas = horas, columnas = meses
    tabla = df.pivot_table(
        values="uso_ES_FR_pct",
        index="hora",
        columns="mes",
        aggfunc="mean"
    ).round(1)

    # Creamos la figura
    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        tabla,
        ax=ax,
        cmap="YlOrRd",
        annot=True,
        fmt=".0f",
        linewidths=0.3,
        cbar_kws={"label": "Uso de la interconexión (%)"},
        vmin=0,
        vmax=100
    )

    ax.set_title(
        "Uso medio de la interconexión ES→FR por hora y mes (%)",
        fontweight="bold",
        pad=15
    )
    ax.set_xlabel("Mes")
    ax.set_ylabel("Hora del día")

    plt.tight_layout()
    guardar_figura("heatmap_congestiones.png")


# -------------------------------------------------------------
# GRÁFICA 2: RESUMEN MENSUAL DE CONGESTIONES
# -------------------------------------------------------------

def grafica_resumen_congestiones():
    """
    Genera un gráfico de barras con el número de horas
    congestionadas por mes en cada interconexión.
    """

    print("\nGenerando resumen mensual de congestiones...")

    ruta = os.path.join(CARPETA_RESULTADOS, "congestiones_mensual.csv")
    if not os.path.exists(ruta):
        print("  ✗ No encontrado congestiones_mensual.csv — ejecuta analysis.py primero")
        return

    df = pd.read_csv(ruta, index_col=0, parse_dates=True)

    fig, ax = plt.subplots(figsize=(10, 5))

    x = range(len(df))
    ancho = 0.35

    # Barras para ES-FR y FR-DE
    ax.bar(
        [i - ancho/2 for i in x],
        df["horas_congestion_ES_FR"],
        width=ancho,
        color=COLORES["ES"],
        alpha=0.8,
        label="ES → FR"
    )
    ax.bar(
        [i + ancho/2 for i in x],
        df["horas_congestion_FR_DE"],
        width=ancho,
        color=COLORES["FR"],
        alpha=0.8,
        label="FR → DE"
    )

    ax.set_title(
        "Horas de congestión por mes (uso ≥ 90% NTC)",
        fontweight="bold"
    )
    ax.set_ylabel("Número de horas")
    ax.set_xticks(list(x))
    ax.set_xticklabels(
        [str(d)[:7] for d in df.index],
        rotation=30
    )
    ax.legend()

    plt.tight_layout()
    guardar_figura("congestiones_mensual.png")


# -------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------------

def visualizar_todo():
    """
    Genera todas las gráficas de congestiones.
    """
    print("=" * 50)
    print("GENERANDO VISUALIZACIONES — GRUPO 4")
    print("=" * 50)

    grafica_heatmap_congestiones()
    grafica_resumen_congestiones()

    print("\n" + "=" * 50)
    print("VISUALIZACIONES COMPLETADAS")
    print(f"Gráficas guardadas en: {CARPETA_FIGURAS}/")
    print("=" * 50)


# -------------------------------------------------------------
# PUNTO DE ENTRADA
# -------------------------------------------------------------

if __name__ == "__main__":
    visualizar_todo()