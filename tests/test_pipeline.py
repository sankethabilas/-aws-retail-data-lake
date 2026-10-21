import json

import pandas as pd

from src.run_pipeline import run


def test_pipeline_rerun_is_idempotent_and_reconciles(tmp_path, raw_csv):
    dirs = {"curated_dir": tmp_path / "curated", "quarantine_dir": tmp_path / "q",
            "reports_dir": tmp_path / "reports"}
    first = run(raw_csv, **dirs)
    second = run(raw_csv, **dirs)
    assert first["rows_written"] == second["rows_written"]
    written = pd.read_parquet(dirs["curated_dir"])
    assert len(written) == second["rows_written"]  # no duplicate output after rerun
    assert round(written["revenue"].sum(), 2) == second["net_revenue"]
    assert json.loads((tmp_path / "reports" / "run_manifest.json").read_text())["rows_read"] == 4
