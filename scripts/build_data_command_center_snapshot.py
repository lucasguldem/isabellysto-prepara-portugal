from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

import pandas as pd


PRIVACY_LEVEL = "Level 2: Aggregates + Companies"

FORBIDDEN_PII_KEYS = {
    "email",
    "email_status",
    "first_name",
    "last_name",
    "full_name",
    "linkedin_url",
    "job_title",
    "contact_country",
    "contact_location",
    "contact_industry",
    "added_at",
    "company_website",
    "company_location",
    "company_state",
    "company_city",
    "company_size_raw",
    "company_size_min",
    "company_size_max",
    "is_email_valid",
    "contact_company_country_mismatch",
}

PRIVACY_FIRST_COUNTRIES = {"Germany", "France", "Belgium", "Switzerland"}
SCALE_FIRST_COUNTRIES = {"United Kingdom", "Ireland", "Estonia", "Lithuania"}


@dataclass(frozen=True)
class SnapshotPaths:
    gold: Path
    country_priority: Path
    role_category: Path
    company_size: Path
    summary: Path
    quality_report: Path | None = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return json.loads(frame.to_json(orient="records"))


def _safe_number(value: Any) -> int | float | str | None:
    if pd.isna(value):
        return None
    if isinstance(value, float):
        return round(value, 6)
    if hasattr(value, "item"):
        return value.item()
    return value


def _sanitize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: _safe_number(value) for key, value in row.items()} for row in records]


def _build_market(country_priority: pd.DataFrame) -> list[dict[str, Any]]:
    columns = [
        "company_country",
        "lead_count",
        "company_count",
        "executive_share",
        "compliance_share",
        "mismatch_share",
        "country_rank",
        "priority_tier",
        "messaging_angle",
        "strategic_recommendation",
    ]
    market = country_priority.loc[:, columns].sort_values(["country_rank", "company_country"])
    return _sanitize_records(_records(market))


def _build_personas(role_category: pd.DataFrame) -> list[dict[str, Any]]:
    personas = role_category.loc[:, ["role_category", "lead_count", "company_count", "lead_share"]].sort_values(
        ["lead_count", "role_category"], ascending=[False, True]
    )
    return _sanitize_records(_records(personas))


def _build_segments(company_size: pd.DataFrame) -> list[dict[str, Any]]:
    segments = company_size.loc[:, ["company_size_segment", "lead_count", "company_count"]].copy()
    total_leads = max(float(segments["lead_count"].sum()), 1.0)
    segments["lead_share"] = segments["lead_count"] / total_leads
    return _sanitize_records(_records(segments.sort_values("company_size_segment")))


def _role_mix(group: pd.DataFrame) -> dict[str, int]:
    counts = group["role_category"].fillna("Unknown").value_counts().sort_index()
    return {str(role): int(count) for role, count in counts.items()}


def _dominant_value(group: pd.DataFrame, column: str, fallback: str, ignored: set[str] | None = None) -> str:
    ignored_values = ignored or set()
    values = (
        group[column]
        .dropna()
        .astype(str)
        .map(str.strip)
        .loc[lambda series: (series != "") & ~series.isin(ignored_values)]
    )
    if values.empty:
        return fallback
    ranked = (
        values.reset_index(drop=True)
        .reset_index(name="value")
        .groupby("value")
        .agg(count=("index", "count"), first_seen=("index", "min"))
        .sort_values(["count", "first_seen"], ascending=[False, True])
    )
    return str(ranked.index[0])


def _build_companies(gold: pd.DataFrame, country_priority: pd.DataFrame) -> list[dict[str, Any]]:
    tier_by_country = country_priority.set_index("company_country")["priority_tier"].to_dict()
    angle_by_country = country_priority.set_index("company_country")["messaging_angle"].to_dict()
    recommendation_by_country = country_priority.set_index("company_country")["strategic_recommendation"].to_dict()

    named_companies = gold.loc[
        gold["company_name"].notna() & (gold["company_name"].astype(str).str.strip() != "")
    ].copy()
    companies: list[dict[str, Any]] = []
    for company_name, group in named_companies.groupby("company_name", dropna=False):
        country = _dominant_value(group, "company_country", "")
        companies.append(
            {
                "company_name": "" if pd.isna(company_name) else str(company_name),
                "company_country": country,
                "company_industry": _dominant_value(group, "company_industry", "Unknown"),
                "company_size_segment": _dominant_value(group, "company_size_segment", "4. Unknown", {"4. Unknown"}),
                "lead_count": int(len(group)),
                "role_mix": _role_mix(group),
                "priority_tier": str(tier_by_country.get(country, "Tier 3")),
                "messaging_angle": str(angle_by_country.get(country, "Balanced anti-bot performance with compliance-ready messaging")),
                "strategic_recommendation": str(recommendation_by_country.get(country, "")),
            }
        )

    return sorted(
        companies,
        key=lambda row: (-int(row["lead_count"]), str(row["priority_tier"]), str(row["company_country"]), str(row["company_name"])),
    )


def _summary_lines(summary: str) -> list[str]:
    lines: list[str] = []
    for raw_line in summary.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("|") or line.startswith("- "):
            continue
        compact = re.sub(r"`", "", line)
        if len(compact) > 220:
            compact = compact[:217].rstrip() + "..."
        lines.append(compact)
    return lines


