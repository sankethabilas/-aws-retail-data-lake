# Source data profiling

Measured on 2026-10-20 from `data/raw/online_retail.csv`, which `python -m src.download_data` creates.
Reproduce with `python -m src.profile_data`.
Every number below comes from that run, not from other write-ups of the dataset.

## Shape and types

- 541,909 rows × 8 columns: `InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country`.
- All columns are read as text on purpose. Numbers and dates are parsed explicitly, and none failed to parse:
  - `Quantity`: 0 unparseable
  - `UnitPrice`: 0 unparseable
  - `InvoiceDate`: 0 unparseable

## Nulls per column

| Column | Nulls |
|---|---|
| InvoiceNo | 0 |
| StockCode | 0 |
| Description | 1,454 |
| Quantity | 0 |
| InvoiceDate | 0 |
| UnitPrice | 0 |
| CustomerID | 135,080 (about 25% of rows) |
| Country | 0 |

## Data quality counts

| Check | Count |
|---|---|
| Exact duplicate rows (all 8 columns identical) | 5,268 |
| Cancellation rows (`InvoiceNo` starts with `C`) | 9,288 |
| Cancellation invoices (distinct) | 3,836 |
| Quantity < 0 | 10,624 |
| Quantity < 0 and a cancellation | 9,288 |
| Quantity < 0 and not a cancellation | 1,336 |
| Quantity = 0 | 0 |
| UnitPrice = 0 | 2,515 |
| UnitPrice < 0 | 2 |

## Coverage

| Item | Value |
|---|---|
| Date range | 2010-12-01 08:26:00 to 2011-12-09 12:50:00 |
| Distinct invoices | 25,900 |
| Distinct customers | 4,372 |
| Distinct stock codes | 4,070 |
| Countries | 38 |
| Top countries by rows | United Kingdom 495,478 · Germany 9,495 · France 8,557 |

## Observations for Day 3 validation rules

- **Every cancellation has a negative quantity.** None has a quantity of 0 or more.
- **All 1,336 negative-quantity rows that are not cancellations have a unit price of 0.** These look like stock adjustments (damaged, lost or found stock), so they should be kept as `ADJUSTMENT`, not rejected.
- **Both negative-price rows are accounting entries**, not sales:
  - Invoices `A563186` and `A563187`, StockCode `B`, "Adjust bad debt", quantity 1, price -11,062.06.
  - Note that these invoice numbers start with `A`, not a digit.
  - Rule: reject them with `negative_unit_price`.
- **No rows have a zero quantity or an unparseable date** in this file. The rules for those cases still need to exist and be tested.
- **About 25% of rows have no `CustomerID`.** Keep them, with `customer_id` left NULL, so revenue totals stay complete.
- **There are 5,268 exact duplicates.** Keep the first copy, drop the rest, and report the count.
