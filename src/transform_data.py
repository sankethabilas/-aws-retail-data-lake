"""Business transformations and Parquet output for curated sales data."""

import shutil
from pathlib import Path

import numpy as np
import pandas as pd

SOURCE_COLUMNS = ["invoice_no", "stock_code", "description", "quantity",
                  "invoice_date", "unit_price", "customer_id", "country"]


def add_business_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["quantity"] = out["quantity"].astype("int64")
    # Millisecond precision: Athena reads ms Parquet timestamps reliably.
    out["invoice_date"] = out["invoice_date"].astype("datetime64[ms]")
    out["is_cancellation"] = out["invoice_no"].str.startswith("C").astype(bool)
    out["transaction_type"] = np.select(
        [out["is_cancellation"], out["quantity"] < 0],
        ["CANCELLATION", "ADJUSTMENT"], default="SALE")
    out["revenue"] = (out["quantity"] * out["unit_price"]).round(2)
    out["year"] = out["invoice_date"].dt.year.astype("int32")
    out["month"] = out["invoice_date"].dt.month.astype("int32")
    return out


def deduplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Drop rows whose eight source columns are identical; keep the first."""
    before = len(df)
    out = df.drop_duplicates(subset=SOURCE_COLUMNS, keep="first")
    return out, before - len(out)


def write_partitioned_parquet(df: pd.DataFrame, out_dir: Path) -> list[Path]:
    """Replace the whole curated dataset so reruns never duplicate data."""
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    df.to_parquet(out_dir, partition_cols=["year", "month"], index=False,
                  compression="snappy", engine="pyarrow")
    return sorted(out_dir.rglob("*.parquet"))
