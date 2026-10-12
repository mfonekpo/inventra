# 🛠️ Structure Analysis: `sales_orders_lines.csv`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `sales_orders_lines.csv`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **`so_id`** | `VARCHAR / TEXT` | `SO-990591` | Verify Key Constraint |
| **`line_number`** | `INT64` | `1` | Quantitative/Descriptive |
| **`product_id`** | `VARCHAR / TEXT` | `P018` | Verify Key Constraint |
| **`quantity`** | `INT64` | `19` | Quantitative/Descriptive |
| **`unit_price`** | `INT64` | `11300` | Quantitative/Descriptive |
| **`gst_rate`** | `INT64` | `28` | Quantitative/Descriptive |
| **`line_total`** | `INT64` | `214700` | Quantitative/Descriptive |
| **`gst_amount`** | `FLOAT64` | `60116.00000000001` | Quantitative/Descriptive |
| **`line_grand_total`** | `FLOAT64` | `274816.0` | Quantitative/Descriptive |

### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
