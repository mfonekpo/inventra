# Heavy Supplier, Inventory & Warehouse Analytics

## Data Cleaning and Quality Improvement Plan

**Project stage:** Phase 1, Data Foundation and Preparation
**Document version:** 1.0
**Prepared:** 11 October 2026
**Execution model:** Solo portfolio project
**Technology:** Python, DuckDB, SQL, dbt, GitHub
**Document status:** Baseline assessed; proposed rules and remediation plan; implementation evidence still required
**Suggested repository location:** `docs/data_cleaning_and_quality_plan.md`

---

## 1. Executive summary

This document defines how source data will be cleaned, validated, monitored, and released for analytics in the Heavy Supplier, Inventory & Warehouse Analytics project. It covers all 12 supplied CSV sources. Its primary goal is to enable dependable downstream work on product movement, inventory health, warehouse operations, supplier performance, procurement, and customer analytics.

The project uses a **preserve, standardise, validate, investigate, and publish** approach:

1. Preserve the supplied CSV records as immutable raw inputs.
2. Standardise formats and types without changing business meaning.
3. Test structural constraints, relationships, financial calculations, and operational rules.
4. Separate confirmed data defects from permissible nulls and unresolved business questions.
5. Prevent known ambiguous records from silently distorting analytical results.
6. Release clearly scoped datasets with documented limitations and reproducible checks.

**Important limitation:** This is a data quality plan, not a claim that all anomalies have been repaired. Counts below are observations from the supplied extracts; decisions marked **Pending** require further evidence or an explicitly documented assumption. No real company or business stakeholder has confirmed these rules.

### 1.1 Business and technical consumers

The programme brief names supply chain and operations teams, warehouse managers, procurement and planning teams, data analysts, and data scientists. The first three are the proposed primary business users. Analytics and data science workflows are technical downstream consumers.

Consequently, a record may be usable for one analytical purpose and unsuitable for another. For example, a payment whose `invoice_id` matches multiple invoices can be counted in a standalone payment-volume report while being excluded from **invoice-attributed** payment measures until attribution is verified.

### 1.2 Scope and non-goals

**In scope:** schema validation, source metadata, type conversions, canonical category values, required fields, candidate and composite keys, referential integrity, temporal logic, monetary reconciliation, inventory balance investigations, exception datasets, dbt checks, regression checks, and documentation.

**Not yet in scope:** correcting source-system records without authority, inventing financial or operational facts, force-fitting inventory levels to target thresholds, choosing dimensional fact grains, implementing predictive models, warehouse space optimisation, production service-level agreements, or redesigning source applications.

---

## 2. Data inventory and baseline

### 2.1 Files and observed grains

| Source                         |              Rows |                        Columns | Proposed record grain              | Initial key evidence                |
| ------------------------------ | ----------------: | -----------------------------: | ---------------------------------- | ----------------------------------- |
| `branches.csv`               |                 6 |                             13 | One branch                         | `branch_id` unique                |
| `customers.csv`              |               500 |                             15 | One customer record                | `customer_id` unique              |
| `inventory_master.csv`       |               180 |                              8 | One product and branch combination | `(product_id, branch_id)` unique  |
| `invoices.csv`               |            18,033 |                             10 | One invoice source record          | `invoice_id` **not** unique |
| `payments.csv`               |            19,257 |                              5 | One payment source record          | `payment_id` **not** unique |
| `products.csv`               |                30 |                             23 | One product                        | `product_id` unique               |
| `purchase_orders_header.csv` |            24,000 |                             10 | One purchase order                 | `po_id` unique                    |
| `purchase_orders_lines.csv`  |           155,495 |                              9 | One purchase order line            | `(po_id, line_number)` unique     |
| `sales_orders_header.csv`    |            20,000 |                             11 | One sales order                    | `so_id` unique                    |
| `sales_orders_lines.csv`     |           130,402 |                              9 | One sales order line               | `(so_id, line_number)` unique     |
| `stock_ledger.csv`           |           237,230 |                              9 | One recorded stock movement        | `movement_id` unique              |
| `suppliers.csv`              |                 8 |                             12 | One supplier                       | `supplier_id` unique              |
| **Total**                | **605,141** | **134 combined columns** |                                    |                                     |

The grains are hypotheses supported by the observed keys, not guarantees about future extracts. The inventory master is a current balance extract, not automatically a daily history.

### 2.2 Baseline facts from supplied files

| Check                                                          | Observed result | Interpretation                                                        |
| -------------------------------------------------------------- | --------------: | --------------------------------------------------------------------- |
| Fully identical source rows                                    |               0 | No whole-row duplicate found in initial profiling                     |
| `invoices.invoice_id` repeated occurrences beyond one per ID |             197 | 196 distinct IDs have multiple invoice records                        |
| `payments.payment_id` repeated occurrences beyond one per ID |             202 | 201 distinct IDs have multiple payment records                        |
| Payments referring to a non-unique invoice ID                  |             417 | Unsafe to attribute with a naive`invoice_id` join                   |
| `inventory_master.current_stock > max_stock`                 |      180 of 180 | Configured maximum and balance semantics need investigation           |
| Ledger movements referencing cancelled purchase orders         |           1,542 | Requires cancellation/reversal interpretation                         |
| Ledger movements referencing cancelled sales orders            |           1,275 | Requires cancellation/reversal interpretation                         |
| Missing`received_date` on cancelled purchase orders          |           2,370 | Likely appropriate conditional missingness                            |
| Missing`received_date` on received purchase orders           |               0 | Conditional receipt-date rule currently passes                        |
| Cancelled sales orders with a populated`delivery_date`       |           1,967 | `delivery_date` may not mean actual fulfilment for cancelled orders |
| Orphan foreign keys in 17 initially tested joins               |               0 | Existence alone does**not** prove relationship cardinality      |
| Stock movements                                                |         237,230 | `IN`: 127,611; `OUT`: 107,165; `ADJUSTMENT`: 2,454              |

**Financial baseline:** Purchase and sales order header totals reconcile to their respective line totals in the supplied extracts; the independently checked line calculation, GST calculation, and line grand total checks have no discrepancies greater than 0.01 in their displayed numeric scale. Invoice values reconcile to the linked sales order values using `so_id`, and the invoice header amount equals net amount plus GST to the same 0.01 tolerance. This is evidence about *arithmetic*, not proof that the source amounts, taxes, or currencies are authoritative.

**Date coverage:** Purchase and sales order dates span 1 January 2019 through 31 December 2024. Other business dates extend into 2025, including payment dates through 20 March 2025 and product `last_purchase_date` through 27 April 2025. Historical extracts should not be judged against today's date as if they were continuously updated feeds.

**Baseline scope:** Counts above were verified against the supplied CSV versions. If input files change, rerun the checks and update the baseline; do not copy these numbers forward as permanent guarantees.

---

## 3. Data quality policy

### 3.1 Quality dimensions

| Dimension              | Working definition                                                         | Typical evidence                                                               |
| ---------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Completeness           | Values required by a particular business condition are present             | Non-null counts and conditional null tests                                     |
| Uniqueness             | The documented record key identifies at most one record                    | Key collision counts                                                           |
| Validity               | Values match type, format, domain, and approved range                      | Cast failure and allowed-value tests                                           |
| Referential integrity  | Referenced entities exist **and expected cardinality is respected** | Orphan and ambiguous-parent tests                                              |
| Consistency            | The same operational fact agrees across relevant records                   | Header-to-line totals, linked attributes                                       |
| Accuracy               | A value corresponds to the underlying real-world fact                      | Requires source evidence or domain confirmation; cannot be proved by SQL alone |
| Temporal consistency   | Event dates follow justified lifecycle rules                               | Order, fulfilment, invoice, and payment date comparisons                       |
| Freshness / timeliness | Data arrives in time for a defined usage requirement                       | Extract-as-of metadata versus agreed cadence                                   |
| Traceability           | A cleaned value can be explained using its original record                 | Source file, row number, load ID, transformation lineage                       |

