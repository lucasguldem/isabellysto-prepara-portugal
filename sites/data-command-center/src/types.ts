export type StoryModule = 'market' | 'icp' | 'recommendations' | 'unlocked';

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

export type SafeCompany = {
  company_name: string;
  company_country: string;
  company_industry: string;
  company_size_segment: string;
  lead_count: number;
  role_mix: Record<string, number>;
  priority_tier: string;
  messaging_angle: string;
  strategic_recommendation: string;
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

export type CommandCenterSnapshot = {
  metadata: SnapshotMetadata;
  market: MarketCountry[];
  personas: PersonaMetric[];
  segments: SegmentMetric[];
  companies: SafeCompany[];
  recommendations: Recommendation[];
  narrative: NarrativeLine[];
};

export type CommandCenterFilters = {
  country: string;
  tier: string;
  companySize: string;
  roleCategory: string;
  messagingAngle: string;
};

export type CountrySceneNode = {
  country: string;
  rank: number;
  leads: number;
  companies: number;
  tier: string;
  messagingAngle: string;
  color: string;
  height: number;
  radius: number;
  position: [number, number, number];
};
