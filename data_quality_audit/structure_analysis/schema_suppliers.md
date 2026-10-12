# 🛠️ Structure Analysis: `suppliers.csv`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `suppliers.csv`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **`supplier_id`** | `VARCHAR / TEXT` | `SUP0001` | Verify Key Constraint |
| **`supplier_name`** | `VARCHAR / TEXT` | `Shenzhen OEM Supplies` | Quantitative/Descriptive |
| **`supplier_type`** | `VARCHAR / TEXT` | `OEM` | Quantitative/Descriptive |
| **`product_category`** | `VARCHAR / TEXT` | `Medium Parts` | Quantitative/Descriptive |
| **`city`** | `VARCHAR / TEXT` | `Shenzhen` | Quantitative/Descriptive |
| **`province`** | `VARCHAR / TEXT` | `Guangdong` | Quantitative/Descriptive |
| **`region`** | `VARCHAR / TEXT` | `South China` | Quantitative/Descriptive |
| **`pincode`** | `INT64` | `586808` | Verify Key Constraint |
| **`lead_time_days`** | `INT64` | `19` | Quantitative/Descriptive |
| **`reliability_score`** | `INT64` | `5` | Quantitative/Descriptive |
| **`import_duty_rate`** | `INT64` | `8` | Quantitative/Descriptive |
| **`china_tax_id`** | `VARCHAR / TEXT` | `90SUZHOU398241` | Verify Key Constraint |

### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
