# Structure Analysis: `branches.csv`

**Phase 1 Component:** Data Foundation & Preparation
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout

* **File Name:** `branches.csv`
* **Format:** Comma-Separated Values (`.csv`)
* **Delimiter:** Comma (`,`)
* **Granularity:** One row per individual record.city

### 2. Physical Schema Blueprint

| Column Name                            | Inferred Data Type | Sample Value      | Structural Rule / Constraint |
| :------------------------------------- | :----------------- | :---------------- | :--------------------------- |
| **`branch_id`**                | `VARCHAR / TEXT` | `DEL001`        | Verify Key Constraint        |
| **`branch_name`**              | `VARCHAR / TEXT` | `Delhi Central` | Quantitative/Descriptive     |
| **`city`**                     | `VARCHAR / TEXT` | `Delhi`         | Quantitative/Descriptive     |
| **`state`**                    | `VARCHAR / TEXT` | `Delhi`         | Quantitative/Descriptive     |
| **`region`**                   | `VARCHAR / TEXT` | `North`         | Quantitative/Descriptive     |
| **`warehouse_type`**           | `VARCHAR / TEXT` | `Central`       | Quantitative/Descriptive     |
| **`warehouse_capacity`**       | `VARCHAR / TEXT` | `45230 sqft`    | Quantitative/Descriptive     |
| **`service_center_available`** | `VARCHAR / TEXT` | `Yes`           | Quantitative/Descriptive     |
| **`manager_id`**               | `INT64`          | `9593`          | Verify Key Constraint        |
| **`total_employees`**          | `INT64`          | `92`            | Quantitative/Descriptive     |
| **`avg_monthly_revenue`**      | `INT64`          | `5234890`       | Quantitative/Descriptive     |
| **`monthly_operational_cost`** | `INT64`          | `3189000`       | Quantitative/Descriptive     |
| **`market_demand_index`**      | `INT64`          | `9`             | Quantitative/Descriptive     |

### 3. Relational Mapping & Required Transformations

* **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
* **Required dbt Cleaning (Staging Layer):**
  1. Check for trailing whitespaces using `TRIM()`.
  2. Ensure proper numeric casting for metric fields.
  3. Standardize column cases to snake_case if necessary.
  4. Remove `sqft` from `warehouse_capacity` column.
