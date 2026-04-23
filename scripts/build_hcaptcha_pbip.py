from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PBIP_ROOT = PROJECT_ROOT / "dashboards" / "hcaptcha_report"
REPORT_NAME = "hcaptcha_report.Report"
MODEL_NAME = "hcaptcha_report.SemanticModel"
PBIP_FILE = "hcaptcha_report.pbip"

DATASET_LOGICAL_ID = "7d1a61c8-d30e-43c9-a4d4-5f3ee0a7d8d1"
REPORT_LOGICAL_ID = "ef4b92bc-3d0f-4e9e-bf50-bde2dd3f2f8d"


def wsl_unc_path(path: Path) -> str:
    distro = os.environ.get("WSL_DISTRO_NAME", "Ubuntu-24.04")
    return "\\\\wsl.localhost\\{}\\{}".format(distro, str(path).lstrip("/").replace("/", "\\"))


def ensure_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def text_style(font_size: str, color: str = "#0f172a", bold: bool = False) -> dict:
    style = {
        "fontFamily": "Segoe UI",
        "fontSize": font_size,
        "color": color,
    }
    if bold:
        style["fontWeight"] = "bold"
        style["fontFamily"] = "Segoe UI Semibold"
    return style


def textbox_visual(name: str, x: float, y: float, width: float, height: float, paragraphs: list[list[tuple[str, dict]]], z: float) -> dict:
    config = {
        "name": name,
        "layouts": [
            {
                "id": 0,
                "position": {
                    "x": x,
                    "y": y,
                    "z": z,
                    "width": width,
                    "height": height,
                    "tabOrder": int(z),
                },
            }
        ],
        "singleVisual": {
            "visualType": "textbox",
            "drillFilterOtherVisuals": True,
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {"value": value, "textStyle": style}
                                        for value, style in text_runs
                                    ]
                                }
                                for text_runs in paragraphs
                            ]
                        }
                    }
                ]
            },
            "vcObjects": {},
        },
    }
    return {
        "config": json.dumps(config, ensure_ascii=False, separators=(",", ":")),
        "filters": "[]",
        "height": height,
        "width": width,
        "x": x,
        "y": y,
        "z": z,
    }


def image_visual(name: str, item_name: str, x: float, y: float, width: float, height: float, z: float) -> dict:
    config = {
        "name": name,
        "layouts": [
            {
                "id": 0,
                "position": {
                    "x": x,
                    "y": y,
                    "z": z,
                    "width": width,
                    "height": height,
                    "tabOrder": int(z),
                },
            }
        ],
        "singleVisual": {
            "visualType": "image",
            "drillFilterOtherVisuals": True,
            "objects": {
                "general": [
                    {
                        "properties": {
                            "imageUrl": {
                                "expr": {
                                    "ResourcePackageItem": {
                                        "PackageName": "RegisteredResources",
                                        "PackageType": 1,
                                        "ItemName": item_name,
                                    }
                                }
                            }
                        }
                    }
                ]
            },
        },
    }
    return {
        "config": json.dumps(config, ensure_ascii=False, separators=(",", ":")),
        "filters": "[]",
        "height": height,
        "width": width,
        "x": x,
        "y": y,
        "z": z,
    }


def make_section(name: str, display_name: str, ordinal: int, visuals: list[dict]) -> dict:
    return {
        "config": json.dumps({"visibility": 1}),
        "displayName": display_name,
        "displayOption": 1,
        "filters": "[]",
        "height": 720.0,
        "name": name,
        "ordinal": ordinal,
        "visualContainers": visuals,
        "width": 1280.0,
    }


def report_theme() -> dict:
    return {
        "name": "hcaptcha_theme",
        "dataColors": ["#0f766e", "#1d4ed8", "#ea580c", "#64748b", "#0f172a"],
        "background": "#f8fafc",
        "foreground": "#0f172a",
        "tableAccent": "#0f766e",
        "visualStyles": {
            "*": {
                "*": {
                    "title": [
                        {
                            "fontFamily": "Segoe UI",
                            "fontSize": 12,
                            "color": {"solid": {"color": "#0f172a"}},
                        }
                    ]
                }
            }
        },
    }


