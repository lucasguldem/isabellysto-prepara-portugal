from pathlib import Path
import json
import sys

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from hcaptcha_pipeline import DEFAULT_THRESHOLDS, evaluate_quality_metrics, main  # type: ignore[attr-defined]


def _sample_raw_rows() -> list[dict]:
    return [
        {
            "E-mail": "lead@example.com",
            "Status do e-mail": "valid",
            "Nome": "Alex",
            "Sobrenome": "Doe",
            "Nome completo": "Alex Doe",
            "LinkedIn": "https://linkedin.com/in/example",
            "Cargo": "CTO & Founder",
            "País": "Germany",
            "Localização": "Berlin, Germany",
            "Setor": "Computer Software",
            "Adicionar data": "2025-02-13 15:24:00",
            "Nome da empresa": "Acme",
            "URL da empresa": "https://acme.example",
            "Tamanho da empresa": "51-200",
            "País da empresa": "Germany",
            "Localização da empresa": "Berlin, Germany",
            "Estado": "Berlin",
            "Cidade": "Berlin",
            "Setor da empresa": "Computer Software",
            "Classificação": "Grande",
        },
        {
            "E-mail": "lead@example.com",
            "Status do e-mail": "unknown",
            "Nome": "Alex",
            "Sobrenome": "Doe",
            "Nome completo": "Alex Doe",
            "LinkedIn": None,
            "Cargo": "CTO & Founder",
            "País": "Germany",
            "Localização": "Berlin, Germany",
            "Setor": "Computer Software",
            "Adicionar data": "2025-02-13 15:24:00",
            "Nome da empresa": "Acme",
            "URL da empresa": "https://acme.example",
            "Tamanho da empresa": None,
            "País da empresa": "Germany",
            "Localização da empresa": "Berlin, Germany",
            "Estado": "Berlin",
            "Cidade": "Berlin",
            "Setor da empresa": "Computer Software",
            "Classificação": "Grande",
        },
    ]


def test_evaluate_quality_metrics_flags_quarantine_when_duplicate_rate_is_too_high():
    report = evaluate_quality_metrics(
        raw_rows=100,
        clean_rows=60,
        duplicate_rate=0.31,
        non_european_rate=0.05,
        missing_company_country_rate=0.02,
        other_role_rate=0.10,
        unknown_company_size_rate=0.08,
        previous_approved_row_count=95,
        previous_duplicate_rate=0.12,
        thresholds=DEFAULT_THRESHOLDS,
    )

    assert report["decision"] == "quarantine"
    assert "duplicate_rate" in report["blocking_failures"]


def test_main_returns_non_zero_when_fail_on_quality_gate_is_enabled(tmp_path):
    input_path = tmp_path / "raw.csv"
    output_dir = tmp_path / "processed"
    quality_dir = tmp_path / "quality"

    pd.DataFrame(_sample_raw_rows()).to_csv(input_path, index=False)

    exit_code = main(
        [
            "--input",
            str(input_path),
            "--output-dir",
            str(output_dir),
            "--quality-dir",
            str(quality_dir),
            "--fail-on-quality-gate",
        ]
    )

    latest_report = json.loads((quality_dir / "latest_quality_report.json").read_text(encoding="utf-8"))

    assert exit_code == 1
    assert latest_report["decision"] == "quarantine"
    assert not (output_dir / "hcaptcha_europe_gold.csv").exists()