### 3.2 Issue severity and outcomes

| Level                 | Meaning                                                         | Treatment                                                                      |
| --------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **P0 Critical** | Known risk of material misstatement or unresolvable attribution | Block the affected published metric or mart; preserve and report exceptions    |
| **P1 High**     | Material operational anomaly or important contract violation    | Investigate; restrict affected analytics or publish only with explicit caveats |
| **P2 Medium**   | Deterministic parsing, standardisation, or documentation issue  | Implement and test an approved transformation                                  |
| **P3 Low**      | Expected variability or informational anomaly                   | Record and monitor without modifying business facts                            |

The priority is **project-defined**, not an official dbt classification. Map P0/P1 gating rules to dbt `error` only after confirming the rule is valid; use warnings or exception reporting for suspicious but not definitively invalid source records. Prefer *selective* blocking: an invoice join defect should not prevent unrelated product analysis.

### 3.3 Permitted actions

| Action                         | Permitted when                                                  | Example                                                             |
| ------------------------------ | --------------------------------------------------------------- | ------------------------------------------------------------------- |
| `STANDARDISE`                | The source meaning is preserved                                 | Trim surrounding whitespace in keys                                 |
| `PARSE`                      | Input syntax and expected unit are defined                      | Convert`45230 sqft` to numeric `45230` and retain unit `sqft` |
| `PRESERVE_NULL`              | A missing value is valid for the row's lifecycle                | Receipt date of a cancelled purchase order                          |
| `FLAG`                       | A value is suspicious but not yet proven incorrect              | Stock beyond configured maximum                                     |
| `QUARANTINE_FOR_USE_CASE`    | A record cannot safely enter a specific join/metric             | Payment linked to an ambiguous invoice ID                           |
| `CORRECT_WITH_EVIDENCE`      | Authoritative source evidence and correction are recorded       | Verified source-system correction                                   |
| `REJECT_FROM_PUBLISHED_MART` | A confirmed contract violation would materially misstate output | Unparseable required quantity in an approved fact model             |

**Prohibited shortcuts:** dropping repeated identifiers without investigation; replacing missing dates with today's date; filling missing transaction amounts with zero without explicit semantics; capping real balances to reorder thresholds; assigning ambiguous payments to arbitrary invoices; changing historical currency/price fields based on current prices; changing signs of adjustments without a verified ordering rule.

### 3.4 Numeric rules

* Preserve money fields as source strings in raw tables. Parse deliberately to `DECIMAL`, with the chosen scale backed by business conventions and source precision.
* Use **0.01 as an initial investigation tolerance** for displayed reconciliations, not as a legally approved rounding rule. Re-evaluate against source precision, currency, and tax method before financial publication.
* Store percentages in documented units, for example `28` means `28%`; do not mix `28` with `0.28`.
* Preserve identifier and postal-code values as text, even if all their characters are digits.
* Require explicit unit semantics for dimensions, weight, capacity, quantities, and any conversion to volume or area.

### 3.5 Change and lineage rules

* Preserve the original files unmodified, record SHA-256 checksums, and store a source-file manifest.
* Capture `_source_file`, `_source_row_number`, `_load_batch_id`, and `_ingested_at` when loading. The source row number must be captured reliably during ingestion, not reconstructed from an unordered SQL scan.
* Running ingestion twice for an identical batch must not double-load records. Choose either transactional replace-by-batch or a verified idempotent load key.
* Keep raw records and staged records traceable. Staging should normally preserve source grain and row count; any exception must be explicitly documented.
* Record each remediation as a version-controlled change linked to a rule ID and issue ID.
* Avoid checking sensitive customer information, raw financial detail, or unapproved source files into a public GitHub repository.

---

## 4. Quality rule catalogue for every source

**Legend:** `E` = zero violations required before affected output is published; `W` = warning/investigation; `C` = conditional or requires confirmation. Each row is a *proposed rule* unless the baseline section explicitly states a test has already been executed.

### 4.1 `branches.csv`

**Grain:** one branch. **Business key:** `branch_id`. **Columns:** `branch_id`, `branch_name`, `city`, `state`, `region`, `warehouse_type`, `warehouse_capacity`, `service_center_available`, `manager_id`, `total_employees`, `avg_monthly_revenue`, `monthly_operational_cost`, `market_demand_index`.

| Rule ID | Rule and expected treatment                                                                                                      | Gate |
| ------- | -------------------------------------------------------------------------------------------------------------------------------- | ---- |
| BR001   | `branch_id` exists and is unique. Preserve as string.                                                                          | E    |
| BR002   | Required branch name, city, state, and region must be nonblank.                                                                  | E    |
| BR003   | `warehouse_capacity` parses into positive numeric capacity plus documented original unit; preserve original string.            | E    |
| BR004   | Only approved units may feed area/volume utilisation; current source is text such as`45230 sqft`.                              | C    |
| BR005   | `service_center_available` maps only approved `Yes`/`No` values to a Boolean; unknown labels flagged.                      | E    |
| BR006   | Employee counts are nonnegative whole numbers; monetary operating metrics are numeric and nonnegative subject to source meaning. | E    |
| BR007   | `warehouse_type` and `region` retain approved source categories; unexpected values reported.                                 | W    |
| BR008   | `manager_id` is an identifier, not a measure; no employee-master relationship exists in the supplied files.                    | C    |
| BR009   | `market_demand_index` is numeric; allowed scale requires metadata before imposing a hard range.                                | C    |

**Cleaning:** trim identifiers and labels; parse capacity into `warehouse_capacity_value` and `warehouse_capacity_unit`; standardise Yes/No; do not imply that full physical capacity is usable storage space.

### 4.2 `customers.csv`

**Grain:** one customer record. **Business key:** `customer_id`. **Columns:** `customer_id`, `customer_type`, `industry_segment`, `city`, `state`, `pincode`, `region`, `branch_id`, `credit_limit`, `current_balance`, `payment_terms`, `customer_since`, `last_purchase_date`, `total_purchase_value`, `customer_rating`.

| Rule ID | Rule and expected treatment                                                                                                    | Gate |
| ------- | ------------------------------------------------------------------------------------------------------------------------------ | ---- |
| CU001   | `customer_id` is present and unique.                                                                                         | E    |
| CU002   | `branch_id` references one existing branch; check cardinality as well as existence.                                          | E    |
| CU003   | `pincode` remains a string; check source pattern only after confirming relevant jurisdiction.                                | C    |
| CU004   | `customer_since` and `last_purchase_date` parse as dates.                                                                  | E    |
| CU005   | Last purchase is not earlier than customer inception; whether it matches the sales extract requires a scope check.             | W    |
| CU006   | `credit_limit`, `current_balance`, and `total_purchase_value` parse as nonnegative monetary values.                      | E    |
| CU007   | `customer_rating` belongs to an approved scale; supplied values are 1 through 5.                                             | C    |
| CU008   | `customer_type` and `payment_terms` use canonical observed labels; flag unfamiliar labels.                                 | W    |
| CU009   | A balance above credit limit is a business exception, not automatically a parse failure.                                       | W    |
| CU010   | Do not replace stored lifetime purchase value with a sum of the limited sales extract without agreeing a matching time window. | C    |

