# Data dictionary

## Validation rules

`src/validate_data.py` checks every source row against the rules below.
A row that fails any rule goes to quarantine with a `rejection_reason`.

| Priority | Reason | Condition |
|---|---|---|
| 1 | `missing_invoice_no` | `InvoiceNo` is blank after trimming |
| 2 | `missing_stock_code` | `StockCode` is blank after trimming |
| 3 | `invalid_invoice_date` | `InvoiceDate` cannot be parsed as a date |
| 4 | `invalid_quantity` | `Quantity` is not a number, is 0, or is not a whole number |
| 5 | `invalid_unit_price` | `UnitPrice` is not a number |
| 6 | `negative_unit_price` | `UnitPrice` < 0 |

A missing column stops the run with `SchemaError`, which names the missing columns.
Extra columns are ignored.

### One reason per row

Each rejected row gets exactly one reason: the first rule it fails, in priority order.
For example, a row with a bad date and a negative price is reported only as `invalid_invoice_date`.
This means the counts in `rejected_by_reason` add up to `rows_rejected`.

### Rows kept on purpose

These rows look unusual but are valid, so they are not rejected:

- **Missing `CustomerID`** (135,080 rows, about 25%). `customer_id` stays NULL. Customers are never invented.
- **Missing `Description`** (1,454 rows).
- **Unit price of 0** (2,515 rows).
- **Negative quantity.** These rows are cancellations (`InvoiceNo` starts with `C`) or stock adjustments, and are labelled on Day 4.

### Invoices starting with `A`

The two rows on invoices `A563186` and `A563187` ("Adjust bad debt", price -11,062.06) are accounting entries, not sales.
They are rejected as `negative_unit_price`.
The rejection is based on the price, not on the invoice number starting with `A`.

### Cleaning applied before the rules

- Text columns have whitespace trimmed and repeated spaces collapsed. Empty text becomes NULL.
- `stock_code` is upper-cased.
- `customer_id` is stored as text without the trailing `.0` (`"17850.0"` becomes `"17850"`).
- Column names are converted to snake_case.

## Curated columns

`src/transform_data.py` writes these columns to `data/curated/sales/` as snappy-compressed Parquet, partitioned as `year=YYYY/month=M`.

| Column | Type | Meaning | Rule | Example |
|---|---|---|---|---|
| `invoice_no` | string | Invoice number | Trimmed; `C` prefix means cancellation | `536365` |
| `stock_code` | string | Product code | Trimmed, upper-cased | `85123A` |
| `description` | string | Product name | Trimmed; may be NULL | `WHITE HANGING HEART T-LIGHT HOLDER` |
| `quantity` | int64 | Units on the line | Non-zero whole number; negative for cancellations and adjustments | `6` |
| `invoice_date` | timestamp (ms) | Invoice date and time | Millisecond precision so Athena reads it reliably | `2010-12-01 08:26:00` |
| `unit_price` | double | Price per unit (GBP) | ≥ 0 | `2.55` |
| `customer_id` | string | Customer number | NULL when the source has none; never invented | `17850` |
| `country` | string | Customer country | Trimmed | `United Kingdom` |
| `is_cancellation` | boolean | Line is on a cancellation invoice | `invoice_no` starts with `C` | `false` |
| `transaction_type` | string | Line type | `CANCELLATION` if a cancellation, else `ADJUSTMENT` if quantity < 0, else `SALE` | `SALE` |
| `revenue` | double | Line value | `quantity × unit_price`, rounded to 2 dp; negative for cancellations | `15.3` |
| `year` | int (partition) | Invoice year | From `invoice_date` | `2010` |
| `month` | int (partition) | Invoice month, 1–12 | From `invoice_date` | `12` |

### Business rules

- **Cancellations are kept.** Their negative revenue reduces net revenue.
- **Stock adjustments** (negative quantity, not a cancellation, price 0) are kept as `ADJUSTMENT` and excluded from product sales rankings.
- **Net revenue** is `SUM(revenue)` over all rows. **Gross revenue** is `SUM(revenue)` over `SALE` rows only.
- **Exact duplicates** (all 8 source columns identical after cleaning) are dropped, keeping the first copy. The same product repeated on one invoice with different values is kept.
- **Reruns replace** the whole curated folder, so running the pipeline twice never duplicates data.
