# Isabellysto Data Command Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static-deployable immersive 3D command-center site backed by a sanitized JSON snapshot of the hCaptcha Europe analytics outputs.

**Architecture:** A Python sanitizer creates `sites/data-command-center/public/data/command-center.json` from the existing CSV and Markdown outputs, excluding person-level PII. A Vite React app under `sites/data-command-center/` consumes only that snapshot and renders a hybrid guided/exploratory 3D dashboard with React Three Fiber, D3 scales, Tailwind UI panels, and Framer Motion transitions.

**Tech Stack:** Python, pandas, pytest, React, Vite, TypeScript, React Three Fiber, Three.js, D3, Tailwind CSS, Framer Motion, Vitest, Playwright.

---

## File Structure

- Create `scripts/build_data_command_center_snapshot.py`: CLI and pure functions for safe JSON snapshot generation.
- Create `tests/test_data_command_center_snapshot.py`: sanitizer contract tests for privacy, aggregation, recommendations, and CLI output.
- Create `sites/data-command-center/package.json`: frontend package scripts and dependencies.
- Create `sites/data-command-center/index.html`: Vite HTML entry.
- Create `sites/data-command-center/vite.config.ts`: Vite + React config.
- Create `sites/data-command-center/tsconfig.json`: TypeScript settings.
- Create `sites/data-command-center/tailwind.config.js`: Tailwind content and theme tokens.
- Create `sites/data-command-center/postcss.config.js`: Tailwind/PostCSS bridge.
- Create `sites/data-command-center/src/main.tsx`: React entry.
- Create `sites/data-command-center/src/App.tsx`: app composition and state controller.
- Create `sites/data-command-center/src/styles.css`: Tailwind directives and global cyber-intelligence styling.
- Create `sites/data-command-center/src/lib/commandCenter.ts`: data loading, filtering, formatting, and scene layout helpers.
- Create `sites/data-command-center/src/lib/commandCenter.test.ts`: Vitest coverage for frontend data helpers.
- Create `sites/data-command-center/src/types.ts`: shared frontend data types.
- Create `sites/data-command-center/src/components/CommandScene.tsx`: React Three Fiber scene, modules, controls, and animated data geometry.
- Create `sites/data-command-center/src/components/HologramPanel.tsx`: reusable glass panel primitive.
- Create `sites/data-command-center/src/components/InterfaceShell.tsx`: top bar, module rail, telemetry, console, and filters.
- Create `sites/data-command-center/src/components/BootSequence.tsx`: cinematic boot overlay.
- Create `sites/data-command-center/public/data/command-center.json`: generated sanitized snapshot.
- Create `sites/data-command-center/tests/command-center.spec.ts`: Playwright smoke test for nonblank 3D canvas and core interactions.
- Create `sites/data-command-center/playwright.config.ts`: Playwright web server and screenshot settings.

---

### Task 1: Sanitizer Tests

**Files:**
- Create: `tests/test_data_command_center_snapshot.py`

- [ ] **Step 1: Write the failing sanitizer tests**

Create tests that build tiny source CSV/Markdown fixtures in `tmp_path`, call the sanitizer API, and assert:

```python
from scripts.build_data_command_center_snapshot import build_snapshot, write_snapshot

def test_snapshot_excludes_person_level_pii(tmp_path):
    paths = make_fixture_files(tmp_path)
    snapshot = build_snapshot(paths)
    forbidden = {"email", "first_name", "last_name", "full_name", "linkedin_url", "contact_location"}
    encoded = json.dumps(snapshot)
    for key in forbidden:
        assert key not in encoded

def test_snapshot_preserves_aggregate_totals_and_company_records(tmp_path):
    paths = make_fixture_files(tmp_path)
    snapshot = build_snapshot(paths)
    assert snapshot["metadata"]["source_rows"] == 4
    assert snapshot["metadata"]["unique_companies"] == 3
    assert snapshot["market"][0]["company_country"] == "Germany"
    assert snapshot["companies"][0]["lead_count"] == 2
    assert {"company_name", "company_country", "company_industry", "company_size_segment", "lead_count", "role_mix", "priority_tier"} <= set(snapshot["companies"][0])

def test_write_snapshot_creates_json_file(tmp_path):
    paths = make_fixture_files(tmp_path)
    output = tmp_path / "public" / "data" / "command-center.json"
    write_snapshot(build_snapshot(paths), output)
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["metadata"]["privacy_level"] == "Level 2: Aggregates + Companies"
```