**Cleaning:** trim text, parse dates and amounts, preserve pincode as text, and retain original classification labels alongside mapped values if a canonicalisation table is introduced.

### 4.3 `products.csv`

**Grain:** one product. **Business key:** `product_id`. **Columns:** `product_id`, `product_name`, `category`, `machine_type`, `brand`, `model_compatibility`, `unit_cost`, `unit_price`, `margin_percentage`, `gst_rate`, `weight_kg`, `dimensions_cm`, `material_type`, `warranty_months`, `reorder_level`, `safety_stock`, `max_stock_level`, `lead_time_days`, `criticality_level`, `usage_frequency`, `uom`, `last_purchase_price`, `last_purchase_date`.

| Rule ID | Rule and expected treatment                                                                                                          | Gate |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------ | ---- |
| PR001   | `product_id` is nonblank and unique.                                                                                               | E    |
| PR002   | Essential product descriptors are present; category and UOM mappings are controlled.                                                 | E    |
| PR003   | Unit prices, costs, weights, and lead times parse as valid nonnegative values; determine where zero is legitimate.                   | E    |
| PR004   | `dimensions_cm` parses into exactly three positive numeric dimensions; retain raw string.                                          | E    |
| PR005   | Parsed dimensions imply centimetres based on field name, but confirm orientation and whether values are packaged or item dimensions. | C    |
| PR006   | `gst_rate` is parsed as a percentage with its raw representation retained; compare line-level historical rates cautiously.         | E    |
| PR007   | `reorder_level`, `safety_stock`, and `max_stock_level` are nonnegative and internally consistent according to agreed policy.   | C    |
| PR008   | `margin_percentage` is not assumed to be gross margin, markup, or an authoritative formula until its definition is checked.        | C    |
| PR009   | `criticality_level`, `usage_frequency`, and `uom` follow approved categories.                                                  | W    |
| PR010   | `last_purchase_date` parses and `last_purchase_price` is nonnegative; historical scope may extend beyond order-header coverage.  | E    |

**Cleaning:** split dimensions into `length_cm`, `width_cm`, `height_cm` (only if order is defined); calculate candidate volume for exploratory use, clearly labelled as an estimate. Do not replace historical order prices with today's product catalog price.

### 4.4 `suppliers.csv`

**Grain:** one supplier. **Business key:** `supplier_id`. **Columns:** `supplier_id`, `supplier_name`, `supplier_type`, `product_category`, `city`, `province`, `region`, `pincode`, `lead_time_days`, `reliability_score`, `import_duty_rate`, `china_tax_id`.

| Rule ID | Rule and expected treatment                                                                               | Gate |
| ------- | --------------------------------------------------------------------------------------------------------- | ---- |
| SU001   | `supplier_id` is nonblank and unique.                                                                   | E    |
| SU002   | Supplier name and location descriptors are preserved and nonblank where required.                         | E    |
| SU003   | Supplier lead time is a valid nonnegative integer; clarify calendar versus business days.                 | C    |
| SU004   | `reliability_score` parses and has a documented scale; observed values alone do not establish policy.   | C    |
| SU005   | `import_duty_rate` parses to a percentage and falls in a confirmed business-legal domain.               | C    |
| SU006   | `pincode` and `china_tax_id` are stored as strings, preserving leading zeros and character structure. | E    |
| SU007   | `supplier_type` and `product_category` are mapped from approved observed values.                      | W    |

**Cleaning:** preserve identifiers as text; avoid inventing external supplier master data or applying assumed postal-code lengths.

### 4.5 `inventory_master.csv`

**Grain:** one product at one branch. **Composite key:** `(product_id, branch_id)`. **Columns:** `product_id`, `branch_id`, `opening_stock`, `reorder_level`, `safety_stock`, `max_stock`, `current_stock`, `warehouse_bin`.

| Rule ID | Rule and expected treatment                                                                                                  | Gate |
| ------- | ---------------------------------------------------------------------------------------------------------------------------- | ---- |
| IM001   | `(product_id, branch_id)` is complete and unique.                                                                          | E    |
| IM002   | Product and branch references exist uniquely in their parent tables.                                                         | E    |
| IM003   | All stock quantities and thresholds parse as integer quantities in a common, confirmed unit.                                 | E    |
| IM004   | Negative stocks and negative thresholds are flagged; source interpretation must clarify backorders/adjustments.              | C    |
| IM005   | `current_stock > max_stock` is an **alert, not a cap or automatic rejection** until maximum semantics are confirmed. | W    |
| IM006   | Product-level thresholds and branch-level thresholds must not be treated as identical; document which has precedence.        | C    |
| IM007   | Validate whether`opening_stock + signed_movements = current_stock` at an agreed cutoff and event order.                    | C    |
| IM008   | Preserve`warehouse_bin`; assess whether one value per product/branch really represents physical locations.                 | C    |
| IM009   | Snapshot effective date and`current_stock` measurement time must be established before trend-based use.                    | C    |

**Known issue:** 180/180 rows exceed `max_stock`; all 180 branch-level `max_stock` values also differ from their product master `max_stock_level` values. The source may represent a generated or inconsistent scenario; do not silently conform it to thresholds.

### 4.6 `purchase_orders_header.csv`

**Grain:** one purchase order. **Business key:** `po_id`. **Columns:** `po_id`, `supplier_id`, `branch_id`, `order_date`, `expected_delivery_date`, `received_date`, `po_status`, `total_cost`, `total_gst_amount`, `grand_total`.

| Rule ID | Rule and expected treatment                                                                       | Gate |
| ------- | ------------------------------------------------------------------------------------------------- | ---- |
| PH001   | `po_id` is nonblank and unique.                                                                 | E    |
| PH002   | Supplier and branch references are present and valid.                                             | E    |
| PH003   | Three date fields are parseable when populated.                                                   | E    |
| PH004   | Order date is not after expected delivery date.                                                   | E    |
| PH005   | Received orders must have a`received_date` that is not before `order_date`.                   | E    |
| PH006   | Cancelled orders may have null`received_date`; do not impute one.                               | E    |
| PH007   | `po_status` uses confirmed values `Received` and `Cancelled`, or newly approved categories. | E    |
| PH008   | `grand_total` reconciles with `total_cost + total_gst_amount` within agreed precision.        | E    |
| PH009   | Header totals reconcile with grouped line totals, after grain and duplicate checks.               | E    |
| PH010   | Delivery lateness is assessed only for received orders; early deliveries are not errors.          | C    |

**Known issue:** 2,370 null receipt dates all correspond to cancelled POs, as expected by the proposed conditional rule.

### 4.7 `purchase_orders_lines.csv`

**Grain:** one line in one purchase order. **Composite key:** `(po_id, line_number)`. **Columns:** `po_id`, `line_number`, `product_id`, `quantity`, `unit_cost`, `gst_rate`, `line_total`, `gst_amount`, `line_grand_total`.

