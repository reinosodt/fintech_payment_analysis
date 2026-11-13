# Fintech Payment Analysis

A data analytics project built with Python and pandas to investigate payment data quality, failed and chargeback rates, revenue by product and payment method, and differences across risk segments.

> **Project status:** The code has been reorganized and aligned with the reference notebook. The results summarized below come from the execution documented in that notebook. Run the project again using the original CSV files to regenerate the tables and charts.

## Project Objectives

- Identify data quality issues in payment records.
- Apply data cleaning rules based on investigated patterns rather than arbitrarily removing observations.
- Compare failed and chargeback rates across regions and risk segments.
- Measure collected revenue using only records with a `paid` status.
- Evaluate how including or excluding extreme amounts of 50,000 affects total revenue.
- Communicate findings through data visualizations.

## Data Cleaning Decisions

- Investigate duplicated `payment_id` values using the observed pattern `customer_id == payment_id + 1`. Remove the copy that does not match this pattern.
- Convert amounts using decimal commas into numeric values.
- Standardize the `paidd` status to `paid`.
- Flag negative amounts and extreme values without removing them from the dataset.
- Standardize currencies to USD based on the justification documented in the reference notebook. Preserve `currency_original` for traceability.
- Convert invalid dates to `NaT` while keeping their corresponding rows.
- Retain payments without customer information and label them as `Sin cliente`.
- Preserve the literal text `None` because its meaning has not been confirmed.

## Key Results from the Reference Analysis

### Data Quality

| Finding | Records |
|---|---:|
| Original rows | 100,000 |
| Incorrect `payment_id` copies removed based on the investigated pattern | 250 |
| Rows after cleaning | 99,750 |
| Decimal-comma amounts corrected | 6,018 |
| `paidd` statuses standardized to `paid` | 6,030 |
| Negative amounts flagged and retained | 6,300 |
| Amounts of 50,000 flagged and retained | 56 |
| Invalid payment dates | 5,549 |
| Invalid registration dates | 57 |
| Payments without customer information retained | 6,086 |

### Incident Rates by Region

| Region | `failed` | `chargeback` | Combined |
|---|---:|---:|---:|
| Europe | 11.02% | 3.78% | 14.80% |
| Caribbean | 11.06% | 3.65% | 14.71% |
| North America | 9.77% | 3.22% | 12.99% |
| Andean | 10.09% | 0.00% | 10.09% |
| No customer data | 0.00% | 0.00% | 0.00% |

### Revenue by Product

Only payments with a `paid` status are included. Negative amounts are flagged separately and are not included in these totals.

| Product | Including 50,000 | Excluding 50,000 |
|---|---:|---:|
| Card | US$ 1,778,180.35 | US$ 628,180.35 |
| Loan | US$ 1,740,682.77 | US$ 690,682.77 |
| Wallet | US$ 1,271,922.88 | US$ 671,922.88 |

Without the 50,000 amounts, Loan ranks first by product. When these amounts are included, Card takes the lead. This demonstrates how sensitive the totals are to extreme values; it does not establish that these values are errors.

### Incident Rates by Risk Segment

| Risk Segment | `failed` | `chargeback` | Combined |
|---|---:|---:|---:|
| Low | 8.45% | 1.37% | 9.83% |
| Medium | 18.35% | 0.00% | 18.35% |
| High | 6.29% | 12.32% | 18.62% |
| No customer data | 0.00% | 0.00% | 0.00% |

### Visualizations

The project generates four charts:

1. `01_tasa_fallos_region.png`: Comparison of failed and chargeback rates across regions.
2. `02_importes_productos.png`: Comparison of revenue by product, including and excluding US$50,000 amounts.
3. `03_heatmap_riesgo.png`: Heatmap comparing failed and chargeback rates across risk segments.
4. `04_distribucion_importes.png`: Distribution of positive amounts and frequency of negative amounts.

The regional and risk visualizations exclude records without customer information.

## Project Structure

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

## Installation and Execution

Python 3.10 or higher is recommended.

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Install dependencies

Activate your virtual environment and install the project dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the project

From the root project directory, execute:

```bash
python main.py
```

The four charts will be saved in the `graficos/` directory.

## Limitations

- The rule used to identify duplicated IDs is based on a pattern observed in this specific dataset. It should not be generalized to other systems without further validation.
- Currency standardization depends on the evidence documented in the reference notebook. No foreign exchange conversion is performed.
- Negative and extreme amounts require business confirmation to determine their actual meaning.
- The reported rates are descriptive and do not establish causality.

## Technologies

Python · pandas · NumPy · Matplotlib

---

**Field:** Data Analytics · Fintech

**Portfolio Project:** Data Analysis, Cleaning, and Visualization

[Read this project in Spanish](README_ES.md)
