# 🛠️ Structure Analysis: `stock_ledger.csv`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `stock_ledger.csv`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **`movement_id`** | `VARCHAR / TEXT` | `MOV-OUT-184742` | Verify Key Constraint |
| **`product_id`** | `VARCHAR / TEXT` | `P001` | Verify Key Constraint |
| **`branch_id`** | `VARCHAR / TEXT` | `AHM001` | Verify Key Constraint |
| **`movement_type`** | `VARCHAR / TEXT` | `OUT` | Quantitative/Descriptive |
| **`movement_date`** | `VARCHAR / TEXT` | `2019-01-03` | Quantitative/Descriptive |
| **`quantity`** | `INT64` | `8` | Quantitative/Descriptive |
| **`reference_type`** | `VARCHAR / TEXT` | `SO` | Quantitative/Descriptive |
| **`reference_id`** | `VARCHAR / TEXT` | `SO-157767` | Verify Key Constraint |
| **`running_balance`** | `INT64` | `228` | Quantitative/Descriptive |

### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
