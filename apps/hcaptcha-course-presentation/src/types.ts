export type SnapshotMetadata = {
  generated_at: string;
  privacy_level: string;
  source_rows: number;
  unique_companies: number;
  source_files: {
    gold: string;
    country_priority: string;
    role_category: string;
    company_size: string;
    summary: string;
  };
  quality_decision: string | null;
};

export type MarketCountry = {
  company_country: string;
  lead_count: number;
  company_count: number;
  executive_share: number;
  compliance_share: number;
  mismatch_share: number;
  country_rank: number;
  priority_tier: string;
  messaging_angle: string;
  strategic_recommendation: string;
};

export type PersonaMetric = {
  role_category: string;
  lead_count: number;
  company_count: number;
  lead_share: number;
};

export type SegmentMetric = {
  company_size_segment: string;
  lead_count: number;
  company_count: number;
  lead_share: number;
};

export type CompanyAggregate = {
  company_country: string;
  company_size_segment: string;
  lead_count: number;
  role_mix: Record<string, number>;
};

export type Recommendation = {
  track: string;
  countries: string[];
  message: string;
};

export type NarrativeLine = {
  level: string;
  message: string;
};

export type AdoptionSignal = {
  signal: string;
  value: string;
  detail: string;
  interpretation: string;
  strength: string;
};

export type BarrierOpportunity = {
  theme: string;
  barrier: string;
  opportunity: string;
  move: string;
};

export type ActionPhase = {
  phase: string;
  focus: string;
  markets: string;
  buyer: string;
  message: string;
  kpi: string;
};

export type ChallengeCoverage = {
  requirement: string;
  status: string;
  evidence: string;
  artifact: string;
};

export type GlossaryTerm = {
  term: string;
  category: string;
  definition: string;
  in_project: string;
  why_it_matters: string;
};

export type PresentationSnapshot = {
  metadata: SnapshotMetadata;
  market: MarketCountry[];
  personas: PersonaMetric[];
  segments: SegmentMetric[];
  companies: CompanyAggregate[];
  recommendations: Recommendation[];
  narrative: NarrativeLine[];
  adoption_signals: AdoptionSignal[];
  barriers: BarrierOpportunity[];
  action_plan: ActionPhase[];
  challenge_coverage: ChallengeCoverage[];
  glossary_terms: GlossaryTerm[];
};

export type PresentationFilters = {
  country: string;
  persona: string;
  segment: string;
};

export type PresentationOptions = {
  countries: string[];
  personas: string[];
  segments: string[];
};

export type PresentationFocus = {
  market: MarketCountry | null;
  persona: PersonaMetric | null;
  segment: SegmentMetric | null;
  filteredLeadCount: number;
  filteredCompanyCount: number;
  countryLabel: string;
  personaLabel: string;
  segmentLabel: string;
  filterSummary: string;
  headline: string;
};
