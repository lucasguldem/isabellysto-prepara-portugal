from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

import pandas as pd


PRIVACY_LEVEL = "Level 1: Aggregates + Anonymous Companies"

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
    "company_name",
    "company_industry",
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


def _format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _format_number(value: int | float) -> str:
    return f"{int(value):,}"


def _segment_share(segments: list[dict[str, Any]], needle: str) -> float:
    for segment in segments:
        if needle.lower() in str(segment["company_size_segment"]).lower():
            return float(segment.get("lead_share") or 0)
    return 0.0


def _persona_share(personas: list[dict[str, Any]], roles: set[str]) -> float:
    return sum(float(persona.get("lead_share") or 0) for persona in personas if str(persona["role_category"]) in roles)


def _build_adoption_signals(
    gold: pd.DataFrame,
    market: list[dict[str, Any]],
    personas: list[dict[str, Any]],
    segments: list[dict[str, Any]],
) -> list[dict[str, str]]:
    total_leads = max(len(gold), 1)
    top_five_leads = sum(int(country["lead_count"]) for country in market[:5])
    cross_border_count = int(gold["contact_company_country_mismatch"].fillna(False).sum())
    decision_roles = {"Executive / Technical Decision Maker", "Data / Compliance"}
    decision_share = _persona_share(personas, decision_roles)
    enterprise_share = _segment_share(segments, "Enterprise")
    top_market = str(market[0]["company_country"]) if market else "Top market"

    return [
        {
            "signal": "Concentracao geografica",
            "value": _format_percent(top_five_leads / total_leads),
            "detail": f"dos leads europeus estao nos 5 maiores mercados; {top_market} lidera o recorte.",
            "interpretation": "Permite outbound e ABM com foco, sem pulverizar a entrada europeia.",
            "strength": "Alta",
        },
        {
            "signal": "Compradores qualificados",
            "value": _format_percent(decision_share),
            "detail": "dos leads estao em decisao tecnica, dados ou compliance.",
            "interpretation": "A mensagem precisa unir seguranca, privacidade e facilidade de implementacao.",
            "strength": "Alta",
        },
        {
            "signal": "Maturidade enterprise",
            "value": _format_percent(enterprise_share),
            "detail": "dos leads estao em empresas enterprise.",
            "interpretation": "O primeiro caso de valor deve mirar contas com maior risco, volume e governanca.",
            "strength": "Media",
        },
        {
            "signal": "Operacao distribuida",
            "value": _format_percent(cross_border_count / total_leads),
            "detail": f"{_format_number(cross_border_count)} leads tem pais do contato diferente do pais da empresa.",
            "interpretation": "Este e um proxy de equipes internacionais, nao uma medicao direta de comportamento.",
            "strength": "Media",
        },
    ]


def _build_barriers_and_opportunities() -> list[dict[str, str]]:
    return [
        {
            "theme": "Privacidade e GDPR",
            "barrier": "Compradores europeus podem exigir prova de minimizacao de dados, base legal e transferencia internacional.",
            "opportunity": "Posicionar a hCaptcha como alternativa privacy-first com menor dependencia do ecossistema Google.",
            "move": "Abrir a conversa com compliance, DPA, minimizacao, cookies tecnicos e governanca de dados.",
        },
        {
            "theme": "Inercia do reCAPTCHA",
            "barrier": "Muitas empresas ja usam reCAPTCHA e evitam troca quando percebem risco tecnico.",
            "opportunity": "Explorar compatibilidade de integracao e migração simples como redutor de friccao.",
            "move": "Usar mensagem de substituicao progressiva: piloto em formularios de maior risco antes de rollout amplo.",
        },
        {
            "theme": "Experiencia do usuario",
            "barrier": "CAPTCHA pode ser visto como atrito para conversao e acessibilidade.",
            "opportunity": "Vender protecao anti-bot com modos de baixa friccao e ajuste por risco.",
            "move": "Separar discurso tecnico: bot score, modos invisiveis/passivos e reducao de falso positivo.",
        },
        {
            "theme": "Dados sem intencao direta",
            "barrier": "A base nao informa uso atual de CAPTCHA, stack tecnologico ou eventos de interesse.",
            "opportunity": "Transformar a analise em lista priorizada para validacao comercial rapida.",
            "move": "Medir resposta por pais, persona e porte nos primeiros ciclos de outbound.",
        },
    ]


