"""Run the full local pipeline: validate, quarantine, transform, write, report."""

import argparse
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from src.transform_data import (
    add_business_columns,
    deduplicate,
    write_partitioned_parquet,
)
from src.validate_data import (
    build_validation_report,
    check_schema,
    parse_types,
    rejection_reasons,
)

log = logging.getLogger("pipeline")


def run(input_csv: Path, curated_dir: Path, quarantine_dir: Path, reports_dir: Path) -> dict:
    started = time.perf_counter()
    raw = pd.read_csv(input_csv, dtype=str, keep_default_na=True)
    check_schema(raw)
    typed = parse_types(raw)
    reasons = rejection_reasons(typed)
    report = build_validation_report(raw, typed, reasons)

    quarantine_dir.mkdir(parents=True, exist_ok=True)
    rejected = raw.loc[reasons.notna()].assign(rejection_reason=reasons[reasons.notna()])
    rejected.to_csv(quarantine_dir / "rejected_rows.csv", index=False)

    valid = add_business_columns(typed.loc[reasons.isna()])
    curated, dupes = deduplicate(valid)
    files = write_partitioned_parquet(curated, curated_dir)

    manifest = {
        "run_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "input": str(input_csv),
        "rows_read": report["rows_read"],
        "rows_rejected": report["rows_rejected"],
        "duplicates_removed": dupes,
        "rows_written": len(curated),
        "net_revenue": round(float(curated["revenue"].sum()), 2),
        "parquet_files": len(files),
        "parquet_bytes": sum(f.stat().st_size for f in files),
        "seconds": round(time.perf_counter() - started, 1),
    }
    # Row-count reconciliation: if a future change silently loses rows, the run fails.
    assert manifest["rows_read"] == (manifest["rows_rejected"] + manifest["duplicates_removed"]
                                     + manifest["rows_written"]), "row counts do not reconcile"

    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
    (reports_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2))
    log.info("Run complete: %s", manifest)
    return manifest


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    p = argparse.ArgumentParser(description="Retail sales batch ETL")
    p.add_argument("--input", default="data/raw/online_retail.csv")
    p.add_argument("--curated-dir", default="data/curated/sales")
    p.add_argument("--quarantine-dir", default="data/quarantine")
    p.add_argument("--reports-dir", default="reports")
    a = p.parse_args()
    run(Path(a.input), Path(a.curated_dir), Path(a.quarantine_dir), Path(a.reports_dir))
