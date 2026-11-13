"""Transformaciones y análisis de negocio para los pagos fintech."""
import pandas as pd


def transformar(df, productos, regiones):
    """Integra catálogos y crea variables para los análisis posteriores."""
    df = df.copy()
    filas_iniciales = len(df)

    # La moneda del catálogo se omite porque la moneda del pago ya fue
    # normalizada y se conserva en currency_original.
    df = df.merge(
        productos.drop(columns=["currency"], errors="ignore"),
        on="product_id", how="left", validate="many_to_one"
    )
    df = df.merge(
        regiones, on="region_id", how="left", validate="many_to_one"
    )
    assert len(df) == filas_iniciales, "Los merges modificaron el número de filas."

    # Los pagos sin cliente no tienen región asociada en el catálogo.
    df["region_name"] = df["region_name"].fillna("Sin cliente")

    dias = {
        0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"
    }
    df["mes"] = df["pay_dt"].dt.month
    df["dia"] = df["pay_dt"].dt.day
    df["dia_semana"] = df["pay_dt"].dt.dayofweek.map(dias)

    normal = df["alerta_monto"].eq("normal")
    df["rango_monto"] = pd.cut(
        df["payment_amount"].where(normal),
        bins=[0, 20, 35, 50],
        labels=["bajo", "medio", "alto"]
    )

    df["es_failed"] = df["payment_status"].eq("failed")
    df["es_chargeback"] = df["payment_status"].eq("chargeback")
    df["es_fallido"] = df["es_failed"] | df["es_chargeback"]
    return df


def analizar_region(df):
    """Calcula las tasas de failed y chargeback por región, incluyendo Sin cliente."""
    resultado = df.groupby("region_name").agg(
        pagos=("payment_id", "count"),
        tasa_failed=("es_failed", "mean"),
        tasa_chargeback=("es_chargeback", "mean"),
        tasa_fallido=("es_fallido", "mean"),
    )
    columnas = ["tasa_failed", "tasa_chargeback", "tasa_fallido"]
    resultado[columnas] = (resultado[columnas] * 100).round(2)
    return resultado.sort_values("tasa_chargeback", ascending=False)


def analizar_producto_metodo(df):
    """Compara dinero cobrado (solo paid) con y sin importes extremos de 50,000."""
    normal = df["alerta_monto"].eq("normal")
    extremos = df["alerta_monto"].eq("50000")
    pagados = df["payment_status"].eq("paid")

    def crear_pivot(mascara):
        return pd.pivot_table(
            df.loc[mascara], values="payment_amount",
            index="product_type", columns="pay_method",
            aggfunc="sum", fill_value=0,
            margins=True, margins_name="Total"
        ).round(2)

    resultado_sin = crear_pivot(normal & pagados)
    resultado_con = crear_pivot((normal | extremos) & pagados)
    return resultado_con, resultado_sin


def analizar_riesgo(df):
    """Calcula tasas de failed, chargeback y su combinación por segmento."""
    resultado = pd.pivot_table(
        df, index="risk_segment",
        values=["es_failed", "es_chargeback", "es_fallido"],
        aggfunc="mean"
    )
    resultado = (resultado * 100).round(2)
    orden = [x for x in ["Low", "Medium", "High", "Sin cliente"] if x in resultado.index]
    return resultado.reindex(orden)


def analizar_distribucion(df):
    """Devuelve métricas descriptivas de importes normales y alertas."""
    normales = df.loc[df["alerta_monto"].eq("normal"), "payment_amount"].dropna()
    return {
        "descripcion_importes_normales": normales.describe(),
        "cantidad_negativos": int(df["alerta_monto"].eq("negativo").sum()),
        "cantidad_extremos": int(df["alerta_monto"].eq("50000").sum()),
        "suma_negativos": float(df.loc[df["alerta_monto"].eq("negativo"), "payment_amount"].sum()),
    }