def report_definition() -> dict:
    resources = [
        {
            "resourcePackage": {
                "disabled": False,
                "items": [
                    {"name": "CY23SU04", "path": "BaseThemes/CY23SU04.json", "type": 202}
                ],
                "name": "SharedResources",
                "type": 2,
            }
        },
        {
            "resourcePackage": {
                "disabled": False,
                "items": [
                    {"name": "hcaptcha_theme.json", "path": "hcaptcha_theme.json", "type": 201},
                    {"name": "01_market_overview_top_countries.png", "path": "01_market_overview_top_countries.png", "type": 100},
                    {"name": "02_icp_role_size_heatmap.png", "path": "02_icp_role_size_heatmap.png", "type": 100},
                    {"name": "03_cross_border_signal.png", "path": "03_cross_border_signal.png", "type": 100},
                ],
                "name": "RegisteredResources",
                "type": 1,
            }
        },
    ]

    config = {
        "version": "5.48",
        "themeCollection": {
            "baseTheme": {"name": "CY23SU04", "version": "5.43", "type": 2},
            "customTheme": {"name": "hcaptcha_theme.json", "version": "5.48", "type": 1},
        },
        "activeSectionIndex": 0,
    }

    sections = [
        make_section(
            "ReportSectionMarketOverview",
            "Market Overview",
            0,
            [
                textbox_visual(
                    "overview-title",
                    42,
                    18,
                    860,
                    60,
                    [
                        [("hCaptcha na Europa: mercados prioritários", text_style("24pt", bold=True))],
                    ],
                    1000,
                ),
                textbox_visual(
                    "overview-subtitle",
                    42,
                    82,
                    1120,
                    72,
                    [
                        [("Leitura executiva: Germany, United Kingdom e France concentram a massa crítica inicial de prospecção.", text_style("12pt"))],
                        [("A recomendação comercial é dividir a narrativa entre privacidade/compliance e eficiência técnica por mercado.", text_style("12pt"))],
                    ],
                    900,
                ),
                image_visual(
                    "overview-image",
                    "01_market_overview_top_countries.png",
                    42,
                    170,
                    860,
                    500,
                    800,
                ),
                textbox_visual(
                    "overview-notes",
                    930,
                    170,
                    300,
                    300,
                    [
                        [("Tier 1", text_style("14pt", "#0f766e", bold=True))],
                        [("Germany: narrativa privacy-first e alternativa GDPR-safe ao reCAPTCHA.", text_style("11pt"))],
                        [("United Kingdom: foco em eficiência, UX e escala para SaaS e software.", text_style("11pt"))],
                        [("France: reforço regulatório e governança de dados.", text_style("11pt"))],
                    ],
                    700,
                ),
            ],
        ),
        make_section(
            "ReportSectionICP",
            "ICP & Personas",
            1,
            [
                textbox_visual(
                    "icp-title",
                    42,
                    18,
                    880,
                    60,
                    [[("ICP por porte e centro decisório", text_style("24pt", bold=True))]],
                    1000,
                ),
                textbox_visual(
                    "icp-subtitle",
                    42,
                    82,
                    1120,
                    56,
                    [[("A base é dominada por Executive / Technical Decision Maker e Data / Compliance, exigindo discurso comercial duplo.", text_style("12pt"))]],
                    900,
                ),
                image_visual(
                    "icp-image",
                    "02_icp_role_size_heatmap.png",
                    42,
                    160,
                    760,
                    520,
                    800,
                ),
                textbox_visual(
                    "icp-notes",
                    840,
                    160,
                    380,
                    320,
                    [
                        [("Leituras principais", text_style("14pt", "#1d4ed8", bold=True))],
                        [("Enterprise: Compliance e liderança técnica aparecem com maior peso relativo.", text_style("11pt"))],
                        [("Startup / SMB: CTOs e líderes técnicos ganham protagonismo.", text_style("11pt"))],
                        [("Mensagem recomendada: compliance para enterprise; performance e baixa fricção para SMB.", text_style("11pt"))],
                    ],
                    700,
                ),
            ],
        ),
        make_section(
            "ReportSectionCrossBorder",
            "Cross-Border Signal",
            2,
            [
                textbox_visual(
                    "cross-title",
                    42,
                    18,
                    920,
                    60,
                    [[("Sinal de operação distribuída", text_style("24pt", bold=True))]],
                    1000,
                ),
                textbox_visual(
                    "cross-subtitle",
                    42,
                    82,
                    1140,
                    56,
                    [[("A divergência entre país do contato e país da empresa aponta contas com operação transnacional, sensíveis a edge security.", text_style("12pt"))]],
                    900,
                ),
                image_visual(
                    "cross-image",
                    "03_cross_border_signal.png",
                    42,
                    160,
                    760,
                    520,
                    800,
                ),
                textbox_visual(
                    "cross-notes",
                    840,
                    160,
                    380,
                    320,
                    [
                        [("Implicações GTM", text_style("14pt", "#ea580c", bold=True))],
                        [("Contas distribuídas valorizam proteção consistente entre regiões e baixa latência.", text_style("11pt"))],
                        [("Belgium, Ireland e United Kingdom aparecem com taxa elevada de mismatch relativa.", text_style("11pt"))],
                        [("Narrativa recomendada: cobertura global de borda com menor atrito regulatório.", text_style("11pt"))],
                    ],
                    700,
                ),
            ],
        ),
        make_section(
            "ReportSectionNextAction",
            "Next Best Action",
            3,
            [
                textbox_visual(
                    "next-title",
                    42,
                    18,
                    900,
                    60,
                    [[("Roadmap prescritivo para vendas", text_style("24pt", bold=True))]],
                    1000,
                ),
                textbox_visual(
                    "next-body",
                    42,
                    120,
                    1160,
                    420,
                    [
                        [("1. Iniciar ABM em Germany e France com trilha Privacy / Compliance para enterprise.", text_style("14pt", bold=True))],
                        [("2. Ativar outbound técnico em United Kingdom para SaaS e software com foco em performance anti-bot e UX.", text_style("14pt", bold=True))],
                        [("3. Expandir para Spain e Portugal com discurso híbrido de compliance e escala.", text_style("14pt", bold=True))],
                        [("4. Manter Lithuania, Estonia e Ireland como mercados Tier 2 com cadência menor e narrativa digital-first.", text_style("14pt", bold=True))],
                        [("Materialização do arquivo standalone: abra hcaptcha_report.pbip no Power BI Desktop e salve como .pbix.", text_style("13pt", "#0f766e"))],
                    ],
                    900,
                ),
            ],
        ),
    ]

    return {
        "config": json.dumps(config, ensure_ascii=False, separators=(",", ":")),
        "filters": [],
        "layoutOptimization": 1,
        "pods": [],
        "publicCustomVisuals": [],
        "resourcePackages": resources,
        "sections": sections,
        "theme": "hcaptcha_theme.json",
    }


