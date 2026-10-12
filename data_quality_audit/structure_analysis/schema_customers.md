# 🛠️ Structure Analysis: `customers.csv`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `customers.csv`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **`customer_id`** | `VARCHAR / TEXT` | `C0001` | Verify Key Constraint |
| **`customer_type`** | `VARCHAR / TEXT` | `Retail` | Quantitative/Descriptive |
| **`industry_segment`** | `VARCHAR / TEXT` | `Construction` | Quantitative/Descriptive |
| **`city`** | `VARCHAR / TEXT` | `Kolkata` | Quantitative/Descriptive |
| **`state`** | `VARCHAR / TEXT` | `West Bengal` | Quantitative/Descriptive |
| **`pincode`** | `INT64` | `991035` | Verify Key Constraint |
| **`region`** | `VARCHAR / TEXT` | `East` | Quantitative/Descriptive |
| **`branch_id`** | `VARCHAR / TEXT` | `KOL001` | Verify Key Constraint |
| **`credit_limit`** | `INT64` | `45896` | Quantitative/Descriptive |
| **`current_balance`** | `INT64` | `43284` | Quantitative/Descriptive |
| **`payment_terms`** | `VARCHAR / TEXT` | `Advance` | Quantitative/Descriptive |
| **`customer_since`** | `VARCHAR / TEXT` | `2024-04-10` | Quantitative/Descriptive |
| **`last_purchase_date`** | `VARCHAR / TEXT` | `2024-04-25` | Quantitative/Descriptive |
| **`total_purchase_value`** | `INT64` | `3892818` | Quantitative/Descriptive |
| **`customer_rating`** | `INT64` | `4` | Quantitative/Descriptive |

### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
