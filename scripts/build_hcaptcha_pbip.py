from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PBIP_ROOT = PROJECT_ROOT / "powerbi" / "hcaptcha-positioning"
REPORT_NAME = "hcaptcha_report.Report"
MODEL_NAME = "hcaptcha_report.SemanticModel"
PBIP_FILE = "hcaptcha_report.pbip"
PIPELINE_SETTINGS = PROJECT_ROOT / "config" / "pipeline_settings.json"

DATASET_LOGICAL_ID = "7d1a61c8-d30e-43c9-a4d4-5f3ee0a7d8d1"
REPORT_LOGICAL_ID = "ef4b92bc-3d0f-4e9e-bf50-bde2dd3f2f8d"


def wsl_unc_path(path: Path) -> str:
    distro = os.environ.get("WSL_DISTRO_NAME", "Ubuntu-24.04")
    return "\\\\wsl.localhost\\{}\\{}".format(distro, str(path).lstrip("/").replace("/", "\\"))


def desktop_data_root() -> str:
    if PIPELINE_SETTINGS.exists():
        settings = json.loads(PIPELINE_SETTINGS.read_text(encoding="utf-8"))
        gateway_mirror = settings.get("directories", {}).get("gateway_mirror")
        if gateway_mirror:
            return str(gateway_mirror).replace("/mnt/c/", "C:/").replace("/", "\\")
    return wsl_unc_path(PROJECT_ROOT / "data" / "processed")


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
        "fontFamily": "Aptos",
        "fontSize": font_size,
        "color": color,
    }
    if bold:
        style["fontWeight"] = "bold"
        style["fontFamily"] = "Aptos Display"
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


def _string_literal(value: str) -> dict:
    return {"expr": {"Literal": {"Value": f"'{value}'"}}}


def visual_title_objects(title: str) -> dict:
    return {
        "title": [
            {
                "properties": {
                    "titleText": _string_literal(title),
                    "fontFamily": _string_literal("Aptos Display"),
                    "fontColor": {"solid": {"color": "#183A59"}},
                    "alignment": _string_literal("left"),
                }
            }
        ],
    }


def _source_ref(source: str) -> dict:
    return {"SourceRef": {"Source": source}}


def column_select(source: str, table: str, column: str, native_name: str | None = None) -> dict:
    return {
        "Column": {
            "Expression": _source_ref(source),
            "Property": column,
        },
        "Name": f"{table}.{column}",
        "NativeReferenceName": native_name or column,
    }


def measure_select(source: str, table: str, measure: str, native_name: str | None = None) -> dict:
    return {
        "Measure": {
            "Expression": _source_ref(source),
            "Property": measure,
        },
        "Name": f"{table}.{measure}",
        "NativeReferenceName": native_name or measure,
    }


def sum_select(source: str, table: str, column: str, native_name: str | None = None) -> dict:
    return {
        "Aggregation": {
            "Expression": {
                "Column": {
                    "Expression": _source_ref(source),
                    "Property": column,
                }
            },
            "Function": 0,
        },
        "Name": f"Sum({table}.{column})",
        "NativeReferenceName": native_name or f"Sum of {column}",
    }


def native_visual(
    name: str,
    visual_type: str,
    x: float,
    y: float,
    width: float,
    height: float,
    z: float,
    title: str,
    from_tables: list[dict],
    selects: list[dict],
    projections: dict[str, list[dict]],
    objects: dict | None = None,
) -> dict:
    pbir_visual_type = {
        "clusteredBarChart": "barChart",
        "stackedBarChart": "barChart",
        "clusteredColumnChart": "columnChart",
    }.get(visual_type, visual_type)
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
            "visualType": pbir_visual_type,
            "projections": projections,
            "prototypeQuery": {
                "Version": 2,
                "From": from_tables,
                "Select": selects,
            },
            "drillFilterOtherVisuals": True,
            "hasDefaultSort": True,
            "objects": objects or visual_title_objects(title),
            "vcObjects": {
                "title": [
                    {
                        "properties": {
                            "text": _string_literal(title),
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


def pbir_report_definition() -> dict:
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.1.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "CY23SU04",
                "reportVersionAtImport": {
                    "visual": "2.5.0",
                    "report": "3.1.0",
                    "page": "2.3.0",
                },
                "type": "SharedResources",
            },
            "customTheme": {
                "name": "hcaptcha_theme.json",
                "reportVersionAtImport": {
                    "visual": "2.5.0",
                    "report": "3.1.0",
                    "page": "2.3.0",
                },
                "type": "RegisteredResources",
            },
        },
        "resourcePackages": [
            {
                "name": "SharedResources",
                "type": "SharedResources",
                "items": [
                    {
                        "name": "CY23SU04",
                        "path": "BaseThemes/CY23SU04.json",
                        "type": "BaseTheme",
                    }
                ],
            },
            {
                "name": "RegisteredResources",
                "type": "RegisteredResources",
                "items": [
                    {
                        "name": "hcaptcha_theme.json",
                        "path": "hcaptcha_theme.json",
                        "type": "CustomTheme",
                    }
                ],
            },
        ],
    }


def pbir_pages_metadata(sections: list[dict]) -> dict:
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [section["name"] for section in sections],
        "activePageName": sections[0]["name"],
    }


