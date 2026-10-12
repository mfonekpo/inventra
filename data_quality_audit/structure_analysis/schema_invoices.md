# 🛠️ Structure Analysis: `invoices.csv`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `invoices.csv`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **`invoice_id`** | `VARCHAR / TEXT` | `INV-325361` | Verify Key Constraint |
| **`so_id`** | `VARCHAR / TEXT` | `SO-990591` | Verify Key Constraint |
| **`customer_id`** | `VARCHAR / TEXT` | `C0070` | Verify Key Constraint |
| **`branch_id`** | `VARCHAR / TEXT` | `AHM001` | Verify Key Constraint |
| **`invoice_date`** | `VARCHAR / TEXT` | `2022-05-28` | Quantitative/Descriptive |
| **`due_date`** | `VARCHAR / TEXT` | `2022-06-27` | Quantitative/Descriptive |
| **`total_order_value`** | `INT64` | `1345720` | Quantitative/Descriptive |
| **`total_gst_amount`** | `FLOAT64` | `374439.6` | Quantitative/Descriptive |
| **`grand_total`** | `FLOAT64` | `1720159.6` | Quantitative/Descriptive |
| **`payment_status`** | `VARCHAR / TEXT` | `Unpaid` | Quantitative/Descriptive |

### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
