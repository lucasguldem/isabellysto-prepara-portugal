import { expect, test } from '@playwright/test';

test('renders a nonblank 3D command center and unlocks exploration', async ({ page }, testInfo) => {
  await page.goto('/');

  await expect(page.getByText('System Boot')).toBeVisible();
  await page.getByRole('button', { name: /Enter Command Center/i }).click();

  const canvas = page.locator('canvas').first();
  await expect(canvas).toBeVisible();
  await expect(page.locator('.top-status strong')).toHaveText('Isabellysto Data Command Center');
  await page.waitForTimeout(900);

  const nonBlank = await canvas.evaluate((element) => {
    const canvasElement = element as HTMLCanvasElement;
    const gl =
      canvasElement.getContext('webgl2', { preserveDrawingBuffer: true }) ??
      canvasElement.getContext('webgl', { preserveDrawingBuffer: true });
    if (!gl) return false;
    const width = Math.max(canvasElement.width, 1);
    const height = Math.max(canvasElement.height, 1);
    const pixels = new Uint8Array(4);
    gl.readPixels(Math.floor(width / 2), Math.floor(height / 2), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    return pixels[0] + pixels[1] + pixels[2] > 0;
  });
  expect(nonBlank).toBe(true);

  await page.getByRole('button', { name: /Unlock Exploration/i }).click();
  await expect(page.getByText('Filters Online')).toBeVisible();
  await expect(page.locator('select').first()).toBeVisible();

  await page.screenshot({
    path: `test-results/command-center-${testInfo.project.name}.png`,
    fullPage: true,
  });
});
