# Retail Sales Data Lake on AWS

> Draft. This README is filled in as the project is built.

A batch data pipeline that turns a retailer's raw transaction export into a queryable data lake on AWS.
The ETL runs locally in Python and pandas.
The cloud layer is Amazon S3, the AWS Glue Data Catalog and Amazon Athena, kept to near-zero cost.

**Stack:** Python · pandas · pytest · GitHub Actions · Amazon S3 · AWS Glue Data Catalog · Amazon Athena · IAM · AWS Budgets

## Business problem

The business is a UK-based online retailer that sells gifts. It exports a year of transactions as one flat file.

That file can't be used for reporting as it is:

- Cancellations are mixed in with sales.
- Stock adjustments look like negative sales.
- Some rows are exact duplicates.
- About a quarter of rows have no customer ID.
- A few rows are accounting entries, not sales.

Totals computed straight from the file are wrong, and nobody can say by how much.

This project builds a pipeline that:

- validates every row, and quarantines bad rows with a reason instead of dropping them silently;
- labels each row as a sale, cancellation or adjustment;
- stores clean, partitioned Parquet in S3;
- lets analysts answer revenue questions in SQL, with totals that reconcile back to the source.

## Questions answered

- What are daily and monthly net revenue, and how do they trend over the year?
- Which products sell best, by quantity and by revenue? Stock adjustments are excluded.
- Which countries bring in the most revenue?
- What share of invoices and revenue do cancellations account for?
- How clean is the source data? How many rows were rejected, and why?

**Metric definitions:**

- **Revenue** means **net revenue** (sales minus cancellations) unless a query says *gross*.
- **Gross revenue** counts SALE rows only.
- **Invoice counts** exclude cancellation invoices.

## Architecture

```
UCI Online Retail (.xlsx)
        │  download_data.py (once → source CSV)
        ▼
  Python ETL (local) ──► quarantine/ rejected rows
  validate · clean    ──► reports/ validation report + run manifest
  dedupe · revenue
        │
        ├──► S3 raw zone       raw/ CSV, unchanged
        └──► S3 curated zone   Parquet (snappy), year=YYYY/month=M
                    │
                    ▼
           Glue Data Catalog (retail_db)
                    │
                    ▼
           Athena SQL analytics (workgroup with scan limit)
```

1. **Ingest:** download the workbook once and convert it to the CSV that stands in for the company's source file.
2. **Validate:** check the schema, parse types, and tag each invalid row with a rejection reason.
3. **Transform:**
   - clean text;
   - flag cancellations and stock adjustments;
   - calculate revenue;
   - remove exact duplicates;
   - add year and month partition columns.
4. **Load:** write snappy Parquet partitioned by year and month, and replace the curated output in S3 each run, so reruns never duplicate data.
5. **Catalog and query:** register tables with explicit `CREATE EXTERNAL TABLE` DDL, answer the business questions in Athena, and reconcile the totals with Python.

## Status

| Stage | Status |
|---|---|
| Project setup and AWS guardrails | Done |
| Download and profiling ([docs/profiling.md](docs/profiling.md)) | Done |
| Validation, transformation, tests and CI | Planned |
| S3, Glue Data Catalog, Athena | Planned |

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python -m src.download_data   # creates data/raw/online_retail.csv
python -m src.profile_data    # prints the profiling counts
```

## Dataset

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository.
<https://doi.org/10.24432/C5BW33>. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The dataset has 541,909 transactions from 2010-12-01 to 2011-12-09.
The data isn't stored in this repo. See [data/README.md](data/README.md) for how to download it.
