"""Download the UCI Online Retail dataset and convert it to the source CSV."""

import argparse
import logging
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"

log = logging.getLogger(__name__)


def download(raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    zip_path = raw_dir / "online_retail.zip"
    if not zip_path.exists():
        log.info("Downloading %s", URL)
        urllib.request.urlretrieve(URL, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(raw_dir)
    return raw_dir / "Online Retail.xlsx"


def to_csv(xlsx_path: Path, csv_path: Path) -> int:
    # Read everything as text so IDs like InvoiceNo/StockCode keep their exact form.
    df = pd.read_excel(xlsx_path, dtype=str)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    return len(df)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/raw")
    args = parser.parse_args()
    raw_dir = Path(args.raw_dir)
    rows = to_csv(download(raw_dir), raw_dir / "online_retail.csv")
    log.info("Wrote %s rows to %s", rows, raw_dir / "online_retail.csv")
