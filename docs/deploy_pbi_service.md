# Power BI Service Deployment Guide

## Purpose

This project is designed to be published to Power BI Service without depending on live credentials inside the repository. The deployment kit prepares the dataset for a hybrid setup in which:

- ETL runs inside WSL/Linux
- approved Gold CSVs are mirrored to a stable Windows folder
- Power BI Desktop publishes the report
- an on-premises gateway enables scheduled refresh in the Service

## Why the Windows mirror exists

Power BI scheduled refresh is sensitive to data-source accessibility and Microsoft documents limitations around dynamic data sources. For this reason, the production-like path for this project uses a fixed Windows folder such as:

`C:\Users\02luc\Documents\PowerBIData\hcaptcha\processed`

That path is configured in `config/pipeline_settings.json` as `directories.gateway_mirror`.

## Deployment Steps

### 1. Prepare the local mirror

Run:

```bash
python scripts/export_gateway_ready.py --config config/pipeline_settings.json
```

This mirrors the approved CSVs from `data/processed/` into the Windows-host path that the gateway will use.

### 2. Validate local prerequisites

Run:

```bash
python scripts/pbi_preflight.py --config config/pipeline_settings.json
```

This checks:

- required Power BI Service environment variables
- whether the gateway mirror path exists

### 3. Open and publish the report

1. Open `dashboards/hcaptcha_report/hcaptcha_report.pbip` in Power BI Desktop.
2. Confirm that the Power Query source uses the stable Windows mirror path.
3. Refresh the model in Desktop.
4. Publish the report to the target workspace.

### 4. Configure the gateway

1. Install or open the `On-premises Data Gateway` on the Windows host.
2. Add the data source connection that matches the dataset source.
3. Ensure the dataset owner or service principal has access to the gateway data source.
4. In Power BI Service, bind the dataset to the gateway data source.

### 5. Configure refresh

1. Configure scheduled refresh in the dataset settings.
2. If you want API-triggered refresh, create an Entra app registration and populate the local environment variables from `config/pbi_service.env.example`.
3. Validate the request shape with:

```bash
python scripts/pbi_refresh.py --dry-run
```

4. When credentials are available, run:

```bash
python scripts/pbi_refresh.py
```

## Required Environment Variables

- `PBI_TENANT_ID`
- `PBI_CLIENT_ID`
- `PBI_CLIENT_SECRET`
- `PBI_WORKSPACE_ID`
- `PBI_DATASET_ID`
- `PBI_GATEWAY_MIRROR_PATH` (optional override)
- `PBI_REFRESH_NOTIFY_OPTION` (optional)

## Recommended Operational Flow

1. A new CSV lands in `data/raw/inbox/`.
2. `watcher.py` processes the file and applies the quality gates.
3. If approved, the Gold layer is promoted, the Windows mirror is updated, and refresh is attempted if the Power BI variables are configured.
4. If not approved, the file is quarantined and no refresh is triggered.

## References

- Refresh overview and dynamic data sources:
  https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data
- Gateway data source management:
  https://learn.microsoft.com/en-us/power-bi/connect-data/service-gateway-data-sources
- Refresh dataset API:
  https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/refresh-dataset
- Bind dataset to gateway:
  https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/bind-to-gateway
- Update refresh schedule:
  https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/update-refresh-schedule
