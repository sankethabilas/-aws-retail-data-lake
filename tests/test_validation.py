import pandas as pd
import pytest

from src.validate_data import (
    SchemaError,
    build_validation_report,
    check_schema,
    parse_types,
    rejection_reasons,
)


def test_missing_required_column_fails_clearly(raw_df):
    with pytest.raises(SchemaError, match="UnitPrice"):
        check_schema(raw_df.drop(columns=["UnitPrice"]))


def test_invalid_date_is_rejected(raw_df):
    raw_df.loc[0, "InvoiceDate"] = "not-a-date"
    reasons = rejection_reasons(parse_types(raw_df))
    assert reasons.iloc[0] == "invalid_invoice_date"


def test_missing_customer_id_is_retained(raw_df):
    reasons = rejection_reasons(parse_types(raw_df))
    assert pd.isna(reasons.iloc[3])  # row 3 has no CustomerID but is valid


def test_negative_unit_price_is_rejected(raw_df):
    raw_df.loc[0, "UnitPrice"] = "-11062.06"
    assert rejection_reasons(parse_types(raw_df)).iloc[0] == "negative_unit_price"


def test_text_is_trimmed(raw_df):
    assert parse_types(raw_df)["country"].iloc[3] == "France"


@pytest.mark.parametrize("quantity", ["0", "1.5", "six"])
def test_zero_fractional_or_text_quantity_is_rejected(raw_df, quantity):
    raw_df.loc[0, "Quantity"] = quantity
    assert rejection_reasons(parse_types(raw_df)).iloc[0] == "invalid_quantity"


def test_first_failing_rule_wins_and_counts_reconcile(raw_df):
    raw_df.loc[0, "InvoiceDate"] = "not-a-date"
    raw_df.loc[0, "UnitPrice"] = "-1"
    typed = parse_types(raw_df)
    reasons = rejection_reasons(typed)
    report = build_validation_report(raw_df, typed, reasons)
    assert reasons.iloc[0] == "invalid_invoice_date"
    assert report["rejected_by_reason"] == {"invalid_invoice_date": 1}
    assert report["rows_valid"] + report["rows_rejected"] == report["rows_read"]