def build_model_files() -> dict[str, str]:
    data_root = wsl_unc_path(PROJECT_ROOT / "data" / "processed")

    expressions = f"""expression DataRoot = "{data_root}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
\tlineageTag: 48cb2b8d-8ec9-42bf-93c1-b6d0f1787d11

\tannotation PBI_ResultType = Text
"""

    model = """model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tdiscourageImplicitMeasures
\tsourceQueryCulture: en-US
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

queryGroup 'Source Data'

\tannotation PBI_QueryGroupOrder = 0

annotation __PBI_TimeIntelligenceEnabled = 0

annotation __TEdtr = 1

annotation PBI_ProTooling = ["DevMode"]

ref table Leads
ref table 'Country Priority'
ref table 'Role Category'
ref table 'Company Size'
ref table About

ref culture en-US
"""

    relationships = """relationship 7a2152fc-e347-48e8-84bb-9ce92ecf79b7
\tfromColumn: Leads.company_country
\ttoColumn: 'Country Priority'.company_country

relationship 8896ce94-fdb4-4647-8e7f-36ec1ea275f1
\tfromColumn: Leads.role_category
\ttoColumn: 'Role Category'.role_category

relationship 62f74127-79ad-4df4-9c84-9041637dd349
\tfromColumn: Leads.company_size_segment
\ttoColumn: 'Company Size'.company_size_segment
"""

    about_table = """table About
\tlineageTag: 5c0d2a56-9770-4ef7-8620-f5080b84f848

\tcolumn Key
\t\tdataType: string
\t\tlineageTag: 38176fbf-c6db-4f2d-ab9f-c10f98521f6b
\t\tsummarizeBy: none
\t\tsourceColumn: Key

\tcolumn Value
\t\tdataType: string
\t\tlineageTag: 81c2d81a-b6ff-420f-8158-66cb4edb7a1e
\t\tsummarizeBy: none
\t\tsourceColumn: Value

\tcolumn Order
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 26c19df4-9fc6-46e7-98ab-fa7d4ab3cfe6
\t\tsummarizeBy: none
\t\tsourceColumn: Order

\tpartition About = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = #table({"Key", "Value"}, {
\t\t\t\t        {"Dataset", "hCaptcha Europe Positioning"},
\t\t\t\t        {"Source", "data/processed/*.csv"},
\t\t\t\t        {"Build", "Generated from scripts/build_hcaptcha_pbip.py"},
\t\t\t\t        {"Materialization", "Open hcaptcha_report.pbip in Power BI Desktop and save as .pbix"}
\t\t\t\t    }),
\t\t\t\t    #"Added Index" = Table.AddIndexColumn(Source, "Order", 1, 1, Int64.Type)
\t\t\t\tin
\t\t\t\t    #"Added Index"

\tannotation PBI_ResultType = Table
"""

    leads_table = """table Leads
\tlineageTag: 1d3de8f6-9f99-4ac3-8a14-5f7c6290ec51

\tmeasure Leads = COUNTROWS('Leads')
\t\tformatString: #,##0
\t\tlineageTag: 7b5f9967-42cf-42d4-ac50-9be2040d6fbe

\tmeasure Companies = DISTINCTCOUNT('Leads'[company_name])
\t\tformatString: #,##0
\t\tlineageTag: 2af1ef4d-4e63-41b4-8adb-b7446466fda3

\tmeasure 'Countries In Scope' = DISTINCTCOUNT('Leads'[company_country])
\t\tformatString: #,##0
\t\tlineageTag: 4a08ce9f-2507-4ac6-9b26-f4908e71474c

\tmeasure 'Cross-Border Contacts' = CALCULATE([Leads], 'Leads'[contact_company_country_mismatch] = TRUE())
\t\tformatString: #,##0
\t\tlineageTag: f0f40b58-34a0-4167-b468-7c06db5e9a44

\tmeasure 'Cross-Border Share' = DIVIDE([Cross-Border Contacts], [Leads])
\t\tformatString: 0.0 %
\t\tlineageTag: bb2a6e8f-0dab-49eb-b1c3-2eff83d5242b

\tmeasure 'Executive Leads' = CALCULATE([Leads], 'Leads'[role_category] = "Executive / Technical Decision Maker")
\t\tformatString: #,##0
\t\tlineageTag: 427ef40c-cffd-47d4-9d7a-0cc4791543e1

\tmeasure 'Compliance Leads' = CALCULATE([Leads], 'Leads'[role_category] = "Data / Compliance")
\t\tformatString: #,##0
\t\tlineageTag: 3733ec84-4f7c-4b58-b7d7-e5287ffdd4f1

\tmeasure 'Enterprise Leads' = CALCULATE([Leads], 'Leads'[company_size_segment] = "3. Enterprise")
\t\tformatString: #,##0
\t\tlineageTag: aeeaa46b-8b73-4d52-85c5-9c95e4bfbeb6

\tmeasure 'Mid-Market Leads' = CALCULATE([Leads], 'Leads'[company_size_segment] = "2. Mid-Market")
\t\tformatString: #,##0
\t\tlineageTag: 66a5774a-bfb7-4667-b660-8d938efdbafd

\tmeasure 'Startup / SMB Leads' = CALCULATE([Leads], 'Leads'[company_size_segment] = "1. Startup / SMB")
\t\tformatString: #,##0
\t\tlineageTag: 7a6afdf5-1e16-4037-b924-4f1e90287f16

\tcolumn email
\t\tdataType: string
\t\tlineageTag: 803e57bc-f808-497e-8d4e-68e8cc055e07
\t\tsummarizeBy: none
\t\tsourceColumn: email

\tcolumn email_status
\t\tdataType: string
\t\tlineageTag: 90f9238c-e677-4442-b865-466c7e116ff9
\t\tsummarizeBy: none
\t\tsourceColumn: email_status

\tcolumn full_name
\t\tdataType: string
\t\tlineageTag: 0e1b2d06-2f65-43d6-a9a4-5209b5c0567e
\t\tsummarizeBy: none
\t\tsourceColumn: full_name

\tcolumn job_title
\t\tdataType: string
\t\tlineageTag: f4720127-2526-42a8-8394-0c8dcc244fb2
\t\tsummarizeBy: none
\t\tsourceColumn: job_title

\tcolumn contact_country
\t\tdataType: string
\t\tlineageTag: 78f34266-a388-4d97-bb60-f0808ef8ac91
\t\tsummarizeBy: none
\t\tsourceColumn: contact_country

\tcolumn added_at
\t\tdataType: dateTime
\t\tformatString: General Date
\t\tlineageTag: e9ba6b8d-4fe7-4914-8280-f5403809ae95
\t\tsummarizeBy: none
\t\tsourceColumn: added_at

\t\tannotation UnderlyingDateTimeDataType = DateTime

\tcolumn company_name
\t\tdataType: string
\t\tlineageTag: 3274a1c5-6f05-4e69-af81-f99da82fcfa5
\t\tisDefaultLabel
\t\tsummarizeBy: none
\t\tsourceColumn: company_name

\tcolumn company_size_raw
\t\tdataType: string
\t\tlineageTag: 425fe80f-a6e4-45a7-8757-032d0c0612ca
\t\tsummarizeBy: none
\t\tsourceColumn: company_size_raw

\tcolumn company_country
\t\tdataType: string
\t\tlineageTag: 89d8602e-fdcc-48df-9672-5b987467a7b2
\t\tsummarizeBy: none
\t\tsourceColumn: company_country

\tcolumn company_industry
\t\tdataType: string
\t\tlineageTag: 8753ac98-c459-4e95-a4ea-6ecdb5d7c68c
\t\tsummarizeBy: none
\t\tsourceColumn: company_industry

\tcolumn role_category
\t\tdataType: string
\t\tlineageTag: 8d21eb17-5adf-4c95-9a0d-f717b31b1a72
\t\tsummarizeBy: none
\t\tsourceColumn: role_category

\tcolumn company_size_segment
\t\tdataType: string
\t\tlineageTag: a0d5a563-bddc-459a-8150-748814eff89e
\t\tsummarizeBy: none
\t\tsourceColumn: company_size_segment

\tcolumn company_size_min
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: ad14c2c6-6246-470a-9eea-6d208777ff8c
\t\tsummarizeBy: none
\t\tsourceColumn: company_size_min

\tcolumn company_size_max
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 5f10b57e-c255-4c6d-83c4-658f9870d4f9
\t\tsummarizeBy: none
\t\tsourceColumn: company_size_max

\tcolumn is_email_valid
\t\tdataType: boolean
\t\tlineageTag: 71338875-b47f-4823-96c0-93a328ff68a2
\t\tsummarizeBy: none
\t\tsourceColumn: is_email_valid

\tcolumn is_european_company
\t\tdataType: boolean
\t\tlineageTag: c80e4b41-bf7a-4470-a73b-4b61c1ec41cd
\t\tsummarizeBy: none
\t\tsourceColumn: is_european_company

\tcolumn contact_company_country_mismatch
\t\tdataType: boolean
\t\tlineageTag: a035e017-c249-4cb6-8fed-18a76f26d202
\t\tsummarizeBy: none
\t\tsourceColumn: contact_company_country_mismatch

\tpartition Leads = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents(DataRoot & "\\\\hcaptcha_europe_gold.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
\t\t\t\t        {"email", type text},
\t\t\t\t        {"email_status", type text},
\t\t\t\t        {"full_name", type text},
\t\t\t\t        {"job_title", type text},
\t\t\t\t        {"contact_country", type text},
\t\t\t\t        {"added_at", type datetime},
\t\t\t\t        {"company_name", type text},
\t\t\t\t        {"company_size_raw", type text},
\t\t\t\t        {"company_country", type text},
\t\t\t\t        {"company_industry", type text},
\t\t\t\t        {"role_category", type text},
\t\t\t\t        {"company_size_segment", type text},
\t\t\t\t        {"company_size_min", Int64.Type},
\t\t\t\t        {"company_size_max", Int64.Type},
\t\t\t\t        {"is_email_valid", type logical},
\t\t\t\t        {"is_european_company", type logical},
\t\t\t\t        {"contact_company_country_mismatch", type logical}
\t\t\t\t    }),
\t\t\t\t    #"Selected Columns" = Table.SelectColumns(#"Changed Type",{
\t\t\t\t        "email", "email_status", "full_name", "job_title", "contact_country", "added_at", "company_name",
\t\t\t\t        "company_size_raw", "company_country", "company_industry", "role_category", "company_size_segment",
\t\t\t\t        "company_size_min", "company_size_max", "is_email_valid", "is_european_company", "contact_company_country_mismatch"
\t\t\t\t    })
\t\t\t\tin
\t\t\t\t    #"Selected Columns"

\tannotation PBI_ResultType = Table
"""

    country_priority_table = """table 'Country Priority'
\tlineageTag: e88ba3f0-93a2-4810-98f2-b1f41edce7d8

\tcolumn company_country
\t\tdataType: string
\t\tisKey
\t\tlineageTag: 5ec4699c-2a31-4cd6-ad19-8774fcac2af8
\t\tsummarizeBy: none
\t\tsourceColumn: company_country

\tcolumn lead_count
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 2cf0ec0a-2a46-4f2b-9471-21e385eae5e0
\t\tsummarizeBy: sum
\t\tsourceColumn: lead_count

\tcolumn company_count
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: d6a9858d-7d0c-4f2d-bb4f-f4d5b78beec2
\t\tsummarizeBy: sum
\t\tsourceColumn: company_count

\tcolumn executive_share
\t\tdataType: double
\t\tformatString: 0.0 %
\t\tlineageTag: f5a2b1f2-6714-4354-ae6b-31a4e5a5c88e
\t\tsummarizeBy: none
\t\tsourceColumn: executive_share

\tcolumn compliance_share
\t\tdataType: double
\t\tformatString: 0.0 %
\t\tlineageTag: 25b46d05-85ef-4f6d-8f2e-f738652a22f8
\t\tsummarizeBy: none
\t\tsourceColumn: compliance_share

\tcolumn mismatch_share
\t\tdataType: double
\t\tformatString: 0.0 %
\t\tlineageTag: c3bb4b78-d630-4e27-b696-d6746b8f6a1a
\t\tsummarizeBy: none
\t\tsourceColumn: mismatch_share

\tcolumn country_rank
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 6fe1415f-5f35-4126-a82c-7b45bb7d92c6
\t\tsummarizeBy: none
\t\tsourceColumn: country_rank

\tcolumn priority_tier
\t\tdataType: string
\t\tlineageTag: 4fcb72f8-eec9-42c0-8bae-c9d9017b7171
\t\tsummarizeBy: none
\t\tsourceColumn: priority_tier

\tcolumn messaging_angle
\t\tdataType: string
\t\tlineageTag: ee88ba37-d903-4d4c-85be-fb289db1e770
\t\tsummarizeBy: none
\t\tsourceColumn: messaging_angle

\tcolumn strategic_recommendation
\t\tdataType: string
\t\tlineageTag: 7693f432-2f01-46cb-b41d-614bd81890b1
\t\tsummarizeBy: none
\t\tsourceColumn: strategic_recommendation

\tpartition 'Country Priority' = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents(DataRoot & "\\\\dim_country_priority.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
\t\t\t\t        {"company_country", type text},
\t\t\t\t        {"lead_count", Int64.Type},
\t\t\t\t        {"company_count", Int64.Type},
\t\t\t\t        {"executive_share", type number},
\t\t\t\t        {"compliance_share", type number},
\t\t\t\t        {"mismatch_share", type number},
\t\t\t\t        {"country_rank", Int64.Type},
\t\t\t\t        {"priority_tier", type text},
\t\t\t\t        {"messaging_angle", type text},
\t\t\t\t        {"strategic_recommendation", type text}
\t\t\t\t    })
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""

    role_category_table = """table 'Role Category'
