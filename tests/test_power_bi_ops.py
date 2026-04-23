from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from export_gateway_ready import sync_processed_outputs_to_gateway  # type: ignore[attr-defined]
from pbi_preflight import collect_missing_env_vars  # type: ignore[attr-defined]


def test_collect_missing_env_vars_reports_required_power_bi_service_settings():
    missing = collect_missing_env_vars({})

    assert "PBI_TENANT_ID" in missing
    assert "PBI_DATASET_ID" in missing


def test_sync_processed_outputs_to_gateway_copies_csv_files(tmp_path):
    source_dir = tmp_path / "processed"
    target_dir = tmp_path / "gateway"
    source_dir.mkdir()
    target_dir.mkdir()

    (source_dir / "hcaptcha_europe_gold.csv").write_text("col\nvalue\n", encoding="utf-8")
    (source_dir / "dim_country_priority.csv").write_text("col\nvalue\n", encoding="utf-8")

    copied = sync_processed_outputs_to_gateway(source_dir, target_dir)

    assert len(copied) == 2
    assert (target_dir / "hcaptcha_europe_gold.csv").exists()
    assert (target_dir / "dim_country_priority.csv").exists()
