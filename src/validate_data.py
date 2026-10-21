"""Schema and record-level validation for the retail sales source file."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["InvoiceNo", "StockCode", "Description", "Quantity",
                    "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
COLUMN_MAP = {"InvoiceNo": "invoice_no", "StockCode": "stock_code", "Description": "description",
              "Quantity": "quantity", "InvoiceDate": "invoice_date", "UnitPrice": "unit_price",
              "CustomerID": "customer_id", "Country": "country"}


class SchemaError(ValueError):
    """Raised when the source file does not have the expected columns."""


def check_schema(df: pd.DataFrame) -> None:
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise SchemaError(f"Missing required columns: {missing}")


def _clean_text(s: pd.Series) -> pd.Series:
    s = s.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    return s.replace("", pd.NA)


def parse_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df[REQUIRED_COLUMNS].rename(columns=COLUMN_MAP).copy()
    for col in ["invoice_no", "stock_code", "description", "country"]:
        out[col] = _clean_text(out[col])
    out["stock_code"] = out["stock_code"].str.upper()
    out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce")
    out["unit_price"] = pd.to_numeric(out["unit_price"], errors="coerce")
    out["invoice_date"] = pd.to_datetime(out["invoice_date"], errors="coerce",
                                         format="ISO8601")
    # CustomerID arrives as "17850.0" or blank: keep as nullable text, never invent IDs.
    cid = pd.to_numeric(out["customer_id"], errors="coerce").astype("Int64")
    out["customer_id"] = cid.astype("string")
    return out


def rejection_reasons(df: pd.DataFrame) -> pd.Series:
    """Return the first failing rule per row, or <NA> when the row is valid."""
    rules = [
        ("missing_invoice_no", df["invoice_no"].isna()),
        ("missing_stock_code", df["stock_code"].isna()),
        ("invalid_invoice_date", df["invoice_date"].isna()),
        ("invalid_quantity", df["quantity"].isna() | (df["quantity"] == 0)
            | (df["quantity"] % 1 != 0)),
        ("invalid_unit_price", df["unit_price"].isna()),
        ("negative_unit_price", df["unit_price"] < 0),
    ]
    reasons = np.select([cond.fillna(True).to_numpy(dtype=bool) for _, cond in rules],
                        [name for name, _ in rules], default="")
    return pd.Series(reasons, index=df.index, dtype="string").replace("", pd.NA)


def build_validation_report(raw: pd.DataFrame, typed: pd.DataFrame,
                            reasons: pd.Series) -> dict:
    rejected = reasons.notna()
    dates = typed["invoice_date"]
    return {
        "rows_read": len(raw),
        "rows_valid": int((~rejected).sum()),
        "rows_rejected": int(rejected.sum()),
        "rejected_by_reason": {k: int(v) for k, v in reasons.value_counts().items()},
        "null_counts": {k: int(v) for k, v in typed.isna().sum().items()},
        "exact_duplicate_rows": int(raw.duplicated().sum()),
        "cancellation_rows": int(typed["invoice_no"].str.startswith("C", na=False).sum()),
        "min_invoice_date": str(dates.min()), "max_invoice_date": str(dates.max()),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate the source CSV and write a report")
    parser.add_argument("--csv", default="data/raw/online_retail.csv")
    parser.add_argument("--reports-dir", default="reports")
    args = parser.parse_args()

    raw = pd.read_csv(args.csv, dtype=str)
    check_schema(raw)
    typed = parse_types(raw)
    report = build_validation_report(raw, typed, rejection_reasons(typed))

    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
