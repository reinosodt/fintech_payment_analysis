# Fintech Payment Analysis | Análisis de pagos fintech

Proyecto de análisis de datos con Python y pandas para estudiar la calidad de registros de pagos, las tasas de `failed` y `chargeback`, el dinero cobrado por producto y método de pago, y las diferencias entre segmentos de riesgo.

> **Estado:** código reorganizado y alineado con el notebook de referencia. Los resultados resumidos abajo proceden de la ejecución registrada en ese notebook; vuelve a ejecutar el proyecto con los CSV originales para regenerar las tablas y gráficos.

## Objetivos

- Diagnosticar problemas de calidad en los registros.
- Aplicar reglas de limpieza basadas en patrones investigados, sin eliminar observaciones arbitrariamente.
- Comparar tasas de `failed` y `chargeback` por región y segmento de riesgo.
- Medir dinero cobrado usando exclusivamente registros con estado `paid`.
- Evaluar la sensibilidad de los totales al incluir o excluir importes extremos de 50,000.
- Comunicar resultados mediante visualizaciones.

## Decisiones de limpieza

- Se investigan los `payment_id` repetidos mediante el patrón observado `customer_id == payment_id + 1`; se elimina la copia que no cumple dicho patrón.
- Los importes con coma decimal se convierten a valores numéricos.
- El estado `paidd` se normaliza a `paid`.
- Los importes negativos y los importes extremos se marcan, pero no se eliminan del dataset.
- Las monedas se normalizan a USD siguiendo la justificación del notebook de referencia; se conserva `currency_original` para trazabilidad.
- Las fechas imposibles se convierten en `NaT`, conservando sus filas.
- Los pagos sin información de cliente se conservan y se etiquetan como `Sin cliente`.
- El texto literal `None` se conserva como texto porque su significado no está confirmado.

## Resultados principales de la referencia

### Calidad de datos

| Hallazgo | Registros |
|---|---:|
| Filas originales | 100,000 |
| Copias incorrectas de `payment_id` eliminadas según el patrón investigado | 250 |
| Filas después de limpiar | 99,750 |
| Importes con coma decimal corregidos | 6,018 |
| Estados `paidd` normalizados a `paid` | 6,030 |
| Importes negativos marcados y conservados | 6,300 |
| Importes de 50,000 marcados y conservados | 56 |
| Fechas de pago inválidas | 5,549 |
| Fechas de registro inválidas | 57 |
| Pagos sin datos de cliente conservados | 6,086 |

### Tasas de incidencias por región

| Región | `failed` | `chargeback` | Combinada |
|---|---:|---:|---:|
| Europa | 11.02% | 3.78% | 14.80% |
| Caribe | 11.06% | 3.65% | 14.71% |
| Norteamérica | 9.77% | 3.22% | 12.99% |
| Andina | 10.09% | 0.00% | 10.09% |
| Sin cliente | 0.00% | 0.00% | 0.00% |

### Dinero cobrado por producto

Se consideran exclusivamente pagos con estado `paid`. Los importes negativos se marcan por separado y no forman parte de estas sumas.

| Producto | Incluyendo 50,000 | Excluyendo 50,000 |
|---|---:|---:|
| Card | US$ 1,778,180.35 | US$ 628,180.35 |
| Loan | US$ 1,740,682.77 | US$ 690,682.77 |
| Wallet | US$ 1,271,922.88 | US$ 671,922.88 |

Sin los importes de 50,000, Loan lidera por producto. Al incluirlos, Card pasa al primer lugar. Esto muestra la sensibilidad de los totales a los importes extremos; no demuestra que sean errores.

### Tasas de incidencias por segmento de riesgo

| Segmento | `failed` | `chargeback` | Combinada |
|---|---:|---:|---:|
| Low | 8.45% | 1.37% | 9.83% |
| Medium | 18.35% | 0.00% | 18.35% |
| High | 6.29% | 12.32% | 18.62% |
| Sin cliente | 0.00% | 0.00% | 0.00% |

### Visualizaciones

El proyecto genera cuatro gráficos:

1. `01_tasa_fallos_region.png`: comparación de las tasas de pagos failed y chargeback por región.
2. `02_importes_productos.png`: comparación del dinero cobrado por producto, con y sin importes de US$ 50,000.
3. `03_heatmap_riesgo.png`: comparación de las tasas failed y chargeback por segmento de riesgo.
4. `04_distribucion_importes.png`: distribución de importes positivos y frecuencia de importes negativos.

Las visualizaciones de región y riesgo excluyen los registros sin información de cliente.

## Estructura

```text
fintech-payment-analysis/
│
├── README.md
├── main.py
├── limpieza.py
├── analisis.py
├── visualizacion.py
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── diccionario_datos.md
│   ├── pagos_fintech.csv
│   ├── productos.csv
│   └── regiones.csv
│
├── notebooks/
│   └── investigacion.ipynb
│
└── graficos/
    ├── 01_tasa_fallos_region.png
    ├── 02_importes_productos.png
    ├── 03_heatmap_riesgo.png
    └── 04_distribucion_importes.png
```

## Instalación y ejecución

Se recomienda Python 3.10 o superior.

```bash
python -m venv .venv
```

Activa el entorno virtual y después instala las dependencias:

```bash
pip install -r requirements.txt
```

Ejecuta desde la carpeta raíz:

```bash
python main.py
```

Los cuatro gráficos se guardarán en `graficos/`.

## Limitaciones

- La regla para los identificadores repetidos se basa en el patrón observado en este dataset; no debe generalizarse a otros sistemas sin validación.
- La normalización de moneda depende de la evidencia descrita en el notebook de referencia. No se realiza conversión de divisas.
- Los importes negativos y extremos requieren confirmación del negocio para determinar su significado.
- Las tasas son descriptivas y no demuestran causalidad.

## Tecnologías

Python · pandas · NumPy · Matplotlib 

---

**Área:** Data Analytics · Fintech  
**Proyecto de portafolio:** análisis, limpieza y visualización de datos
