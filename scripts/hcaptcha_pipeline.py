from __future__ import annotations

import argparse
import json
import re
import shutil
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from tempfile import mkdtemp
from typing import Any, Mapping

import pandas as pd


RAW_TO_STANDARD_COLUMNS = {
    "E-mail": "email",
    "Status do e-mail": "email_status",
    "Nome": "first_name",
    "Sobrenome": "last_name",
    "Nome completo": "full_name",
    "LinkedIn": "linkedin_url",
    "Cargo": "job_title",
    "País": "contact_country",
    "Localização": "contact_location",
    "Setor": "contact_industry",
    "Adicionar data": "added_at",
    "Nome da empresa": "company_name",
    "URL da empresa": "company_website",
    "Tamanho da empresa": "company_size_raw",
    "País da empresa": "company_country",
    "Localização da empresa": "company_location",
    "Estado": "company_state",
    "Cidade": "company_city",
    "Setor da empresa": "company_industry",
    "Classificação": "company_size_label_raw",
}


EUROPEAN_COUNTRIES = {
    "Albania",
    "Andorra",
    "Austria",
    "Belarus",
    "Belgium",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Kosovo",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Moldova",
    "Montenegro",
    "Netherlands",
    "North Macedonia",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "San Marino",
    "Serbia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "Ukraine",
    "United Kingdom",
    "Vatican City",
}


COUNTRY_ALIASES = {
    "uk": "United Kingdom",
    "u k": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "deutschland": "Germany",
    "espana": "Spain",
    "czech republic": "Czechia",
    "republic of ireland": "Ireland",
}


COUNTRY_LOOKUP = {
    **{re.sub(r"\s+", " ", country.lower()).strip(): country for country in EUROPEAN_COUNTRIES},
    "brazil": "Brazil",
    "united states": "United States",
    "india": "India",
    "china": "China",
    "mexico": "Mexico",
    "afghanistan": "Afghanistan",
    "turkey": "Turkey",
    "switzerland": "Switzerland",
}
COUNTRY_LOOKUP.update(COUNTRY_ALIASES)


PRIVACY_FIRST_COUNTRIES = {"Germany", "France", "Belgium", "Austria", "Switzerland"}
EFFICIENCY_FIRST_COUNTRIES = {"United Kingdom", "Ireland", "Estonia", "Lithuania"}


DEFAULT_DIRECTORIES = {
    "raw_inbox": "data/raw/inbox",
    "raw_archive": "data/raw/archive",
    "raw_quarantine": "data/raw/quarantine",
    "processed": "data/processed",
    "quality": "reports/quality",
    "ops": "reports/ops",
    "gateway_mirror": "/mnt/c/Users/02luc/Documents/PowerBIData/hcaptcha/processed",
}


DEFAULT_THRESHOLDS = {
    "missing_company_country_rate": {"warning": 0.10, "blocking": 0.20},
    "non_european_rate": {"warning": 0.15, "blocking": 0.35},
    "duplicate_rate": {"warning": 0.15, "blocking": 0.30, "delta_warning": 0.10},
    "other_role_rate": {"warning": 0.15, "blocking": 0.30},
    "unknown_company_size_rate": {"warning": 0.15, "blocking": 0.30},
    "row_count_drop_rate": {"warning": 0.20, "blocking": 0.50},
    "row_count_growth_rate": {"warning": 1.00, "blocking": 2.00},
}


DEFAULT_SETTINGS = {
    "directories": DEFAULT_DIRECTORIES,
    "thresholds": DEFAULT_THRESHOLDS,
}


ROLE_RULES = [
    ("Security / Risk", [r"\bciso\b", "security", "cybersecurity", "cyber security", "risk", "fraud"]),
    (
        "Executive / Technical Decision Maker",
        [
            r"\bcto\b",
            "chief technology officer",
            "chief technical officer",
            "director of technology",
            "technical director",
            "head of it",
            "it director",
            "vp engineering",
            "vp technology",
            "chief information officer",
            r"\bcio\b",
        ],
    ),
    (
        "Data / Compliance",
        [
            "compliance",
            "data protection",
            r"\bdpo\b",
            "privacy",
            "governance",
            "gdpr",
            "data manager",
            "manager data",
            "datamanager",
        ],
    ),
    (
        "IT / Engineering Management",
        [
            "it manager",
            "project manager",
            "engineering manager",
            "platform manager",
            "delivery manager",
            "team lead",
            "lead engineer",
            "lead developer",
            "head of engineering",
        ],
    ),
    (
        "Individual Contributor / Specialist",
        [
            "engineer",
            "developer",
            "devops",
            "sre",
            "architect",
            "administrator",
            "analyst",
            "specialist",
        ],
    ),
]