| Rule ID | Rule and expected treatment                                                                                    | Gate |
| ------- | -------------------------------------------------------------------------------------------------------------- | ---- |
| PL001   | `(po_id, line_number)` is complete and unique.                                                               | E    |
| PL002   | Purchase order and product references resolve uniquely.                                                        | E    |
| PL003   | `line_number` is a positive integer; numbering gaps should be investigated but need not be rejected.         | W    |
| PL004   | Quantity is a positive integer for this observed dataset; document returns/credits before extending this rule. | E    |
| PL005   | `unit_cost` and GST values parse as appropriate decimals; percentages have defined units.                    | E    |
| PL006   | `line_total ≈ quantity × unit_cost`.                                                                       | E    |
| PL007   | `gst_amount ≈ line_total × gst_rate / 100`.                                                                | E    |
| PL008   | `line_grand_total ≈ line_total + gst_amount`.                                                               | E    |
| PL009   | Compare line GST to product catalog GST only as an investigation; historical rates can differ.                 | W    |

### 4.8 `sales_orders_header.csv`

**Grain:** one sales order. **Business key:** `so_id`. **Columns:** `so_id`, `customer_id`, `branch_id`, `order_date`, `delivery_date`, `order_status`, `payment_terms`, `total_order_value`, `total_gst_amount`, `grand_total`, `sales_channel`.

| Rule ID | Rule and expected treatment                                                                              | Gate |
| ------- | -------------------------------------------------------------------------------------------------------- | ---- |
| SH001   | `so_id` is complete and unique.                                                                        | E    |
| SH002   | Customer and branch references resolve uniquely.                                                         | E    |
| SH003   | Order and delivery dates are parseable.                                                                  | E    |
| SH004   | For delivered orders, delivery date must not precede order date.                                         | E    |
| SH005   | For cancelled orders,`delivery_date` meaning requires confirmation; do not assume actual fulfilment.   | C    |
| SH006   | `order_status` follows approved source values `Delivered` and `Cancelled`.                         | E    |
| SH007   | Financial totals satisfy`grand_total ≈ total_order_value + total_gst_amount`.                         | E    |
| SH008   | Header financial totals reconcile to grouped sales order lines.                                          | E    |
| SH009   | Sales channel and payment terms are mapped using approved categories.                                    | W    |
| SH010   | Cancelled orders must not contribute to fulfilled-sales KPIs unless business policy specifies otherwise. | C    |

**Known issue:** all 1,967 cancelled SOs have a populated `delivery_date`. It may be a planned date, generated placeholder, or something else. Investigate before any delivery-performance KPI uses it.

### 4.9 `sales_orders_lines.csv`

**Grain:** one line in one sales order. **Composite key:** `(so_id, line_number)`. **Columns:** `so_id`, `line_number`, `product_id`, `quantity`, `unit_price`, `gst_rate`, `line_total`, `gst_amount`, `line_grand_total`.

| Rule ID | Rule and expected treatment                                                                                             | Gate |
| ------- | ----------------------------------------------------------------------------------------------------------------------- | ---- |
| SL001   | `(so_id, line_number)` is complete and unique.                                                                        | E    |
| SL002   | Sales order and product references resolve uniquely.                                                                    | E    |
| SL003   | Line number and quantity are positive integers for the current extract.                                                 | E    |
| SL004   | `line_total ≈ quantity × unit_price`.                                                                               | E    |
| SL005   | `gst_amount ≈ line_total × gst_rate / 100`.                                                                         | E    |
| SL006   | `line_grand_total ≈ line_total + gst_amount`.                                                                        | E    |
| SL007   | Cancelled order lines are retained; exclude from**fulfilled** demand metrics as defined, not from every analysis. | C    |
| SL008   | Use historical line-level unit price rather than overwriting with product-master list price.                            | E    |

### 4.10 `invoices.csv`

**Grain:** one source invoice record. **Columns:** `invoice_id`, `so_id`, `customer_id`, `branch_id`, `invoice_date`, `due_date`, `total_order_value`, `total_gst_amount`, `grand_total`, `payment_status`.

| Rule ID | Rule and expected treatment                                                                                                         | Gate |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---- |
| IV001   | Invoice ID is nonblank. A`unique` assumption on raw `invoice_id` currently **fails**.                                     | W    |
| IV002   | `so_id` references a unique sales order; `so_id` is observed unique in this extract only.                                       | E    |
| IV003   | Invoice customer and branch match the referenced sales order.                                                                       | E    |
| IV004   | Invoice dates parse, and due date is not earlier than invoice date.                                                                 | E    |
| IV005   | Invoice grand total reconciles to invoice net plus GST.                                                                             | E    |
| IV006   | Invoice values match referenced sales order values under agreed invoice-generation rules.                                           | E    |
| IV007   | `payment_status` belongs to `Paid`, `Partially Paid`, `Unpaid` or approved values.                                          | E    |
| IV008   | Do not create a unique invoice dimension keyed only on nonunique`invoice_id`.                                                     | E    |
| IV009   | Preserve individual invoice records with a technical source-row identifier; this does not resolve business identity collisions.     | E    |
| IV010   | Investigate whether`so_id` can serve as a dataset-specific invoice-record join bridge without assuming this holds in future data. | C    |

**Known issue:** 197 extra occurrences of invoice IDs; 196 identifiers repeat. The collisions create ambiguous payment-to-invoice relationships.

### 4.11 `payments.csv`

**Grain:** one source payment record. **Columns:** `payment_id`, `invoice_id`, `payment_date`, `payment_amount`, `payment_method`.

| Rule ID | Rule and expected treatment                                                                                                                                        | Gate |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- |
| PY001   | Payment ID is nonblank. A`unique` assumption on raw `payment_id` currently **fails**.                                                                    | W    |
| PY002   | Payment-to-invoice**existence** is verified separately from invoice identifier uniqueness.                                                                   | E    |
| PY003   | Report`invoice_id` values with more than one parent invoice; do not join ambiguously.                                                                            | E    |
| PY004   | `payment_date` parses; date order can be assessed only after a unique invoice match is established.                                                              | E    |
| PY005   | `payment_amount` is numeric and positive for the current positive-payment business process.                                                                      | E    |
| PY006   | Payment method belongs to a confirmed approved set.                                                                                                                | W    |
| PY007   | Keep one traceable source row for each payment; do not deduplicate payment IDs by guessing which record is authentic.                                              | E    |
| PY008   | Exclude ambiguous matches**only from invoice-attributed outputs**; report count and total excluded amount.                                                   | E    |
| PY009   | Reconcile invoice payment status against summed matched payments**only after** resolving attribution and defining refunds/credits/partial-payment semantics. | C    |

**Known issue:** 202 extra occurrences of payment IDs; 417 payment records refer to invoice IDs matching multiple invoice records. Zero orphan matches does **not** mean the joins are safe.

### 4.12 `stock_ledger.csv`

**Grain:** one recorded stock movement. **Business key:** `movement_id`. **Columns:** `movement_id`, `product_id`, `branch_id`, `movement_type`, `movement_date`, `quantity`, `reference_type`, `reference_id`, `running_balance`.

