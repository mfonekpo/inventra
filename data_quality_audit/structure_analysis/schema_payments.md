# 🛠️ Structure Analysis: `payments.csv`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `payments.csv`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **`payment_id`** | `VARCHAR / TEXT` | `PAY-207775` | Verify Key Constraint |
| **`invoice_id`** | `VARCHAR / TEXT` | `INV-786913` | Verify Key Constraint |
| **`payment_date`** | `VARCHAR / TEXT` | `2023-10-07` | Quantitative/Descriptive |
| **`payment_amount`** | `FLOAT64` | `3354624.0` | Quantitative/Descriptive |
| **`payment_method`** | `VARCHAR / TEXT` | `Cheque` | Quantitative/Descriptive |

### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
