import { describe, expect, it } from 'vitest';
import type { CommandCenterSnapshot } from '../types';
import {
  createCountrySceneLayout,
  formatPercent,
  getFilteredCompanies,
  getModuleCopy,
  tierColor,
} from './commandCenter';

const snapshot: CommandCenterSnapshot = {
  metadata: {
    generated_at: '2026-04-25T00:00:00Z',
    privacy_level: 'Level 2: Aggregates + Companies',
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
  ],
  segments: [
    {
      company_size_segment: '3. Enterprise',
      lead_count: 2,
      company_count: 1,
      lead_share: 0.5,
    },
  ],
  companies: [
    {
      company_name: 'Acme Security',
      company_country: 'Germany',
      company_industry: 'Cybersecurity',
      company_size_segment: '3. Enterprise',
      lead_count: 2,
      role_mix: {
        'Data / Compliance': 1,
        'Executive / Technical Decision Maker': 1,
      },
      priority_tier: 'Tier 1',
      messaging_angle: 'Privacy-first and GDPR-safe alternative to reCAPTCHA',
      strategic_recommendation: 'Target Germany with privacy-first messaging.',
    },
    {
      company_name: 'Vector SaaS',
      company_country: 'United Kingdom',
      company_industry: 'Computer Software',
      company_size_segment: '2. Mid-Market',
      lead_count: 1,
      role_mix: {
        'Executive / Technical Decision Maker': 1,
      },
      priority_tier: 'Tier 1',
      messaging_angle: 'Developer efficiency and scalable anti-bot performance',
      strategic_recommendation: 'Target United Kingdom with scale-first messaging.',
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
};

describe('command center helpers', () => {
  it('formats percentages for telemetry panels', () => {
    expect(formatPercent(0.4126)).toBe('41.3%');
  });

  it('filters companies across country, tier, segment and role', () => {
    const companies = getFilteredCompanies(snapshot, {
      country: 'Germany',
      tier: 'Tier 1',
      companySize: '3. Enterprise',
      roleCategory: 'Data / Compliance',
      messagingAngle: 'Privacy-first and GDPR-safe alternative to reCAPTCHA',
    });

    expect(companies).toHaveLength(1);
    expect(companies[0].company_name).toBe('Acme Security');
  });

  it('creates deterministic country scene layout with larger volumes taller than smaller ones', () => {
    const layout = createCountrySceneLayout(snapshot.market);

    expect(layout.map((node) => node.country)).toEqual(['Germany', 'United Kingdom']);
    expect(layout[0].height).toBeGreaterThan(layout[1].height);
    expect(layout[0].position).toHaveLength(3);
  });

  it('returns narrative copy for each story module', () => {
    expect(getModuleCopy('market', snapshot)[0]).toContain('Germany');
    expect(getModuleCopy('icp', snapshot)[0]).toContain('Executive');
    expect(getModuleCopy('recommendations', snapshot)[0]).toContain('Privacy-first');
  });

  it('maps strategic tiers and angles to stable emissive colors', () => {
    expect(tierColor('Tier 1', 'Privacy-first and GDPR-safe alternative to reCAPTCHA')).toBe('#22d3ee');
    expect(tierColor('Tier 2', 'Developer efficiency and scalable anti-bot performance')).toBe('#a78bfa');
  });
});