def pbir_page_definition(section: dict) -> dict:
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
        "name": section["name"],
        "displayName": section["displayName"],
        "displayOption": "FitToPage",
        "height": int(section["height"]),
        "width": int(section["width"]),
    }


def _source_refs_use_entities(payload: dict | list | object, aliases: dict[str, str]) -> object:
    if isinstance(payload, dict):
        if "SourceRef" in payload and "Source" in payload["SourceRef"]:
            source = payload["SourceRef"]["Source"]
            return {"SourceRef": {"Entity": aliases[source]}}
        return {
            key: _source_refs_use_entities(value, aliases)
            for key, value in payload.items()
        }
    if isinstance(payload, list):
        return [_source_refs_use_entities(item, aliases) for item in payload]
    return payload


def _field_from_select(select: dict, aliases: dict[str, str]) -> dict:
    for expression_type in ("Column", "Measure", "Aggregation"):
        if expression_type in select:
            return {
                expression_type: _source_refs_use_entities(
                    select[expression_type],
                    aliases,
                )
            }
    raise ValueError(f"Unsupported select expression: {select}")


def _pbir_query_from_legacy_visual(single_visual: dict) -> dict:
    prototype_query = single_visual["prototypeQuery"]
    aliases = {
        source["Name"]: source["Entity"]
        for source in prototype_query["From"]
    }
    fields_by_query_ref = {
        select["Name"]: _field_from_select(select, aliases)
        for select in prototype_query["Select"]
    }

    query_state = {}
    for role, role_projections in single_visual["projections"].items():
        query_state[role] = {
            "projections": [
                {
                    **({"active": projection["active"]} if "active" in projection else {}),
                    "field": fields_by_query_ref[projection["queryRef"]],
                    "queryRef": projection["queryRef"],
                }
                for projection in role_projections
            ]
        }

    query = {"queryState": query_state}
    sort_projection = next(
        (
            projection
            for role in ("Y", "Values")
            for projection in single_visual["projections"].get(role, [])
            if projection["queryRef"] in fields_by_query_ref
        ),
        None,
    )
    if sort_projection and "Y" in single_visual["projections"]:
        query["sortDefinition"] = {
            "sort": [
                {
                    "field": fields_by_query_ref[sort_projection["queryRef"]],
                    "direction": "Descending",
                }
            ]
        }

    return query


def pbir_visual_definition(visual_container: dict) -> dict:
    config = json.loads(visual_container["config"])
    position = config["layouts"][0]["position"]
    single_visual = config["singleVisual"]
    visual = {
        "visualType": single_visual["visualType"],
    }
    if "projections" in single_visual and "prototypeQuery" in single_visual:
        visual["query"] = _pbir_query_from_legacy_visual(single_visual)
    if single_visual.get("drillFilterOtherVisuals"):
        visual["drillFilterOtherVisuals"] = single_visual["drillFilterOtherVisuals"]
    if single_visual.get("objects"):
        visual["objects"] = single_visual["objects"]

    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json",
        "name": config["name"],
        "position": {
            "x": position["x"],
            "y": position["y"],
            "z": position["z"],
            "height": position["height"],
            "width": position["width"],
            "tabOrder": position["tabOrder"],
        },
        "visual": visual,
    }


