from pathlib import Path


def test_presentation_app_uses_clear_course_delivery_name():
    app_root = Path("apps/hcaptcha-course-presentation")

    assert app_root.exists()
    assert (app_root / "package.json").exists()
    assert (app_root / "public/hcaptcha-positioning-deck.pdf").exists()
    assert (app_root / "public/data/presentation-snapshot.json").exists()
    assert not (app_root / "public/data/command-center.json").exists()
    assert not Path("sites/data-command-center").exists()


def test_powerbi_project_uses_domain_specific_directory():
    powerbi_root = Path("powerbi/hcaptcha-positioning")

    assert powerbi_root.exists()
    assert (powerbi_root / "hcaptcha_report.pbip").exists()
    assert not Path("dashboards/hcaptcha_report").exists()


def test_documentation_uses_topic_directories():
    assert Path("docs/powerbi/dashboard_blueprint.md").exists()
    assert Path("docs/modeling/semantic_model_notes.md").exists()
    assert not Path("dashboards/power_bi_blueprint.md").exists()
    assert not Path("models/semantic_model_notes.md").exists()
