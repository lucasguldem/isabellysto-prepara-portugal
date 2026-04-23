from __future__ import annotations

import argparse
import csv
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import time

from hcaptcha_pipeline import DEFAULT_DIRECTORIES, load_settings, run_pipeline
from export_gateway_ready import sync_processed_outputs_to_gateway
from pbi_preflight import collect_missing_env_vars
from pbi_refresh import trigger_refresh


def wait_for_file_settle(path: Path, attempts: int = 10, sleep_seconds: float = 1.0) -> None:
    last_size = -1
    for _ in range(attempts):
        current_size = path.stat().st_size
        if current_size == last_size:
            return
        last_size = current_size
        time.sleep(sleep_seconds)
    raise TimeoutError(f"File did not settle in time: {path}")


def choose_final_raw_destination(decision: str, archive_dir: Path, quarantine_dir: Path) -> Path:
    if decision == "approved":
        return archive_dir
    return quarantine_dir


def _unique_destination(path: Path) -> Path:
    if not path.exists():
        return path
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return path.with_name(f"{path.stem}_{timestamp}{path.suffix}")


def write_refresh_status(ops_dir: Path, payload: dict) -> dict[str, Path]:
    ops_dir.mkdir(parents=True, exist_ok=True)
    latest_path = ops_dir / "last_refresh_status.json"
    latest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    history_path = ops_dir / "refresh_history.csv"
    row = {
        "timestamp_utc": payload["timestamp_utc"],
        "input_path": payload["input_path"],
        "decision": payload["decision"],
        "status": payload["status"],
        "gateway_files_synced": payload["gateway_files_synced"],
        "final_raw_path": payload["final_raw_path"],
        "refresh_status_code": payload.get("refresh_status_code"),
        "error": payload.get("error"),
    }
    history_exists = history_path.exists()
    with history_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if not history_exists:
            writer.writeheader()
        writer.writerow(row)
    return {"latest": latest_path, "history": history_path}


def process_inbox_file(path: Path, settings: dict) -> dict:
    directories = settings["directories"]
    wait_for_file_settle(path)

    result = run_pipeline(
        input_path=path,
        output_dir=directories["processed"],
        quality_dir=directories["quality"],
    )
    decision = result["report"]["decision"]
    archive_dir = Path(directories["raw_archive"])
    quarantine_dir = Path(directories["raw_quarantine"])
    final_dir = choose_final_raw_destination(decision, archive_dir, quarantine_dir)
    final_dir.mkdir(parents=True, exist_ok=True)
    final_path = _unique_destination(final_dir / path.name)
    path.replace(final_path)

    gateway_files_synced = 0
    refresh_status = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "input_path": str(path),
        "decision": decision,
        "status": "skipped_quarantine",
        "gateway_files_synced": 0,
        "final_raw_path": str(final_path),
    }

    if decision == "approved":
        gateway_files = sync_processed_outputs_to_gateway(
            Path(directories["processed"]),
            Path(directories.get("gateway_mirror", DEFAULT_DIRECTORIES["gateway_mirror"])),
        )
        gateway_files_synced = len(gateway_files)
        refresh_status["gateway_files_synced"] = gateway_files_synced

        missing_env = collect_missing_env_vars(dict(os.environ))
        if missing_env:
            refresh_status["status"] = "skipped_missing_env"
            refresh_status["missing_env_vars"] = missing_env
        else:
            try:
                refresh_response = trigger_refresh(dict(os.environ))
                refresh_status["status"] = "triggered"
                refresh_status["refresh_status_code"] = refresh_response.get("status")
            except Exception as exc:  # pragma: no cover - network and credentials are environment-dependent
                refresh_status["status"] = "failed"
                refresh_status["error"] = str(exc)

    ops_dir = Path(directories.get("ops", DEFAULT_DIRECTORIES["ops"]))
    refresh_logs = write_refresh_status(ops_dir, refresh_status)
    result["final_raw_path"] = str(final_path)
    result["decision"] = decision
    result["gateway_files_synced"] = gateway_files_synced
    result["refresh_logs"] = {key: str(value) for key, value in refresh_logs.items()}
    return result


def process_inbox(settings: dict) -> list[dict]:
    inbox_dir = Path(settings["directories"]["raw_inbox"])
    inbox_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    for csv_path in sorted(inbox_dir.glob("*.csv")):
        results.append(process_inbox_file(csv_path, settings))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Watch or process inbox CSV files for the hCaptcha ETL pipeline.")
    parser.add_argument("--config", default=None, help="Optional JSON config path.")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process the current inbox contents once and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = load_settings(args.config)

    if args.once:
        process_inbox(settings)
        return 0

    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError as exc:  # pragma: no cover - dependency availability varies by environment
        raise SystemExit(
            "watchdog is required for continuous watch mode. Install it or run with --once."
        ) from exc

    inbox_dir = Path(settings["directories"]["raw_inbox"])
    inbox_dir.mkdir(parents=True, exist_ok=True)

    class InboxHandler(FileSystemEventHandler):
        def on_created(self, event) -> None:  # type: ignore[override]
            if event.is_directory or not str(event.src_path).lower().endswith(".csv"):
                return
            process_inbox_file(Path(event.src_path), settings)

    observer = Observer()
    observer.schedule(InboxHandler(), str(inbox_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
