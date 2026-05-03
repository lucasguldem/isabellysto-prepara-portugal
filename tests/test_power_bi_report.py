from __future__ import annotations

import json
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_hcaptcha_pbip import report_definition  # type: ignore[attr-defined]


NATIVE_VISUAL_TYPES = {
    "card",
    "barChart",
    "columnChart",
    "tableEx",
    "slicer",
}

ALLOWED_PBIR_VISUAL_TYPES = NATIVE_VISUAL_TYPES | {"textbox"}


def _visual_config(visual_container: dict[str, object]) -> dict[str, object]:
    return json.loads(str(visual_container["config"]))


def _single_visuals(report: dict[str, object]) -> list[dict[str, object]]:
    visuals: list[dict[str, object]] = []
    for section in report["sections"]:
        for container in section["visualContainers"]:
            config = _visual_config(container)
            single_visual = config.get("singleVisual")
            if single_visual:
                visuals.append(single_visual)
    return visuals


def test_report_uses_native_power_bi_visuals_instead_of_static_images():
    report = report_definition()
    visual_types = {visual["visualType"] for visual in _single_visuals(report)}

    assert "image" not in visual_types
    assert NATIVE_VISUAL_TYPES <= visual_types


def test_native_visuals_include_data_bindings_for_interactivity():
    report = report_definition()
    data_visuals = [
        visual
        for visual in _single_visuals(report)
        if visual["visualType"] in NATIVE_VISUAL_TYPES
    ]

    assert data_visuals
    for visual in data_visuals:
        assert visual["projections"]
        assert visual["prototypeQuery"]["Select"]


def test_report_no_longer_registers_generated_png_blueprint_resources():
    report = report_definition()
    registered_items = report["resourcePackages"][1]["resourcePackage"]["items"]

    assert all(not item["name"].endswith(".png") for item in registered_items)


def test_report_does_not_mix_pbir_and_legacy_pbir_formats():
    legacy_report = Path("powerbi/hcaptcha-positioning/hcaptcha_report.Report/report.json")

    assert not legacy_report.exists()


def test_active_pbir_definition_uses_native_visuals_without_png_resources():
    report_dir = Path("powerbi/hcaptcha-positioning/hcaptcha_report.Report")
    pbir_report = json.loads((report_dir / "definition" / "report.json").read_text(encoding="utf-8"))
    visual_paths = sorted((report_dir / "definition" / "pages").glob("*/visuals/*/visual.json"))
    visual_types = {
        json.loads(path.read_text(encoding="utf-8"))["visual"]["visualType"]
        for path in visual_paths
    }

    assert "image" not in visual_types
    assert NATIVE_VISUAL_TYPES <= visual_types
    assert all(
        not item["name"].endswith(".png")
        for package in pbir_report["resourcePackages"]
        for item in package["items"]
    )


def test_active_pbir_visuals_use_query_state_not_legacy_visual_properties():
    report_dir = Path("powerbi/hcaptcha-positioning/hcaptcha_report.Report")
    forbidden_visual_properties = {"projections", "prototypeQuery", "hasDefaultSort", "vcObjects"}
    data_visuals = []

    for path in (report_dir / "definition" / "pages").glob("*/visuals/*/visual.json"):
        visual_container = json.loads(path.read_text(encoding="utf-8"))
        visual = visual_container["visual"]
        assert not (forbidden_visual_properties & set(visual))
        if visual["visualType"] in NATIVE_VISUAL_TYPES:
            data_visuals.append(visual)

    assert data_visuals
    for visual in data_visuals:
        assert visual["query"]["queryState"]


def test_active_pbir_visual_types_are_built_in_visuals():
    report_dir = Path("powerbi/hcaptcha-positioning/hcaptcha_report.Report")
    visual_types = {
        json.loads(path.read_text(encoding="utf-8"))["visual"]["visualType"]
        for path in (report_dir / "definition" / "pages").glob("*/visuals/*/visual.json")
    }

    assert visual_types <= ALLOWED_PBIR_VISUAL_TYPES