def _build_action_plan(market: list[dict[str, Any]], personas: list[dict[str, Any]], segments: list[dict[str, Any]]) -> list[dict[str, str]]:
    privacy_targets = ", ".join(_countries_for_track(market, PRIVACY_FIRST_COUNTRIES)[:3]) or "Germany, France"
    scale_targets = ", ".join(_countries_for_track(market, SCALE_FIRST_COUNTRIES)[:3]) or "United Kingdom"
    expansion_targets = ", ".join(
        str(row["company_country"])
        for row in market
        if str(row["company_country"]) not in PRIVACY_FIRST_COUNTRIES | SCALE_FIRST_COUNTRIES
    ) or "Spain, Portugal"
    top_persona = str(personas[0]["role_category"]) if personas else "Technical decision maker"
    top_segment_row = max(segments, key=lambda row: int(row.get("lead_count") or 0), default={"company_size_segment": "Enterprise"})
    top_segment = str(top_segment_row["company_size_segment"]).replace("3. ", "").replace("2. ", "").replace("1. ", "")

    return [
        {
            "phase": "0-30 dias",
            "focus": "Validar tese privacy-first",
            "markets": privacy_targets,
            "buyer": "Compliance, DPO, CISO, Head of IT",
            "message": "Alternativa anti-bot com privacidade, soberania e prontidao para GDPR.",
            "kpi": "Taxa de resposta por persona e reunioes qualificadas.",
        },
        {
            "phase": "31-60 dias",
            "focus": "Provar adocao tecnica",
            "markets": scale_targets,
            "buyer": top_persona,
            "message": "Troca simples do reCAPTCHA, baixa friccao de UX e protecao escalavel.",
            "kpi": "Pilotos iniciados e barreiras tecnicas mapeadas.",
        },
        {
            "phase": "61-90 dias",
            "focus": f"Escalar para {top_segment}",
            "markets": expansion_targets,
            "buyer": "CTO, IT Manager, Data / Compliance",
            "message": "Playbook ajustado por pais, porte e maturidade regulatoria.",
            "kpi": "Pipeline por mercado e conversao de piloto para oportunidade.",
        },
    ]


def _build_challenge_coverage() -> list[dict[str, str]]:
    return [
        {
            "requirement": "Perfis dos potenciais clientes",
            "status": "Coberto",
            "evidence": "Categorias de cargo, share por persona e leitura de comprador tecnico/compliance.",
            "artifact": "Power BI: Buyer Intelligence; Site: slide Personas.",
        },
        {
            "requirement": "Segmentacao por pais/regiao",
            "status": "Coberto",
            "evidence": "Ranking por pais, tiers de prioridade e mensagem por mercado.",
            "artifact": "Power BI: Market Command; Site: slide Mercados.",
        },
        {
            "requirement": "Tamanho das empresas",
            "status": "Coberto",
            "evidence": "Buckets Startup / SMB, Mid-Market, Enterprise e share por porte.",
            "artifact": "Power BI: Buyer Intelligence; Site: slide Porte.",
        },
        {
            "requirement": "Comportamento e interesses",
            "status": "Inferido",
            "evidence": "A planilha nao tem eventos; foram usados proxies firmograficos e sinal cross-border.",
            "artifact": "Power BI: Border Signal; Site: slide Comportamento.",
        },
        {
            "requirement": "Barreiras e oportunidades",
            "status": "Coberto",
            "evidence": "GDPR, inercia do reCAPTCHA, friccao de UX e validacao comercial.",
            "artifact": "Relatorio executivo; Site: slide Barreiras.",
        },
        {
            "requirement": "Dashboard interativo e relatorio",
            "status": "Coberto",
            "evidence": "PBIP versionavel, relatorio em Markdown, PDF publico e roteiro privado.",
            "artifact": "Power BI + reports + presentation site.",
        },
    ]


def _build_companies(gold: pd.DataFrame, country_priority: pd.DataFrame) -> list[dict[str, Any]]:
    named_companies = gold.loc[
        gold["company_name"].notna() & (gold["company_name"].astype(str).str.strip() != "")
    ].copy()

    if named_companies.empty:
        return []

    named_companies["_row_order"] = range(len(named_companies))
    size_candidates = named_companies.loc[named_companies["company_size_segment"] != "4. Unknown"]
    if size_candidates.empty:
        size_candidates = named_companies

    country = (
        named_companies.groupby(["company_name", "company_country"], dropna=False)
        .agg(count=("company_country", "size"), first_seen=("_row_order", "min"))
        .sort_values(["company_name", "count", "first_seen"], ascending=[True, False, True])
        .reset_index()
        .drop_duplicates("company_name")
        .set_index("company_name")["company_country"]
    )
    size = (
        size_candidates.groupby(["company_name", "company_size_segment"], dropna=False)
        .agg(count=("company_size_segment", "size"), first_seen=("_row_order", "min"))
        .sort_values(["company_name", "count", "first_seen"], ascending=[True, False, True])
        .reset_index()
        .drop_duplicates("company_name")
        .set_index("company_name")["company_size_segment"]
    )
    lead_count = named_companies.groupby("company_name", dropna=False).size()
    role_counts = (
        named_companies.assign(role_category=named_companies["role_category"].fillna("Unknown"))
        .groupby(["company_name", "role_category"], dropna=False)
        .size()
        .reset_index(name="lead_count")
        .sort_values(["company_name", "role_category"])
    )
    role_mix_by_company: dict[str, dict[str, int]] = {}
    for row in role_counts.itertuples(index=False):
        role_mix_by_company.setdefault(str(row.company_name), {})[str(row.role_category)] = int(row.lead_count)
    role_mix = pd.Series(role_mix_by_company, name="role_mix")

    company_frame = pd.concat(
        [
            country.rename("company_country"),
            size.rename("company_size_segment"),
            lead_count.rename("lead_count"),
            role_mix,
        ],
        axis=1,
    ).fillna({"company_country": "", "company_size_segment": "4. Unknown"})

    return sorted(
        _sanitize_records(
            _records(
                company_frame.reset_index(drop=True).loc[
                    :,
                    ["company_country", "company_size_segment", "lead_count", "role_mix"],
                ]
            )
        ),
        key=lambda row: (-int(row["lead_count"]), str(row["company_country"]), str(row["company_size_segment"])),
    )