def load_raw_dataset(csv_path: str | Path) -> pd.DataFrame:
    return pd.read_csv(csv_path, dtype=str)


def clean_cell(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none"}:
        return None
    return re.sub(r"\s+", " ", text)


def normalize_text(value: object) -> str:
    text = clean_cell(value)
    if text is None:
        return ""
    ascii_text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^a-z0-9]+", " ", ascii_text.lower()).strip()


def normalize_country(value: object) -> str | None:
    text = clean_cell(value)
    if text is None:
        return None
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    return COUNTRY_LOOKUP.get(normalized, text)


def is_european_country(country: object) -> bool:
    normalized = normalize_country(country)
    return normalized in EUROPEAN_COUNTRIES


def categorize_role(job_title: object) -> str:
    normalized = normalize_text(job_title)
    if not normalized:
        return "Other"
    for category, patterns in ROLE_RULES:
        if any(re.search(pattern, normalized) for pattern in patterns):
            return category
    return "Other"


def _parse_int_token(token: str | None) -> int | None:
    if token is None:
        return None
    text = token.strip()
    if not text:
        return None
    if "." in text and "," in text:
        text = text.split(",")[0].replace(".", "")
    digits = re.sub(r"[^\d]", "", text)
    if not digits:
        return None
    return int(digits)


def parse_company_size_bounds(value: object) -> tuple[int | None, int | None]:
    text = clean_cell(value)
    if text is None:
        return (None, None)

    compact = text.lower().replace(" ", "")
    if compact == "self":
        return (1, 1)

    range_match = re.match(r"^([\d.,]+)-([\d.,]+)$", compact)
    if range_match:
        return (_parse_int_token(range_match.group(1)), _parse_int_token(range_match.group(2)))

    plus_match = re.match(r"^([\d.,]+)\+$", compact)
    if plus_match:
        lower = _parse_int_token(plus_match.group(1))
        return (lower, None)

    single = _parse_int_token(compact)
    return (single, single)


def categorize_company_size(value: object) -> str:
    lower, upper = parse_company_size_bounds(value)
    anchor = upper or lower
    if anchor is None:
        return "4. Unknown"
    if anchor <= 50:
        return "1. Startup / SMB"
    if anchor <= 250:
        return "2. Mid-Market"
    return "3. Enterprise"


def _email_status_score(value: object) -> int:
    normalized = normalize_text(value)
    return {"valid": 3, "unknown": 2, "not valid": 1}.get(normalized, 0)


