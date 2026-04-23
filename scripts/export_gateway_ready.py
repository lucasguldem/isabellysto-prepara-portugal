from __future__ import annotations

import argparse
from pathlib import Path
import shutil

from hcaptcha_pipeline import DEFAULT_DIRECTORIES, load_settings


def sync_processed_outputs_to_gateway(source_dir: Path, target_dir: Path) -> list[Path]:
    target_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []

    for csv_path in sorted(source_dir.glob("*.csv")):
        temp_target = target_dir / f"{csv_path.name}.tmp"
        final_target = target_dir / csv_path.name
        shutil.copy2(csv_path, temp_target)
        temp_target.replace(final_target)
        copied.append(final_target)

    return copied


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mirror approved Gold CSVs to a stable gateway-ready folder.")
    parser.add_argument("--config", default=None, help="Optional JSON config path.")
    parser.add_argument("--source-dir", default=None, help="Override processed CSV source directory.")
    parser.add_argument("--target-dir", default=None, help="Override gateway mirror target directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = load_settings(args.config)

    source_dir = Path(args.source_dir or settings["directories"]["processed"] or DEFAULT_DIRECTORIES["processed"])
    target_dir = Path(
        args.target_dir or settings["directories"]["gateway_mirror"] or DEFAULT_DIRECTORIES["gateway_mirror"]
    )
    copied = sync_processed_outputs_to_gateway(source_dir, target_dir)
    print(f"Copied {len(copied)} file(s) to {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
