# Results

Every number here was measured on this project's own runs.

## Day 4: full pipeline run

Measured on 2026-10-21 with `python -m src.run_pipeline` (pandas 3.0.6, pyarrow 26.0.0, Windows 11).
Numbers come from `reports/run_manifest.json` and `reports/validation_report.json`.

### Row counts

| Step | Rows |
|---|---|
| Rows read | 541,909 |
| Rejected to quarantine | 2 (both `negative_unit_price`) |
| Exact duplicates removed | 5,268 |
| Rows written to curated Parquet | 536,639 |

Reconciliation: 2 + 5,268 + 536,639 = 541,909. The pipeline asserts this on every run.

### Curated rows by transaction type

| Type | Rows | Revenue (GBP) |
|---|---|---|
| SALE | 526,052 | 10,642,110.80 |
| CANCELLATION | 9,251 | -893,979.73 |
| ADJUSTMENT | 1,336 | 0.00 |
| **Net revenue** | 536,639 | **9,748,131.07** |

There are 9,251 cancellation rows after deduplication, compared with 9,288 in the source, because 37 cancellation rows were exact duplicates.

### Output and runtime

| Item | Value |
|---|---|
| Partitions (`year=/month=`) | 13 (2010-12 to 2011-12) |
| Parquet files | 13 |
| Parquet size | 5,565,804 bytes (about 5.3 MB) |
| Source CSV size | about 46 MB |
| Runtime | 2.7 s (first run), 2.5 s (rerun) |

### Idempotency

Running the pipeline twice produced manifests that differed only in `run_at_utc` and `seconds`.
All row counts, net revenue, file count and byte size were identical.
