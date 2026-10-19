"""Profile the source CSV: the counts that Day 3 validation rules are based on."""

import argparse
from pathlib import Path

import pandas as pd


def profile(csv_path: Path) -> None:
    # Read as text, like the pipeline does, then parse numbers and dates explicitly.
    df = pd.read_csv(csv_path, dtype=str)
    q = pd.to_numeric(df["Quantity"], errors="coerce")
    p = pd.to_numeric(df["UnitPrice"], errors="coerce")
    d = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    print("shape:", df.shape)
    print("\ndtypes:\n", df.dtypes, sep="")
    print("\nnulls per column:\n", df.isna().sum(), sep="")
    print("\nexact duplicate rows:", df.duplicated().sum())
    print("cancellation rows (InvoiceNo starts with C):", df["InvoiceNo"].str.startswith("C", na=False).sum())
    print("quantity < 0:", (q < 0).sum(), " unparseable:", q.isna().sum())
    print("unit price == 0:", (p == 0).sum(), " < 0:", (p < 0).sum(), " unparseable:", p.isna().sum())
    print("date range:", d.min(), "to", d.max(), " unparseable:", d.isna().sum())
    print("countries:", df["Country"].nunique())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/raw/online_retail.csv")
    args = parser.parse_args()
    profile(Path(args.csv))