| Rule ID | Rule and expected treatment                                                                                                       | Gate |
| ------- | --------------------------------------------------------------------------------------------------------------------------------- | ---- |
| ST001   | `movement_id` is nonblank and unique.                                                                                           | E    |
| ST002   | Product and branch references resolve uniquely.                                                                                   | E    |
| ST003   | Movement date parses; quantity is a positive integer in the current source representation.                                        | E    |
| ST004   | Movement type is one of`IN`, `OUT`, or `ADJUSTMENT`.                                                                        | E    |
| ST005   | Reference type and movement type agree:`IN` to `PO`, `OUT` to `SO`, `ADJUSTMENT` to `ADJ` in the current extract.     | E    |
| ST006   | `PO` references resolve to purchase orders and `SO` references to sales orders.                                               | E    |
| ST007   | Rows referencing cancelled orders must be flagged and traced through any reversal logic.                                          | W    |
| ST008   | Adjustment quantity has no explicit direction; don't assume that positive stored`quantity` always increases balance.            | C    |
| ST009   | Reconcile consecutive`running_balance` values only after establishing deterministic event order within each product and branch. | C    |
| ST010   | Determine whether`running_balance` or `inventory_master.current_stock` is authoritative at a documented as-of instant.        | C    |
| ST011   | Do not derive accurate historical stock snapshots from an unordered same-day ledger.                                              | C    |

**Known issue:** 1,542 ledger rows reference cancelled POs; 1,275 reference cancelled SOs. Adjustment rows store positive `quantity` even though some balance changes are downward. Capture stable source event order before interpreting adjustments.

---

## 5. Cross-table controls and join safety

| Control ID | Related datasets               | Test                                                                                    | Expected action                                        |
| ---------- | ------------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| X001       | All child/parent relationships | Check missing parents after normalising valid key representations                       | Fail affected build for new orphan records             |
| X002       | All joins                      | Check parent cardinality before joining                                                 | Prevent joins that multiply child records unexpectedly |
| X003       | PO header/lines                | Group by`po_id` and reconcile cost, GST, grand total                                  | Fail if mismatch above agreed tolerance                |
| X004       | SO header/lines                | Group by`so_id` and reconcile subtotal, GST, grand total                              | Fail if mismatch above tolerance                       |
| X005       | Invoice/SO                     | Verify`so_id`, `customer_id`, `branch_id`, and applicable totals                  | Investigate exceptions; no blind overwrites            |
| X006       | Payment/invoice                | Split unique matches, missing matches, and ambiguous matches                            | Block invoice-level allocation for ambiguous matches   |
| X007       | Stock ledger/PO                | Validate PO reference, order status, product, branch, and appropriate date logic        | Investigate cancellation and movement logic            |
| X008       | Stock ledger/SO                | Validate SO reference, order status, product, branch, and appropriate date logic        | Investigate cancellation and movement logic            |
| X009       | Inventory/product/branch       | Enforce 1:1 inventory row at product-branch grain and valid parent references           | Fail structural violations                             |
| X010       | Customer/SO                    | Compare customer master summary dates and balances only after defining extract coverage | Document differences, not automatically overwrite      |
| X011       | Product/PO/SO lines            | Keep transaction prices and taxes historically intact                                   | Flag differences from current catalogue for review     |

For stock ledger reference checks, the existing initial profiling validated product and branch references. A separate follow-up check also found zero missing references for `reference_type='PO'` and `reference_type='SO'` in these extracts. Parent **status**, business validity, and event timing remain unresolved.

### 5.1 Fundamental join safety examples

**Unsafe:**

```sql
SELECT SUM(p.payment_amount)
FROM raw.payments p
JOIN raw.invoices i ON p.invoice_id = i.invoice_id;
```

This can multiply payments where one invoice ID matches multiple invoice records.

**Defensive analysis of ambiguity:**

```sql
WITH invoice_key_counts AS (
    SELECT invoice_id, COUNT(*) AS invoice_rows
    FROM raw.invoices
    GROUP BY invoice_id
)
SELECT
    COUNT(*) AS payments_with_ambiguous_invoice_id
FROM raw.payments AS p
JOIN invoice_key_counts AS k
  ON p.invoice_id = k.invoice_id
WHERE k.invoice_rows > 1;
```

Expected baseline: `417`. This query **detects** the problem; it does not recover the correct invoice attribution.

---

## 6. Remediation and investigation playbooks

### 6.1 Invoice collisions: DQI-001 (P0)

**Evidence:** 18,033 invoice rows, 17,836 distinct invoice IDs, 197 duplicate excess occurrences; invoice IDs collide across records. A source-row identifier is needed to preserve all rows, but this is *not* a substitute for a verified business invoice key.

**Procedure:**

1. Export every colliding `invoice_id` with `so_id`, customer, branch, date, amount, source row number, and file checksum.
2. Verify whether different `so_id` values represent separate true invoices rather than data corruption.
3. Check for any authoritative identifier, source-system invoice mapping, or documented rule connecting payments to unique invoice instances.
4. Keep the source records intact and add an `invoice_key_status` such as `unique`, `collision`, or `missing`.
5. Do not attribute payment amounts to a collided invoice ID without defensible evidence.
6. If no mapping exists, publish invoicing metrics that do not require this attribution and include the unresolved exception count.

**Exit:** invoice-level payment allocation is enabled only for verified one-to-one matches or a newly validated join contract.

### 6.2 Duplicate payment identifiers: DQI-002 (P0)

**Evidence:** 19,257 payment rows, 19,055 distinct payment IDs, 202 duplicate excess occurrences.

**Procedure:** inspect each repeated ID's `invoice_id`, date, amount, method, and source row. Distinguish identical events from distinct events with reused IDs using documented evidence. Preserve all source rows until authenticity is resolved. Use a technical row key for storage and test that it remains stable within a fixed extract. Do not use the raw payment ID as a guaranteed primary key of a published fact.

### 6.3 Inventory exceeding maximum: DQI-003 (P1)

**Evidence:** 180/180 current stock balances exceed `max_stock` by large amounts; branch-level and product-level maximums also differ.

**Procedure:** compare product and branch thresholds, inspect opening stock and all movements, confirm UOM and whether maximum means warehouse policy, product default, or expected shelf stock. Record ratios by product and branch, with clearly labelled thresholds. Do not clip, winsorise, or discard valid source quantities as a "cleaning" operation.

**Exit:** the threshold definition and reporting treatment are documented; unless confirmed, KPI output must be labelled *threshold anomaly*, not proven overstock.

### 6.4 Cancelled orders with stock movements: DQI-004 (P1)

**Evidence:** 1,542 `PO` and 1,275 `SO` stock ledger movements link to cancelled order headers.

**Procedure:** inspect movement dates relative to order/cancellation workflow, ledger reference IDs, product, branch, quantity, and any compensating reversals. The datasets do not provide a cancellation timestamp or an explicit reversal flag. Report associations without claiming misconduct or source invalidity. If unresolvable, present sensitivity analyses with and without these movements, but do not overwrite raw records.

### 6.5 Inventory adjustments and chronology: DQI-005 (P1)

**Evidence:** 2,454 `ADJUSTMENT` rows; stored positive quantities do not directly encode direction. `movement_date` lacks intra-day timestamp precision. For some product/branch pairs, physical file order and date-only sorting may imply different latest records.

**Procedure:** preserve stable ingestion sequence, group by product and branch, reconstruct candidate movements using consecutive balances only where ordering is demonstrably reliable, and label inferred adjustment signs as inferred. Check whether an extract-level snapshot timestamp exists. Do not write a definitive historical snapshot fact model until event sequencing and reconciliation are justified.

### 6.6 Expected missing receipt dates: DQI-006 (P3)

**Evidence:** 2,370 cancelled POs have no receipt date; no received PO has this field missing.

**Treatment:** retain `NULL` as legitimate conditional missingness. Add tests for received orders requiring dates. No imputation is necessary.

### 6.7 Cancelled sales orders with delivery dates: DQI-007 (P1)

