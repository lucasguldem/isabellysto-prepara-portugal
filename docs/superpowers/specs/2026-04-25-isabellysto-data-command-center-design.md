# Isabellysto Data Command Center Design

**Date:** 2026-04-25

## Objective

Build an immersive technical presentation site for the hCaptcha Europe positioning analysis. The site will turn the existing analytics outputs into a 3D "Virtual Command Center" that starts with a guided executive narrative and then unlocks an exploratory dashboard for stakeholder questions.

The experience must be suitable for local presentation and future static deployment without exposing personal lead data.

## Approved Direction

### Visual Concept

The site will use a **Dark Cyber-Intelligence** style:

- Ultra-deep navy background (`#020617`) with atmospheric fog in the 3D scene.
- Emissive cyan and violet 3D geometry for charts, clusters, paths, and status indicators.
- Holographic glass UI panels using translucent backgrounds, blur, thin borders, and technical typography.
- A command-center layout, not a marketing landing page.

### Data Exposure Level

The approved exposure level is **Level 2: Aggregates + Companies**:

- Allowed: country metrics, tiering, role categories, company size segments, industries, recommendations, and selected company names.
- Not allowed: emails, names of people, LinkedIn URLs, contact locations tied to a person, or any lead-level personally identifiable information.
- Company drill-down panels may show `company_name`, `company_industry`, `company_size_segment`, `company_country`, and aggregate counts.

### Presentation Flow

The site will use a **hybrid flow**:

1. **System Boot**
   - Cinematic loading sequence that implies CSV ingestion and model activation.
   - Displays only safe pipeline status and aggregate row counts.
2. **Guided Narrative**
   - Module 1: Market map with European priority tiers and lead density.
   - Module 2: ICP/persona module showing role categories and company-size distribution.
   - Module 3: Recommendation module isolating strategic "Gold Leads" and GTM actions from the positioning summary.
3. **Unlocked Mode**
   - Camera pulls back.
   - Orbit controls become available.
   - Side hologram panels expose filters for country, tier, company size, role category, and messaging angle.

## Considered Approaches

### Approach A: Static Snapshot Only

Generate a sanitized JSON once and commit it for the frontend.

- Pros: fastest runtime, simplest deploy, lowest security risk.
- Cons: can drift from the Python pipeline unless manually regenerated.

### Approach B: Local API Over CSV

Run a backend service that reads CSV files in runtime.

- Pros: always reflects local CSV changes and supports deeper exploratory queries.
- Cons: harder to deploy publicly, higher runtime complexity, greater risk of accidental PII exposure.

### Approach C: Hybrid Static-Regenerable Snapshot

Use a Python sanitizer script to transform local CSV and Markdown outputs into a sanitized frontend JSON snapshot. The frontend consumes only that JSON, and the snapshot can be regenerated whenever the pipeline changes.

- Pros: production-friendly, fast 3D runtime, safe deploy path, clear link to the analytics pipeline.
- Cons: requires a regeneration command after data updates.

**Chosen approach:** Approach C.

## Technical Architecture

### Frontend

Use a React app with:

- React Three Fiber for the immersive 3D command center.
- Three.js primitives/materials for grid, fog, particles, volumetric bars, scatter points, and animated hub elements.
- D3 for scale calculations, grouping, ranking, normalization, and coordinate mapping.
- Tailwind CSS for holographic UI panels and controls.
- Framer Motion for panel transitions, boot sequence timing, and narrative text reveals.

The app must be deployable as a static build.

### Data Build Layer

Add a Python sanitizer script that reads:

- `data/processed/hcaptcha_europe_gold.csv`
- `data/processed/dim_country_priority.csv`
- `data/processed/dim_role_category.csv`
- `data/processed/dim_company_size.csv`
- `reports/hcaptcha_positioning_summary.md`
- `reports/quality/latest_quality_report.json`, when available

The script writes a sanitized JSON snapshot under the frontend public data folder. The JSON must contain only presentation-safe data.

### Frontend Data Contract

The snapshot will include:

