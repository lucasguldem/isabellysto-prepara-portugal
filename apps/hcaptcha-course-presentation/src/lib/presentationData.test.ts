import { describe, expect, it } from 'vitest';
import type { PresentationSnapshot } from '../types';
import {
  ALL_FILTER,
  DECK_PDF_PATH,
  GLOSSARY_PDF_PATH,
  formatNumber,
  formatPercent,
  getFilteredCountryMetrics,
  getFilteredPersonaMetrics,
  getFilteredSegmentMetrics,
  getPresentationFocus,
  getPresentationOptions,
} from './presentationData';

const snapshot: PresentationSnapshot = {
  metadata: {
    generated_at: '2026-05-01T00:00:00Z',
    privacy_level: 'Level 1: Aggregates + Anonymous Companies',
    source_rows: 4,
    unique_companies: 3,
    source_files: {
      gold: 'gold.csv',
      country_priority: 'country.csv',
      role_category: 'role.csv',
      company_size: 'size.csv',
      summary: 'summary.md',
    },
    quality_decision: 'approved',
  },
  market: [
    {
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
    },
    {
      company_country: 'United Kingdom',
      lead_count: 174,
      company_count: 138,
      executive_share: 0.34,
      compliance_share: 0.58,
      mismatch_share: 0.18,
      country_rank: 2,
      priority_tier: 'Tier 1',
      messaging_angle: 'Developer efficiency and scalable anti-bot performance',
      strategic_recommendation: 'Target United Kingdom with scale-first messaging.',
    },
  ],
  personas: [
    {
      role_category: 'Executive / Technical Decision Maker',
      lead_count: 2,
      company_count: 2,
      lead_share: 0.5,
    },
    {
      role_category: 'Data / Compliance',
      lead_count: 1,
      company_count: 1,
      lead_share: 0.25,
    },
  ],
  segments: [
    {
      company_size_segment: '3. Enterprise',
      lead_count: 2,
      company_count: 1,
      lead_share: 0.5,
    },
    {
      company_size_segment: '2. Mid-Market',
      lead_count: 1,
      company_count: 1,
      lead_share: 0.25,
    },
  ],
  companies: [
    {
      company_country: 'Germany',
      company_size_segment: '3. Enterprise',
      lead_count: 2,
      role_mix: {
        'Data / Compliance': 1,
        'Executive / Technical Decision Maker': 1,
      },
    },
    {
      company_country: 'Germany',
      company_size_segment: '1. Startup / SMB',
      lead_count: 3,
      role_mix: {
        'Data / Compliance': 3,
      },
    },
    {
      company_country: 'United Kingdom',
      company_size_segment: '2. Mid-Market',
      lead_count: 1,
      role_mix: {
        'Executive / Technical Decision Maker': 1,
      },
    },
  ],
  recommendations: [
    {
      track: 'Privacy-first',
      countries: ['Germany'],
      message: 'Lead with privacy.',
    },
  ],
  narrative: [
    {
      level: 'INFO',
      message: 'Gold dataset loaded.',
    },
  ],
  adoption_signals: [
    {
      signal: 'Concentracao geografica',
      value: '88.4%',
      detail: 'Top mercados concentram a base.',
      interpretation: 'Foco comercial.',
      strength: 'Alta',
    },
  ],
  barriers: [
    {
      theme: 'Privacidade e GDPR',
      barrier: 'Diligencia de dados.',
      opportunity: 'Mensagem privacy-first.',
      move: 'Abrir com compliance.',
    },
  ],
  action_plan: [
    {
      phase: '0-30 dias',
      focus: 'Validar tese',
      markets: 'Germany',
      buyer: 'Compliance',
      message: 'Privacidade.',
      kpi: 'Reunioes qualificadas.',
    },
  ],
  challenge_coverage: [
    {
      requirement: 'Perfis dos potenciais clientes',
      status: 'Coberto',
      evidence: 'Personas mapeadas.',
      artifact: 'Power BI.',
    },
  ],
  glossary_terms: [
    {
      term: 'ETL',
      category: 'Metodologia',
      definition: 'Processo de extrair, transformar e carregar dados.',
      in_project: 'Pipeline Python que cria a base gold.',
      why_it_matters: 'Garante que a analise nasce de dados tratados.',
    },
  ],
};