def deduplicate_contacts(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()

    def _email_key(index: object, value: object) -> str:
        normalized = normalize_text(value)
        return normalized or f"__missing_email__{index}"

    def _company_key(index: object, value: object) -> str:
        normalized = normalize_text(value)
        return normalized or f"__missing_company__{index}"

    working["_email_key"] = [
        _email_key(index, value) for index, value in zip(working.index, working.get("E-mail", pd.Series(index=working.index)))
    ]
    working["_company_key"] = [
        _company_key(index, value)
        for index, value in zip(working.index, working.get("Nome da empresa", pd.Series(index=working.index)))
    ]
    working["_email_status_score"] = working.get("Status do e-mail", pd.Series(index=working.index)).map(
        _email_status_score
    )
    working["_completeness_score"] = (
        working.get("País da empresa", pd.Series(index=working.index)).notna().astype(int)
        + working.get("Tamanho da empresa", pd.Series(index=working.index)).notna().astype(int)
        + working.get("LinkedIn", pd.Series(index=working.index)).notna().astype(int)
        + working.get("Cargo", pd.Series(index=working.index)).notna().astype(int)
    )

    ordered = working.sort_values(
        by=["_email_key", "_company_key", "_email_status_score", "_completeness_score"],
        ascending=[True, True, False, False],
        kind="stable",
    )
    deduped = ordered.drop_duplicates(subset=["_email_key", "_company_key"], keep="first")
    return deduped.drop(
        columns=["_email_key", "_company_key", "_email_status_score", "_completeness_score"]
    ).reset_index(drop=True)


def transform_dataset(df: pd.DataFrame) -> pd.DataFrame:
    deduped = deduplicate_contacts(df)

    cleaned = pd.DataFrame()
    for raw_name, clean_name in RAW_TO_STANDARD_COLUMNS.items():
        cleaned[clean_name] = deduped.get(raw_name)

    for column in [
        "email",
        "first_name",
        "last_name",
        "full_name",
        "linkedin_url",
        "job_title",
        "contact_location",
        "contact_industry",
        "company_name",
        "company_website",
        "company_size_raw",
        "company_location",
        "company_state",
        "company_city",
        "company_industry",
        "company_size_label_raw",
    ]:
        cleaned[column] = cleaned[column].map(clean_cell)

    cleaned["email"] = cleaned["email"].map(lambda value: clean_cell(value).lower() if clean_cell(value) else None)
    cleaned["email_status"] = cleaned["email_status"].map(
        lambda value: normalize_text(value).replace("  ", " ") or None
    )
    cleaned["contact_country"] = cleaned["contact_country"].map(normalize_country)
    cleaned["company_country"] = cleaned["company_country"].map(normalize_country)
    cleaned["added_at"] = pd.to_datetime(cleaned["added_at"], errors="coerce")
    cleaned["role_category"] = cleaned["job_title"].map(categorize_role)
    cleaned["company_size_segment"] = cleaned["company_size_raw"].map(categorize_company_size)
    size_bounds = cleaned["company_size_raw"].map(parse_company_size_bounds)
    cleaned["company_size_min"] = size_bounds.map(lambda value: value[0])
    cleaned["company_size_max"] = size_bounds.map(lambda value: value[1])
    cleaned["is_email_valid"] = cleaned["email_status"].eq("valid").astype(object)
    cleaned["is_european_company"] = cleaned["company_country"].map(is_european_country).astype(object)
    cleaned["contact_company_country_mismatch"] = (
        cleaned["contact_country"].notna()
        & cleaned["company_country"].notna()
        & cleaned["contact_country"].ne(cleaned["company_country"])
    ).astype(object)

    cleaned = cleaned.loc[cleaned["is_european_company"] == True].reset_index(drop=True)
    return cleaned


def build_role_category_dimension(clean_df: pd.DataFrame) -> pd.DataFrame:
    role_dim = (
        clean_df.groupby("role_category", dropna=False)
        .agg(
            lead_count=("email", "count"),
            company_count=("company_name", "nunique"),
        )
        .reset_index()
        .sort_values(["lead_count", "company_count"], ascending=[False, False])
        .reset_index(drop=True)
    )
    total = role_dim["lead_count"].sum() or 1
    role_dim["lead_share"] = role_dim["lead_count"] / total
    return role_dim


def build_company_size_dimension(clean_df: pd.DataFrame) -> pd.DataFrame:
    size_dim = (
        clean_df.groupby("company_size_segment", dropna=False)
        .agg(
            lead_count=("email", "count"),
            company_count=("company_name", "nunique"),
        )
        .reset_index()
        .sort_values("lead_count", ascending=False)
        .reset_index(drop=True)
    )
    return size_dim


def _country_messaging_angle(country: str) -> str:
    if country in PRIVACY_FIRST_COUNTRIES:
        return "Privacy-first and GDPR-safe alternative to reCAPTCHA"
    if country in EFFICIENCY_FIRST_COUNTRIES:
        return "Developer efficiency and scalable anti-bot performance"
    return "Balanced anti-bot performance with compliance-ready messaging"


def build_country_priority_dimension(clean_df: pd.DataFrame) -> pd.DataFrame:
    country_dim = (
        clean_df.groupby("company_country", dropna=False)
        .agg(
            lead_count=("email", "count"),
            company_count=("company_name", "nunique"),
            executive_share=("role_category", lambda series: (series == "Executive / Technical Decision Maker").mean()),
            compliance_share=("role_category", lambda series: (series == "Data / Compliance").mean()),
            mismatch_share=("contact_company_country_mismatch", "mean"),
        )
        .reset_index()
        .sort_values(["lead_count", "company_count"], ascending=[False, False])
        .reset_index(drop=True)
    )
    country_dim["country_rank"] = country_dim.index + 1
    country_dim["priority_tier"] = country_dim["country_rank"].map(
        lambda rank: "Tier 1" if rank <= 5 else ("Tier 2" if rank <= 10 else "Tier 3")
    )
    country_dim["messaging_angle"] = country_dim["company_country"].map(_country_messaging_angle)
    country_dim["strategic_recommendation"] = country_dim.apply(
        lambda row: (
            f"Target {row['company_country']} with {row['messaging_angle'].lower()}."
        ),
        axis=1,
    )
    return country_dim


def build_data_quality_summary(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> pd.DataFrame:
    duplicated_mask = raw_df.duplicated(subset=["E-mail", "Nome da empresa"], keep=False)
    summary = pd.DataFrame(
        [
            {"metric": "raw_rows", "value": int(len(raw_df))},
            {"metric": "raw_duplicate_rows", "value": int(duplicated_mask.sum())},
            {"metric": "clean_rows", "value": int(len(clean_df))},
            {"metric": "european_rows", "value": int(clean_df["is_european_company"].eq(True).sum())},
            {
                "metric": "cross_border_contact_rows",
                "value": int(clean_df["contact_company_country_mismatch"].eq(True).sum()),
            },
        ]
    )
    return summary


def export_processed_outputs(clean_df: pd.DataFrame, output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    files = {
        "gold": output_path / "hcaptcha_europe_gold.csv",
        "role_dim": output_path / "dim_role_category.csv",
        "size_dim": output_path / "dim_company_size.csv",
        "country_dim": output_path / "dim_country_priority.csv",
    }

    clean_df.to_csv(files["gold"], index=False)
    build_role_category_dimension(clean_df).to_csv(files["role_dim"], index=False)
    build_company_size_dimension(clean_df).to_csv(files["size_dim"], index=False)
    build_country_priority_dimension(clean_df).to_csv(files["country_dim"], index=False)
    return files


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {key: value for key, value in base.items()}
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(base.get(key), Mapping):
            merged[key] = _deep_merge(base[key], value)
        else:
            merged[key] = value
    return merged


def load_settings(config_path: str | Path | None = None) -> dict[str, Any]:
    settings = _deep_merge({}, DEFAULT_SETTINGS)
    if config_path is None:
        return settings

    config_file = Path(config_path)
    if not config_file.exists():
        return settings

    payload = json.loads(config_file.read_text(encoding="utf-8"))
    return _deep_merge(settings, payload)


def _safe_rate(numerator: int | float, denominator: int | float) -> float:
    if not denominator:
        return 0.0
    return float(numerator) / float(denominator)


def collect_quality_metrics(
    raw_df: pd.DataFrame,
    clean_df: pd.DataFrame,
    previous_approved_row_count: int | None = None,
    previous_duplicate_rate: float | None = None,
) -> dict[str, float | int | None]:
    duplicate_mask = raw_df.duplicated(subset=["E-mail", "Nome da empresa"], keep=False)
    raw_rows = int(len(raw_df))
    clean_rows = int(len(clean_df))
    missing_company_country_rows = int(raw_df.get("País da empresa", pd.Series(dtype=object)).isna().sum())
    non_european_rows = int(
        raw_df.get("País da empresa", pd.Series(dtype=object)).map(is_european_country).fillna(False).eq(False).sum()
    )
    other_role_rows = int(clean_df.get("role_category", pd.Series(dtype=object)).eq("Other").sum())
    unknown_company_size_rows = int(
        clean_df.get("company_size_segment", pd.Series(dtype=object)).eq("4. Unknown").sum()
    )

    return {
        "raw_rows": raw_rows,
        "clean_rows": clean_rows,
        "duplicate_rate": _safe_rate(int(duplicate_mask.sum()), raw_rows),
        "missing_company_country_rate": _safe_rate(missing_company_country_rows, raw_rows),
        "non_european_rate": _safe_rate(non_european_rows, raw_rows),
        "other_role_rate": _safe_rate(other_role_rows, clean_rows),
        "unknown_company_size_rate": _safe_rate(unknown_company_size_rows, clean_rows),
        "previous_approved_row_count": previous_approved_row_count,
        "previous_duplicate_rate": previous_duplicate_rate,
    }


def evaluate_quality_metrics(
    raw_rows: int,
    clean_rows: int,
    duplicate_rate: float,
    non_european_rate: float,
    missing_company_country_rate: float,
    other_role_rate: float,
    unknown_company_size_rate: float,
    previous_approved_row_count: int | None,
    previous_duplicate_rate: float | None = None,
    thresholds: Mapping[str, Mapping[str, float]] | None = None,
) -> dict[str, Any]:
    active_thresholds = thresholds or DEFAULT_THRESHOLDS
    metrics = {
        "raw_rows": raw_rows,
        "clean_rows": clean_rows,
        "duplicate_rate": duplicate_rate,
        "non_european_rate": non_european_rate,
        "missing_company_country_rate": missing_company_country_rate,
        "other_role_rate": other_role_rate,
        "unknown_company_size_rate": unknown_company_size_rate,
    }

    blocking_failures: list[str] = []
    warnings: list[str] = []

    def _evaluate_threshold(metric_name: str, value: float) -> None:
        threshold = active_thresholds.get(metric_name, {})
        blocking = threshold.get("blocking")
        warning = threshold.get("warning")
        if blocking is not None and value >= blocking:
            blocking_failures.append(metric_name)
            return
        if warning is not None and value >= warning:
            warnings.append(metric_name)

    for metric_name in [
        "duplicate_rate",
        "non_european_rate",
        "missing_company_country_rate",
        "other_role_rate",
        "unknown_company_size_rate",
    ]:
        _evaluate_threshold(metric_name, float(metrics[metric_name]))

    if previous_duplicate_rate is not None:
        duplicate_delta = duplicate_rate - previous_duplicate_rate
        metrics["duplicate_rate_delta"] = duplicate_delta
        delta_warning = active_thresholds.get("duplicate_rate", {}).get("delta_warning")
        if delta_warning is not None and duplicate_delta >= delta_warning:
            warnings.append("duplicate_rate_delta")

    if previous_approved_row_count:
        if clean_rows < previous_approved_row_count:
            row_count_drop_rate = _safe_rate(previous_approved_row_count - clean_rows, previous_approved_row_count)
            metrics["row_count_drop_rate"] = row_count_drop_rate
            _evaluate_threshold("row_count_drop_rate", row_count_drop_rate)
        elif clean_rows > previous_approved_row_count:
            row_count_growth_rate = _safe_rate(clean_rows - previous_approved_row_count, previous_approved_row_count)
            metrics["row_count_growth_rate"] = row_count_growth_rate
            _evaluate_threshold("row_count_growth_rate", row_count_growth_rate)

    return {
        "decision": "quarantine" if blocking_failures else "approved",
        "blocking_failures": blocking_failures,
        "warnings": warnings,
        "metrics": metrics,
    }


def load_previous_approved_metrics(quality_dir: str | Path) -> dict[str, float | int] | None:
    history_path = Path(quality_dir) / "quality_history.csv"
    if not history_path.exists():
        return None

    history_df = pd.read_csv(history_path)
    if history_df.empty or "decision" not in history_df.columns:
        return None

    approved = history_df.loc[history_df["decision"] == "approved"]
    if approved.empty:
        return None

    latest = approved.iloc[-1]
    result: dict[str, float | int] = {}
    if pd.notna(latest.get("clean_rows")):
        result["clean_rows"] = int(latest["clean_rows"])
    if pd.notna(latest.get("duplicate_rate")):
        result["duplicate_rate"] = float(latest["duplicate_rate"])
    return result or None


def build_quality_report(
    raw_df: pd.DataFrame,
    clean_df: pd.DataFrame,
    input_path: str | Path,
    thresholds: Mapping[str, Mapping[str, float]] | None = None,
    previous_approved_metrics: Mapping[str, float | int] | None = None,
) -> dict[str, Any]:
    previous_approved_metrics = previous_approved_metrics or {}
    metrics = collect_quality_metrics(
        raw_df=raw_df,
        clean_df=clean_df,
        previous_approved_row_count=(
            int(previous_approved_metrics["clean_rows"]) if "clean_rows" in previous_approved_metrics else None
        ),
        previous_duplicate_rate=(
            float(previous_approved_metrics["duplicate_rate"])
            if "duplicate_rate" in previous_approved_metrics
            else None
        ),
    )
    evaluation = evaluate_quality_metrics(
        raw_rows=int(metrics["raw_rows"]),
        clean_rows=int(metrics["clean_rows"]),
        duplicate_rate=float(metrics["duplicate_rate"]),
        non_european_rate=float(metrics["non_european_rate"]),
        missing_company_country_rate=float(metrics["missing_company_country_rate"]),
        other_role_rate=float(metrics["other_role_rate"]),
        unknown_company_size_rate=float(metrics["unknown_company_size_rate"]),
        previous_approved_row_count=(
            int(metrics["previous_approved_row_count"])
            if metrics["previous_approved_row_count"] is not None
            else None
        ),
        previous_duplicate_rate=(
            float(metrics["previous_duplicate_rate"])
            if metrics["previous_duplicate_rate"] is not None
            else None
        ),
        thresholds=thresholds,
    )
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "input_path": str(Path(input_path)),
        "decision": evaluation["decision"],
        "blocking_failures": evaluation["blocking_failures"],
        "warnings": evaluation["warnings"],
        "metrics": evaluation["metrics"],
    }


def write_quality_outputs(report: Mapping[str, Any], quality_dir: str | Path) -> dict[str, Path]:
    quality_path = Path(quality_dir)
    quality_path.mkdir(parents=True, exist_ok=True)

    latest_path = quality_path / "latest_quality_report.json"
    latest_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    history_path = quality_path / "quality_history.csv"
    row = {
        "timestamp_utc": report["timestamp_utc"],
        "input_path": report["input_path"],
        "decision": report["decision"],
        "blocking_failures": "|".join(report["blocking_failures"]),
        "warnings": "|".join(report["warnings"]),
    }
    for key, value in report["metrics"].items():
        row[key] = value

    history_df = pd.DataFrame([row])
    if history_path.exists():
        existing = pd.read_csv(history_path)
        history_df = pd.concat([existing, history_df], ignore_index=True)
    history_df.to_csv(history_path, index=False)

    return {"latest_report": latest_path, "history": history_path}


def _promote_staged_outputs(staged_files: Mapping[str, Path], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    promoted: dict[str, Path] = {}
    for key, staged_file in staged_files.items():
        target = output_path / staged_file.name
        staged_file.replace(target)
        promoted[key] = target
    return promoted


def _cleanup_directory(path: str | Path) -> None:
    target = Path(path)
    if target.exists():
        shutil.rmtree(target)


def run_pipeline(
    input_path: str | Path,
    output_dir: str | Path,
    quality_dir: str | Path,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    settings = load_settings(config_path)
    raw_df = load_raw_dataset(input_path)
    clean_df = transform_dataset(raw_df)
    previous_approved_metrics = load_previous_approved_metrics(quality_dir)
    report = build_quality_report(
        raw_df=raw_df,
        clean_df=clean_df,
        input_path=input_path,
        thresholds=settings["thresholds"],
        previous_approved_metrics=previous_approved_metrics,
    )

    staging_dir = Path(mkdtemp(prefix="hcaptcha_staging_", dir=str(Path(output_dir).parent.resolve())))
    staged_files = export_processed_outputs(clean_df, staging_dir)
    promoted_files: dict[str, Path] = {}

    if report["decision"] == "approved":
        promoted_files = _promote_staged_outputs(staged_files, output_dir)
    _cleanup_directory(staging_dir)

    quality_files = write_quality_outputs(report, quality_dir)

    return {
        "report": report,
        "quality_files": quality_files,
        "output_files": promoted_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the hCaptcha ETL pipeline with quality gates.")
    parser.add_argument("--input", required=True, help="Path to the raw CSV file.")
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_DIRECTORIES["processed"],
        help="Directory where approved Gold outputs are promoted.",
    )
    parser.add_argument(
        "--quality-dir",
        default=DEFAULT_DIRECTORIES["quality"],
        help="Directory for quality reports and history.",
    )
    parser.add_argument("--config", default=None, help="Optional JSON config file with thresholds and directories.")
    parser.add_argument(
        "--fail-on-quality-gate",
        action="store_true",
        help="Return exit code 1 when the load is quarantined.",
    )
    return parser


def run_pipeline_command(args: argparse.Namespace) -> int:
    result = run_pipeline(
        input_path=args.input,
        output_dir=args.output_dir,
        quality_dir=args.quality_dir,
        config_path=args.config,
    )
    report = result["report"]
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "blocking_failures": report["blocking_failures"],
                "warnings": report["warnings"],
            },
            ensure_ascii=False,
        )
    )
    if args.fail_on_quality_gate and report["decision"] != "approved":
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_pipeline_command(args)


if __name__ == "__main__":
    raise SystemExit(main())
