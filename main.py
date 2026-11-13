"""Punto de entrada: ejecuta carga, limpieza, transformación, análisis y gráficos."""
from pathlib import Path
import pandas as pd
from limpieza import cargar_datos, limpiar, diagnosticar
from analisis import transformar, analizar_region, analizar_producto_metodo, analizar_riesgo, analizar_distribucion
from visualizacion import graficar

ROOT = Path(__file__).resolve().parent


def cargar_catalogos():
    """Carga los catálogos auxiliares desde data/."""
    rutas = [ROOT / "data" / "productos.csv", ROOT / "data" / "regiones.csv"]
    for ruta in rutas:
        if not ruta.exists():
            raise FileNotFoundError(f"No se encontró {ruta}. Revisa la carpeta data/.")
    productos = pd.read_csv(rutas[0])
    regiones = pd.read_csv(rutas[1])
    return productos, regiones


def main():
    print("=" * 68, "\n1. CARGA Y DIAGNÓSTICO\n", "=" * 68)
    original = cargar_datos()
    productos, regiones = cargar_catalogos()
    print("Dimensiones originales:", original.shape)
    print(diagnosticar(original).to_string())

    print("\n2. LIMPIEZA")
    limpio = limpiar(original)

    print("\n3. TRANSFORMACIÓN")
    transformado = transformar(limpio, productos, regiones)
    assert len(transformado) == len(limpio), "La transformación cambió el número de filas."

    print("\n4. TASAS POR REGIÓN")
    por_region = analizar_region(transformado)
    print(por_region.to_string())

    print("\n5. DINERO COBRADO POR PRODUCTO Y MÉTODO")
    con_extremos, sin_extremos = analizar_producto_metodo(transformado)
    print("Incluyendo importes de 50,000:\n", con_extremos.to_string())
    print("\nExcluyendo importes de 50,000:\n", sin_extremos.to_string())

    print("\n6. TASAS POR RIESGO")
    por_riesgo = analizar_riesgo(transformado)
    print(por_riesgo.to_string())

    print("\n7. DISTRIBUCIÓN Y ALERTAS")
    for nombre, valor in analizar_distribucion(transformado).items():
        print(f"\n{nombre}:\n{valor}")

    print("\n8. VISUALIZACIONES")
    graficar(transformado, por_region, con_extremos, sin_extremos, por_riesgo)
    print("\nProceso completado.")


if __name__ == "__main__":
    main()
