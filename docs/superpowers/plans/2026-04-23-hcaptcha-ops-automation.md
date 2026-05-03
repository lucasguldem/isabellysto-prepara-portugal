# hCaptcha Operations Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a clean public repository for the current hCaptcha project and implement automated ingestion, quality/drift protection, and a Power BI Service deployment kit that is safe to run without live tenant credentials.

**Architecture:** Keep the core ETL rules in `scripts/hcaptcha_pipeline.py`, extend it with a CLI and quality evaluation, and build small focused operational scripts around it. Separate approved versus rejected loads through staging, archive, and quarantine directories. Keep Power BI Service integration deploy-ready by mirroring approved outputs to a fixed Windows gateway path and providing preflight and refresh tooling plus runbooks.

**Tech Stack:** Python 3, pandas, pytest, watchdog, JSON/CSV operational logs, Power BI PBIP/TMDL, Power BI REST API docs

---

### Task 1: Repository Hardening and Public Baseline

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `data/raw/.gitkeep`
- Create: `data/raw/inbox/.gitkeep`
- Create: `data/raw/archive/.gitkeep`
- Create: `data/raw/quarantine/.gitkeep`
- Create: `data/processed/.gitkeep`
- Create: `reports/quality/.gitkeep`
- Create: `reports/ops/.gitkeep`
- Modify: `powerbi/hcaptcha-positioning/README.md`

- [ ] **Step 1: Write the failing repository-structure test**

```python
def test_repository_ignores_sensitive_and_generated_artifacts():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    assert "data/raw/*" in gitignore
    assert "data/processed/*" in gitignore
    assert "*.pbix" in gitignore
    assert "tools/" in gitignore
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_repo_setup.py::test_repository_ignores_sensitive_and_generated_artifacts -q`
Expected: FAIL because `tests/test_repo_setup.py` or `.gitignore` does not exist yet

- [ ] **Step 3: Add the repository hardening files**

```text
.gitignore
README.md
data/raw/.gitkeep
data/raw/inbox/.gitkeep
data/raw/archive/.gitkeep
data/raw/quarantine/.gitkeep
data/processed/.gitkeep
reports/quality/.gitkeep
reports/ops/.gitkeep
```

- [ ] **Step 4: Run the repository-structure test again**

Run: `pytest tests/test_repo_setup.py::test_repository_ignores_sensitive_and_generated_artifacts -q`
Expected: PASS

- [ ] **Step 5: Initialize Git and create the baseline commit**

Run:

```bash
git init
git add .
git commit -m "feat: foundation for automated market intelligence"
git branch -M main
git remote add origin git@github.com:lucasguldem/isabellysto-prepara-portugal.git
git push -u origin main
```

### Task 2: TDD for Pipeline CLI and Quality Gates

**Files:**
- Create: `tests/test_pipeline_cli.py`
- Modify: `scripts/hcaptcha_pipeline.py`
- Create: `config/pipeline_settings.json`

- [ ] **Step 1: Write failing tests for quality metrics and gate decisions**

```python
def test_evaluate_quality_flags_quarantine_when_duplicate_rate_is_too_high():
    report = evaluate_quality_metrics(
        raw_rows=100,
        clean_rows=60,
        duplicate_rate=0.31,
        non_european_rate=0.05,
        missing_company_country_rate=0.02,
        other_role_rate=0.10,
        unknown_company_size_rate=0.08,
        previous_approved_row_count=95,
        thresholds=DEFAULT_THRESHOLDS,
    )
    assert report["decision"] == "quarantine"
    assert "duplicate_rate" in report["blocking_failures"]
```

- [ ] **Step 2: Run the new pipeline CLI tests and confirm failure**

Run: `pytest tests/test_pipeline_cli.py -q`
Expected: FAIL because `evaluate_quality_metrics` and CLI helpers do not exist yet

- [ ] **Step 3: Implement the minimal CLI and quality logic**

```python
def evaluate_quality_metrics(
    raw_rows: int,
    clean_rows: int,
    duplicate_rate: float,
    non_european_rate: float,
    missing_company_country_rate: float,
    other_role_rate: float,
    unknown_company_size_rate: float,
    previous_approved_row_count: int | None,
    thresholds: dict,
) -> dict:
    return {"decision": "approved", "blocking_failures": [], "warnings": []}

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_pipeline_command(args)

if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Re-run the pipeline CLI tests**

Run: `pytest tests/test_pipeline_cli.py -q`
Expected: PASS

- [ ] **Step 5: Refactor only after green**

Run: `pytest tests/test_pipeline.py tests/test_pipeline_cli.py -q`
Expected: PASS

### Task 3: Automated Ingestion Watcher

**Files:**
- Create: `tests/test_watcher.py`
- Create: `scripts/watcher.py`

- [ ] **Step 1: Write failing tests for file settling and routing**

```python
def test_choose_final_raw_destination_returns_archive_for_approved_load():
    assert choose_final_raw_destination("approved", Path("data/raw/archive"), Path("data/raw/quarantine")).name == "archive"