**Evidence:** 1,967 cancelled SOs have `delivery_date` populated.

**Treatment:** preserve dates as provided. Do not count these orders as fulfilled solely because a delivery date exists. Record that the semantic distinction between planned and actual delivery is unresolved.

### 6.8 Product margin definition: DQI-008 (P2)

**Evidence:** the product catalogue includes `margin_percentage`, `unit_cost`, and `unit_price`. Sample values do not establish a consistently verified formula. **Gross margin** and **markup on cost** use different denominators.

**Treatment:** retain `margin_percentage` as supplied. If required for analytics, compute separate explicit fields, such as `(price - cost) / price × 100` for gross margin and `(price - cost) / cost × 100` for markup, with safeguards against division by zero. Do not silently relabel one as the other.

### 6.9 String units and fixed schema: DQI-009 (P2)

**Evidence:** `branches.warehouse_capacity` includes `sqft` and `products.dimensions_cm` uses strings such as `40x25x25`.

**Treatment:** parse units/dimensions into typed fields with parse failure flags, preserve raw strings, and validate expected counts and positivity. Conversion of dimensions into usable warehouse area requires an additional storage model and cannot be inferred from item dimensions alone.

---

## 7. Target architecture and cleaning boundaries

```text
CSV source files (immutable + checksums)
                  |
                  v
Python ingestion (schema, metadata, idempotency)
                  |
                  v
DuckDB raw tables (source values retained)
                  |
                  v
dbt staging (rename, trim, parse, standardise)
                  |
             +----+----+
             |         |
             v         v
        dbt tests   issue / exception views
             |         |
             +----+----+
                  |
                  v
Intermediate models (validated joins and rules)
                  |
                  v
Analytical marts (clearly documented inclusion criteria)
```

**Raw layer:** lossless source records, immutable source metadata, no arbitrary business changes.

**Staging layer:** one primary staging model per source; preserve original grain; names, types, controlled categorisation, parse error indicators. dbt recommends staging models as reusable atomic building blocks rather than pre-aggregating or multiplying rows.

**Intermediate layer:** reusable validated joins, relationship classification, signed-movement investigation logic, order-level reconciliation, and exception attribution.

**Mart layer:** explicit metric definitions, record eligibility, known exclusions, quality status, and as-of assumptions. Publish metrics only when their inputs and calculation semantics are fit for purpose.

---

## 8. Implementation templates and tests

The examples below are implementation starting points. They must be incorporated into a configured dbt project and checked against the installed dbt and dbt-duckdb versions. `arguments:` in generic-test YAML is supported from dbt Core v1.10.5 onward and required in dbt v2; pin compatible versions.

### 8.1 Source declarations

**`models/staging/sources.yml`**

```yaml
version: 2

sources:
  - name: operations
    schema: raw
    tables:
      - name: branches
      - name: customers
      - name: inventory_master
      - name: invoices
      - name: payments
      - name: products
      - name: purchase_orders_header
      - name: purchase_orders_lines
      - name: sales_orders_header
      - name: sales_orders_lines
      - name: stock_ledger
      - name: suppliers
```

### 8.2 Example: staging a purchase order header

**`models/staging/stg_purchase_orders_header.sql`**

```sql
WITH source AS (
    SELECT *
    FROM {{ source('operations', 'purchase_orders_header') }}
),
parsed AS (
    SELECT
        NULLIF(TRIM(po_id), '') AS po_id,
        NULLIF(TRIM(supplier_id), '') AS supplier_id,
        NULLIF(TRIM(branch_id), '') AS branch_id,
        order_date AS source_order_date,
        TRY_CAST(NULLIF(TRIM(order_date), '') AS DATE) AS order_date,
        TRY_CAST(NULLIF(TRIM(expected_delivery_date), '') AS DATE)
            AS expected_delivery_date,
        TRY_CAST(NULLIF(TRIM(received_date), '') AS DATE) AS received_date,
        NULLIF(TRIM(po_status), '') AS po_status,
        TRY_CAST(NULLIF(TRIM(total_cost), '') AS DECIMAL(20, 4))
            AS total_cost,
        TRY_CAST(NULLIF(TRIM(total_gst_amount), '') AS DECIMAL(20, 4))
            AS total_gst_amount,
        TRY_CAST(NULLIF(TRIM(grand_total), '') AS DECIMAL(20, 4))
            AS grand_total
    FROM source
)
SELECT
    *,
    source_order_date IS NOT NULL
       AND TRIM(source_order_date) <> ''
       AND order_date IS NULL AS invalid_order_date
FROM parsed
```

This example preserves the original `order_date` text to distinguish a missing value from a parsing failure. For a completed implementation, apply the same principle to other critical source values and carry ingestion metadata through staging. `DECIMAL(20,4)` remains a provisional type choice until the source monetary precision is approved.

### 8.3 Example: dbt generic tests

**`models/staging/stg_purchase_orders_header.yml`**

```yaml
version: 2

models:
  - name: stg_purchase_orders_header
    description: Standardised purchase order headers, one row per po_id.
    columns:
      - name: po_id
        data_tests:
          - not_null
          - unique
      - name: supplier_id
        data_tests:
          - not_null
      - name: po_status
        data_tests:
          - not_null
          - accepted_values:
              arguments:
                values: ['Received', 'Cancelled']
```

After creating a supplier staging model, add `relationships` checks for `supplier_id`. For a composite key, use a singular test for duplicate `(po_id, line_number)` pairs or an approved package test; do not use `unique` on the individual line-number column.

### 8.4 Example: conditionally required receipt date

**`tests/assert_received_po_has_receipt_date.sql`**

```sql
SELECT po_id, po_status, received_date
FROM {{ ref('stg_purchase_orders_header') }}
WHERE po_status = 'Received'
  AND received_date IS NULL
```

A dbt singular test succeeds when it returns **no violating records**. Its present expected result is zero rows.

### 8.5 Example: report duplicate invoice identifiers without deleting rows

**`models/intermediate/int_invoice_identifier_collisions.sql`**

```sql
{{ config(materialized='view') }}

SELECT
    invoice_id,
    COUNT(*) AS invoice_row_count,
    COUNT(DISTINCT so_id) AS distinct_sales_orders
FROM {{ ref('stg_invoices') }}
GROUP BY invoice_id
HAVING COUNT(*) > 1
```

This is an *exception-report model*, not a guaranteed passing test. Its known nonzero result is useful. Avoid declaring `invoice_id` unique on the raw or staging source while the constraint is known to fail. If you choose to test that business constraint, mark it as expected failing evidence or warn while the issue remains unresolved; do not disguise the failure as a pass.

### 8.6 Example: flag an inventory anomaly without removing it

**`models/intermediate/int_inventory_threshold_exceptions.sql`**

```sql
{{ config(materialized='view') }}

SELECT
    product_id,
    branch_id,
    current_stock,
    max_stock,
    current_stock - max_stock AS units_above_configured_max
FROM {{ ref('stg_inventory_master') }}
WHERE current_stock > max_stock
```

This is diagnostic output, not proof that physical warehouse capacity has been exceeded.

### 8.7 Test execution and evidence

Typical commands after ingestion and configuration:

```bash
dbt debug --profiles-dir .
dbt build --select staging --profiles-dir .
dbt test --profiles-dir .
```

Before running the entire project, ensure all referenced models actually exist. Where known anomalies have intentionally nonzero failure counts, use exception models and an explicit release gate; do not misrepresent a fully failing `dbt build` as a successful quality outcome.

