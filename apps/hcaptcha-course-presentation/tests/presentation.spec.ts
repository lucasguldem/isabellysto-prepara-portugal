import { expect, test } from '@playwright/test';

test('shows the generated PDF and final reader-ready presentation filters', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: /Posicionamento europeu da hCaptcha/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: /A hCaptcha deve se posicionar como alternativa anti-bot/i })).toBeVisible();
  await expect(page.getByRole('navigation', { name: /Slides da apresentacao/i })).toBeVisible();
  await expect(page.locator('iframe[title="Previa HTML do PDF final"]')).toBeVisible();
  await expect(page.getByLabel('Pais')).toBeVisible();
  await expect(page.getByLabel('Persona')).toBeVisible();
  await expect(page.getByLabel('Porte')).toBeVisible();
  await expect(page.getByText('Frase de defesa')).toHaveCount(0);
  await expect(page.getByText('Contas para citar na apresentacao')).toHaveCount(0);
  await expect(page.getByText('Roteiro de fala')).toHaveCount(0);
  await expect(page.getByText('Roteiro completo da apresentacao')).toHaveCount(0);
  await expect(page.locator('.speaker-notes')).toHaveCount(0);
  await expect(page.locator('.script-panel')).toHaveCount(0);
  await expect(page.getByText('A resposta ao desafio e que a hCaptcha deve entrar na Europa')).toHaveCount(0);
  await expect(page.getByText('Astara')).toHaveCount(0);
  await expect(page.getByText('PandaScore')).toHaveCount(0);
  await expect(page.getByRole('heading', { name: /Glossario tecnico/i })).toBeVisible();
  await expect(page.getByText('ETL')).toBeVisible();
  await expect(page.getByText('Proxy firmografico')).toBeVisible();
  await expect(page.getByRole('link', { name: /Abrir glossario/i })).toHaveAttribute('href', '/glossario-termos-tecnicos.pdf');

  await page.getByRole('button', { name: /03 · Mercados/i }).click();
  await page.getByLabel('Pais').selectOption('Germany');
  await page.getByLabel('Persona').selectOption('Data / Compliance');

  await expect(page.locator('.focus-box')).toContainText('Privacy-first');
  await expect(page.locator('.filter-help')).toContainText('Data / Compliance');
  await expect(page.locator('.live-stage')).toContainText(/Germany|Europa/);
});

test('presents dynamic charts and a decision flow as final live slides', async ({ page }) => {
  await page.goto('/');

  await page.getByRole('button', { name: /03 · Mercados/i }).click();
  await expect(page.locator('.chart-bars')).toBeVisible();
  await expect(page.locator('.bar-fill').first()).toBeVisible();

  await page.getByRole('button', { name: /06 · Sinais/i }).click();
  await expect(page.locator('.signal-board')).toContainText('Compradores qualificados');
  await expect(page.locator('.signal-board')).toContainText('Operacao distribuida');

  await page.getByRole('button', { name: /07 · Barreiras/i }).click();
  await expect(page.locator('.barrier-board')).toContainText('Privacidade e GDPR');
  await expect(page.locator('.barrier-board')).toContainText('Inercia do reCAPTCHA');

  await page.getByRole('button', { name: /08 · Dashboard/i }).click();
  await expect(page.locator('.coverage-board')).toContainText('Dashboard interativo e relatorio');

  await page.getByRole('button', { name: /09 · Processo/i }).click();
  await expect(page.locator('.live-stage .decision-flow')).toContainText('Enunciado');
  await expect(page.locator('.live-stage .decision-flow')).toContainText('Recomendacao');
  await expect(page.getByLabel('Trilha completa de decisao do projeto')).toContainText('Do dado bruto a decisao comercial');
  await expect(page.getByText('Fluxograma usado para chegar na recomendacao')).toHaveCount(0);
});

test('embeds the updated PDF HTML instead of the previous deck copy', async ({ page }) => {
  await page.goto('/');

  const deckFrame = page.frameLocator('iframe[title="Previa HTML do PDF final"]');
  await expect(deckFrame.getByRole('heading', { name: /A hCaptcha deve se posicionar como alternativa anti-bot/i })).toBeVisible();
  await expect(deckFrame.getByText('hCaptcha deve entrar com privacidade e escala tecnica')).toHaveCount(0);
  await expect(deckFrame.getByText('Contas para citar')).toHaveCount(0);
  await expect(page.locator('iframe[title="Previa HTML do glossario tecnico"]')).toBeVisible();
});

test('keeps the pixel presentation layout readable on desktop and mobile', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto('/');

  const liveStage = await page.locator('.live-stage').boundingBox();
  const controls = await page.locator('.presentation-controls').boundingBox();

  expect(liveStage?.width).toBeGreaterThan(760);
  expect(controls?.width).toBeGreaterThan(760);

  await page.setViewportSize({ width: 412, height: 915 });
  await page.goto('/');
  await expect(page.locator('.live-stage')).toBeVisible();
  await expect(page.getByRole('heading', { name: /Do dado bruto a decisao comercial/i })).toBeVisible();
});
