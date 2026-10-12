# 🛠️ Structure Analysis: `inventory_master.csv`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `inventory_master.csv`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **`product_id`** | `VARCHAR / TEXT` | `P001` | Verify Key Constraint |
| **`branch_id`** | `VARCHAR / TEXT` | `DEL001` | Verify Key Constraint |
| **`opening_stock`** | `INT64` | `196` | Quantitative/Descriptive |
| **`reorder_level`** | `INT64` | `59` | Quantitative/Descriptive |
| **`safety_stock`** | `INT64` | `46` | Quantitative/Descriptive |
| **`max_stock`** | `INT64` | `340` | Quantitative/Descriptive |
| **`current_stock`** | `INT64` | `115928` | Quantitative/Descriptive |
| **`warehouse_bin`** | `VARCHAR / TEXT` | `C15` | Quantitative/Descriptive |

### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