def _build_narrative(summary_text: str) -> list[dict[str, str]]:
    selected = _summary_lines(summary_text)[:9]
    fallback = [
        "Gold dataset loaded for hCaptcha Europe positioning.",
        "Market, ICP and recommendation modules are ready.",
    ]
    messages = selected if selected else fallback
    return [{"level": "INFO", "message": message} for message in messages]


def _countries_for_track(market: list[dict[str, Any]], allowed: set[str]) -> list[str]:
    return [str(row["company_country"]) for row in market if str(row["company_country"]) in allowed]


def _build_recommendations(market: list[dict[str, Any]]) -> list[dict[str, Any]]:
    balanced_countries = [
        str(row["company_country"])
        for row in market
        if str(row["company_country"]) not in PRIVACY_FIRST_COUNTRIES | SCALE_FIRST_COUNTRIES
        and str(row.get("priority_tier")) in {"Tier 1", "Tier 2"}
    ]
    return [
        {
            "track": "Privacy-first",
            "countries": _countries_for_track(market, PRIVACY_FIRST_COUNTRIES),
            "message": "Lead with privacy, sovereignty, GDPR alignment and reCAPTCHA displacement.",
        },
        {
            "track": "Scale-first",
            "countries": _countries_for_track(market, SCALE_FIRST_COUNTRIES),
            "message": "Lead with developer efficiency, low-friction anti-bot protection and fast implementation.",
        },
        {
            "track": "Balanced expansion",
            "countries": balanced_countries,
            "message": "Use compliance-ready anti-bot performance for expansion markets.",
        },
    ]


def _load_quality_decision(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    report = json.loads(path.read_text(encoding="utf-8"))
    decision = report.get("decision")
    return str(decision) if decision else None


def _assert_no_forbidden_keys(snapshot: Mapping[str, Any]) -> None:
    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            overlap = set(value) & FORBIDDEN_PII_KEYS
            if overlap:
                raise ValueError(f"Snapshot contains forbidden PII keys: {sorted(overlap)}")
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(snapshot)


def build_snapshot(paths: SnapshotPaths, generated_at: str | None = None) -> dict[str, Any]:
    gold = pd.read_csv(paths.gold)
    country_priority = pd.read_csv(paths.country_priority)
    role_category = pd.read_csv(paths.role_category)
    company_size = pd.read_csv(paths.company_size)
    summary_text = paths.summary.read_text(encoding="utf-8")

    generated = generated_at or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    market = _build_market(country_priority)
    snapshot: dict[str, Any] = {
        "metadata": {
            "generated_at": generated,
            "privacy_level": PRIVACY_LEVEL,
            "source_rows": int(len(gold)),
            "unique_companies": int(gold["company_name"].nunique()),
            "source_files": {
                "gold": str(paths.gold),
                "country_priority": str(paths.country_priority),
                "role_category": str(paths.role_category),
                "company_size": str(paths.company_size),
                "summary": str(paths.summary),
            },
            "quality_decision": _load_quality_decision(paths.quality_report),
        },
        "market": market,
        "personas": _build_personas(role_category),
        "segments": _build_segments(company_size),
        "companies": _build_companies(gold, country_priority),
        "recommendations": _build_recommendations(market),
        "narrative": _build_narrative(summary_text),
    }
    _assert_no_forbidden_keys(snapshot)
    return snapshot


def write_snapshot(snapshot: Mapping[str, Any], output_path: Path) -> None:
    _assert_no_forbidden_keys(snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _default_paths(root: Path) -> SnapshotPaths:
    return SnapshotPaths(
        gold=root / "data/processed/hcaptcha_europe_gold.csv",
        country_priority=root / "data/processed/dim_country_priority.csv",
        role_category=root / "data/processed/dim_role_category.csv",
        company_size=root / "data/processed/dim_company_size.csv",
        summary=root / "reports/hcaptcha_positioning_summary.md",
        quality_report=root / "reports/quality/latest_quality_report.json",
    )


def _parser() -> argparse.ArgumentParser:
    root = _repo_root()
    defaults = _default_paths(root)
    parser = argparse.ArgumentParser(description="Build the sanitized JSON snapshot for the Data Command Center site.")
    parser.add_argument("--gold", type=Path, default=defaults.gold)
    parser.add_argument("--country-priority", type=Path, default=defaults.country_priority)
    parser.add_argument("--role-category", type=Path, default=defaults.role_category)
    parser.add_argument("--company-size", type=Path, default=defaults.company_size)
    parser.add_argument("--summary", type=Path, default=defaults.summary)
    parser.add_argument("--quality-report", type=Path, default=defaults.quality_report)
    parser.add_argument("--output", type=Path, default=root / "sites/data-command-center/public/data/command-center.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    paths = SnapshotPaths(
        gold=args.gold,
        country_priority=args.country_priority,
        role_category=args.role_category,
        company_size=args.company_size,
        summary=args.summary,
        quality_report=args.quality_report if args.quality_report.exists() else None,
    )
    write_snapshot(build_snapshot(paths), args.output)
    print(f"Wrote sanitized command-center snapshot to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