\tlineageTag: b0fa54e9-76c0-4b89-aa49-9f15fc22be5f

\tcolumn role_category
\t\tdataType: string
\t\tisKey
\t\tlineageTag: 65aa0dfb-ac85-4b32-a746-cd0cf3bd9f5a
\t\tsummarizeBy: none
\t\tsourceColumn: role_category

\tcolumn lead_count
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: e6fce4dc-c774-47c6-b384-50d9f6c64fe0
\t\tsummarizeBy: sum
\t\tsourceColumn: lead_count

\tcolumn company_count
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 55cb18dc-2e66-49fc-81a5-7db4d573f493
\t\tsummarizeBy: sum
\t\tsourceColumn: company_count

\tcolumn lead_share
\t\tdataType: double
\t\tformatString: 0.0 %
\t\tlineageTag: 32116fcc-2ed0-4e38-9918-1efcdd2705d8
\t\tsummarizeBy: none
\t\tsourceColumn: lead_share

\tpartition 'Role Category' = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents(DataRoot & "\\\\dim_role_category.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
\t\t\t\t        {"role_category", type text},
\t\t\t\t        {"lead_count", Int64.Type},
\t\t\t\t        {"company_count", Int64.Type},
\t\t\t\t        {"lead_share", type number}
\t\t\t\t    })
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""

    company_size_table = """table 'Company Size'
\tlineageTag: 13b64b8b-403b-4c71-81d7-f10fb88d82c9

\tcolumn company_size_segment
\t\tdataType: string
\t\tisKey
\t\tlineageTag: 1a9ef2d1-a415-4b77-b2dc-1a3d78f28fd5
\t\tsummarizeBy: none
\t\tsourceColumn: company_size_segment

\tcolumn lead_count
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 4475cb31-2cac-4afb-bb14-570f3d8f9040
\t\tsummarizeBy: sum
\t\tsourceColumn: lead_count

\tcolumn company_count
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 17329813-5d4c-459f-9589-b25d61fa4f37
\t\tsummarizeBy: sum
\t\tsourceColumn: company_count

\tpartition 'Company Size' = m
\t\tmode: import
\t\tsource =
\t\t\t\tlet
\t\t\t\t    Source = Csv.Document(File.Contents(DataRoot & "\\\\dim_company_size.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
\t\t\t\t    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t\t    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
\t\t\t\t        {"company_size_segment", type text},
\t\t\t\t        {"lead_count", Int64.Type},
\t\t\t\t        {"company_count", Int64.Type}
\t\t\t\t    })
\t\t\t\tin
\t\t\t\t    #"Changed Type"

\tannotation PBI_ResultType = Table
"""

    culture = """culture en-US
"""

    return {
        "database.tmdl": "database Database\n\tcompatibilityLevel: 1601\n\tcompatibilityMode: PowerBI\n",
        "model.tmdl": model,
        "expressions.tmdl": expressions,
        "relationships.tmdl": relationships,
        "cultures/en-US.tmdl": culture,
        "tables/Leads.tmdl": leads_table,
        "tables/Country Priority.tmdl": country_priority_table,
        "tables/Role Category.tmdl": role_category_table,
        "tables/Company Size.tmdl": company_size_table,
        "tables/About.tmdl": about_table,
    }