Store outputs or summary counts from `target/run_results.json`, table row counts, rejected/flagged amounts, and investigation notes in the evidence directory. If dbt test failures are stored, restrict any sensitive row-level evidence appropriately.

---

## 9. Measurement and improvement scorecard

### 9.1 Metrics and denominators

| Measure                           | Formula                                                                 | Interpretation                                       |
| --------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------- |
| Required-field completeness       | Validly populated**required** values / applicable required values | Conditional nulls excluded from required denominator |
| Candidate-key uniqueness          | Distinct key combinations / total records                               | Diagnostic until key semantics approved              |
| Relationship existence pass rate  | Child rows with at least one parent / checked child rows                | Not sufficient to prove unambiguous joins            |
| Unique-parent match rate          | Child rows with exactly one parent / applicable child rows              | Required for safe attribution                        |
| Parse success rate                | Successfully parsed nonblank values / attempted nonblank values         | Measure separately from missingness                  |
| Monetary reconciliation pass rate | Groups within approved tolerance / evaluated groups                     | Subject to documented currency and rounding          |
| Staging preservation rate         | Staged source row count / original source row count                     | Target 100% for unfiltered staging                   |
| Exception exposure                | Flagged or quarantined record count**and associated amounts**     | Shows scope of excluded data                         |
| Open critical issues              | P0 issues lacking resolution or approved release limitation             | Must be zero for affected published metric           |

Do **not** collapse these into a single weighted quality score without defending the weights. A high aggregate score can mask one serious payment attribution problem.

### 9.2 Baseline versus target versus actual

| Indicator                                  | Baseline | Intended outcome                                                                               | Post-cleaning actual          |
| ------------------------------------------ | -------: | ---------------------------------------------------------------------------------------------- | ----------------------------- |
| Invoice ID duplicate excess                |      197 | Collisions resolved or isolated from unsafe joins                                              | **Not implemented yet** |
| Payment ID duplicate excess                |      202 | Transactions retained and identity risk documented                                             | **Not implemented yet** |
| Ambiguous payment-to-invoice rows          |      417 | Zero ambiguous rows in**published invoice-attributed metrics**; exception count reported | **Not implemented yet** |
| Inventory rows above configured max        |      180 | Definitions verified; anomalies transparently flagged                                          | **Not implemented yet** |
| Ledger movements tied to cancelled orders  |    2,817 | Reversal/status semantics investigated and documented                                          | **Not implemented yet** |
| Received POs missing receipt date          |        0 | Remain at zero                                                                                 | **Not implemented yet** |
| Cancelled POs missing receipt date         |    2,370 | Remain valid nulls where business rule holds                                                   | **Not implemented yet** |
| Cancelled SOs with populated delivery date |    1,967 | Clarify semantics and prevent inappropriate delivered-order KPIs                               | **Not implemented yet** |

A resolved finding may remain in the raw data. Improvement can consist of safe transformation, exception isolation, explicit caveats, and prevention of downstream misstatement, not necessarily reducing the raw anomaly count to zero.

---

## 10. Issue register and decision log

| Issue ID | Issue                                       | Priority | Evidence                    | Current decision                                      | Status                             |
| -------- | ------------------------------------------- | -------- | --------------------------- | ----------------------------------------------------- | ---------------------------------- |
| DQI-001  | Invoice ID collisions                       | P0       | 197 excess duplicates       | Preserve; classify; block ambiguous allocation        | **Open**                     |
| DQI-002  | Payment ID collisions                       | P0       | 202 excess duplicates       | Preserve individual rows; verify identity             | **Open**                     |
| DQI-003  | Stock above configured maximum              | P1       | 180/180 affected            | Flag; review units and thresholds                     | **Open**                     |
| DQI-004  | Ledger activity against cancelled orders    | P1       | 2,817 records               | Investigate reversals and timing                      | **Open**                     |
| DQI-005  | Inventory adjustment direction and ordering | P1       | 2,454 adjustments           | Preserve sequence; investigate signed balance changes | **Open**                     |
| DQI-006  | Missing receipt dates on cancelled POs      | P3       | 2,370 rows                  | Preserve valid conditional nulls                      | **Policy proposed**          |
| DQI-007  | Cancelled SOs with delivery dates           | P1       | 1,967 rows                  | Do not infer delivery from date alone                 | **Open**                     |
| DQI-008  | Product`margin_percentage` definition     | P2       | Catalogue field present     | Do not assume gross margin/markup                     | **Open**                     |
| DQI-009  | Text capacity and dimensions                | P2       | `sqft`; `dimensions_cm` | Parse with unit checks                                | **Ready for implementation** |

**Single-person ownership:** All decisions, code reviews, and sign-offs are recorded by the project maintainer. Where business confirmation is unavailable, label decisions `Assumption` or `Unresolved`; do not invent external approval.

For each future decision, add a record containing:

```text
Decision ID:
Related rule / issue:
Original source evidence:
Proposed interpretation:
Alternative interpretations considered:
Chosen transformation or publication restriction:
Validation SQL / test:
Effect on downstream metrics:
Decision status: Confirmed by source / Assumption / Unresolved
Date and Git commit:
```

---

## 11. End-to-end solo execution workflow

### Stage A. Freeze and record source baseline

- [ ] Place the 12 original files in the local raw directory; confirm repository exclusion policy.
- [ ] Record file names, SHA-256 hashes, modification metadata, row counts, column names, and ingestion batch identifier.
- [ ] Confirm source totals and date coverage match the inventory in Section 2.
- [ ] Define row provenance in the ingestion script.

**Artifact:** `reports/source_manifest.csv` and a verified source profiling report.

### Stage B. Implement deterministic staging cleaning

- [ ] Set up raw DuckDB tables that preserve original values.
- [ ] Create 12 dbt staging models, initially one per raw source.
- [ ] Standardise key whitespace and categorical representations carefully.
- [ ] Cast dates, whole-number fields, decimals, and percentages with failure indicators.
- [ ] Parse capacity and dimensions, preserving units and raw representations.
- [ ] Assert source-to-staging row preservation and key-grain stability.

**Artifact:** version-controlled `models/staging/` and `models/staging/*.yml`.

### Stage C. Add integrity and reconciliation controls

- [ ] Implement candidate/composite key checks.
- [ ] Implement parent existence and cardinality checks.
- [ ] Implement line-level and header-level monetary reconciliations.
- [ ] Add conditionally required dates and temporal lifecycle checks.
- [ ] Build diagnostic exception models for known collisions and inventory anomalies.
- [ ] Check tests against intentionally corrupted small synthetic samples to confirm that the tests actually detect failures.

**Artifact:** `tests/`, exception views, and reproducible test output.

### Stage D. Investigate business-rule anomalies

- [ ] Document collided invoice and payment identifiers, without deleting source rows.
- [ ] Quantify ambiguous payment row counts and amounts.
- [ ] Review stock threshold definitions and product/branch discrepancies.
- [ ] Investigate cancelled order stock movements and adjustment signs.
- [ ] Document unresolved questions about cancelled SO delivery dates and historical stock as-of times.
- [ ] Update issue register with decisions, evidence, and residual limitations.

**Artifact:** `docs/data_quality_issue_register.md` or CSV and investigation SQL.

### Stage E. Publish limited trusted outputs

