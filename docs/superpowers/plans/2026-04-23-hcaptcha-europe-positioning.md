# hCaptcha Europe Positioning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tested data-cleaning and analytics pipeline that transforms the raw Snov.io export into Power BI-ready European GTM datasets and a Jupyter notebook with blueprint visuals.

**Architecture:** Keep reusable data rules in a Python module and keep the notebook focused on orchestration, EDA, exports, and charts. The gold dataset is company-market oriented, using `País da empresa` as the geographic source of truth while preserving contact-level fields for distributed-operations analysis.

**Tech Stack:** Python 3, pandas, pytest, Jupyter Notebook, plotly, seaborn, matplotlib

---

### Task 1: Project Skeleton and Documentation

**Files:**
- Create: `docs/superpowers/specs/2026-04-23-hcaptcha-europe-positioning-design.md`
- Create: `docs/superpowers/plans/2026-04-23-hcaptcha-europe-positioning.md`
- Create: `scripts/hcaptcha_pipeline.py`
- Create: `data/processed/.gitkeep`
- Create: `notebooks/.gitkeep`

- [ ] Step 1: Create the directory structure for docs, source, notebook, and processed outputs.
- [ ] Step 2: Save the approved design document.
- [ ] Step 3: Save this implementation plan.

### Task 2: TDD for Cleaning Rules

**Files:**
- Create: `tests/test_pipeline.py`
- Create: `scripts/hcaptcha_pipeline.py`

- [ ] Step 1: Write failing tests for company size parsing, role normalization, Europe filtering, and duplicate selection.
- [ ] Step 2: Run `pytest tests/test_pipeline.py -q` and verify the new tests fail for the expected missing implementation reasons.
- [ ] Step 3: Implement the minimal pipeline helpers in `scripts/hcaptcha_pipeline.py`.
- [ ] Step 4: Re-run `pytest tests/test_pipeline.py -q` and make the tests pass.
- [ ] Step 5: Refactor only after green.

### Task 3: Notebook and Dataset Exports

**Files:**
- Create: `notebooks/hcaptcha_europe_positioning.ipynb`
- Modify: `scripts/hcaptcha_pipeline.py`

- [ ] Step 1: Build a notebook that loads the raw CSV, runs the pipeline, profiles anomalies, and computes strategic summaries.
- [ ] Step 2: Add blueprint visuals for geography, personas, company size, and distributed-operations analysis.
- [ ] Step 3: Export the gold dataset and supporting dimensions to `data/processed/`.
- [ ] Step 4: Execute the notebook and verify artifacts are written.

### Task 4: Verification

**Files:**
- Verify: `tests/test_pipeline.py`
- Verify: `notebooks/hcaptcha_europe_positioning.ipynb`
- Verify: `data/processed/`

- [ ] Step 1: Run `pytest -q`.
- [ ] Step 2: Execute the notebook with `jupyter nbconvert --to notebook --execute --inplace notebooks/hcaptcha_europe_positioning.ipynb`.
- [ ] Step 3: Confirm the processed CSVs exist and contain the expected columns.
- [ ] Step 4: Summarize analytical findings and any residual risks.
