import { describe, expect, it } from 'vitest';
import type { MarketCountry, PresentationFocus, PresentationSnapshot, PersonaMetric, SegmentMetric } from '../types';
import {
  getFilterHelp,
  getSlideAudienceText,
  getSlidePresenterText,
  liveSlides,
  recommendationForMarket,
  stripSegment,
} from './presentationContent';

const market: MarketCountry = {
  company_country: 'Germany',
  lead_count: 277,
  company_count: 254,
  executive_share: 0.69,
  compliance_share: 0.18,
  mismatch_share: 0.05,
  country_rank: 1,
  priority_tier: 'Tier 1',
  messaging_angle: 'Privacy-first and GDPR-safe alternative to reCAPTCHA',
  strategic_recommendation: 'Target Germany with privacy-first messaging.',
};

const persona: PersonaMetric = {
  role_category: 'Executive / Technical Decision Maker',
  lead_count: 364,
  company_count: 346,
  lead_share: 0.412698,
};

const segment: SegmentMetric = {
  company_size_segment: '3. Enterprise',
  lead_count: 378,
  company_count: 315,
  lead_share: 0.428571,
};

const snapshot = {
  metadata: {
    source_rows: 882,
    unique_companies: 748,
  },
} as PresentationSnapshot;

const focus = {
  filterSummary: 'Europa: 880 leads em 748 empresas para persona todos e porte todos.',
  filteredLeadCount: 880,
  filteredCompanyCount: 748,
} as PresentationFocus;

describe('presentation content', () => {
  it('keeps the live deck compact and reader-ready', () => {
    expect(liveSlides).toHaveLength(10);
    expect(liveSlides.map((slide) => slide.id)).toEqual([
      'challenge',
      'data',
      'market',
      'personas',
      'segments',
      'behavior',
      'barriers',
      'dashboard',
      'process',
      'recommendation',
    ]);
  });

  it('formats final recommendations in Portuguese instead of exposing raw generated copy', () => {
    expect(recommendationForMarket(market)).toContain('priorizar Alemanha');
    expect(recommendationForMarket(market)).not.toContain('Target Germany');
  });

  it('builds presenter text from the selected segment and focus', () => {
    expect(stripSegment(segment.company_size_segment)).toBe('Enterprise');
    expect(getSlidePresenterText('recommendation', snapshot, focus, market, persona, segment)).toContain('880 leads em 748 empresas');
    expect(getFilterHelp('market', focus)).toContain('Recorte atual');
  });

  it('keeps audience slide text shorter than presenter notes', () => {
    const audienceText = getSlideAudienceText('challenge', snapshot, focus, market, persona, segment);
    const presenterText = getSlidePresenterText('challenge', snapshot, focus, market, persona, segment);

    expect(audienceText).toContain('GDPR');
    expect(audienceText).toContain('base gold');
    expect(audienceText.length).toBeLessThan(presenterText.length);
    expect(audienceText.length).toBeGreaterThan(220);
    expect(audienceText).not.toContain('Eu comeco');
  });

  it('adds challenge-critical behavior and barrier slides', () => {
    expect(getSlideAudienceText('behavior', snapshot, focus, market, persona, segment)).toContain('propensao');
    expect(getSlideAudienceText('barriers', snapshot, focus, market, persona, segment)).toContain('barreiras');
    expect(getFilterHelp('dashboard', focus)).toContain('pergunta do desafio');
  });
});
