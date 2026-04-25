import { motion } from 'framer-motion';
import { Boxes, CircleGauge, Database, Eye, LockOpen, RadioTower } from 'lucide-react';
import HologramPanel from './HologramPanel';
import { ALL_FILTER, formatPercent, getModuleCopy } from '../lib/commandCenter';
import type {
  CommandCenterFilters,
  CommandCenterSnapshot,
  SafeCompany,
  StoryModule,
} from '../types';

type InterfaceShellProps = {
  snapshot: CommandCenterSnapshot;
  activeModule: StoryModule;
  onModuleChange: (module: StoryModule) => void;
  unlocked: boolean;
  onUnlock: () => void;
  selectedCountry: string;
  onSelectCountry: (country: string) => void;
  filters: CommandCenterFilters;
  onFiltersChange: (filters: CommandCenterFilters) => void;
  companies: SafeCompany[];
};

const modules: Array<{ id: StoryModule; label: string; icon: typeof Database }> = [
  { id: 'market', label: 'Market Map', icon: RadioTower },
  { id: 'icp', label: 'ICP Matrix', icon: CircleGauge },
  { id: 'recommendations', label: 'Gold Leads', icon: Boxes },
  { id: 'unlocked', label: 'Unlocked', icon: LockOpen },
];

function unique(values: string[]): string[] {
  return [ALL_FILTER, ...Array.from(new Set(values.filter(Boolean))).sort()];
}

function SelectField({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="select-field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function InterfaceShell({
  snapshot,
  activeModule,
  onModuleChange,
  unlocked,
  onUnlock,
  selectedCountry,
  onSelectCountry,
  filters,
  onFiltersChange,
  companies,
}: InterfaceShellProps) {
  const market = snapshot.market.find((country) => country.company_country === selectedCountry) ?? snapshot.market[0];
  const copy = getModuleCopy(activeModule, snapshot);
  const countries = unique(snapshot.market.map((country) => country.company_country));
  const tiers = unique(snapshot.market.map((country) => country.priority_tier));
  const sizes = unique(snapshot.segments.map((segment) => segment.company_size_segment));
  const roles = unique(snapshot.personas.map((persona) => persona.role_category));
  const angles = unique(snapshot.market.map((country) => country.messaging_angle));

  return (
    <div className="interface-layer">
      <header className="top-status">
        <div>
          <p className="eyebrow">hCaptcha Europe Intelligence</p>
          <strong>Isabellysto Data Command Center</strong>
        </div>
        <div className="status-metrics">
          <span>{snapshot.metadata.source_rows} leads</span>
          <span>{snapshot.metadata.unique_companies} companies</span>
          <span>{snapshot.metadata.privacy_level}</span>
        </div>
      </header>

      <nav className="module-rail" aria-label="Story modules">
        {modules.map((module) => {
          const Icon = module.icon;
          return (
            <button
              key={module.id}
              className={activeModule === module.id ? 'active' : ''}
              onClick={() => onModuleChange(module.id)}
              title={module.label}
            >
              <Icon size={19} />
              <span>{module.label}</span>
            </button>
          );
        })}
      </nav>

      <motion.aside
        className="right-stack"
        initial={{ opacity: 0, x: 22 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <HologramPanel eyebrow="Selected Market" title={market.company_country}>
          <div className="metric-grid">
            <div>
              <span>Leads</span>
              <strong>{market.lead_count}</strong>
            </div>
            <div>
              <span>Companies</span>
              <strong>{market.company_count}</strong>
            </div>
            <div>
              <span>Compliance</span>
              <strong>{formatPercent(market.compliance_share)}</strong>
            </div>
            <div>
              <span>Distributed</span>
              <strong>{formatPercent(market.mismatch_share)}</strong>
            </div>
          </div>
          <p className="recommendation">{market.strategic_recommendation}</p>
          <select
            className="country-select"
            value={selectedCountry}
            onChange={(event) => onSelectCountry(event.target.value)}
          >
            {snapshot.market.map((country) => (
              <option key={country.company_country}>{country.company_country}</option>
            ))}
          </select>
        </HologramPanel>

        <HologramPanel eyebrow="Company Hologram" title="Top Safe Accounts">
          <div className="company-list">
            {companies.slice(0, 6).map((company) => (
              <article key={`${company.company_name}-${company.company_country}`}>
                <strong>{company.company_name}</strong>
                <span>{company.company_country} / {company.company_size_segment.replace(/^\d+\.\s*/, '')}</span>
                <small>{company.company_industry}</small>
              </article>
            ))}
          </div>
        </HologramPanel>
      </motion.aside>

      <HologramPanel className="console-panel" eyebrow="Narrative Console" title="System Logs">
        {copy.map((line, index) => (
          <p key={`${line}-${index}`}>
            <span>{String(index + 1).padStart(2, '0')}</span>
            {line}
          </p>
        ))}
      </HologramPanel>

      <HologramPanel className="left-filters" eyebrow="Exploration Layer" title={unlocked ? 'Filters Online' : 'Locked'}>
        {unlocked ? (
          <div className="filter-grid">
            <SelectField label="Country" value={filters.country} options={countries} onChange={(country) => onFiltersChange({ ...filters, country })} />
            <SelectField label="Tier" value={filters.tier} options={tiers} onChange={(tier) => onFiltersChange({ ...filters, tier })} />
            <SelectField label="Size" value={filters.companySize} options={sizes} onChange={(companySize) => onFiltersChange({ ...filters, companySize })} />
            <SelectField label="Role" value={filters.roleCategory} options={roles} onChange={(roleCategory) => onFiltersChange({ ...filters, roleCategory })} />
            <SelectField label="Angle" value={filters.messagingAngle} options={angles} onChange={(messagingAngle) => onFiltersChange({ ...filters, messagingAngle })} />
          </div>
        ) : (
          <button className="primary-action" onClick={onUnlock}>
            <Eye size={17} />
            Unlock Exploration
          </button>
        )}
      </HologramPanel>
    </div>
  );
}
