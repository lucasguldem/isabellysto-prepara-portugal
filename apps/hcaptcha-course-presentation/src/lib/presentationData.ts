import type {
  PresentationSnapshot,
  MarketCountry,
  PersonaMetric,
  PresentationFilters,
  PresentationFocus,
  PresentationOptions,
  CompanyAggregate,
  SegmentMetric,
} from '../types';

export const ALL_FILTER = 'All';
export const DECK_PDF_PATH = '/hcaptcha-positioning-deck.pdf';
export const GLOSSARY_PDF_PATH = '/glossario-termos-tecnicos.pdf';

const numberFormatter = new Intl.NumberFormat('en-US');

export function formatNumber(value: number): string {
  return numberFormatter.format(value);
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function uniqueWithAll(values: string[]): string[] {
  return [ALL_FILTER, ...Array.from(new Set(values.filter(Boolean))).sort()];
}

function stripSegmentPrefix(value: string): string {
  return value.replace(/^\d+\.\s*/, '');
}

function findByFilter<T>(
  items: T[],
  selected: string,
  pick: (item: T) => string,
): T | null {
  if (selected === ALL_FILTER) return items[0] ?? null;
  return items.find((item) => pick(item) === selected) ?? null;
}

function stripFilterLabel(value: string): string {
  return value === ALL_FILTER ? 'todos' : stripSegmentPrefix(value);
}

function leadWord(count: number): string {
  return count === 1 ? 'lead' : 'leads';
}

function companyWord(count: number): string {
  return count === 1 ? 'empresa' : 'empresas';
}

function companyMatchesPersona(company: CompanyAggregate, persona: string): boolean {
  return persona === ALL_FILTER || (company.role_mix[persona] ?? 0) > 0;
}

function companyMatchesSegment(company: CompanyAggregate, segment: string): boolean {
  return segment === ALL_FILTER || company.company_size_segment === segment;
}

function companyMatchesCountry(company: CompanyAggregate, country: string): boolean {
  return country === ALL_FILTER || company.company_country === country;
}

function companyMatchesFilters(
  company: CompanyAggregate,
  filters: PresentationFilters,
  ignored: Array<keyof PresentationFilters> = [],
): boolean {
  const ignore = new Set(ignored);
  return (
    (ignore.has('country') || companyMatchesCountry(company, filters.country)) &&
    (ignore.has('persona') || companyMatchesPersona(company, filters.persona)) &&
    (ignore.has('segment') || companyMatchesSegment(company, filters.segment))
  );
}

function personaLeadContribution(company: CompanyAggregate, persona: string): number {
  if (persona === ALL_FILTER) return company.lead_count;
  return company.role_mix[persona] ?? 0;
}

function leadCount(companies: CompanyAggregate[], persona: string): number {
  return companies.reduce((total, company) => total + personaLeadContribution(company, persona), 0);
}

function metricShare(value: number, total: number): number {
  if (!total) return 0;
  return Number((value / total).toFixed(6));
}

function marketHeadline(
  market: MarketCountry | null,
  filters: PresentationFilters,
  filteredLeadCount: number,
  filteredCompanyCount: number,
): string {
  if (!market) return 'Selecione um recorte para orientar a narrativa comercial.';

  const countryText = filters.country === ALL_FILTER ? 'Europa' : market.company_country;
  const personaText = stripFilterLabel(filters.persona);
  const segmentText = stripFilterLabel(filters.segment);

  if (!filteredLeadCount) {
    return `${countryText} nao possui contas no snapshot para persona ${personaText} e porte ${segmentText}. Use outro recorte para comparar a oportunidade.`;
  }

  return `${countryText} soma ${formatNumber(filteredLeadCount)} ${leadWord(filteredLeadCount)} em ${formatNumber(filteredCompanyCount)} ${companyWord(filteredCompanyCount)} para persona ${personaText} e porte ${segmentText}.`;
}

export function getPresentationOptions(snapshot: PresentationSnapshot): PresentationOptions {
  return {
    countries: uniqueWithAll(snapshot.market.map((country) => country.company_country)),
    personas: uniqueWithAll(snapshot.personas.map((persona) => persona.role_category)),
    segments: uniqueWithAll(snapshot.segments.map((segment) => segment.company_size_segment)),
  };
}

export function getFilteredPersonaMetrics(snapshot: PresentationSnapshot, filters: PresentationFilters): PersonaMetric[] {
  const companies = snapshot.companies.filter((company) => companyMatchesFilters(company, filters, ['persona']));
  const totals = new Map<string, { lead_count: number; company_count: number }>();

  companies.forEach((company) => {
    Object.entries(company.role_mix).forEach(([role, count]) => {
      if (!count) return;
      const current = totals.get(role) ?? { lead_count: 0, company_count: 0 };
      current.lead_count += count;
      current.company_count += 1;
      totals.set(role, current);
    });
  });

  const totalLeads = Array.from(totals.values()).reduce((total, metric) => total + metric.lead_count, 0);

  return Array.from(totals.entries())
    .map(([role_category, metric]) => ({
      role_category,
      lead_count: metric.lead_count,
      company_count: metric.company_count,
      lead_share: metricShare(metric.lead_count, totalLeads),
    }))
    .sort((left, right) => right.lead_count - left.lead_count || left.role_category.localeCompare(right.role_category));
}

export function getFilteredSegmentMetrics(snapshot: PresentationSnapshot, filters: PresentationFilters): SegmentMetric[] {
  const companies = snapshot.companies.filter((company) => companyMatchesFilters(company, filters, ['segment']));
  const totals = new Map<string, { lead_count: number; company_count: number }>();

  companies.forEach((company) => {
    const contribution = personaLeadContribution(company, filters.persona);
    if (!contribution) return;
    const current = totals.get(company.company_size_segment) ?? { lead_count: 0, company_count: 0 };
    current.lead_count += contribution;
    current.company_count += 1;
    totals.set(company.company_size_segment, current);
  });

  const totalLeads = Array.from(totals.values()).reduce((total, metric) => total + metric.lead_count, 0);

  return Array.from(totals.entries())
    .map(([company_size_segment, metric]) => ({
      company_size_segment,
      lead_count: metric.lead_count,
      company_count: metric.company_count,
      lead_share: metricShare(metric.lead_count, totalLeads),
    }))
    .sort((left, right) => left.company_size_segment.localeCompare(right.company_size_segment));
}

export function getFilteredCountryMetrics(snapshot: PresentationSnapshot, filters: PresentationFilters): MarketCountry[] {
  const companies = snapshot.companies.filter((company) => companyMatchesFilters(company, filters, ['country']));
  const totals = new Map<string, { lead_count: number; company_count: number }>();
  const originalByCountry = new Map(snapshot.market.map((country) => [country.company_country, country]));

  companies.forEach((company) => {
    const contribution = personaLeadContribution(company, filters.persona);
    if (!contribution) return;
    const current = totals.get(company.company_country) ?? { lead_count: 0, company_count: 0 };
    current.lead_count += contribution;
    current.company_count += 1;
    totals.set(company.company_country, current);
  });

  return Array.from(totals.entries())
    .map(([company_country, metric], index) => {
      const original = originalByCountry.get(company_country);
      return {
        company_country,
        lead_count: metric.lead_count,
        company_count: metric.company_count,
        executive_share: original?.executive_share ?? 0,
        compliance_share: original?.compliance_share ?? 0,
        mismatch_share: original?.mismatch_share ?? 0,
        country_rank: original?.country_rank ?? index + 1,
        priority_tier: original?.priority_tier ?? 'Tier 3',
        messaging_angle: original?.messaging_angle ?? 'Balanced anti-bot performance with compliance-ready messaging',
        strategic_recommendation: original?.strategic_recommendation ?? `Target ${company_country} with balanced anti-bot performance.`,
      };
    })
    .sort((left, right) => right.lead_count - left.lead_count || left.company_country.localeCompare(right.company_country));
}

export function getPresentationFocus(
  snapshot: PresentationSnapshot,
  filters: PresentationFilters,
): PresentationFocus {
  const countryMetrics = getFilteredCountryMetrics(snapshot, filters);
  const market =
    filters.country === ALL_FILTER
      ? (countryMetrics[0] ?? snapshot.market[0] ?? null)
      : findByFilter(snapshot.market, filters.country, (country) => country.company_country);
  const personaMetrics = getFilteredPersonaMetrics(snapshot, filters);
  const segmentMetrics = getFilteredSegmentMetrics(snapshot, filters);
  const persona =
    (filters.persona === ALL_FILTER
      ? (personaMetrics[0] ?? null)
      : findByFilter(personaMetrics, filters.persona, (item) => item.role_category)) ??
    findByFilter(snapshot.personas, filters.persona, (item) => item.role_category);
  const segment =
    (filters.segment === ALL_FILTER
      ? ([...segmentMetrics].sort((left, right) => right.lead_count - left.lead_count)[0] ?? null)
      : findByFilter(segmentMetrics, filters.segment, (item) => item.company_size_segment)) ??
    findByFilter(snapshot.segments, filters.segment, (item) => item.company_size_segment);
  const filteredCompanies = snapshot.companies.filter((company) => companyMatchesFilters(company, filters));
  const filteredLeadCount = leadCount(filteredCompanies, filters.persona);
  const filteredCompanyCount = filteredCompanies.length;
  const countryLabel = filters.country === ALL_FILTER ? 'Europa' : filters.country;
  const personaLabel = stripFilterLabel(filters.persona);
  const segmentLabel = stripFilterLabel(filters.segment);
  const filterSummary = filteredLeadCount
    ? `${countryLabel}: ${formatNumber(filteredLeadCount)} ${leadWord(filteredLeadCount)} em ${formatNumber(filteredCompanyCount)} ${companyWord(filteredCompanyCount)} para persona ${personaLabel} e porte ${segmentLabel}.`
    : `${countryLabel}: nenhum lead no snapshot para persona ${personaLabel} e porte ${segmentLabel}.`;

  return {
    market,
    persona,
    segment,
    filteredLeadCount,
    filteredCompanyCount,
    countryLabel,
    personaLabel,
    segmentLabel,
    filterSummary,
    headline: marketHeadline(market, filters, filteredLeadCount, filteredCompanyCount),
  };
}

export async function loadPresentationSnapshot(): Promise<PresentationSnapshot> {
  const response = await fetch('/data/presentation-snapshot.json');
  if (!response.ok) {
    throw new Error(`Snapshot request failed with ${response.status}`);
  }
  return response.json() as Promise<PresentationSnapshot>;
}