- [ ] **Step 2: Run tests to verify RED**

Run: `pytest tests/test_data_command_center_snapshot.py -v`

Expected: FAIL because `scripts.build_data_command_center_snapshot` does not exist.

---

### Task 2: Sanitizer Implementation

**Files:**
- Create: `scripts/build_data_command_center_snapshot.py`
- Modify: `tests/test_data_command_center_snapshot.py` if an assertion needs a more precise fixture expectation.

- [ ] **Step 1: Implement the sanitizer module**

Implement:

```python
@dataclass(frozen=True)
class SnapshotPaths:
    gold: Path
    country_priority: Path
    role_category: Path
    company_size: Path
    summary: Path
    quality_report: Path | None = None

def build_snapshot(paths: SnapshotPaths, generated_at: str | None = None) -> dict[str, Any]:
    ...

def write_snapshot(snapshot: Mapping[str, Any], output_path: Path) -> None:
    ...

def main(argv: Sequence[str] | None = None) -> int:
    ...
```

The implementation must:

- Read source files with pandas.
- Group company records by safe company fields.
- Include top companies only as company-level records.
- Exclude person-level fields entirely.
- Fail if forbidden PII keys appear in the JSON output.
- Provide CLI arguments for each source path and output path, with defaults matching the repository.

- [ ] **Step 2: Run sanitizer tests to verify GREEN**

Run: `pytest tests/test_data_command_center_snapshot.py -v`

Expected: PASS.

- [ ] **Step 3: Run existing Python test suite**

Run: `pytest`

Expected: all tests pass.

- [ ] **Step 4: Commit sanitizer work**

Run:

```bash
git add scripts/build_data_command_center_snapshot.py tests/test_data_command_center_snapshot.py
git commit -m "feat: add command center data snapshot"
```

---

### Task 3: Frontend Scaffold And Data Helper Tests

**Files:**
- Create: `sites/data-command-center/package.json`
- Create: `sites/data-command-center/index.html`
- Create: `sites/data-command-center/vite.config.ts`
- Create: `sites/data-command-center/tsconfig.json`
- Create: `sites/data-command-center/tailwind.config.js`
- Create: `sites/data-command-center/postcss.config.js`
- Create: `sites/data-command-center/src/lib/commandCenter.test.ts`

- [ ] **Step 1: Create frontend package config**

Create package scripts:

```json
{
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "tsc --noEmit && vite build",
    "test": "vitest run",
    "test:e2e": "playwright test"
  }
}
```

- [ ] **Step 2: Install frontend dependencies**

Run: `npm install` inside `sites/data-command-center`.

Expected: dependencies resolve and `package-lock.json` is created.

- [ ] **Step 3: Write failing frontend helper tests**

Create tests for `getFilteredCompanies`, `getModuleCopy`, `createCountrySceneLayout`, and `formatPercent`.

Run: `npm test -- src/lib/commandCenter.test.ts`

Expected: FAIL because `src/lib/commandCenter.ts` does not exist.

---

### Task 4: Frontend Data Helpers

**Files:**
- Create: `sites/data-command-center/src/types.ts`
- Create: `sites/data-command-center/src/lib/commandCenter.ts`

- [ ] **Step 1: Implement frontend data helper module**

Implement:

- `formatPercent(value: number): string`
- `getFilteredCompanies(snapshot, filters): SafeCompany[]`
- `getModuleCopy(activeModule, snapshot): string[]`
- `createCountrySceneLayout(market): CountrySceneNode[]`
- `tierColor(tier, angle): string`

- [ ] **Step 2: Run frontend helper tests**

Run: `npm test -- src/lib/commandCenter.test.ts`

Expected: PASS.

- [ ] **Step 3: Commit scaffold and helpers**

Run:

```bash
git add sites/data-command-center
git commit -m "feat: scaffold data command center frontend"
```