- [ ] Document eligible/blocked record classes per proposed analytical dataset.
- [ ] Ensure no join creates undocumented fanout.
- [ ] Reconcile included plus excluded records and monetary amounts.
- [ ] Produce before/after quality measures without claiming unresolved anomalies were fixed.
- [ ] Run full reproducibility checks from a clean DuckDB database.
- [ ] Commit code, documentation, metrics, and a clear README.

**Artifact:** `docs/data_quality_improvement_report.md`, dbt documentation, and GitHub submission.

---

## 12. Acceptance criteria and definition of done

The Data Cleaning and Quality Improvement task is complete **only when**:

1. All 12 source extracts have documented schemas, candidate grains, and keys.
2. Source checksums, load provenance, and repeatable ingestion behaviour are demonstrated.
3. Standardisation transformations exist, run successfully, and are peer-reviewable through version control even though the project has one contributor.
4. For every staged model, original row count and key behaviour are either preserved or an approved exception is documented.
5. Key, referential, type, domain, reconciliation, and conditional-null tests have evidence, not merely definitions in this document.
6. The P0 ambiguity risks are either resolved or structurally isolated from affected downstream outputs.
7. All known issues have a disposition: resolved, expected, flagged, quarantined for specific uses, or unresolved with documented limitation.
8. Reports show actual execution results, not unexecuted intentions.
9. An independent developer could reproduce the workflow using the authorised source data and pinned dependencies.
10. The README states which analytical questions are **not yet safely supported**, particularly invoice-attributed payments and historical inventory snapshots.

**Release decision at document creation:** **Not approved for unrestricted analytical publication.** Profiling is complete and arithmetic checks are promising, but key collisions and several operational-semantic issues remain unresolved. Standardised staging work and end-to-end test evidence are not yet complete.

---

## 13. Expected GitHub deliverables

```text
heavy-supplier-analytics/
├── data/
│   ├── raw/                 # local only if source licence/sensitivity requires
│   └── sample/              # shareable, minimal test samples only
├── ingestion/
│   └── load_raw.py
├── models/
│   ├── staging/
│   │   ├── sources.yml
│   │   ├── stg_branches.sql
│   │   ├── stg_customers.sql
│   │   ├── stg_inventory_master.sql
│   │   ├── stg_invoices.sql
│   │   ├── stg_payments.sql
│   │   ├── stg_products.sql
│   │   ├── stg_purchase_orders_header.sql
│   │   ├── stg_purchase_orders_lines.sql
│   │   ├── stg_sales_orders_header.sql
│   │   ├── stg_sales_orders_lines.sql
│   │   ├── stg_stock_ledger.sql
│   │   └── stg_suppliers.sql
│   ├── intermediate/
│   │   └── ...
│   └── marts/               # only when publication criteria are met
├── tests/
│   └── ...
├── reports/
│   ├── source_manifest.csv
│   ├── profiling/
│   ├── quality_baseline.csv
│   └── quality_post_cleaning.csv
├── docs/
│   ├── data_cleaning_and_quality_plan.md
│   ├── data_quality_issue_register.md
│   ├── data_quality_improvement_report.md
│   └── data_dictionary.md
├── .gitignore
├── dbt_project.yml
├── profiles.yml             # no secrets committed
├── requirements.txt         # pin tested dependency versions
└── README.md
```

This is a proposed final layout, not a statement that all files already exist.

---

## 14. References and methodological basis

This is an application-specific quality policy informed by established practices, not a certification against a formal standard. The following references support the technical design:

1. **dbt Developer Hub, Staging models.** Keep staging atomic, reusable, and typically one source to one staging model; avoid unnecessary aggregation and grain changes. [https://docs.getdbt.com/best-practices/how-we-structure/2-staging](https://docs.getdbt.com/best-practices/how-we-structure/2-staging)
2. **dbt Developer Hub, Data tests.** `unique`, `not_null`, `relationships`, `accepted_values`, singular tests, and failure behaviour. [https://docs.getdbt.com/docs/build/data-tests](https://docs.getdbt.com/docs/build/data-tests)
3. **dbt Developer Hub, Test severity.** Configuring test failures and warnings; apply severity with an explicit project policy. [https://docs.getdbt.com/reference/resource-configs/severity](https://docs.getdbt.com/reference/resource-configs/severity)
4. **dbt Developer Hub, Workflow best practices.** Version control, code review, and testing of source assumptions. [https://docs.getdbt.com/best-practices/best-practice-workflows](https://docs.getdbt.com/best-practices/best-practice-workflows)
5. **DuckDB documentation, CSV reading.** Explicit input typing and predictable CSV ingestion. [https://duckdb.org/docs/stable/data/csv/overview](https://duckdb.org/docs/stable/data/csv/overview)
6. **DuckDB documentation, Type casting.** `TRY_CAST` can return `NULL` on failed conversion; failures should be detected separately from originally missing values. [https://duckdb.org/docs/stable/sql/expressions/cast](https://duckdb.org/docs/stable/sql/expressions/cast)

**Evidence source:** the 12 CSV files supplied for this project and their initial source profiling outputs. No formal source-system schema or official operational data contract was provided.

---

## Appendix A. Initial categorical domains observed in source data

These are **observed values in this extract**, not permanent authoritative domains:

| Column                                | Values observed                                                   |
| ------------------------------------- | ----------------------------------------------------------------- |
| `purchase_orders_header.po_status`  | `Received`, `Cancelled`                                       |
| `sales_orders_header.order_status`  | `Delivered`, `Cancelled`                                      |
| `invoices.payment_status`           | `Paid`, `Partially Paid`, `Unpaid`                          |
| `payments.payment_method`           | `UPI`, `Credit Card`, `Bank Transfer`, `Cheque`, `Cash` |
| `stock_ledger.movement_type`        | `IN`, `OUT`, `ADJUSTMENT`                                   |
| `stock_ledger.reference_type`       | `PO`, `SO`, `ADJ`                                           |
| `branches.service_center_available` | `Yes`, `No`                                                   |
| `products.criticality_level`        | `High`, `Medium`, `Low`                                     |
| `products.usage_frequency`          | `High`, `Medium`, `Low`                                     |
| `products.uom`                      | `piece`, `set`, `cartridge`                                 |
| `customers.payment_terms`           | `Advance`, `Net 15`, `Net 30`, `Net 45`, `Net 60`       |
| `sales_orders_header.sales_channel` | `Field Sales`, `Dealer Network`, `Counter Sale`, `Online` |

Unexpected new labels should trigger review rather than automatic conversion to an arbitrary existing category.

## Appendix B. Terms used in this plan

**Business key:** an identifier or combination of identifiers claimed to uniquely represent a business entity. A unique value in one extract is not proof of a durable contract.

**Technical source-row identifier:** stable ingestion metadata that distinguishes individual raw rows; does not repair or establish business identity.

**Grain:** the precise meaning of one row in a table.

**Fanout:** multiplication of rows in a join when a parent key is not unique at the expected grain.

**Quarantine:** preserving records while preventing them from participating in a particular trusted output until eligibility is justified.

**Idempotency:** rerunning an operation using the same inputs does not unintentionally change the result or double-count data.

**Source of truth:** the authoritative record or system for a particular business fact; not automatically established by being the most convenient CSV.

**As-of date:** the point in time a stock position or financial balance represents; different from a file extraction timestamp.

**Data contract:** an agreed specification of structure, key semantics, allowed values, meaning, timing, and quality expectations. This document contains *proposed* contracts pending validation.

---

**End of Data Cleaning and Quality Improvement Plan, version 1.0.**
