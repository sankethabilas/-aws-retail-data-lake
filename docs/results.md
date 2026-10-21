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

## Day 5: CSV vs Parquet

Measured on 2026-10-22 on the same machine and library versions as Day 4.
Read times are the average of 3 runs. The CSV was read with `dtype=str`, the way the pipeline reads it.

| Measurement | Source CSV | Curated Parquet (snappy) |
|---|---|---|
| Size on disk | 47,758,972 bytes (45.5 MB) | 5,565,804 bytes (5.3 MB) |
| Files | 1 | 13 (one per `year=/month=` partition) |
| Rows | 541,909 | 536,639 |
| Read all columns into pandas | 0.606 s | 0.043 s |
| Read only `revenue` | n/a (CSV must be parsed in full) | 0.009 s |

The Parquet output is 8.6x smaller than the CSV (88% less storage) and about 14x faster to read in full.
Reading a single column is faster again, because Parquet is columnar.
The Day 8 Athena bytes-scanned comparison should show the same effect.

### Tests

`pytest -q --cov=src` gives 15 passed in 0.6 s, with 56% line coverage of `src/`.
- `transform_data.py` is at 100% coverage.
- The uncovered lines are the CLI `__main__` blocks and the download and profiling scripts, which need the real dataset.

CI runs `ruff check src tests` and the same pytest command on every push and pull request (`.github/workflows/tests.yml`).
