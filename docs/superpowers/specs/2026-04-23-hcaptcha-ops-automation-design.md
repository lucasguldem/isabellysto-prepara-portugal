# hCaptcha Operations Automation Design

**Date:** 2026-04-23

**Objective:** Harden the repository for public versioning, automate local ingestion of new Snov.io exports, add data-quality and drift gates that protect the Gold layer, and prepare a production-ready Power BI Service deployment kit without requiring live tenant credentials in this environment.

## Problem Framing

The current project already delivers a cleaned analytics asset, a PBIP project, and an executive report. The next stage is operationalization: make the repository safe to publish, make the ETL runnable without manual intervention, prevent bad loads from corrupting the dashboard, and prepare the handoff artifacts required to publish and refresh the model in Power BI Service.

The design goal is to keep the system pragmatic. It should be reliable enough for recurring use, but not overbuilt beyond the current challenge scope.

## Core Decisions

### Repository Governance

- Publish a clean repository state with code, PBIP, tests, and documentation.
- Exclude raw and processed data, local toolchains, local secrets, and binary Power BI artifacts from Git.
- Preserve the folder contract with `.gitkeep` files so the project remains runnable after clone.

### Ingestion Model

- New lead files land in `data/raw/inbox/`.
- A local watcher observes that directory and waits for the file to stop changing before processing.
- Each load is processed into a staging area first, never directly into `data/processed/`.

### Atomic Promotion

- A load that passes validation replaces the current Gold outputs atomically.
- A load that fails validation never overwrites the approved Gold outputs.
- Approved raw files move to `data/raw/archive/`; rejected files move to `data/raw/quarantine/`.

### Quality and Drift Gates

- The pipeline will compute a structured quality report for each load.
- Validation thresholds are stored in configuration, not hard-coded in procedural logic.
- The initial gating set covers:
  - missing `company_country`
  - non-European rows
  - duplicate rate by `email + company_name`
  - `role_category = Other`
  - `company_size_segment = 4. Unknown`
  - volume drift versus the most recent approved load
- Duplicate thresholds:
  - warning above `15%`
  - quarantine above `30%`
  - warning if the duplicate rate increases by more than `10` percentage points versus the previous approved load

### Pipeline Interface

- `scripts/hcaptcha_pipeline.py` becomes a formal CLI entry point.
- The CLI accepts explicit input/output paths and an optional config path so it can be reused by the watcher, manual runs, and future schedulers.
- A `--fail-on-quality-gate` mode makes the pipeline safe for unattended execution.

### Power BI Service Readiness

- The Power BI Service deployment path will not depend on `\\wsl$` or dynamic local paths in production.
- After a load is approved, the Gold CSVs are mirrored to a fixed Windows directory suitable for an on-premises gateway, such as `C:\Users\02luc\Documents\PowerBIData\hcaptcha\processed`.
- The PBIP project remains the versioned source of truth, while the `.pbix` published to Service is configured against the stable Windows mirror path.

This design is based on Microsoft Power BI guidance for scheduled refresh, on-premises gateways, and refresh limitations for dynamic data sources.

## Deliverables

### Code Assets

- `scripts/hcaptcha_pipeline.py` CLI with staging-safe exports and quality evaluation
- `scripts/watcher.py` for local ingestion automation
- `scripts/export_gateway_ready.py` for Windows mirror sync
- `scripts/pbi_preflight.py` for deployment prerequisites validation
- `scripts/pbi_refresh.py` for optional API-triggered refresh

### Configuration Assets

- `config/pipeline_settings.json`
- `config/pbi_service.env.example`

### Documentation

- Senior-level `README.md`
- `docs/deploy_pbi_service.md`
- `docs/operational_runbook.md`

### Operational Outputs

- `reports/quality/latest_quality_report.json`
- `reports/quality/quality_history.csv`
- `reports/ops/last_refresh_status.json`
- `reports/ops/refresh_history.csv`

## Data Flow

1. A CSV is dropped into `data/raw/inbox/`.
2. The watcher confirms the file has settled.
3. The pipeline reads the file and produces staging outputs plus a quality report.
4. If all blocking gates pass:
   - the Gold CSVs are promoted into `data/processed/`
   - the quality history is updated
   - the source file moves to `archive/`
   - the approved outputs are mirrored to the Windows gateway folder
   - a Power BI refresh is optionally triggered if the local deployment variables are configured
5. If a blocking gate fails:
   - the existing Gold outputs remain untouched
   - the source file moves to `quarantine/`
   - the failure is logged in quality and ops outputs

## Testing Strategy

- TDD for all new behavior:
  - CLI argument handling
  - quality gate evaluation
  - duplicate/drift thresholds
  - watcher file-settling behavior
  - archive versus quarantine routing
  - gateway-ready export sync
  - refresh preflight behavior without credentials
- Keep the tests lightweight and local; the Power BI Service API integration is validated through dry-run behavior and request construction, not live calls.

## Risks and Constraints

- No tenant credentials, workspace access, or gateway administration are assumed in this environment.
- Live publication to Power BI Service is intentionally out of scope; the goal is a deploy-ready kit.
- Raw lead data likely contains PII, so the repository must be safe to publish without shipping those files.
- The project is not yet a Git repository, so the hardening step must happen before the design and implementation history can be captured in commits.

## External References

- Power BI refresh overview and dynamic data source limitations:
  - https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data
- Gateway data source management:
  - https://learn.microsoft.com/en-us/power-bi/connect-data/service-gateway-data-sources
- Trigger dataset refresh:
  - https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/refresh-dataset
- Bind dataset to gateway:
  - https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/bind-to-gateway
- Update refresh schedule:
  - https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/update-refresh-schedule