def report_theme() -> dict:
    return {
        "name": "hcaptcha_privacy_intelligence",
        "dataColors": ["#0B6B5F", "#D88A28", "#183A59", "#7A5CFF", "#8A9474", "#C25132", "#2D6E8E"],
        "background": "#F4F1EA",
        "foreground": "#17212B",
        "tableAccent": "#0B6B5F",
        "visualStyles": {
            "*": {
                "*": {
                    "title": [
                        {
                            "show": True,
                            "fontFamily": "Aptos Display",
                            "fontSize": 12,
                            "color": {"solid": {"color": "#183A59"}},
                        }
                    ],
                    "background": [
                        {
                            "show": True,
                            "color": {"solid": {"color": "#FFFCF7"}},
                            "transparency": 0,
                        }
                    ],
                    "border": [
                        {
                            "show": True,
                            "color": {"solid": {"color": "#D7CDBD"}},
                        }
                    ],
                    "visualHeader": [
                        {
                            "show": False,
                        }
                    ],
                }
            },
            "card": {
                "*": {
                    "title": [
                        {
                            "show": True,
                            "fontFamily": "Aptos",
                            "fontSize": 10,
                            "color": {"solid": {"color": "#5D6B72"}},
                        }
                    ],
                    "labels": [
                        {
                            "fontFamily": "Aptos Display",
                            "fontSize": 30,
                            "color": {"solid": {"color": "#0B3B3C"}},
                        }
                    ],
                }
            },
            "barChart": {
                "*": {
                    "categoryAxis": [
                        {
                            "show": True,
                            "fontFamily": "Aptos",
                            "fontSize": 10,
                            "color": {"solid": {"color": "#3D4C56"}},
                        }
                    ],
                    "valueAxis": [
                        {
                            "show": True,
                            "fontFamily": "Aptos",
                            "fontSize": 10,
                            "color": {"solid": {"color": "#3D4C56"}},
                            "gridlineShow": True,
                            "gridlineColor": {"solid": {"color": "#E3D8C8"}},
                        }
                    ],
                    "dataLabels": [
                        {
                            "show": True,
                            "fontFamily": "Aptos Display",
                            "fontSize": 10,
                            "color": {"solid": {"color": "#17212B"}},
                        }
                    ],
                    "legend": [
                        {
                            "show": True,
                            "position": "Top",
                            "fontFamily": "Aptos",
                            "fontSize": 10,
                            "labelColor": {"solid": {"color": "#3D4C56"}},
                        }
                    ],
                }
            },
            "columnChart": {
                "*": {
                    "categoryAxis": [
                        {
                            "show": True,
                            "fontFamily": "Aptos",
                            "fontSize": 10,
                            "color": {"solid": {"color": "#3D4C56"}},
                        }
                    ],
                    "valueAxis": [
                        {
                            "show": True,
                            "fontFamily": "Aptos",
                            "fontSize": 10,
                            "color": {"solid": {"color": "#3D4C56"}},
                            "gridlineShow": True,
                            "gridlineColor": {"solid": {"color": "#E3D8C8"}},
                        }
                    ],
                    "dataLabels": [
                        {
                            "show": True,
                            "fontFamily": "Aptos Display",
                            "fontSize": 10,
                            "color": {"solid": {"color": "#17212B"}},
                        }
                    ],
                }
            },
            "tableEx": {
                "*": {
                    "columnHeaders": [
                        {
                            "fontFamily": "Aptos Display",
                            "fontSize": 11,
                            "fontColor": {"solid": {"color": "#183A59"}},
                            "backColor": {"solid": {"color": "#EDE4D5"}},
                            "outline": "None",
                            "wordWrap": True,
                        }
                    ],
                    "values": [
                        {
                            "fontFamily": "Aptos",
                            "fontSize": 10,
                            "fontColor": {"solid": {"color": "#17212B"}},
                            "backColorPrimary": {"solid": {"color": "#FFFCF7"}},
                            "backColorSecondary": {"solid": {"color": "#F6EFE3"}},
                            "outline": "None",
                            "wordWrap": True,
                        }
                    ],
                    "grid": [
                        {
                            "gridVertical": False,
                            "gridHorizontal": True,
                            "gridHorizontalColor": {"solid": {"color": "#E3D8C8"}},
                            "outlineColor": {"solid": {"color": "#D7CDBD"}},
                            "rowPadding": 8,
                        }
                    ],
                }
            }
        },
    }