---

### Task 5: React UI And 3D Scene

**Files:**
- Create: `sites/data-command-center/src/main.tsx`
- Create: `sites/data-command-center/src/App.tsx`
- Create: `sites/data-command-center/src/styles.css`
- Create: `sites/data-command-center/src/components/BootSequence.tsx`
- Create: `sites/data-command-center/src/components/CommandScene.tsx`
- Create: `sites/data-command-center/src/components/HologramPanel.tsx`
- Create: `sites/data-command-center/src/components/InterfaceShell.tsx`

- [ ] **Step 1: Implement the application shell**

Build the state controller for:

- `booting`
- `activeModule`
- `unlocked`
- selected country
- filters for tier, country, company size, role category, and messaging angle

- [ ] **Step 2: Implement the 3D scene**

Render:

- fogged deep navy scene
- infinite-feeling grid
- emissive central hub
- country volumetric bars
- persona scatter/matrix points
- recommendation arcs/pulses
- orbit controls only when unlocked

- [ ] **Step 3: Implement holographic UI panels**

Render:

- top status bar
- left module rail
- right telemetry panel
- bottom narrative console
- filter controls in unlocked mode
- bounded top-company list

- [ ] **Step 4: Add global styling**

Use Tailwind and custom CSS for the dark cyber-intelligence system, glass panels, readable controls, and responsive layout.

- [ ] **Step 5: Run frontend build**

Run: `npm run build`

Expected: TypeScript and Vite build pass.

- [ ] **Step 6: Commit UI work**

Run:

```bash
git add sites/data-command-center
git commit -m "feat: build immersive command center UI"
```

---

### Task 6: Snapshot Generation And E2E Verification

**Files:**
- Create: `sites/data-command-center/playwright.config.ts`
- Create: `sites/data-command-center/tests/command-center.spec.ts`
- Create/Generate: `sites/data-command-center/public/data/command-center.json`

- [ ] **Step 1: Generate sanitized snapshot**

Run from repository root:

```bash
python scripts/build_data_command_center_snapshot.py --output sites/data-command-center/public/data/command-center.json
```

Expected: `command-center.json` contains Level 2 data only.

- [ ] **Step 2: Write Playwright smoke test**

The test must:

- Open the local app.
- Confirm the boot screen appears.
- Confirm the canvas is present.
- Sample screenshot pixels or canvas data to confirm nonblank rendering.
- Click "Unlock" and confirm filters appear.

- [ ] **Step 3: Run full verification**

Run:

```bash
pytest
npm test
npm run build
npm run test:e2e
```

Expected: all commands pass.

- [ ] **Step 4: Commit generated snapshot and verification files**

Run:

```bash
git add sites/data-command-center
git commit -m "test: verify data command center experience"
```

---

### Task 7: Documentation And Local Launch

**Files:**
- Create: `sites/data-command-center/README.md`
- Modify: root `README.md` to link the command-center site.

- [ ] **Step 1: Document usage**

Document:

- snapshot regeneration command
- local dev command
- static build command
- privacy boundary
- deployment note for Vercel/Netlify/static hosting

- [ ] **Step 2: Run final verification**

Run:

```bash
pytest
npm --prefix sites/data-command-center test
npm --prefix sites/data-command-center run build
```

Expected: all commands pass.

- [ ] **Step 3: Start local dev server**

Run:

```bash
npm --prefix sites/data-command-center run dev -- --port 5173
```

Expected: server starts on a local URL.

- [ ] **Step 4: Commit docs**

Run:

```bash
git add README.md sites/data-command-center/README.md
git commit -m "docs: add command center usage"
```

---

## Self-Review

- Spec coverage: the tasks cover the sanitizer, safe Level 2 JSON, React/R3F frontend, D3 helper calculations, Tailwind/Framer UI, hybrid flow, local/static deployment, data tests, frontend tests, and Playwright verification.
- Placeholder scan: no task relies on unspecified future implementation; each task names files, commands, and expected outcomes.
- Type consistency: backend snapshot sections match frontend types: `metadata`, `market`, `personas`, `segments`, `companies`, `recommendations`, and `narrative`.
