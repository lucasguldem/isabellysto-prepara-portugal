# hCaptcha Course Presentation

PDF-backed interactive presentation for the hCaptcha Europe positioning challenge.

## Data Boundary

The frontend reads only `public/data/presentation-snapshot.json`, a Level 2 sanitized snapshot with:

- aggregate market, persona, segment and recommendation metrics
- safe company-level records
- no personal names, emails, LinkedIn URLs or contact-level fields

## Regenerate Data

From the repository root:

```bash
python scripts/build_presentation_snapshot.py \
  --output apps/hcaptcha-course-presentation/public/data/presentation-snapshot.json
```

## Run Locally

```bash
npm --prefix apps/hcaptcha-course-presentation install
npm --prefix apps/hcaptcha-course-presentation run dev -- --port 5174
```

## Verify

```bash
pytest
npm --prefix apps/hcaptcha-course-presentation test
npm --prefix apps/hcaptcha-course-presentation run build
npm --prefix apps/hcaptcha-course-presentation run test:e2e
```

## Static Deploy

The app is Vite-based and deploys as a static build:

```bash
npm --prefix apps/hcaptcha-course-presentation run build
```

Deploy `apps/hcaptcha-course-presentation/dist/` to Vercel, Netlify or any static host after confirming the generated JSON is safe to publish.