def build_project() -> None:
    ensure_clean_dir(PBIP_ROOT)

    report_root = PBIP_ROOT / REPORT_NAME
    model_root = PBIP_ROOT / MODEL_NAME

    write_json(
        PBIP_ROOT / ".pbixproj.json",
        {
            "version": "0.14",
            "deployments": {},
        },
    )
    write_json(
        PBIP_ROOT / PBIP_FILE,
        {
            "version": "1.0",
            "artifacts": [{"report": {"path": REPORT_NAME}}],
            "settings": {"enableAutoRecovery": True},
        },
    )

    write_json(report_root / "item.config.json", {"version": "1.0", "logicalId": REPORT_LOGICAL_ID})
    write_json(report_root / "item.metadata.json", {"type": "report", "displayName": "hCaptcha Europe Positioning"})
    write_json(
        report_root / "definition.pbir",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {"byPath": {"path": f"../{MODEL_NAME}"}},
        },
    )
    write_json(report_root / "report.json", report_definition())

    write_json(model_root / ".pbi" / "editorSettings.json", {
        "version": "1.0",
        "showHiddenFields": True,
        "parallelQueryLoading": True,
        "relationshipImportEnabled": True,
        "shouldNotifyUserOfNameConflictResolution": True,
    })
    write_json(model_root / "item.config.json", {"version": "1.0", "logicalId": DATASET_LOGICAL_ID})
    write_json(model_root / "item.metadata.json", {"type": "dataset", "displayName": "hCaptcha Europe Positioning"})
    write_json(model_root / "definition.pbidataset", {"version": "3.0", "settings": {"qnaEnabled": True}})

    for relative_path, content in build_model_files().items():
        write_text(model_root / "definition" / relative_path, content)

    write_text(model_root / "diagramLayout.json", "{\n  \"version\": \"1.0\"\n}")
    write_json(report_root / "StaticResources" / "RegisteredResources" / "hcaptcha_theme.json", report_theme())
    write_text(report_root / "item.config.json", json.dumps({"version": "1.0", "logicalId": REPORT_LOGICAL_ID}, indent=2))
    write_text(report_root / "item.metadata.json", json.dumps({"type": "report", "displayName": "hCaptcha Europe Positioning"}, indent=2))

    for filename in [
        "01_market_overview_top_countries.png",
        "02_icp_role_size_heatmap.png",
        "03_cross_border_signal.png",
    ]:
        src = PROJECT_ROOT / "reports" / "figures" / filename
        dst = report_root / "StaticResources" / "RegisteredResources" / filename
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    write_text(
        PBIP_ROOT / "README.md",
        f"""# hCaptcha Power BI Project

Este projeto foi estruturado em formato `PBIP` para desenvolvimento versionável.

## Como abrir

1. Abra [hcaptcha_report.pbip]({PBIP_FILE}) no Power BI Desktop.
2. Verifique o parâmetro `DataRoot` no Semantic Model.
3. Faça o refresh do modelo.
4. Se quiser o artefato monolítico, use `Save As` no Desktop para gerar um `.pbix`.

## Observações

- O modelo lê os CSVs processados em `data/processed/` via caminho UNC do WSL.
- O relatório usa as figuras geradas no notebook como blueprint visual inicial.
- O dataset já inclui medidas para leads, empresas, países, cross-border share e segmentação por persona e porte.
""",
    )


if __name__ == "__main__":
    build_project()
    print(PBIP_ROOT)
