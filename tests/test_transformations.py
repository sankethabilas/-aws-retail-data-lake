import pandas as pd

from src.transform_data import add_business_columns, deduplicate
from src.validate_data import parse_types


def curated(raw_df):
    return add_business_columns(parse_types(raw_df))


def test_revenue_is_quantity_times_price(raw_df):
    assert curated(raw_df)["revenue"].iloc[0] == round(6 * 2.55, 2)


def test_cancellation_is_preserved_and_flagged(raw_df):
    row = curated(raw_df).iloc[1]
    assert row["is_cancellation"] and row["transaction_type"] == "CANCELLATION"
    assert row["revenue"] < 0


def test_negative_quantity_without_c_is_adjustment(raw_df):
    assert curated(raw_df)["transaction_type"].iloc[2] == "ADJUSTMENT"


def test_partition_values_match_invoice_date(raw_df):
    df = curated(raw_df)
    assert (df["year"] == df["invoice_date"].dt.year).all()
    assert (df["month"] == df["invoice_date"].dt.month).all()


def test_exact_duplicates_removed_but_repeated_products_kept(raw_df):
    exact_dup = raw_df.iloc[[0]]
    same_product_other_qty = raw_df.iloc[[0]].assign(Quantity="12")
    df = curated(pd.concat([raw_df, exact_dup, same_product_other_qty], ignore_index=True))
    out, removed = deduplicate(df)
    assert removed == 1 and len(out) == len(raw_df) + 1
