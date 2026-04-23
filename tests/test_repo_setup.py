from pathlib import Path


def test_repository_ignores_sensitive_and_generated_artifacts():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    assert "data/raw/*" in gitignore
    assert "data/processed/*" in gitignore
    assert "*.pbix" in gitignore
    assert "tools/" in gitignore
