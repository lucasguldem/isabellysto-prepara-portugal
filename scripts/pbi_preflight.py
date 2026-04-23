from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Mapping

from hcaptcha_pipeline import DEFAULT_DIRECTORIES, load_settings


REQUIRED_ENV_VARS = [
    "PBI_TENANT_ID",
    "PBI_CLIENT_ID",
    "PBI_CLIENT_SECRET",
    "PBI_WORKSPACE_ID",
    "PBI_DATASET_ID",
]


def collect_missing_env_vars(env: Mapping[str, str]) -> list[str]:
    return [key for key in REQUIRED_ENV_VARS if not env.get(key)]


def build_preflight_report(
    env: Mapping[str, str],
    gateway_path: str | Path,
) -> dict[str, object]:
    gateway_dir = Path(gateway_path)
    missing = collect_missing_env_vars(env)
    return {
        "ready_for_api_refresh": not missing,
        "missing_env_vars": missing,
        "gateway_path": str(gateway_dir),
        "gateway_path_exists": gateway_dir.exists(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate local Power BI Service deployment prerequisites.")
    parser.add_argument("--config", default=None, help="Optional JSON config path.")
    parser.add_argument("--gateway-path", default=None, help="Override the gateway mirror path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = load_settings(args.config)
    gateway_path = args.gateway_path or os.environ.get("PBI_GATEWAY_MIRROR_PATH") or settings["directories"].get(
        "gateway_mirror", DEFAULT_DIRECTORIES["gateway_mirror"]
    )
    report = build_preflight_report(os.environ, gateway_path)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