describe('presentation helpers', () => {
  it('keeps the generated deck path stable for the embedded PDF viewer', () => {
    expect(DECK_PDF_PATH).toBe('/hcaptcha-positioning-deck.pdf');
    expect(GLOSSARY_PDF_PATH).toBe('/glossario-termos-tecnicos.pdf');
  });

  it('formats values for presentation cards', () => {
    expect(formatNumber(1027)).toBe('1,027');
    expect(formatPercent(0.4126)).toBe('41.3%');
  });

  it('derives filter options for the presentation controls', () => {
    expect(getPresentationOptions(snapshot)).toEqual({
      countries: [ALL_FILTER, 'Germany', 'United Kingdom'],
      personas: [ALL_FILTER, 'Data / Compliance', 'Executive / Technical Decision Maker'],
      segments: [ALL_FILTER, '2. Mid-Market', '3. Enterprise'],
    });
  });

  it('builds a focused presentation view from country, persona and segment filters', () => {
    const focus = getPresentationFocus(snapshot, {
      country: 'Germany',
      persona: 'Data / Compliance',
      segment: '3. Enterprise',
    });

    expect(focus.market?.company_country).toBe('Germany');
    expect(focus.persona?.role_category).toBe('Data / Compliance');
    expect(focus.segment?.company_size_segment).toBe('3. Enterprise');
    expect(focus.filteredLeadCount).toBe(1);
    expect(focus.filteredCompanyCount).toBe(1);
    expect(focus.filterSummary).toContain('1 lead');
    expect(focus.filterSummary).toContain('Germany');
    expect(focus.headline).toContain('Germany');
  });

  it('recalculates persona metrics for the selected country and segment instead of using global totals', () => {
    const metrics = getFilteredPersonaMetrics(snapshot, {
      country: 'Germany',
      persona: ALL_FILTER,
      segment: '1. Startup / SMB',
    });

    expect(metrics).toEqual([
      {
        role_category: 'Data / Compliance',
        lead_count: 3,
        company_count: 1,
        lead_share: 1,
      },
    ]);
  });

  it('recalculates segment metrics for the selected country and persona instead of using global totals', () => {
    const metrics = getFilteredSegmentMetrics(snapshot, {
      country: 'Germany',
      persona: 'Data / Compliance',
      segment: ALL_FILTER,
    });

    expect(metrics).toEqual([
      {
        company_size_segment: '1. Startup / SMB',
        lead_count: 3,
        company_count: 1,
        lead_share: 0.75,
      },
      {
        company_size_segment: '3. Enterprise',
        lead_count: 1,
        company_count: 1,
        lead_share: 0.25,
      },
    ]);
  });

  it('recalculates country metrics for selected persona and segment filters', () => {
    const metrics = getFilteredCountryMetrics(snapshot, {
      country: ALL_FILTER,
      persona: 'Executive / Technical Decision Maker',
      segment: '2. Mid-Market',
    });

    expect(metrics.map((country) => [country.company_country, country.lead_count, country.company_count])).toEqual([
      ['United Kingdom', 1, 1],
    ]);
  });

  it('falls back to top-level story when filters are set to all', () => {
    const focus = getPresentationFocus(snapshot, {
      country: ALL_FILTER,
      persona: ALL_FILTER,
      segment: ALL_FILTER,
    });

    expect(focus.market?.company_country).toBe('Germany');
    expect(focus.persona?.role_category).toBe('Data / Compliance');
    expect(focus.segment?.company_size_segment).toBe('1. Startup / SMB');
    expect(focus.filteredLeadCount).toBe(6);
    expect(focus.filteredCompanyCount).toBe(3);
  });
});
