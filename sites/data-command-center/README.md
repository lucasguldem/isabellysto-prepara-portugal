# Isabellysto Data Command Center

Immersive 3D presentation site for the hCaptcha Europe positioning analysis.

## Data Boundary

The frontend reads only `public/data/command-center.json`, a Level 2 sanitized snapshot with:

- aggregate market, persona, segment and recommendation metrics
- safe company-level records
- no personal names, emails, LinkedIn URLs or contact-level fields

## Regenerate Data

From the repository root:

```bash
python scripts/build_data_command_center_snapshot.py \
  --output sites/data-command-center/public/data/command-center.json
```

## Run Locally

```bash
npm --prefix sites/data-command-center install
npm --prefix sites/data-command-center run dev -- --port 5173
```

## Verify

```bash
pytest
npm --prefix sites/data-command-center test
npm --prefix sites/data-command-center run build
npm --prefix sites/data-command-center run test:e2e
```

## Static Deploy

The app is Vite-based and deploys as a static build:

```bash
npm --prefix sites/data-command-center run build
```

Deploy `sites/data-command-center/dist/` to Vercel, Netlify or any static host after confirming the generated JSON is safe to publish.
