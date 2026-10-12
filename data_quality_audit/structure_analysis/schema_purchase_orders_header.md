# 🛠️ Structure Analysis: `purchase_orders_header.csv`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `purchase_orders_header.csv`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
| **`po_id`** | `VARCHAR / TEXT` | `PO-141186` | Verify Key Constraint |
| **`supplier_id`** | `VARCHAR / TEXT` | `SUP0001` | Verify Key Constraint |
| **`branch_id`** | `VARCHAR / TEXT` | `PUN001` | Verify Key Constraint |
| **`order_date`** | `VARCHAR / TEXT` | `2019-04-10` | Quantitative/Descriptive |
| **`expected_delivery_date`** | `VARCHAR / TEXT` | `2019-04-29` | Quantitative/Descriptive |
| **`received_date`** | `VARCHAR / TEXT` | `2019-04-29` | Quantitative/Descriptive |
| **`po_status`** | `VARCHAR / TEXT` | `Received` | Quantitative/Descriptive |
| **`total_cost`** | `FLOAT64` | `22955232.11` | Quantitative/Descriptive |
| **`total_gst_amount`** | `FLOAT64` | `6427464.990800001` | Quantitative/Descriptive |
| **`grand_total`** | `FLOAT64` | `29382697.1008` | Quantitative/Descriptive |

### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
