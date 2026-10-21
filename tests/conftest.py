import pandas as pd
import pytest

ROWS = [  # InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
    ["536365", "85123A", "WHITE HANGING HEART", "6", "2010-12-01 08:26:00", "2.55", "17850.0", "United Kingdom"],
    ["C536379", "D", "Discount", "-1", "2010-12-01 09:41:00", "27.50", "14527.0", "United Kingdom"],
    ["536414", "22139", None, "-56", "2010-12-01 11:52:00", "0", None, "United Kingdom"],
    ["536370", "22728", "ALARM CLOCK", "24", "2011-01-05 08:45:00", "3.75", None, " France "],
]
COLUMNS = ["InvoiceNo", "StockCode", "Description", "Quantity",
           "InvoiceDate", "UnitPrice", "CustomerID", "Country"]


@pytest.fixture
def raw_df():
    return pd.DataFrame(ROWS, columns=COLUMNS, dtype="object")


@pytest.fixture
def raw_csv(tmp_path, raw_df):
    path = tmp_path / "source.csv"
    raw_df.to_csv(path, index=False)
    return path