def report_definition() -> dict:
    leads_from = [{"Name": "l", "Entity": "Leads", "Type": 0}]
    country_from = [{"Name": "cp", "Entity": "Country Priority", "Type": 0}]

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
            "Market Command",
            0,
            [
                textbox_visual(
                    "overview-title",
                    42,
                    18,
                    1040,
                    72,
                    [
                        [("PRIVACY INTELLIGENCE // Europe GTM command center", text_style("11pt", "#0B6B5F", bold=True))],
                        [("Onde privacidade vira vantagem comercial", text_style("25pt", "#17212B", bold=True))],
                    ],
                    1000,
                ),
                textbox_visual(
                    "overview-subtitle",
                    42,
                    96,
                    860,
                    58,
                    [
                        [("Leitura executiva dos mercados europeus com maior densidade para uma narrativa privacy-first, GDPR-safe e orientada a eficiência técnica.", text_style("12pt", "#3D4C56"))],
                    ],
                    900,
                ),
                native_visual(
                    "overview-country-slicer",
                    "slicer",
                    980,
                    38,
                    220,
                    100,
                    870,
                    "Country lens",
                    leads_from,
                    [column_select("l", "Leads", "Country")],
                    {"Values": [{"queryRef": "Leads.Country"}]},
                ),
                native_visual(
                    "overview-leads-card",
                    "card",
                    42,
                    175,
                    235,
                    110,
                    850,
                    "Eligible leads",
                    leads_from,
                    [measure_select("l", "Leads", "Leads")],
                    {"Values": [{"queryRef": "Leads.Leads"}]},
                ),
                native_visual(
                    "overview-companies-card",
                    "card",
                    297,
                    175,
                    235,
                    110,
                    840,
                    "Unique accounts",
                    leads_from,
                    [measure_select("l", "Leads", "Companies")],
                    {"Values": [{"queryRef": "Leads.Companies"}]},
                ),
                native_visual(
                    "overview-countries-card",
                    "card",
                    552,
                    175,
                    235,
                    110,
                    830,
                    "Markets in scope",
                    leads_from,
                    [measure_select("l", "Leads", "Countries In Scope")],
                    {"Values": [{"queryRef": "Leads.Countries In Scope"}]},
                ),
                native_visual(
                    "overview-country-bars",
                    "clusteredBarChart",
                    42,
                    320,
                    720,
                    330,
                    800,
                    "Market gravity by company country",
                    leads_from,
                    [
                        column_select("l", "Leads", "Country"),
                        measure_select("l", "Leads", "Leads"),
                    ],
                    {
                        "Category": [{"queryRef": "Leads.Country", "active": True}],
                        "Y": [{"queryRef": "Leads.Leads"}],
                    },
                ),
                native_visual(
                    "overview-country-table",
                    "tableEx",
                    790,
                    175,
                    430,
                    255,
                    790,
                    "Executive market pulse",
                    leads_from,
                    [
                        column_select("l", "Leads", "Country"),
                        measure_select("l", "Leads", "Leads"),
                        measure_select("l", "Leads", "Companies"),
                        measure_select("l", "Leads", "Cross-Border Share"),
                        measure_select("l", "Leads", "Executive Leads"),
                    ],
                    {
                        "Values": [
                            {"queryRef": "Leads.Country"},
                            {"queryRef": "Leads.Leads"},
                            {"queryRef": "Leads.Companies"},
                            {"queryRef": "Leads.Cross-Border Share"},
                            {"queryRef": "Leads.Executive Leads"},
                        ]
                    },
                ),
                textbox_visual(
                    "overview-market-narrative",
                    790,
                    455,
                    430,
                    195,
                    [
                        [("Reading cue", text_style("11pt", "#0B6B5F", bold=True))],
                        [("Germany, France and United Kingdom form the commercial gravity core; use country selection to pressure-test every page live.", text_style("15pt", "#17212B", bold=True))],
                        [("The compact ledger keeps the page scannable while the chart carries the comparison.", text_style("11pt", "#5D6B72"))],
                    ],
                    780,
                ),
            ],
        ),
        make_section(
            "ReportSectionICP",
            "Buyer Intelligence",
            1,
            [
                textbox_visual(
                    "icp-title",
                    42,
                    18,
                    920,
                    72,
                    [
                        [("BUYER INTELLIGENCE // Persona and company-size lens", text_style("11pt", "#D88A28", bold=True))],
                        [("Quem compra, quem influencia e como adaptar a mensagem", text_style("25pt", "#17212B", bold=True))],
                    ],
                    1000,
                ),
                textbox_visual(
                    "icp-subtitle",
                    42,
                    96,
                    820,
                    48,
                    [[("A oportunidade se concentra em decisores técnicos e compradores de compliance; a venda precisa alternar entre soberania, segurança e baixa fricção.", text_style("12pt", "#3D4C56"))]],
                    900,
                ),
                native_visual(
                    "icp-size-slicer",
                    "slicer",
                    905,
                    38,
                    275,
                    100,
                    870,
                    "Company-size lens",
                    leads_from,
                    [column_select("l", "Leads", "Segment", "Company Size")],
                    {"Values": [{"queryRef": "Leads.Segment"}]},
                ),
                native_visual(
                    "icp-role-bars",
                    "clusteredBarChart",
                    42,
                    170,
                    560,
                    240,
                    820,
                    "Persona concentration",
                    leads_from,
                    [
                        column_select("l", "Leads", "Role", "Role Category"),
                        measure_select("l", "Leads", "Leads"),
                    ],
                    {
                        "Category": [{"queryRef": "Leads.Role", "active": True}],
                        "Y": [{"queryRef": "Leads.Leads"}],
                    },
                ),
                native_visual(
                    "icp-size-columns",
                    "clusteredColumnChart",
                    640,
                    170,
                    540,
                    240,
                    810,
                    "Company-size momentum",
                    leads_from,
                    [
                        column_select("l", "Leads", "Segment", "Company Size"),
                        measure_select("l", "Leads", "Leads"),
                    ],
                    {
                        "Category": [{"queryRef": "Leads.Segment", "active": True}],
                        "Y": [{"queryRef": "Leads.Leads"}],
                    },
                ),
                native_visual(
                    "icp-role-size-stacked",
                    "stackedBarChart",
                    42,
                    445,
                    760,
                    220,
                    800,
                    "Persona by company segment",
                    leads_from,
                    [
                        column_select("l", "Leads", "Role", "Role Category"),
                        column_select("l", "Leads", "Segment", "Company Size"),
                        measure_select("l", "Leads", "Leads"),
                    ],
                    {
                        "Category": [{"queryRef": "Leads.Role", "active": True}],
                        "Series": [{"queryRef": "Leads.Segment"}],
                        "Y": [{"queryRef": "Leads.Leads"}],
                    },
                ),
                native_visual(
                    "icp-role-table",
                    "tableEx",
                    840,
                    445,
                    380,
                    220,
                    790,
                    "Buyer segment detail",
                    leads_from,
                    [
                        column_select("l", "Leads", "Role", "Role Category"),
                        measure_select("l", "Leads", "Leads"),
                        measure_select("l", "Leads", "Companies"),
                    ],
                    {
                        "Values": [
                            {"queryRef": "Leads.Role"},
                            {"queryRef": "Leads.Leads"},
                            {"queryRef": "Leads.Companies"},
                        ]
                    },
                ),
            ],
        ),
        make_section(
            "ReportSectionCrossBorder",
            "Border Signal",
            2,
            [
                textbox_visual(
                    "cross-title",
                    42,
                    18,
                    920,
                    72,
                    [
                        [("BORDER SIGNAL // Distributed-operation detector", text_style("11pt", "#7A5CFF", bold=True))],
                        [("Onde operações transnacionais elevam o valor da segurança de borda", text_style("25pt", "#17212B", bold=True))],
                    ],
                    1000,
                ),
                textbox_visual(
                    "cross-subtitle",
                    42,
                    96,
                    840,
                    48,
                    [[("A divergência entre país do contato e país da empresa indica contas com presença distribuída, maior sensibilidade regulatória e necessidade de proteção consistente entre regiões.", text_style("12pt", "#3D4C56"))]],
                    900,
                ),
                native_visual(
                    "cross-share-card",
                    "card",
                    42,
                    170,
                    260,
                    110,
                    840,
                    "Cross-border share",
                    leads_from,
                    [measure_select("l", "Leads", "Cross-Border Share")],
                    {"Values": [{"queryRef": "Leads.Cross-Border Share"}]},
                ),
                native_visual(
                    "cross-contacts-card",
                    "card",
                    322,
                    170,
                    260,
                    110,
                    830,
                    "Cross-border contacts",
                    leads_from,
                    [measure_select("l", "Leads", "Cross-Border Contacts")],
                    {"Values": [{"queryRef": "Leads.Cross-Border Contacts"}]},
                ),
                native_visual(
                    "cross-mismatch-slicer",
                    "slicer",
                    980,
                    38,
                    220,
                    100,
                    820,
                    "Mismatch lens",
                    leads_from,
                    [column_select("l", "Leads", "Mismatch")],
                    {"Values": [{"queryRef": "Leads.Mismatch"}]},
                ),
                native_visual(
                    "cross-mismatch-bars",
                    "clusteredBarChart",
                    42,
                    315,
                    725,
                    335,
                    800,
                    "Distributed-operation signal by market",
                    leads_from,
                    [
                        column_select("l", "Leads", "Country"),
                        measure_select("l", "Leads", "Cross-Border Share"),
                    ],
                    {
                        "Category": [{"queryRef": "Leads.Country", "active": True}],
                        "Y": [{"queryRef": "Leads.Cross-Border Share"}],
                    },
                ),
                native_visual(
                    "cross-country-table",
                    "tableEx",
                    795,
                    170,
                    425,
                    250,
                    790,
                    "Market signal ledger",
                    leads_from,
                    [
                        column_select("l", "Leads", "Country"),
                        measure_select("l", "Leads", "Leads"),
                        measure_select("l", "Leads", "Cross-Border Contacts"),
                        measure_select("l", "Leads", "Cross-Border Share"),
                    ],
                    {
                        "Values": [
                            {"queryRef": "Leads.Country"},
                            {"queryRef": "Leads.Leads"},
                            {"queryRef": "Leads.Cross-Border Contacts"},
                            {"queryRef": "Leads.Cross-Border Share"},
                        ]
                    },
                ),
                textbox_visual(
                    "cross-border-narrative",
                    795,
                    445,
                    425,
                    205,
                    [
                        [("Interpretation", text_style("11pt", "#7A5CFF", bold=True))],
                        [("High mismatch share is not noise: it points to distributed teams, border-sensitive data flows and stronger need for consistent bot-defense policy.", text_style("14pt", "#17212B", bold=True))],
                        [("Use the mismatch slicer to isolate pure cross-border accounts during the presentation.", text_style("11pt", "#5D6B72"))],
                    ],
                    780,
                ),
            ],
        ),
        make_section(
            "ReportSectionNextAction",
            "Action Map",
            3,
            [
                textbox_visual(
                    "next-title",
                    42,
                    18,
                    980,
                    72,
                    [
                        [("ACTION MAP // From insight to commercial motion", text_style("11pt", "#0B6B5F", bold=True))],
                        [("Sequência recomendada para ativar o mercado europeu", text_style("25pt", "#17212B", bold=True))],
                    ],
                    1000,
                ),
                textbox_visual(
                    "next-subtitle",
                    42,
                    96,
                    960,
                    42,
                    [[("Use esta página como slide final: priorização de mercado, narrativa recomendada e cadência de expansão para transformar a análise em plano comercial.", text_style("12pt", "#3D4C56"))]],
                    900,
                ),
                native_visual(
                    "next-action-table",
                    "tableEx",
                    42,
                    165,
                    540,
                    500,
                    880,
                    "Prioritized go-to-market ledger",
                    country_from,
                    [
                        column_select("cp", "Country Priority", "Rank"),
                        column_select("cp", "Country Priority", "Country"),
                        column_select("cp", "Country Priority", "Tier"),
                        column_select("cp", "Country Priority", "Leads"),
                        column_select("cp", "Country Priority", "Companies"),
                    ],
                    {
                        "Values": [
                            {"queryRef": "Country Priority.Rank"},
                            {"queryRef": "Country Priority.Country"},
                            {"queryRef": "Country Priority.Tier"},
                            {"queryRef": "Country Priority.Leads"},
                            {"queryRef": "Country Priority.Companies"},
                        ]
                    },
                ),
                native_visual(
                    "next-tier-bars",
                    "clusteredColumnChart",
                    630,
                    165,
                    570,
                    215,
                    820,
                    "Lead density by priority tier",
                    country_from,
                    [
                        column_select("cp", "Country Priority", "Tier"),
                        sum_select("cp", "Country Priority", "Leads"),
                    ],
                    {
                        "Category": [{"queryRef": "Country Priority.Tier", "active": True}],
                        "Y": [{"queryRef": "Sum(Country Priority.Leads)"}],
                    },
                ),
                textbox_visual(
                    "next-body",
                    630,
                    410,
                    600,
                    255,
                    [
                        [("Commercial motion", text_style("11pt", "#0B6B5F", bold=True))],
                        [("1. ABM privacy-first em Germany e France para enterprise.", text_style("14pt", "#17212B", bold=True))],
                        [("2. United Kingdom com narrativa performance + UX.", text_style("14pt", "#17212B", bold=True))],
                        [("3. Spain e Portugal como expansão híbrida: compliance + escala.", text_style("14pt", "#17212B", bold=True))],
                        [("4. Tier 2 digital-first para Ireland, Lithuania e Estonia.", text_style("14pt", "#17212B", bold=True))],
                        [("A tabela fica curta de propósito: a recomendação vira discurso, não scroll horizontal.", text_style("11pt", "#5D6B72"))],
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
    data_root = desktop_data_root()

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
\tfromColumn: Leads.Country
\ttoColumn: 'Country Priority'.Country

relationship 8896ce94-fdb4-4647-8e7f-36ec1ea275f1
\tfromColumn: Leads.Role
\ttoColumn: 'Role Category'.Role

relationship 62f74127-79ad-4df4-9c84-9041637dd349
\tfromColumn: Leads.Segment
\ttoColumn: 'Company Size'.Segment
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
\t\t\t\t        {"Source", "DataRoot Windows mirror synced from data/processed/*.csv"},
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

\tmeasure 'Countries In Scope' = DISTINCTCOUNT('Leads'[Country])
\t\tformatString: #,##0
\t\tlineageTag: 4a08ce9f-2507-4ac6-9b26-f4908e71474c

\tmeasure 'Cross-Border Contacts' = CALCULATE([Leads], 'Leads'[Mismatch] = TRUE())
\t\tformatString: #,##0
\t\tlineageTag: f0f40b58-34a0-4167-b468-7c06db5e9a44

\tmeasure 'Cross-Border Share' = DIVIDE([Cross-Border Contacts], [Leads])
\t\tformatString: 0.0 %
\t\tlineageTag: bb2a6e8f-0dab-49eb-b1c3-2eff83d5242b

\tmeasure 'Executive Leads' = CALCULATE([Leads], 'Leads'[Role] = "Executive / Technical Decision Maker")
\t\tformatString: #,##0
\t\tlineageTag: 427ef40c-cffd-47d4-9d7a-0cc4791543e1

\tmeasure 'Compliance Leads' = CALCULATE([Leads], 'Leads'[Role] = "Data / Compliance")
\t\tformatString: #,##0
\t\tlineageTag: 3733ec84-4f7c-4b58-b7d7-e5287ffdd4f1

\tmeasure 'Enterprise Leads' = CALCULATE([Leads], 'Leads'[Segment] = "3. Enterprise")
\t\tformatString: #,##0
\t\tlineageTag: aeeaa46b-8b73-4d52-85c5-9c95e4bfbeb6

\tmeasure 'Mid-Market Leads' = CALCULATE([Leads], 'Leads'[Segment] = "2. Mid-Market")
\t\tformatString: #,##0
\t\tlineageTag: 66a5774a-bfb7-4667-b660-8d938efdbafd

\tmeasure 'Startup / SMB Leads' = CALCULATE([Leads], 'Leads'[Segment] = "1. Startup / SMB")
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

\tcolumn Country
\t\tdataType: string
\t\tlineageTag: 89d8602e-fdcc-48df-9672-5b987467a7b2
\t\tsummarizeBy: none
\t\tsourceColumn: company_country

\tcolumn company_industry
\t\tdataType: string
\t\tlineageTag: 8753ac98-c459-4e95-a4ea-6ecdb5d7c68c
\t\tsummarizeBy: none
\t\tsourceColumn: company_industry

\tcolumn Role
\t\tdataType: string
\t\tlineageTag: 8d21eb17-5adf-4c95-9a0d-f717b31b1a72
\t\tsummarizeBy: none
\t\tsourceColumn: role_category

\tcolumn Segment
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

\tcolumn Mismatch
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

\tcolumn Country
\t\tdataType: string
\t\tisKey
\t\tlineageTag: 5ec4699c-2a31-4cd6-ad19-8774fcac2af8
\t\tsummarizeBy: none
\t\tsourceColumn: company_country

\tcolumn Leads
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 2cf0ec0a-2a46-4f2b-9471-21e385eae5e0
\t\tsummarizeBy: sum
\t\tsourceColumn: lead_count

\tcolumn Companies
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

\tcolumn Rank
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 6fe1415f-5f35-4126-a82c-7b45bb7d92c6
\t\tsummarizeBy: none
\t\tsourceColumn: country_rank

\tcolumn Tier
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

\tcolumn Role
\t\tdataType: string
\t\tisKey
\t\tlineageTag: 65aa0dfb-ac85-4b32-a746-cd0cf3bd9f5a
\t\tsummarizeBy: none
\t\tsourceColumn: role_category

\tcolumn Leads
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: e6fce4dc-c774-47c6-b384-50d9f6c64fe0
\t\tsummarizeBy: sum
\t\tsourceColumn: lead_count

\tcolumn Companies
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

\tcolumn Segment
\t\tdataType: string
\t\tisKey
\t\tlineageTag: 1a9ef2d1-a415-4b77-b2dc-1a3d78f28fd5
\t\tsummarizeBy: none
\t\tsourceColumn: company_size_segment

\tcolumn Leads
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: 4475cb31-2cac-4afb-bb14-570f3d8f9040
\t\tsummarizeBy: sum
\t\tsourceColumn: lead_count

\tcolumn Companies
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
    data_root = desktop_data_root()
    ensure_clean_dir(PBIP_ROOT)

    report_root = PBIP_ROOT / REPORT_NAME
    model_root = PBIP_ROOT / MODEL_NAME
    report = report_definition()
    sections = report["sections"]

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

    write_json(
        report_root / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {"type": "Report", "displayName": "hCaptcha Europe Positioning"},
            "config": {"version": "2.0", "logicalId": REPORT_LOGICAL_ID},
        },
    )
    write_json(
        report_root / "definition.pbir",
        {
            "version": "4.0",
            "datasetReference": {"byPath": {"path": f"../{MODEL_NAME}"}},
        },
    )
    write_json(report_root / "definition" / "report.json", pbir_report_definition())
    write_json(
        report_root / "definition" / "version.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
            "version": "2.0.0",
        },
    )
    write_json(report_root / "definition" / "pages" / "pages.json", pbir_pages_metadata(sections))
    for section in sections:
        page_root = report_root / "definition" / "pages" / section["name"]
        write_json(page_root / "page.json", pbir_page_definition(section))
        for visual_container in section["visualContainers"]:
            visual = pbir_visual_definition(visual_container)
            write_json(page_root / "visuals" / visual["name"] / "visual.json", visual)

    write_json(model_root / ".pbi" / "editorSettings.json", {
        "version": "1.0",
        "showHiddenFields": True,
        "parallelQueryLoading": True,
        "relationshipImportEnabled": True,
        "shouldNotifyUserOfNameConflictResolution": True,
    })
    write_json(
        model_root / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {"type": "SemanticModel", "displayName": "hCaptcha Europe Positioning"},
            "config": {"version": "2.0", "logicalId": DATASET_LOGICAL_ID},
        },
    )
    write_json(model_root / "definition.pbism", {"version": "4.2", "settings": {"qnaEnabled": True}})

    for relative_path, content in build_model_files().items():
        write_text(model_root / "definition" / relative_path, content)

    write_text(model_root / "diagramLayout.json", "{\n  \"version\": \"1.0\"\n}")
    write_json(report_root / "StaticResources" / "RegisteredResources" / "hcaptcha_theme.json", report_theme())

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

- O modelo lê os CSVs processados pelo parâmetro `DataRoot`, apontando para `{data_root}`.
- Esse diretório Windows é sincronizado a partir de `data/processed/` por `scripts/export_gateway_ready.py`.
- O relatório usa visuais nativos do Power BI para cards, barras, tabelas e filtros interativos.
- O dataset já inclui medidas para leads, empresas, países, cross-border share e segmentação por persona e porte.
""",
    )


if __name__ == "__main__":
    build_project()
    print(PBIP_ROOT)
