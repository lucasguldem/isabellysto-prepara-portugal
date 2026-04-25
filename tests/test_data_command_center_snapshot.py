from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_data_command_center_snapshot import (  # type: ignore[attr-defined]
    SnapshotPaths,
    build_snapshot,
    write_snapshot,
)


def make_fixture_files(tmp_path: Path) -> SnapshotPaths:
    gold = tmp_path / "hcaptcha_europe_gold.csv"
    country_priority = tmp_path / "dim_country_priority.csv"
    role_category = tmp_path / "dim_role_category.csv"
    company_size = tmp_path / "dim_company_size.csv"
    summary = tmp_path / "hcaptcha_positioning_summary.md"
    quality_report = tmp_path / "latest_quality_report.json"

    pd.DataFrame(
        [
            {
                "email": "person1@example.com",
                "first_name": "Alex",
                "last_name": "Doe",
                "full_name": "Alex Doe",
                "linkedin_url": "https://linkedin.com/in/person1",
                "contact_location": "Berlin, Germany",
                "company_name": "Acme Security",
                "company_country": "Germany",
                "company_industry": "Cybersecurity",
                "company_size_segment": "3. Enterprise",
                "role_category": "Executive / Technical Decision Maker",
                "contact_company_country_mismatch": False,
            },
            {
                "email": "person2@example.com",
                "first_name": "Taylor",
                "last_name": "Doe",
                "full_name": "Taylor Doe",
                "linkedin_url": "https://linkedin.com/in/person2",
                "contact_location": "Lisbon, Portugal",
                "company_name": "Acme Security",
                "company_country": "Germany",
                "company_industry": "Cybersecurity",
                "company_size_segment": "3. Enterprise",
                "role_category": "Data / Compliance",
                "contact_company_country_mismatch": True,
            },
            {
                "email": "person3@example.com",
                "first_name": "Sam",
                "last_name": "Roe",
                "full_name": "Sam Roe",
                "linkedin_url": "https://linkedin.com/in/person3",
                "contact_location": "London, United Kingdom",
                "company_name": "Vector SaaS",
                "company_country": "United Kingdom",
                "company_industry": "Computer Software",
                "company_size_segment": "2. Mid-Market",
                "role_category": "Executive / Technical Decision Maker",
                "contact_company_country_mismatch": False,
            },
            {
                "email": "person4@example.com",
                "first_name": "Robin",
                "last_name": "Stone",
                "full_name": "Robin Stone",
                "linkedin_url": "https://linkedin.com/in/person4",
                "contact_location": "Paris, France",
                "company_name": "Paris Data",
                "company_country": "France",
                "company_industry": "Data Infrastructure",
                "company_size_segment": "1. Startup / SMB",
                "role_category": "Data / Compliance",
                "contact_company_country_mismatch": False,
            },
        ]
    ).to_csv(gold, index=False)

    pd.DataFrame(
        [
            {
                "company_country": "Germany",
                "lead_count": 2,
                "company_count": 1,
                "executive_share": 0.5,
                "compliance_share": 0.5,
                "mismatch_share": 0.5,
                "country_rank": 1,
                "priority_tier": "Tier 1",
                "messaging_angle": "Privacy-first and GDPR-safe alternative to reCAPTCHA",
                "strategic_recommendation": "Target Germany with privacy-first messaging.",
            },
            {
                "company_country": "United Kingdom",
                "lead_count": 1,
                "company_count": 1,
                "executive_share": 1.0,
                "compliance_share": 0.0,
                "mismatch_share": 0.0,
                "country_rank": 2,
                "priority_tier": "Tier 1",
                "messaging_angle": "Developer efficiency and scalable anti-bot performance",
                "strategic_recommendation": "Target United Kingdom with scale-first messaging.",
            },
        ]
    ).to_csv(country_priority, index=False)

    pd.DataFrame(
        [
            {
                "role_category": "Executive / Technical Decision Maker",
                "lead_count": 2,
                "company_count": 2,
                "lead_share": 0.5,
            },
            {
                "role_category": "Data / Compliance",
                "lead_count": 2,
                "company_count": 2,
                "lead_share": 0.5,
            },
        ]
    ).to_csv(role_category, index=False)

    pd.DataFrame(
        [
            {"company_size_segment": "3. Enterprise", "lead_count": 2, "company_count": 1},
            {"company_size_segment": "2. Mid-Market", "lead_count": 1, "company_count": 1},
            {"company_size_segment": "1. Startup / SMB", "lead_count": 1, "company_count": 1},
        ]
    ).to_csv(company_size, index=False)

    summary.write_text(
        """# Relatorio Executivo

## 1. Sumario Executivo

A conclusao central e que a entrada na Europa deve seguir um modelo de duplo impacto.

## 6. Conclusao de Negocio

A proxima melhor acao e iniciar uma lista priorizada de outbound e ABM com as contas da Alemanha e Franca.
""",
        encoding="utf-8",
    )
    quality_report.write_text(json.dumps({"decision": "approved"}), encoding="utf-8")

    return SnapshotPaths(
        gold=gold,
        country_priority=country_priority,
        role_category=role_category,
        company_size=company_size,
        summary=summary,
        quality_report=quality_report,
    )


def test_snapshot_excludes_person_level_pii(tmp_path: Path):
    paths = make_fixture_files(tmp_path)

    snapshot = build_snapshot(paths, generated_at="2026-04-25T00:00:00Z")

    forbidden = {"email", "first_name", "last_name", "full_name", "linkedin_url", "contact_location"}
    encoded = json.dumps(snapshot)
    for key in forbidden:
        assert key not in encoded


def test_snapshot_preserves_aggregate_totals_and_company_records(tmp_path: Path):
    paths = make_fixture_files(tmp_path)

    snapshot = build_snapshot(paths, generated_at="2026-04-25T00:00:00Z")

    assert snapshot["metadata"]["source_rows"] == 4
    assert snapshot["metadata"]["unique_companies"] == 3
    assert snapshot["market"][0]["company_country"] == "Germany"
    assert snapshot["market"][0]["lead_count"] == 2
    assert snapshot["companies"][0]["company_name"] == "Acme Security"
    assert snapshot["companies"][0]["lead_count"] == 2
    assert snapshot["companies"][0]["role_mix"] == {
        "Data / Compliance": 1,
        "Executive / Technical Decision Maker": 1,
    }
    assert {
        "company_name",
        "company_country",
        "company_industry",
        "company_size_segment",
        "lead_count",
        "role_mix",
        "priority_tier",
    } <= set(snapshot["companies"][0])


def test_snapshot_contains_recommendations_and_quality_context(tmp_path: Path):
    paths = make_fixture_files(tmp_path)

    snapshot = build_snapshot(paths, generated_at="2026-04-25T00:00:00Z")

    assert snapshot["metadata"]["quality_decision"] == "approved"
    assert snapshot["recommendations"][0]["track"] == "Privacy-first"
    assert "Germany" in snapshot["recommendations"][0]["countries"]
    assert any("duplo impacto" in line["message"] for line in snapshot["narrative"])


def test_write_snapshot_creates_json_file(tmp_path: Path):
    paths = make_fixture_files(tmp_path)
    output = tmp_path / "public" / "data" / "command-center.json"

    write_snapshot(build_snapshot(paths, generated_at="2026-04-25T00:00:00Z"), output)

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["metadata"]["privacy_level"] == "Level 2: Aggregates + Companies"
