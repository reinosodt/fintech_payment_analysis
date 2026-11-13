"""Visualizaciones del proyecto de análisis de pagos fintech.

Este módulo representa los resultados calculados en analisis.py.
No vuelve a calcular tasas ni importes por región, producto o riesgo.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator


# ==============================================================
# ESTILO GENERAL
# ==============================================================

COLOR_PRINCIPAL = "#2563EB"
COLOR_SECUNDARIO = "#D1C3AC"
COLOR_NEGATIVO = "#E76F6F"
COLOR_TEXTO = "#172033"
COLOR_GRILLA = "#D9E0EA"
COLOR_SECUNDARIO_TEXTO = "#64748B"


def configurar_estilo():
    """Aplica un estilo visual uniforme a los gráficos."""
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#CBD5E1",
        "axes.labelcolor": COLOR_TEXTO,
        "xtick.color": COLOR_SECUNDARIO_TEXTO,
        "ytick.color": COLOR_SECUNDARIO_TEXTO,
        "text.color": COLOR_TEXTO,
        "axes.titleweight": "bold",
        "axes.titlesize": 15,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "font.family": "DejaVu Sans",
        "savefig.facecolor": "white",
    })


def limpiar_ejes(ax, eje="x"):
    """Reduce elementos decorativos y mejora la lectura."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_GRILLA)
    ax.spines["bottom"].set_color(COLOR_GRILLA)
    ax.grid(axis=eje, color=COLOR_GRILLA, linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)


def guardar_figura(fig, ruta):
    """Guarda la figura en alta resolución y libera memoria."""
    fig.tight_layout()
    fig.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.close(fig)


def formato_usd(valor, posicion=None):
    """Muestra importes completos en dólares, sin notación científica."""
    return f"US$ {valor:,.0f}"


# ==============================================================
# FUNCIÓN PRINCIPAL DE VISUALIZACIÓN
# ==============================================================

