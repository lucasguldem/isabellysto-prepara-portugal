import { describe, expect, it } from 'vitest';

const { readFileSync } = (await import('node:' + 'fs')) as {
  readFileSync: (path: URL | string, encoding: 'utf8') => string;
};
const appSource = readFileSync(new URL('./App.tsx', import.meta.url), 'utf8');
const stylesSource = readFileSync(new URL('./styles.css', import.meta.url), 'utf8');

describe('style contract', () => {
  it('does not keep selectors from removed presentation layouts', () => {
    const removedSelectors = [
      'challenge-section',
      'process-section',
      'challenge-grid',
      'challenge-card',
      'process-grid',
      'process-step',
      'workbench',
      'deck-frame',
      'deck-toolbar',
      'control-panel',
      'filters',
      'company-list',
      'company-card',
      'empty-copy',
      'speaker-notes',
      'script-panel',
    ];

    removedSelectors.forEach((selector) => {
      expect(appSource).not.toMatch(new RegExp(`className=["'][^"']*${selector}`));
      expect(stylesSource).not.toContain(`.${selector}`);
    });
  });

  it('does not hide final presentation content behind entry animations', () => {
    const removedAnimations = ['boot-up', 'slide-swap', 'card-pop', 'row-in', 'grow-bar', 'panel-pulse'];

    removedAnimations.forEach((animation) => {
      expect(stylesSource).not.toContain(animation);
    });
  });

  it('keeps presenter-only script copy out of the public site', () => {
    expect(appSource).not.toContain('Roteiro de fala');
    expect(appSource).not.toContain('Roteiro completo da apresentacao');
    expect(appSource).not.toContain('getSlidePresenterText');
  });
});
