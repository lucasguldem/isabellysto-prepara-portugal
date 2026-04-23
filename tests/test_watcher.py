from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from watcher import choose_final_raw_destination, process_inbox_file  # type: ignore[attr-defined]


def test_choose_final_raw_destination_returns_archive_for_approved_load():
    destination = choose_final_raw_destination(
        "approved",
        Path("data/raw/archive"),
        Path("data/raw/quarantine"),
    )

    assert destination.name == "archive"


def test_process_inbox_file_moves_quarantined_file_to_quarantine(tmp_path, monkeypatch):
    inbox_file = tmp_path / "inbox" / "sample.csv"
    inbox_file.parent.mkdir(parents=True, exist_ok=True)
    inbox_file.write_text("fake-data", encoding="utf-8")

    quarantine_dir = tmp_path / "quarantine"

    monkeypatch.setattr("watcher.wait_for_file_settle", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "watcher.run_pipeline",
        lambda **kwargs: {"report": {"decision": "quarantine"}, "quality_files": {}, "output_files": {}},
    )

    result = process_inbox_file(
        inbox_file,
        {
            "directories": {
                "processed": str(tmp_path / "processed"),
                "quality": str(tmp_path / "quality"),
                "raw_archive": str(tmp_path / "archive"),
                "raw_quarantine": str(quarantine_dir),
            }
        },
    )

    moved_file = quarantine_dir / "sample.csv"

    assert result["decision"] == "quarantine"
    assert moved_file.exists()
    assert not inbox_file.exists()


def test_process_inbox_file_syncs_gateway_outputs_for_approved_load(tmp_path, monkeypatch):
    inbox_file = tmp_path / "inbox" / "sample.csv"
    inbox_file.parent.mkdir(parents=True, exist_ok=True)
    inbox_file.write_text("fake-data", encoding="utf-8")

    archive_dir = tmp_path / "archive"

    monkeypatch.setattr("watcher.wait_for_file_settle", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "watcher.run_pipeline",
        lambda **kwargs: {"report": {"decision": "approved"}, "quality_files": {}, "output_files": {}},
    )
    monkeypatch.setattr(
        "watcher.sync_processed_outputs_to_gateway",
        lambda source_dir, target_dir: [target_dir / "hcaptcha_europe_gold.csv"],
    )
    monkeypatch.setattr("watcher.collect_missing_env_vars", lambda env: ["PBI_TENANT_ID"])

    result = process_inbox_file(
        inbox_file,
        {
            "directories": {
                "processed": str(tmp_path / "processed"),
                "quality": str(tmp_path / "quality"),
                "raw_archive": str(archive_dir),
                "raw_quarantine": str(tmp_path / "quarantine"),
                "gateway_mirror": str(tmp_path / "gateway"),
                "ops": str(tmp_path / "ops"),
            }
        },
    )

    moved_file = archive_dir / "sample.csv"

    assert result["decision"] == "approved"
    assert result["gateway_files_synced"] == 1
    assert moved_file.exists()