def _build_glossary_terms() -> list[dict[str, str]]:
    terms = [
        {
            "term": "ETL",
            "category": "Metodologia",
            "definition": "Processo de extrair dados de uma fonte, transformar esses dados com regras de limpeza e carregar o resultado em uma base pronta para analise.",
            "in_project": "Pipeline Python que le a planilha original, limpa paises, cargos e porte, remove duplicidades e gera a base gold usada no Power BI e no site.",
            "why_it_matters": "Sem ETL, a recomendacao ficaria vulneravel a registros duplicados, paises inconsistentes e cargos impossiveis de comparar.",
        },
        {
            "term": "Base raw",
            "category": "Dados",
            "definition": "Conjunto de dados no formato original, antes de tratamento, validacao ou padronizacao.",
            "in_project": "A planilha inicial do desafio tinha 1.027 registros vindos da exportacao usada no exercicio da Snov.io.",
            "why_it_matters": "Mostra o ponto de partida e deixa claro que a analise nao foi feita diretamente em dados brutos.",
        },
        {
            "term": "Base gold",
            "category": "Dados",
            "definition": "Versao tratada e validada dos dados, pronta para analise, dashboard e defesa executiva.",
            "in_project": "A base final tem 882 leads europeus elegiveis em 748 empresas, sem expor PII no site.",
            "why_it_matters": "E a fonte confiavel para os indicadores de mercado, persona, porte e recomendacao.",
        },
        {
            "term": "Power BI",
            "category": "BI",
            "definition": "Ferramenta de business intelligence usada para criar modelos, medidas, filtros e dashboards interativos.",
            "in_project": "O dashboard PBIP organiza Market Command, Buyer Intelligence, Border Signal e Action Map.",
            "why_it_matters": "Atende o objetivo final do desafio: apoiar decisoes estrategicas por meio de um dashboard interativo.",
        },
        {
            "term": "PBIP",
            "category": "BI",
            "definition": "Formato de projeto do Power BI que salva relatorio e modelo sem depender apenas de um arquivo binario PBIX.",
            "in_project": "O relatorio versionavel esta em powerbi/hcaptcha-positioning/hcaptcha_report.pbip.",
            "why_it_matters": "Permite revisar estrutura, paginas e modelo no Git, algo melhor para producao e manutencao.",
        },
        {
            "term": "Lead",
            "category": "Comercial",
            "definition": "Contato profissional que pode ser abordado em uma estrategia comercial.",
            "in_project": "Cada lead representa um profissional associado a uma empresa europeia elegivel.",
            "why_it_matters": "A contagem de leads mede alcance comercial, mas precisa ser analisada junto com empresas unicas.",
        },
        {
            "term": "Persona",
            "category": "Comercial",
            "definition": "Perfil de comprador ou influenciador usado para adaptar mensagem, argumento e canal de abordagem.",
            "in_project": "Os cargos foram agrupados em categorias como Executive / Technical Decision Maker e Data / Compliance.",
            "why_it_matters": "A hCaptcha precisa vender para tecnologia e compliance com argumentos diferentes.",
        },
        {
            "term": "ICP",
            "category": "Comercial",
            "definition": "Ideal Customer Profile, ou perfil de cliente ideal para priorizar mercado, porte, dor e potencial de compra.",
            "in_project": "O ICP inicial combina mercados Tier 1, decisores tecnicos/compliance e contas enterprise ou mid-market qualificadas.",
            "why_it_matters": "Ajuda a transformar uma lista de contatos em estrategia comercial acionavel.",
        },
        {
            "term": "ABM",
            "category": "Comercial",
            "definition": "Account-Based Marketing, estrategia de marketing e vendas focada em contas prioritarias em vez de abordagem massiva.",
            "in_project": "A recomendacao usa ABM para concentrar esforco em Alemanha, Franca e Reino Unido antes de escalar.",
            "why_it_matters": "Reduz dispersao comercial e aumenta a chance de validar a mensagem em contas de maior impacto.",
        },
        {
            "term": "GDPR",
            "category": "Regulacao",
            "definition": "Regulamento Geral de Protecao de Dados da Uniao Europeia, base para exigencias de privacidade e tratamento de dados pessoais.",
            "in_project": "A narrativa privacy-first usa GDPR como contexto de compra para mercados como Alemanha e Franca.",
            "why_it_matters": "Explica por que privacidade pode ser diferencial competitivo na Europa.",
        },
        {
            "term": "reCAPTCHA",
            "category": "Produto",
            "definition": "Servico anti-bot do Google usado para diferenciar humanos de automacoes em sites e formularios.",
            "in_project": "A hCaptcha e posicionada como alternativa ao reCAPTCHA com apelo de privacidade, soberania e migracao tecnica.",
            "why_it_matters": "E o concorrente e referencia de comparacao mais reconhecivel para a banca.",
        },
        {
            "term": "hCaptcha",
            "category": "Produto",
            "definition": "Solucao de protecao anti-bot e verificacao humana usada para proteger formularios, logins e fluxos digitais contra automacao abusiva.",
            "in_project": "E a empresa/produto analisado no desafio de posicionamento europeu.",
            "why_it_matters": "Define o objeto estrategico da analise: como entrar, para quem vender e com qual mensagem.",
        },
        {
            "term": "Proxy firmografico",
            "category": "Metodologia",
            "definition": "Sinal indireto baseado em atributos da empresa ou do contato, usado quando a base nao tem comportamento direto medido.",
            "in_project": "Cargo, pais, porte e divergencia pais do contato versus pais da empresa foram usados como proxies de propensao.",
            "why_it_matters": "Deixa claro que comportamento e interesse foram inferidos, nao medidos por cliques ou visitas.",
        },
        {
            "term": "Cross-border signal",
            "category": "Metodologia",
            "definition": "Sinal de operacao distribuida quando o pais do contato difere do pais principal da empresa.",
            "in_project": "10,1% da base gold apresenta divergencia entre pais do contato e pais da empresa.",
            "why_it_matters": "Ajuda a justificar mensagens de consistencia global, baixa friccao e conformidade multinacional.",
        },
        {
            "term": "Quality gate",
            "category": "Dados",
            "definition": "Controle que verifica se uma etapa do pipeline atingiu criterios minimos de qualidade antes de seguir.",
            "in_project": "O snapshot e o pipeline so sao usados na apresentacao quando a decisao de qualidade esta aprovada.",
            "why_it_matters": "Aumenta confiabilidade da defesa e reduz risco de apresentar dado sujo.",
        },
        {
            "term": "Snapshot",
            "category": "Dados",
            "definition": "Copia estatica de um conjunto de dados em um momento especifico.",
            "in_project": "O site usa presentation-snapshot.json para carregar dados anonimizados e agregados.",
            "why_it_matters": "Garante que site, PDF e defesa usam a mesma versao dos dados.",
        },
    ]

    return sorted(terms, key=lambda item: (item["category"], item["term"]))


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
    personas = _build_personas(role_category)
    segments = _build_segments(company_size)
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
        "personas": personas,
        "segments": segments,
        "companies": _build_companies(gold, country_priority),
        "recommendations": _build_recommendations(market),
        "narrative": _build_narrative(summary_text),
        "adoption_signals": _build_adoption_signals(gold, market, personas, segments),
        "barriers": _build_barriers_and_opportunities(),
        "action_plan": _build_action_plan(market, personas, segments),
        "challenge_coverage": _build_challenge_coverage(),
        "glossary_terms": _build_glossary_terms(),
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
    parser = argparse.ArgumentParser(description="Build the sanitized JSON snapshot for the Course Presentation site.")
    parser.add_argument("--gold", type=Path, default=defaults.gold)
    parser.add_argument("--country-priority", type=Path, default=defaults.country_priority)
    parser.add_argument("--role-category", type=Path, default=defaults.role_category)
    parser.add_argument("--company-size", type=Path, default=defaults.company_size)
    parser.add_argument("--summary", type=Path, default=defaults.summary)
    parser.add_argument("--quality-report", type=Path, default=defaults.quality_report)
    parser.add_argument("--output", type=Path, default=root / "apps/hcaptcha-course-presentation/public/data/presentation-snapshot.json")
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
    print(f"Wrote sanitized presentation snapshot to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