- `metadata`: generation timestamp, source row counts, unique company count, source filenames, and privacy level.
- `market`: country-level metrics such as lead count, company count, rank, priority tier, messaging angle, executive share, compliance share, and mismatch share.
- `personas`: role-category counts and shares.
- `segments`: company-size counts and shares.
- `companies`: company-level safe records with company name, country, industry, size segment, lead count, role mix, and priority tier.
- `recommendations`: concise GTM recommendations parsed or curated from the executive report.
- `narrative`: short system-log style copy blocks derived from the summary report without exposing PII.

## 3D Scene Design

### Spatial Model

- A central hCaptcha intelligence hub represents the processed gold dataset.
- Country clusters orbit or sit around the hub, positioned using a deterministic country coordinate map for Europe.
- Bar heights encode lead volume.
- Color encodes priority tier and messaging angle.
- Particle intensity encodes company count or strategic density.
- Cross-border mismatch is shown as animated arcs or pulses between contact/company geography at an aggregate level only.

### Story Modules

**Module 1: Market Map**

- Shows top European countries by lead volume.
- Highlights Germany, United Kingdom, France, Spain, and Portugal as Tier 1 markets.
- Displays a side panel with leads, companies, rank, tier, and messaging angle.

**Module 2: ICP and Personas**

- Transforms the map into a volumetric scatter or matrix.
- Encodes role category and company size segment.
- Shows the balance between Executive / Technical Decision Maker and Data / Compliance audiences.

**Module 3: Recommendation Engine**

- Isolates priority countries and safe company clusters.
- Displays recommendation logs for privacy-first, scale-first, and balanced GTM tracks.
- Shows top safe companies for the selected cluster without personal contact details.

**Unlocked Mode**

- Enables orbit controls.
- Activates filters and hover/click inspection.
- Keeps the site presentation-ready with guarded, readable panels.

## UI Components

- Boot screen with animated loading telemetry.
- Left module rail for story sections and unlocked filters.
- Right telemetry panel for selected market/company-cluster details.
- Bottom narrative console that renders summary insights as system logs.
- Top status bar with dataset totals, privacy level, and generation timestamp.
- 3D viewport occupying the primary screen space.

## Data Privacy And Governance

- The frontend never reads raw CSV files.
- Sanitized JSON must exclude person-level fields.
- Company records are grouped and deduplicated.
- Any company list must be bounded, sortable, and presented as business context rather than a lead export.
- The public deploy artifact must be safe to serve from static hosting.

## Error Handling

- If the JSON snapshot is missing, the app shows a technical empty state with the regeneration command.
- If a field is missing, affected panels degrade to "Unavailable" instead of crashing.
- If company data is empty, the site still shows aggregate market and persona modules.
- The sanitizer must fail loudly if expected source files are missing or if forbidden PII fields appear in the exported JSON.

## Testing And Verification

### Data Verification

- Unit tests for the sanitizer must assert that forbidden PII keys are absent.
- Tests must confirm aggregate totals match the source CSV after grouping.
- Tests must validate required JSON sections and representative fields.

### Frontend Verification

- Run the build and lint/type checks available in the frontend stack.
- Verify with Playwright screenshots on desktop and mobile viewports.
- Confirm the 3D canvas is nonblank and visually framed.
- Confirm story mode advances through all modules.
- Confirm unlocked mode allows orbit controls and filter interactions.

## Implementation Boundaries

- Do not modify existing Power BI PBIP files unless explicitly requested.
- Keep the web app isolated under a dedicated frontend directory.
- Keep the data sanitizer scoped to safe presentation JSON generation.
- Reuse existing project outputs instead of changing the ETL pipeline unless a data-contract issue requires a small, focused adjustment.

## Open Decisions Resolved

- Visual style: Dark Cyber-Intelligence.
- Data exposure: Aggregates plus company-level safe fields, no PII.
- Flow: Hybrid guided story plus unlocked exploration.
- Runtime data model: Static frontend with regenerable sanitized JSON.
- Deployment target: local dev server now, static deployment-ready later.
