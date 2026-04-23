# Operational Runbook

## Scope

This runbook describes the day-to-day operation of the local ingestion pipeline, quality gates, gateway mirror, and Power BI refresh readiness.

## Directory Lifecycle

- `data/raw/inbox/`: drop new CSV exports here
- `data/raw/archive/`: approved loads move here
- `data/raw/quarantine/`: failed loads move here
- `data/processed/`: approved Gold outputs only
- `reports/quality/`: quality report and history
- `reports/ops/`: refresh status and history

## Standard Commands

### Manual ETL run

```bash
python scripts/hcaptcha_pipeline.py \
  --input /path/to/export.csv \
  --output-dir data/processed \
  --quality-dir reports/quality \
  --config config/pipeline_settings.json
```

### Inbox processing

```bash
python scripts/watcher.py --once --config config/pipeline_settings.json
```

### Continuous monitoring

```bash
python scripts/watcher.py --config config/pipeline_settings.json
```

## Quality Gate Outcomes

### Approved

- Gold CSVs are promoted to `data/processed/`
- source file moves to `archive/`
- gateway mirror sync runs
- refresh is attempted if Power BI credentials are configured

### Quarantine

- current Gold CSVs remain unchanged
- source file moves to `quarantine/`
- refresh is skipped

## Main Quality Signals

- duplicate rate by `email + company`
- missing `company_country`
- non-European company share
- `role_category = Other`
- `company_size_segment = 4. Unknown`
- row-count drift against the previous approved load

## Logs to Inspect

### Quality

- `reports/quality/latest_quality_report.json`
- `reports/quality/quality_history.csv`

### Operations

- `reports/ops/last_refresh_status.json`
- `reports/ops/refresh_history.csv`

## Failure Handling

### Quality failure

1. Open `reports/quality/latest_quality_report.json`.
2. Inspect `blocking_failures` and `warnings`.
3. If the issue is a mapping gap, update the pipeline rules and reprocess.
4. If the issue is source corruption, keep the file in quarantine and request a new export.

### Gateway mirror issue

1. Confirm the Windows mirror path exists.
2. Re-run:

```bash
python scripts/export_gateway_ready.py --config config/pipeline_settings.json
```

### Power BI refresh skipped

1. Run:

```bash
python scripts/pbi_preflight.py --config config/pipeline_settings.json
```

2. Populate missing environment variables from `config/pbi_service.env.example`.

### Power BI gateway failure

Check these first on the Windows host:

1. Confirm the machine is powered on and connected.
2. Confirm the `On-premises Data Gateway` service is running.

Example PowerShell checks:

```powershell
Get-Service PBIEgwService
Start-Service PBIEgwService
```

3. Confirm the dataset is still bound to the correct gateway data source.
4. Confirm the published dataset still points to the stable Windows mirror path.

## Recommended Daily Routine

1. Drop the new CSV export into `data/raw/inbox/`.
2. Run `watcher.py --once` or leave watch mode active.
3. Confirm the file moved to `archive/` or `quarantine/`.
4. Inspect the latest quality report.
5. If refresh is configured, inspect `reports/ops/last_refresh_status.json`.
