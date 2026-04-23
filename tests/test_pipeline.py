from pathlib import Path
import sys

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from hcaptcha_pipeline import (  # type: ignore[attr-defined]
    categorize_company_size,
    categorize_role,
    deduplicate_contacts,
    is_european_country,
    transform_dataset,
)


def test_categorize_role_groups_executive_variants():
    assert categorize_role("CTO & Founder") == "Executive / Technical Decision Maker"
    assert categorize_role("Chief Technology Officer") == "Executive / Technical Decision Maker"
    assert categorize_role("Head of IT") == "Executive / Technical Decision Maker"


def test_categorize_role_groups_compliance_and_specialist_variants():
    assert categorize_role("Compliance-Manager") == "Data / Compliance"
    assert categorize_role("Data manager") == "Data / Compliance"
    assert categorize_role("Senior DevOps/SRE Engineer") == "Individual Contributor / Specialist"
    assert categorize_role("IT Project Manager") == "IT / Engineering Management"


def test_categorize_company_size_handles_ranges_and_malformed_numeric_values():
    assert categorize_company_size("1-10") == "1. Startup / SMB"
    assert categorize_company_size("51-200") == "2. Mid-Market"
    assert categorize_company_size("5001-10000") == "3. Enterprise"
    assert categorize_company_size("Self") == "1. Startup / SMB"
    assert categorize_company_size("46.296,00") == "3. Enterprise"
    assert categorize_company_size(None) == "4. Unknown"


def test_is_european_country_uses_company_country_as_market_filter():
    assert is_european_country("Germany") is True
    assert is_european_country("United Kingdom") is True
    assert is_european_country("Estonia") is True
    assert is_european_country("Brazil") is False
    assert is_european_country(None) is False


def test_deduplicate_contacts_keeps_the_best_record_per_email_and_company():
    raw = pd.DataFrame(
        [
            {
                "E-mail": "lead@example.com",
                "Nome da empresa": "Acme",
                "Status do e-mail": "unknown",
                "País da empresa": "Germany",
                "Tamanho da empresa": None,
                "LinkedIn": None,
            },
            {
                "E-mail": "lead@example.com",
                "Nome da empresa": "Acme",
                "Status do e-mail": "valid",
                "País da empresa": "Germany",
                "Tamanho da empresa": "51-200",
                "LinkedIn": "https://linkedin.com/in/example",
            },
        ]
    )

    deduped = deduplicate_contacts(raw)

    assert len(deduped) == 1
    kept = deduped.iloc[0]
    assert kept["Status do e-mail"] == "valid"
    assert kept["Tamanho da empresa"] == "51-200"


def test_transform_dataset_filters_to_europe_and_adds_strategic_columns():
    raw = pd.DataFrame(
        [
            {
                "E-mail": "lead@example.com",
                "Status do e-mail": "valid",
                "Nome": "Alex",
                "Sobrenome": "Doe",
                "Nome completo": "Alex Doe",
                "Usuário - redes sociais": None,
                "LinkedIn": "https://linkedin.com/in/example",
                "Cargo": "CTO & Founder",
                "País": "Brazil",
                "Localização": "Sao Paulo, Brazil",
                "Setor": "Computer Software",
                "Adicionar data": "2025-02-13 15:24:00",
                "Nome da empresa": "Acme",
                "URL da empresa": "https://acme.example",
                "Empresa - redes sociais": None,
                "Tamanho da empresa": "51-200",
                "País da empresa": "Germany",
                "Localização da empresa": "Berlin, Germany",
                "Estado": "Berlin",
                "Cidade": "Berlin",
                "Setor da empresa": "Computer Software",
                "Telefone da sede": None,
                "Telefone": None,
                "Classificação": "Grande",
            },
            {
                "E-mail": "lead2@example.com",
                "Status do e-mail": "valid",
                "Nome": "Taylor",
                "Sobrenome": "Doe",
                "Nome completo": "Taylor Doe",
                "Usuário - redes sociais": None,
                "LinkedIn": "https://linkedin.com/in/example-2",
                "Cargo": "Data Manager",
                "País": "Brazil",
                "Localização": "Sao Paulo, Brazil",
                "Setor": "Computer Software",
                "Adicionar data": "2025-02-13 15:24:00",
                "Nome da empresa": "Globex",
                "URL da empresa": "https://globex.example",
                "Empresa - redes sociais": None,
                "Tamanho da empresa": "11-50",
                "País da empresa": "Brazil",
                "Localização da empresa": "Sao Paulo, Brazil",
                "Estado": "Sao Paulo",
                "Cidade": "Sao Paulo",
                "Setor da empresa": "Computer Software",
                "Telefone da sede": None,
                "Telefone": None,
                "Classificação": "Média",
            },
        ]
    )

    transformed = transform_dataset(raw)

    assert len(transformed) == 1
    row = transformed.iloc[0]
    assert row["company_country"] == "Germany"
    assert row["contact_country"] == "Brazil"
    assert row["role_category"] == "Executive / Technical Decision Maker"
    assert row["company_size_segment"] == "2. Mid-Market"
    assert row["contact_company_country_mismatch"] is True
