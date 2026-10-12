# 🛠️ Structure Analysis: `products.csv`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `products.csv`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **`product_id`** | `VARCHAR / TEXT` | `P001` | Verify Key Constraint |
| **`product_name`** | `VARCHAR / TEXT` | `Hydraulic Pump HP-300` | Quantitative/Descriptive |
| **`category`** | `VARCHAR / TEXT` | `Hydraulic` | Quantitative/Descriptive |
| **`machine_type`** | `VARCHAR / TEXT` | `Excavator` | Quantitative/Descriptive |
| **`brand`** | `VARCHAR / TEXT` | `CAT` | Quantitative/Descriptive |
| **`model_compatibility`** | `VARCHAR / TEXT` | `CAT 320D` | Quantitative/Descriptive |
| **`unit_cost`** | `INT64` | `18950` | Quantitative/Descriptive |
| **`unit_price`** | `INT64` | `24500` | Quantitative/Descriptive |
| **`margin_percentage`** | `FLOAT64` | `29.2` | Quantitative/Descriptive |
| **`gst_rate`** | `INT64` | `28` | Quantitative/Descriptive |
| **`weight_kg`** | `FLOAT64` | `38.5` | Quantitative/Descriptive |
| **`dimensions_cm`** | `VARCHAR / TEXT` | `40x25x25` | Quantitative/Descriptive |
| **`material_type`** | `VARCHAR / TEXT` | `steel` | Quantitative/Descriptive |
| **`warranty_months`** | `INT64` | `12` | Quantitative/Descriptive |
| **`reorder_level`** | `INT64` | `15` | Quantitative/Descriptive |
| **`safety_stock`** | `INT64` | `10` | Quantitative/Descriptive |
| **`max_stock_level`** | `INT64` | `40` | Quantitative/Descriptive |
| **`lead_time_days`** | `INT64` | `21` | Quantitative/Descriptive |
| **`criticality_level`** | `VARCHAR / TEXT` | `High` | Quantitative/Descriptive |
| **`usage_frequency`** | `VARCHAR / TEXT` | `Medium` | Quantitative/Descriptive |
| **`uom`** | `VARCHAR / TEXT` | `piece` | Quantitative/Descriptive |
| **`last_purchase_price`** | `INT64` | `18500` | Quantitative/Descriptive |
| **`last_purchase_date`** | `VARCHAR / TEXT` | `2019-03-15` | Quantitative/Descriptive |

### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
