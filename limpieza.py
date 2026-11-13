"""Carga, diagnóstico y limpieza de los datos de pagos fintech."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def cargar_datos():
    """Carga el CSV: celdas vacías -> NaN; el texto literal 'None' se conserva."""
    ruta = DATA_DIR / "pagos_fintech.csv"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Coloca pagos_fintech.csv dentro de la carpeta data/."
        )
    return pd.read_csv(ruta, keep_default_na=False, na_values=[""])


def diagnosticar(df):
    """Resume tipos, nulos, porcentajes y valores únicos; informa IDs repetidos."""
    tabla = pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "nulos": df.isna().sum(),
        "pct_nulos": (df.isna().mean() * 100).round(2),
        "unicos": df.nunique(dropna=True),
    })
    repetidos = df["payment_id"].duplicated(keep=False)
    print("Filas con payment_id repetido:", int(repetidos.sum()))
    print("payment_id distintos repetidos:", int(df.loc[repetidos, "payment_id"].nunique()))
    print("Filas completamente duplicadas:", int(df.duplicated().sum()))
    return tabla


def limpiar(df):
    """Limpia los datos siguiendo las reglas investigadas en el notebook de referencia.

    No elimina importes negativos ni importes de 50,000. Elimina las copias
    incorrectas de payment_id solo cuando incumplen el patrón observado:
    customer_id == payment_id + 1.
    """
    df = df.copy()
    filas_iniciales = len(df)
    resumen = {}

    # 1. Investigar payment_id repetidos y eliminar la copia que no cumple el patrón.
    payment_id_num = pd.to_numeric(df["payment_id"], errors="coerce")
    customer_id_num = pd.to_numeric(df["customer_id"], errors="coerce")
    cumple_patron = customer_id_num.eq(payment_id_num + 1)
    es_id_repetido = df["payment_id"].duplicated(keep=False)
    copia_incorrecta = es_id_repetido & ~cumple_patron
    resumen["copias_incorrectas_payment_id_eliminadas"] = int(copia_incorrecta.sum())
    df = df.loc[~copia_incorrecta].copy()

    ids_restantes = df["payment_id"].duplicated(keep=False).sum()
    print("Copias incorrectas de payment_id eliminadas:", resumen["copias_incorrectas_payment_id_eliminadas"])
    print("Filas con payment_id repetido después:", int(ids_restantes))

    # 2. Convertir importes que usan coma decimal.
    importes_texto = df["payment_amount"].astype("string")
    con_coma = importes_texto.str.contains(",", regex=False, na=False)
    resumen["importes_con_coma_corregidos"] = int(con_coma.sum())
    df["payment_amount"] = pd.to_numeric(
        importes_texto.str.replace(",", ".", regex=False), errors="coerce"
    )
    print("Importes con coma decimal corregidos:", resumen["importes_con_coma_corregidos"])
    print("Importes que no pudieron convertirse:", int(df["payment_amount"].isna().sum()))

    # 3. Marcar importes negativos y valores extremos; no se eliminan.
    df["alerta_monto"] = "normal"
    df.loc[df["payment_amount"] < 0, "alerta_monto"] = "negativo"
    df.loc[df["payment_amount"] == 50000, "alerta_monto"] = "50000"
    resumen["importes_negativos_marcados"] = int((df["alerta_monto"] == "negativo").sum())
    resumen["importes_extremos_marcados"] = int((df["alerta_monto"] == "50000").sum())

    # 4. Corregir el error tipográfico documentado en payment_status.
    paidd = df["payment_status"].eq("paidd")
    resumen["paidd_corregidos"] = int(paidd.sum())
    df["payment_status"] = df["payment_status"].replace({"paidd": "paid"})

    # 5. La referencia concluye que los productos cobran en USD y que las
    # medianas por moneda son prácticamente iguales. Se conserva el valor
    # original para que la normalización sea auditable.
    df["currency_original"] = df["currency"]
    resumen["monedas_normalizadas_a_usd"] = int(df["currency"].ne("USD").sum())
    df["currency"] = "USD"

    # 6. Convertir fechas imposibles o vacías en NaT, conservando las filas.
    df["pay_dt"] = pd.to_datetime(
        df["pay_dt"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
    )
    df["signup_dt"] = pd.to_datetime(
        df["signup_dt"], format="%Y-%m-%d", errors="coerce"
    )
    resumen["fechas_pago_invalidas_o_vacias"] = int(df["pay_dt"].isna().sum())
    resumen["fechas_registro_invalidas_o_vacias"] = int(df["signup_dt"].isna().sum())
    df["registro_despues_del_pago"] = df["signup_dt"] > df["pay_dt"]
    resumen["registros_despues_del_pago"] = int(df["registro_despues_del_pago"].sum())

    # 7. Identificar pagos sin datos de cliente. No se borran: son pagos
    # válidos para el análisis de transacciones y se agrupan aparte.
    df["sin_cliente"] = df["status_customer"].isna()
    resumen["pagos_sin_cliente"] = int(df["sin_cliente"].sum())
    for columna in ["status_customer", "risk_segment", "kyc_level", "income_bracket"]:
        df[columna] = df[columna].fillna("Sin cliente")

    # 8. Mantener el literal 'None' como texto: su significado no está confirmado.
    # No se aplica drop_duplicates general: la regla de duplicados usada es la
    # regla investigada para payment_id, no la igualdad de todas las columnas.

    print("\nRESUMEN DE LIMPIEZA")
    for clave, valor in resumen.items():
        print(f"{clave}: {valor:,}")
    print(f"Filas iniciales: {filas_iniciales:,}")
    print(f"Filas finales: {len(df):,}")
    print(f"Filas eliminadas: {filas_iniciales - len(df):,}")
    return df


if __name__ == "__main__":
    datos = cargar_datos()
    print("DIAGNÓSTICO ORIGINAL")
    print(diagnosticar(datos).to_string())
    datos_limpios = limpiar(datos)
    print("\nDIAGNÓSTICO FINAL")
    print(diagnosticar(datos_limpios).to_string())
