import { scaleLinear } from 'd3-scale';
import type {
  CommandCenterFilters,
  CommandCenterSnapshot,
  CountrySceneNode,
  MarketCountry,
  SafeCompany,
  StoryModule,
} from '../types';

export const ALL_FILTER = 'All';

const COUNTRY_COORDINATES: Record<string, [number, number]> = {
  Germany: [0.8, 0.3],
  'United Kingdom': [-1.9, 0.7],
  France: [-0.5, -0.35],
  Spain: [-1.0, -1.35],
  Portugal: [-1.55, -1.55],
  Poland: [1.6, 0.45],
  Belgium: [-0.65, 0.25],
  Ireland: [-2.3, 0.55],
  Lithuania: [2.0, 0.85],
  Estonia: [2.1, 1.35],
  Italy: [0.35, -1.25],
  Netherlands: [-0.45, 0.55],
  Switzerland: [0.05, -0.55],
};

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function tierColor(tier: string, angle: string): string {
  if (tier === 'Tier 1' && angle.toLowerCase().includes('privacy')) {
    return '#22d3ee';
  }
  if (angle.toLowerCase().includes('developer') || angle.toLowerCase().includes('scale')) {
    return '#a78bfa';
  }
  if (tier === 'Tier 1') {
    return '#38bdf8';
  }
  if (tier === 'Tier 2') {
    return '#f59e0b';
  }
  return '#64748b';
}

export function getFilteredCompanies(
  snapshot: CommandCenterSnapshot,
  filters: CommandCenterFilters,
): SafeCompany[] {
  return snapshot.companies
    .filter((company) => filters.country === ALL_FILTER || company.company_country === filters.country)
    .filter((company) => filters.tier === ALL_FILTER || company.priority_tier === filters.tier)
    .filter((company) => filters.companySize === ALL_FILTER || company.company_size_segment === filters.companySize)
    .filter((company) => filters.messagingAngle === ALL_FILTER || company.messaging_angle === filters.messagingAngle)
    .filter((company) => filters.roleCategory === ALL_FILTER || company.role_mix[filters.roleCategory] > 0)
    .sort((a, b) => b.lead_count - a.lead_count || a.company_name.localeCompare(b.company_name));
}

export function createCountrySceneLayout(market: MarketCountry[]): CountrySceneNode[] {
  const maxLeads = Math.max(...market.map((country) => country.lead_count), 1);
  const heightScale = scaleLinear().domain([0, maxLeads]).range([0.55, 3.7]);
  const radiusScale = scaleLinear().domain([0, maxLeads]).range([0.14, 0.46]);

  return [...market]
    .sort((a, b) => a.country_rank - b.country_rank)
    .map((country, index) => {
      const fallbackAngle = (index / Math.max(market.length, 1)) * Math.PI * 2;
      const fallbackRadius = 3.1 + (index % 3) * 0.35;
      const mapped = COUNTRY_COORDINATES[country.company_country] ?? [
        Math.cos(fallbackAngle) * fallbackRadius,
        Math.sin(fallbackAngle) * fallbackRadius,
      ];
      const x = mapped[0] * 2.1;
      const z = mapped[1] * 2.1;
      const height = heightScale(country.lead_count);
      return {
        country: country.company_country,
        rank: country.country_rank,
        leads: country.lead_count,
        companies: country.company_count,
        tier: country.priority_tier,
        messagingAngle: country.messaging_angle,
        color: tierColor(country.priority_tier, country.messaging_angle),
        height,
        radius: radiusScale(country.lead_count),
        position: [x, height / 2, z] as [number, number, number],
      };
    });
}

export function getModuleCopy(activeModule: StoryModule, snapshot: CommandCenterSnapshot): string[] {
  const topCountry = snapshot.market[0];
  const topPersona = snapshot.personas[0];
  const topSegment = snapshot.segments[0];
  const topRecommendation = snapshot.recommendations[0];

  if (activeModule === 'market') {
    return [
      `${topCountry.company_country} leads the market map with ${topCountry.lead_count} leads across ${topCountry.company_count} companies.`,
      `Tier density concentrates around ${snapshot.market.filter((country) => country.priority_tier === 'Tier 1').length} Tier 1 countries.`,
    ];
  }

  if (activeModule === 'icp') {
    return [
      `${topPersona.role_category} is the dominant buying-center signal at ${formatPercent(topPersona.lead_share)} of leads.`,
      `${topSegment.company_size_segment.replace(/^\d+\.\s*/, '')} carries the strongest company-size signal.`,
    ];
  }

  if (activeModule === 'recommendations') {
    return [
      `${topRecommendation.track} countries: ${topRecommendation.countries.join(', ') || 'None'}.`,
      topRecommendation.message,
    ];
  }

  return snapshot.narrative.slice(0, 4).map((line) => line.message);
}

export async function loadCommandCenterSnapshot(): Promise<CommandCenterSnapshot> {
  const response = await fetch('/data/command-center.json');
  if (!response.ok) {
    throw new Error(`Snapshot request failed with ${response.status}`);
  }
  return response.json() as Promise<CommandCenterSnapshot>;
}

export const defaultFilters: CommandCenterFilters = {
  country: ALL_FILTER,
  tier: ALL_FILTER,
  companySize: ALL_FILTER,
  roleCategory: ALL_FILTER,
  messagingAngle: ALL_FILTER,
};