def test_report_theme_uses_privacy_intelligence_design_system():
    theme = json.loads(
        Path(
            "powerbi/hcaptcha-positioning/hcaptcha_report.Report/StaticResources/RegisteredResources/hcaptcha_theme.json"
        ).read_text(encoding="utf-8")
    )

    assert theme["name"] == "hcaptcha_privacy_intelligence"
    assert theme["background"] == "#F4F1EA"
    assert theme["dataColors"][:4] == ["#0B6B5F", "#D88A28", "#183A59", "#7A5CFF"]
    assert "card" in theme["visualStyles"]
    assert "tableEx" in theme["visualStyles"]


def test_report_pages_use_executive_visual_language():
    report = report_definition()
    section_names = {section["displayName"] for section in report["sections"]}
    text_values = []
    for visual in _single_visuals(report):
        if visual["visualType"] != "textbox":
            continue
        for general_object in visual.get("objects", {}).get("general", []):
            for paragraph in general_object["properties"].get("paragraphs", []):
                for run in paragraph.get("textRuns", []):
                    text_values.append(run["value"])

    assert section_names == {
        "Market Command",
        "Buyer Intelligence",
        "Border Signal",
        "Action Map",
    }
    assert any("PRIVACY INTELLIGENCE" in value for value in text_values)
    assert any("command center" in value.lower() for value in text_values)


def test_tables_are_presentation_ledgers_without_horizontal_scroll_pressure():
    report = report_definition()
    table_visuals = []
    table_containers = []
    for section in report["sections"]:
        for container in section["visualContainers"]:
            config = _visual_config(container)
            visual = config["singleVisual"]
            if visual["visualType"] == "tableEx":
                table_visuals.append(visual)
                table_containers.append(container)

    assert table_visuals
    for visual, container in zip(table_visuals, table_containers, strict=True):
        assert len(visual["projections"]["Values"]) <= 5
        assert container["width"] <= 560


def test_charts_are_sorted_by_business_signal_for_presentation():
    report_dir = Path("powerbi/hcaptcha-positioning/hcaptcha_report.Report")
    chart_paths = [
        path
        for path in (report_dir / "definition" / "pages").glob("*/visuals/*/visual.json")
        if json.loads(path.read_text(encoding="utf-8"))["visual"]["visualType"] in {"barChart", "columnChart"}
    ]

    assert chart_paths
    for path in chart_paths:
        visual = json.loads(path.read_text(encoding="utf-8"))["visual"]
        assert "sortDefinition" in visual["query"]


def test_presentation_visuals_do_not_expose_source_column_names():
    report = report_definition()
    forbidden_fragments = {
        "company_country",
        "role_category",
        "company_size_segment",
        "contact_company_country_mismatch",
        "country_rank",
        "priority_tier",
        "lead_count",
        "company_count",
    }
    query_refs = []

    for visual in _single_visuals(report):
        for projections in visual.get("projections", {}).values():
            for projection in projections:
                query_refs.append(projection["queryRef"])

    assert query_refs
    assert not any(
        fragment in query_ref
        for query_ref in query_refs
        for fragment in forbidden_fragments
    )


def test_semantic_model_uses_windows_gateway_mirror_as_desktop_data_root():
    expressions = Path(
        "powerbi/hcaptcha-positioning/hcaptcha_report.SemanticModel/definition/expressions.tmdl"
    ).read_text(encoding="utf-8")

    assert "C:\\Users\\02luc\\Documents\\PowerBIData\\hcaptcha\\processed" in expressions


def test_primary_interactive_visuals_are_bound_to_fact_table_measures():
    report = report_definition()
    visuals_by_name = {}
    for section in report["sections"]:
        for container in section["visualContainers"]:
            config = _visual_config(container)
            visuals_by_name[config["name"]] = config["singleVisual"]

    primary_visuals = [
        "overview-country-slicer",
        "overview-country-bars",
        "overview-country-table",
        "icp-role-bars",
        "icp-size-columns",
        "icp-role-table",
        "cross-mismatch-slicer",
        "cross-mismatch-bars",
        "cross-country-table",
    ]

    for visual_name in primary_visuals:
        from_entities = {
            source["Entity"]
            for source in visuals_by_name[visual_name]["prototypeQuery"]["From"]
        }
        assert from_entities == {"Leads"}