def graficar(
    df,
    resultado_region,
    resultado_producto_con,
    resultado_producto_sin,
    resultado_riesgo,
):
    """
    Genera cuatro gráficos usando los resultados calculados en analisis.py.

    Los tres primeros gráficos reutilizan los DataFrames recibidos.
    El cuarto necesita los importes individuales de df para construir
    el histograma y, por eso, trabaja directamente con esa columna.
    """
    configurar_estilo()

    carpeta = Path("graficos")
    carpeta.mkdir(parents=True, exist_ok=True)

    if "payment_amount" not in df.columns:
        raise KeyError("Falta la columna 'payment_amount' para el histograma.")

    # ==========================================================
    # GRÁFICO 1: FAILED Y CHARGEBACK POR REGIÓN
    # ==========================================================

    # analizar_region() devuelve region_name como índice y las tasas
    # ya calculadas en porcentaje. Aquí solo preparamos su presentación.
    regiones = resultado_region.copy()
    regiones.index.name = "region_name"
    regiones = regiones.reset_index()

    columnas_region = {
        "region_name", "pagos", "tasa_failed", "tasa_chargeback"
    }
    faltantes = columnas_region.difference(regiones.columns)
    if faltantes:
        raise KeyError(
            "Faltan columnas en resultado_region: "
            f"{sorted(faltantes)}"
        )

    # Se mantiene el criterio del gráfico anterior: no mostrar Sin cliente.
    regiones = regiones.loc[
        regiones["region_name"].ne("Sin cliente")
        & regiones["region_name"].notna()
    ].copy()

    regiones = regiones.sort_values(
        "tasa_fallido", ascending=True
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    posiciones = np.arange(len(regiones))
    alto = 0.34

    barras_failed = ax.barh(
        posiciones - alto / 2,
        regiones["tasa_failed"],
        height=alto,
        color=COLOR_PRINCIPAL,
        label="Failed",
    )

    barras_chargeback = ax.barh(
        posiciones + alto / 2,
        regiones["tasa_chargeback"],
        height=alto,
        color=COLOR_NEGATIVO,
        label="Chargeback",
    )

    max_tasa = max(
        regiones[["tasa_failed", "tasa_chargeback"]].to_numpy().max(),
        1,
    )

    ax.set_xlim(0, max_tasa * 1.35)
    ax.set_yticks(posiciones)
    ax.set_yticklabels(regiones["region_name"].astype(str))
    ax.set_title(
        "Comparación de pagos failed y chargeback por región",
        loc="left",
        pad=14,
    )
    ax.set_xlabel("Porcentaje del total de registros de cada región")
    ax.set_ylabel("")
    ax.legend(frameon=False, loc="lower right")
    limpiar_ejes(ax, eje="x")
    ax.grid(axis="y", visible=False)

    # Las tasas ya vienen calculadas; solo añadimos sus etiquetas.
    for barras in (barras_failed, barras_chargeback):
        for barra in barras:
            porcentaje = barra.get_width()
            ax.text(
                porcentaje + max_tasa * 0.02,
                barra.get_y() + barra.get_height() / 2,
                f"{porcentaje:.2f}%",
                va="center",
                ha="left",
                fontsize=8,
                color=COLOR_TEXTO,
            )

    ax.text(
        0,
        -0.12,
        "Cada tasa utiliza como denominador todos los registros de su región.",
        transform=ax.transAxes,
        fontsize=8,
        color=COLOR_SECUNDARIO_TEXTO,
        va="top",
    )

    guardar_figura(fig, carpeta / "01_tasa_fallos_region.png")

    # ==========================================================
    # GRÁFICO 2: SENSIBILIDAD DE IMPORTES POR PRODUCTO
    # ==========================================================

    # analizar_producto_metodo() devuelve tablas dinámicas:
    # productos en el índice, métodos de pago en las columnas y Total.
    # Se utiliza la columna Total para obtener el importe por producto.
    def extraer_total_producto(tabla, nombre_columna):
        tabla = tabla.copy()
        tabla = tabla.drop(index="Total", errors="ignore")

        if "Total" in tabla.columns:
            serie = tabla["Total"]
        else:
            # Respaldo si la tabla no contiene la columna Total:
            # sumar únicamente las columnas de métodos de pago.
            serie = tabla.select_dtypes(include="number").sum(axis=1)

        serie.name = nombre_columna
        return serie

    importes = pd.concat(
        [
            extraer_total_producto(
                resultado_producto_con, "importe_con"
            ),
            extraer_total_producto(
                resultado_producto_sin, "importe_sin"
            ),
        ],
        axis=1,
    ).fillna(0)

    importes = importes.sort_values("importe_con", ascending=True)

    fig, ax = plt.subplots(figsize=(13, 7))
    posiciones = np.arange(len(importes))
    alto = 0.34

    barras_con = ax.barh(
        posiciones - alto / 2,
        importes["importe_con"],
        height=alto,
        color=COLOR_SECUNDARIO,
        label="Con registros de US$ 50,000",
    )

    barras_sin = ax.barh(
        posiciones + alto / 2,
        importes["importe_sin"],
        height=alto,
        color=COLOR_PRINCIPAL,
        label="Sin registros de US$ 50,000",
    )

    max_importe = max(
        importes[["importe_con", "importe_sin"]].to_numpy().max(),
        1,
    )

    ax.set_xlim(0, max_importe * 1.45)
    ax.xaxis.set_major_formatter(FuncFormatter(formato_usd))
    ax.xaxis.set_major_locator(MaxNLocator(nbins=7))
    ax.set_yticks(posiciones)
    ax.set_yticklabels(importes.index.astype(str))
    ax.set_title(
        "Sensibilidad de importes por producto",
        loc="left",
        pad=14,
    )
    ax.set_xlabel("Suma de pagos realizados (USD)")
    ax.set_ylabel("Tipo de producto")
    ax.legend(frameon=False, loc="lower right")
    limpiar_ejes(ax, eje="x")
    ax.grid(axis="y", visible=False)

    for barras in (barras_con, barras_sin):
        for barra in barras:
            importe = barra.get_width()
            ax.text(
                importe + max_importe * 0.015,
                barra.get_y() + barra.get_height() / 2,
                f"US$ {importe:,.2f}",
                va="center",
                ha="left",
                fontsize=8,
                color=COLOR_TEXTO,
            )

    ax.text(
        0,
        -0.12,
        "Solo se incluyen pagos paid. Los importes se reutilizan de las tablas de análisis.",
        transform=ax.transAxes,
        fontsize=8,
        color=COLOR_SECUNDARIO_TEXTO,
        va="top",
    )

    guardar_figura(fig, carpeta / "02_importes_productos.png")

    
    # ==========================================================
    # GRÁFICO 3: HEATMAP DE TASAS POR SEGMENTO DE RIESGO
    # ==========================================================

    # Reutilizar los resultados calculados en analizar_riesgo().
    riesgo = resultado_riesgo.copy()
    riesgo.index.name = "risk_segment"
    riesgo = riesgo.reset_index()

    # Excluir registros sin cliente.
    riesgo = riesgo.loc[riesgo["risk_segment"].ne("Sin cliente")
        & riesgo["risk_segment"].notna()].copy()

    # Ordenar los segmentos de riesgo.
    orden_riesgo = {"Low": 0, "Medium": 1, "High": 2}

    riesgo["_orden"] = (riesgo["risk_segment"].map(orden_riesgo).fillna(99))
    riesgo = riesgo.sort_values("_orden")

    # Construir la matriz con las tasas ya calculadas.
    matriz = riesgo.set_index("risk_segment")[["es_failed", "es_chargeback", "es_fallido"]]

    # Crear el heatmap.
    fig, ax = plt.subplots(figsize=(10, 6))

    valores = matriz.to_numpy()

    limite_color = max(5, np.ceil(np.nanmax(valores) / 5) * 5)

    imagen = ax.imshow(
        valores,
        cmap="YlOrRd",
        aspect="auto",
        vmin=0,
        vmax=limite_color
    )

    # Etiquetas de los ejes.
    ax.set_xticks(np.arange(len(matriz.columns)))
    ax.set_xticklabels(["Failed", "Chargeback", "Fallido combinado"])
    ax.set_yticks(np.arange(len(matriz.index)))
    ax.set_yticklabels(matriz.index.astype(str))

    # Mostrar los porcentajes dentro de cada celda.
    for i in range(len(matriz.index)):
        for j in range(len(matriz.columns)):

            valor = valores[i, j]

            ax.text(
                j,
                i,
                f"{valor:.2f}%",
                ha="center",
                va="center",
                color=COLOR_TEXTO,
                fontsize=11,
                fontweight="bold"
            )

    # Barra de intensidad de color.
    colorbar = fig.colorbar(imagen, ax=ax)
    colorbar.set_label("Tasa de registros (%)")

    ax.set_title("Tasas de fallos según segmento de riesgo", 
        loc="left", pad=14)
    ax.set_xlabel("Tipo de fallo")
    ax.set_ylabel("Segmento de riesgo")

    # Separadores visuales entre celdas.
    ax.set_xticks(np.arange(-0.5, len(matriz.columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(matriz.index), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)

    # Personalizar los bordes del gráfico.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(COLOR_GRILLA)
    ax.spines["bottom"].set_color(COLOR_GRILLA)

    # Mantener el orden de las capas.
    ax.set_axisbelow(True)

    ax.text(
        0,
        -0.18,
        "Los colores representan la magnitud de cada tasa. "
        "El fallido combinado incluye failed y chargeback.",
        transform=ax.transAxes,
        fontsize=8,
        color=COLOR_SECUNDARIO_TEXTO,
        va="top"
    )

    fig.tight_layout()

    guardar_figura(fig, carpeta / "03_heatmap_riesgo.png")

    # ==========================================================
    # GRÁFICO 4: DISTRIBUCIÓN DE IMPORTES
    # ==============================================================

    # Este gráfico conserva el uso directo de df porque necesita
    # los importes individuales para construir el histograma.
    importes_validos = pd.to_numeric(
        df["payment_amount"],
        errors="coerce",
    ).dropna()

    if importes_validos.empty:
        print("No hay importes numéricos para generar el histograma.")
    else:
        limite_p99 = importes_validos.quantile(0.99)

        importes_visibles = importes_validos[
            importes_validos <= limite_p99
        ]

        positivos = importes_visibles[importes_visibles >= 0]
        negativos = importes_validos[importes_validos < 0]

        fuera_p99 = int((importes_validos > limite_p99).sum())
        porcentaje_fuera = fuera_p99 / len(importes_validos) * 100

        fig, (ax_pos, ax_neg) = plt.subplots(
            1,
            2,
            figsize=(12, 5.4),
            gridspec_kw={"width_ratios": [3.2, 1.15]},
        )

        if not positivos.empty:
            ax_pos.hist(
                positivos,
                bins=35,
                color=COLOR_PRINCIPAL,
                edgecolor="white",
                linewidth=0.7,
            )

            ax_pos.axvline(
                limite_p99,
                color=COLOR_NEGATIVO,
                linestyle="--",
                linewidth=1.8,
                label=f"Percentil 99: {limite_p99:,.2f}",
            )

            ax_pos.legend(frameon=False, fontsize=8)

        ax_pos.set_title("Importes no negativos", loc="left", pad=10)
        ax_pos.set_xlabel("Importe (USD)")
        ax_pos.set_ylabel("Número de registros")
        ax_pos.grid(axis="y", color=COLOR_GRILLA, linewidth=0.8)
        ax_pos.set_axisbelow(True)
        ax_pos.spines["top"].set_visible(False)
        ax_pos.spines["right"].set_visible(False)

        if negativos.empty:
            ax_neg.text(
                0.5,
                0.5,
                "No se encontraron\nimportes negativos",
                transform=ax_neg.transAxes,
                ha="center",
                va="center",
                fontsize=10,
                color=COLOR_SECUNDARIO_TEXTO,
            )
            ax_neg.set_xticks([])
            ax_neg.set_yticks([])
        else:
            conteo_negativos = negativos.value_counts().sort_index()
            posiciones_neg = np.arange(len(conteo_negativos))

            barras_neg = ax_neg.bar(
                posiciones_neg,
                conteo_negativos.values,
                color=COLOR_NEGATIVO,
                edgecolor="white",
                width=0.62,
            )

            ax_neg.set_xticks(posiciones_neg)
            ax_neg.set_xticklabels(
                [f"{valor:g}" for valor in conteo_negativos.index]
            )

            for barra, cantidad in zip(
                barras_neg, conteo_negativos.values
            ):
                ax_neg.text(
                    barra.get_x() + barra.get_width() / 2,
                    barra.get_height(),
                    f"{int(cantidad):,}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

            ax_neg.set_title("Importes negativos", loc="left", pad=10)
            ax_neg.set_xlabel("Importe (USD)")
            ax_neg.set_ylabel("Número de registros")
            ax_neg.grid(axis="y", color=COLOR_GRILLA, linewidth=0.8)
            ax_neg.set_axisbelow(True)
            ax_neg.spines["top"].set_visible(False)
            ax_neg.spines["right"].set_visible(False)

        fig.suptitle(
            "Distribución de importes de pagos",
            x=0.06,
            ha="left",
            fontsize=15,
            fontweight="bold",
        )

        fig.text(
            0.06,
            0.015,
            f"Se muestran importes hasta el percentil 99 ({limite_p99:,.2f}). "
            f"{fuera_p99:,} registros ({porcentaje_fuera:.2f}%) están por encima "
            "del umbral y se excluyen solo de esta visualización.",
            fontsize=8,
            color=COLOR_SECUNDARIO_TEXTO,
        )

        guardar_figura(fig, carpeta / "04_distribucion_importes.png")

    print("Se generaron los gráficos en la carpeta 'graficos'.")
