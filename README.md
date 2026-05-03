# isabellysto-prepara-portugal

## Project Overview

This repository contains a complete analytics engineering workflow for the hCaptcha Europe positioning challenge. The project starts from a lead export sourced from Snov.io and turns it into a reproducible market-intelligence asset with:

- a tested Python ETL pipeline
- a versionable Power BI Project (`PBIP`/`TMDL`)
- an executive report with GTM recommendations
- a public interactive presentation, a private presenter script, and a separate technical glossary PDF
- operational extensions for automated ingestion, quality controls, and Power BI Service deployment readiness

The core business question is: **how should hCaptcha position itself in the European market?**

## Architecture

```mermaid
flowchart LR
    subgraph Source["Source Layer"]
        A[Snov.io lead export<br/>local CSV]
    end

    subgraph Ingestion["Ingestion and Quality"]
        B[Inbox watcher<br/>scripts/watcher.py]
        C[ETL pipeline<br/>scripts/hcaptcha_pipeline.py]
        D[Quality reports<br/>reports/quality]
    end

    subgraph Model["Analytics Model"]
        E[Gold tables and dimensions<br/>data/processed]
        F[Power BI semantic model<br/>PBIP / TMDL]
        G[Versioned report definition<br/>powerbi/hcaptcha-positioning]
    end

    subgraph Delivery["Business Delivery"]
        H[Power BI Desktop / Service]
        I[Executive narrative<br/>reports]
        J[Public presentation app<br/>apps/hcaptcha-course-presentation]
        K[Static report snapshots<br/>reports/figures]
    end

    subgraph Ops["Governance and Operations"]
        L[Deployment preflight<br/>scripts/pbi_preflight.py]
        M[Gateway export<br/>scripts/export_gateway_ready.py]
        N[Refresh automation<br/>scripts/pbi_refresh.py]
        O[Tests<br/>pytest]
    end

    A --> B --> C
    C --> D
    C --> E --> F --> G --> H
    E --> I
    E --> J
    E --> K
    E --> M
    L --> H
    M --> H
    N --> H
    O --> C
    O --> L
```

## Report Snapshots

These PNG snapshots make the main analytical outputs visible directly in GitHub. The complete interactive report remains versioned as a Power BI Project at [`powerbi/hcaptcha-positioning/hcaptcha_report.pbip`](powerbi/hcaptcha-positioning/hcaptcha_report.pbip), while the static figures live under [`reports/figures/`](reports/figures/).

### Market Priority by Country

<img src="reports/figures/01_market_overview_top_countries.png" alt="Top European markets by eligible lead volume" width="100%"/>

### Persona and Company Size Mix

<img src="reports/figures/02_icp_role_size_heatmap.png" alt="Persona mix by company size segment" width="100%"/>

### Cross-Border Signal

<img src="reports/figures/03_cross_border_signal.png" alt="Markets with strongest distributed operation signal" width="100%"/>

## Repository Structure

- `scripts/`: ETL pipeline, Power BI project generation, and operational automation
- `tests/`: pytest coverage for transformation rules and operational scripts
- `notebooks/`: exploratory and delivery notebook assets
- `powerbi/`: versionable Power BI Project (`PBIP`/`TMDL`)
- `apps/`: presentation apps and web delivery surfaces
- `reports/`: executive report plus generated figures and ops logs
- `docs/`: Power BI blueprints, semantic-model notes, design specs, plans, and deployment runbooks
- `data/`: local-only raw and processed data directories kept out of Git by design

## Governance and Privacy

Real lead exports are intentionally excluded from version control. Raw and processed datasets may contain personally identifiable information such as names, emails, and company details. For that reason:

- `data/raw/` and `data/processed/` are ignored by Git
- `.pbix` binaries are ignored; the repository keeps the text-based `PBIP` source instead
- local toolchains and secrets are not published

This repository is designed to be safe for public versioning while keeping the project reproducible.

## How to Run

### 1. Prepare your local data

Place the raw Snov.io export in `data/raw/inbox/` or run the pipeline directly against a local CSV path.

### 2. Install local dependencies

Example:

```bash
python -m pip install pandas pytest jupyter matplotlib seaborn plotly watchdog requests
```

Optional local tooling used during development:

- Power BI Desktop on Windows
- `pbi-tools`
- `.NET`

### 3. Run the ETL pipeline

```bash
python scripts/hcaptcha_pipeline.py \
  --input /path/to/export.csv \
  --output-dir data/processed \
  --quality-dir reports/quality \
  --config config/pipeline_settings.json
```

### 4. Process the inbox automatically

One-shot mode:

```bash
python scripts/watcher.py --once --config config/pipeline_settings.json
```

Continuous watch mode:

```bash
python scripts/watcher.py --config config/pipeline_settings.json
```

### 5. Open the Power BI Project

Open `powerbi/hcaptcha-positioning/hcaptcha_report.pbip` in Power BI Desktop, refresh the model, and save a local `.pbix` if needed.

### 6. Regenerate the presentation snapshot and PDF

```bash
python scripts/build_presentation_snapshot.py
npm --prefix apps/hcaptcha-course-presentation run deck
```

Run the local presentation site:

```bash
npm --prefix apps/hcaptcha-course-presentation run dev -- --port 5174
```

### 7. Prepare the Power BI Service deployment kit

Validate local prerequisites:

```bash
python scripts/pbi_preflight.py --config config/pipeline_settings.json
```

Mirror approved outputs to the Windows gateway path:

```bash
python scripts/export_gateway_ready.py --config config/pipeline_settings.json
```

Preview the Power BI refresh request:

```bash
python scripts/pbi_refresh.py --dry-run
```

## Power BI Service Readiness

The repository includes a deploy-ready path for Power BI Service:

- approved Gold outputs are mirrored to a fixed Windows folder for gateway use
- a deployment preflight validates required settings
- a refresh script can trigger a dataset refresh through the Power BI REST API

See:

- `docs/deploy_pbi_service.md`
- `docs/operational_runbook.md`

## Technical Stack

- Python 3
- pandas
- pytest
- Jupyter
- Power BI PBIP / TMDL
- Power BI REST API

## Current Status

The repository currently contains:

- the original hCaptcha market analysis implementation
- the PBIP project used to materialize the dashboard in Power BI Desktop
- the `apps/hcaptcha-course-presentation` interactive presentation backed by a sanitized Level 2 JSON snapshot
- public PDF deck, private presenter script, and technical glossary artifacts generated from the same data source
- operational design scaffolding for automated ingestion, quality gates, and Service refresh

## Notes

If you clone this repository, keep your own local data files under `data/` and your own credentials in environment variables or local `.env` files that are not committed.