```

- [ ] **Step 2: Run watcher tests to verify failure**

Run: `pytest tests/test_watcher.py -q`
Expected: FAIL because `scripts/watcher.py` does not exist yet

- [ ] **Step 3: Implement minimal watcher behavior**

```python
def wait_for_file_settle(path: Path, attempts: int = 10, sleep_seconds: float = 1.0) -> None:
    last_size = -1
    for _ in range(attempts):
        current_size = path.stat().st_size
        if current_size == last_size:
            return
        last_size = current_size
        time.sleep(sleep_seconds)
    raise TimeoutError(f"File did not settle: {path}")

def process_inbox_file(path: Path, config: dict) -> int:
    wait_for_file_settle(path)
    return run_pipeline_for_file(path, config)
```

- [ ] **Step 4: Re-run watcher tests**

Run: `pytest tests/test_watcher.py -q`
Expected: PASS

- [ ] **Step 5: Run combined tests**

Run: `pytest tests/test_pipeline.py tests/test_pipeline_cli.py tests/test_watcher.py -q`
Expected: PASS

### Task 4: Gateway Mirror and Refresh Toolkit

**Files:**
- Create: `tests/test_power_bi_ops.py`
- Create: `scripts/export_gateway_ready.py`
- Create: `scripts/pbi_preflight.py`
- Create: `scripts/pbi_refresh.py`
- Create: `config/pbi_service.env.example`

- [ ] **Step 1: Write failing tests for gateway mirror and refresh preflight**

```python
def test_collect_missing_env_vars_reports_required_power_bi_service_settings():
    missing = collect_missing_env_vars({})
    assert "PBI_TENANT_ID" in missing
    assert "PBI_DATASET_ID" in missing
```

- [ ] **Step 2: Run Power BI ops tests to verify failure**

Run: `pytest tests/test_power_bi_ops.py -q`
Expected: FAIL because the scripts and helpers do not exist yet

- [ ] **Step 3: Implement the minimal mirror and refresh helpers**

```python
def sync_processed_outputs_to_gateway(source_dir: Path, target_dir: Path) -> list[Path]:
    copied: list[Path] = []
    for csv_path in sorted(source_dir.glob("*.csv")):
        destination = target_dir / csv_path.name
        shutil.copy2(csv_path, destination)
        copied.append(destination)
    return copied

def collect_missing_env_vars(env: Mapping[str, str]) -> list[str]:
    required = ["PBI_TENANT_ID", "PBI_CLIENT_ID", "PBI_DATASET_ID", "PBI_WORKSPACE_ID"]
    return [key for key in required if not env.get(key)]
```

- [ ] **Step 4: Re-run the Power BI ops tests**

Run: `pytest tests/test_power_bi_ops.py -q`
Expected: PASS

- [ ] **Step 5: Verify the dry-run refresh command path**

Run: `python scripts/pbi_refresh.py --dry-run`
Expected: exit code `0` with a message describing the intended refresh request

### Task 5: Runbooks and Operational Documentation

**Files:**
- Create: `docs/deploy_pbi_service.md`
- Create: `docs/operational_runbook.md`
- Modify: `README.md`

- [ ] **Step 1: Document publication and gateway setup**

Include:
- fixed Windows mirror path
- Desktop publish flow
- gateway binding
- scheduled refresh
- service principal prerequisites

- [ ] **Step 2: Document the operational runbook**

Include:
- inbox, archive, quarantine lifecycle
- quality gate outcomes
- refresh logging
- troubleshooting for gateway failures, including checking whether the host is online and whether `PBIEgwService` is running

- [ ] **Step 3: Re-read docs for consistency with the code**

Run: `rg -n "TODO|TBD|placeholder" README.md docs config scripts`
Expected: no output

### Task 6: Final Verification

**Files:**
- Verify: `tests/`
- Verify: `reports/quality/`
- Verify: `reports/ops/`
- Verify: `README.md`
- Verify: `docs/`

- [ ] **Step 1: Run the full test suite**

Run: `pytest -q`
Expected: PASS

- [ ] **Step 2: Run the pipeline CLI against a sample load**

Run:

```bash
python scripts/hcaptcha_pipeline.py \
  --input /mnt/c/Users/02luc/Downloads/Planilha\ -\ Desafio\ de\ Dados\ -\ Página1.csv \
  --output-dir data/processed \
  --quality-dir reports/quality \
  --config config/pipeline_settings.json
```

Expected: exit code `0`, processed outputs written, quality report generated

- [ ] **Step 3: Run the watcher in dry-run or one-shot mode**

Run: `python scripts/watcher.py --once`
Expected: clean exit even when inbox is empty

- [ ] **Step 4: Run Power BI preflight**

Run: `python scripts/pbi_preflight.py`
Expected: clear missing-config output if credentials are absent, no stack trace

- [ ] **Step 5: Summarize residual risks**

Document:
- live Power BI Service publish still requires tenant credentials and gateway admin access
- real scheduled refresh depends on stable Windows path plus gateway registration
