# hCaptcha Europe Positioning Design

**Date:** 2026-04-23

**Objective:** Build a reproducible analytics asset that cleans and structures the European lead dataset, surfaces GTM insights for hCaptcha, and produces Power BI-ready outputs plus notebook-based blueprint visuals.

## Problem Framing

The raw CSV contains technology contacts and companies sourced from Snov.io. The analysis question is not "who are the contacts?" in isolation, but "how should hCaptcha position itself in the European market?" That requires shifting the analytical center of gravity from contact-level noise to company-level market signals.

## Core Decisions

### Geographic Source of Truth

- Use `País da empresa` as the primary geography field for European market filtering and tiering.
- Keep `País` only as a contact attribute for secondary analysis, especially to measure distributed or cross-border operating patterns.

### Deduplication Rule

- Deduplicate on `E-mail + Nome da empresa`.
- Keep the best available record per duplicate cluster by preferring rows with:
  - a valid email status
  - a populated company country
  - a populated company size
  - a populated LinkedIn URL

### Role Normalization

- Normalize raw job titles into strategic role buckets for GTM analysis:
  - `Executive / Technical Decision Maker`
  - `Data / Compliance`
  - `Security / Risk`
  - `IT / Engineering Management`
  - `Individual Contributor / Specialist`
  - `Other`

### Company Size Normalization

- Parse `Tamanho da empresa` into numeric ranges when possible.
- Bucket into:
  - `1. Startup / SMB`
  - `2. Mid-Market`
  - `3. Enterprise`
  - `4. Unknown`

### Europe Eligibility

- Filter the market analysis dataset to companies headquartered in Europe based on a maintained whitelist of European countries.
- Preserve excluded rows in diagnostic views so the notebook can quantify data leakage and cleaning decisions.

## Deliverables

### Code Assets

- Reusable Python cleaning and enrichment module.
- Automated tests covering the cleaning logic and key edge cases.
- Jupyter notebook orchestrating ETL, EDA, exports, and blueprint visuals.

### Data Assets

- `data/processed/hcaptcha_europe_gold.csv`
- `data/processed/dim_role_category.csv`
- `data/processed/dim_company_size.csv`
- `data/processed/dim_country_priority.csv`
- Optional diagnostic exports for duplicates and excluded non-European rows.

### Analytical Outputs

- Country prioritization for European GTM.
- Role and buying-center concentration.
- Company size mix and recommended ICP.
- Distributed-operations signal from `País` vs `País da empresa`.
- Executive summary points ready to be reused in the written report and Power BI.

## Dashboard Blueprint

### Page 1: Market Overview

- Lead count by `País da empresa`
- Unique company count
- Share of strategic personas
- Country tier view

### Page 2: ICP and Personas

- Role bucket frequency
- Role bucket by company size
- Sector concentration by strategic role

### Page 3: Go-to-Market Priorities

- Country by company size matrix
- Distributed-operations gap analysis
- Tier 1 / Tier 2 / Tier 3 market table with rationale

### Page 4: Executive Summary

- Target markets
- Target buyer personas
- Core messaging by market segment
- Barriers and opportunities

## Risks and Constraints

- The workspace is not a git repository, so documentation can be written locally but not committed here.
- Power BI CLI tooling is not available in this environment, so the build target is a Power BI-ready dataset plus notebook mockups rather than a generated `.pbix`.

