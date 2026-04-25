import { useEffect, useMemo, useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import BootSequence from './components/BootSequence';
import CommandScene from './components/CommandScene';
import InterfaceShell from './components/InterfaceShell';
import {
  defaultFilters,
  getFilteredCompanies,
  loadCommandCenterSnapshot,
} from './lib/commandCenter';
import type { CommandCenterFilters, CommandCenterSnapshot, StoryModule } from './types';

function EmptyState({ error }: { error: string }) {
  return (
    <main className="empty-state">
      <section className="holo-panel max-w-3xl">
        <p className="eyebrow">SNAPSHOT UNAVAILABLE</p>
        <h1>Command Center data package is missing</h1>
        <p>
          Generate the sanitized Level 2 data package before launching the interface.
        </p>
        <code>python scripts/build_data_command_center_snapshot.py --output sites/data-command-center/public/data/command-center.json</code>
        <small>{error}</small>
      </section>
    </main>
  );
}

export default function App() {
  const [snapshot, setSnapshot] = useState<CommandCenterSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [booting, setBooting] = useState(true);
  const [activeModule, setActiveModule] = useState<StoryModule>('market');
  const [unlocked, setUnlocked] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState<string>('Germany');
  const [filters, setFilters] = useState<CommandCenterFilters>(defaultFilters);

  useEffect(() => {
    loadCommandCenterSnapshot()
      .then((data) => {
        setSnapshot(data);
        setSelectedCountry(data.market[0]?.company_country ?? 'Germany');
      })
      .catch((cause: Error) => setError(cause.message));
  }, []);

  useEffect(() => {
    if (!snapshot) return;
    const timer = window.setTimeout(() => setBooting(false), 2600);
    return () => window.clearTimeout(timer);
  }, [snapshot]);

  const filteredCompanies = useMemo(
    () => (snapshot ? getFilteredCompanies(snapshot, filters).slice(0, 10) : []),
    [filters, snapshot],
  );

  if (error) {
    return <EmptyState error={error} />;
  }

  if (!snapshot) {
    return (
      <main className="empty-state">
        <div className="holo-panel">Loading command-center telemetry...</div>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <CommandScene
        snapshot={snapshot}
        activeModule={activeModule}
        unlocked={unlocked}
        selectedCountry={selectedCountry}
        onSelectCountry={setSelectedCountry}
      />
      <InterfaceShell
        snapshot={snapshot}
        activeModule={activeModule}
        onModuleChange={(module) => {
          setActiveModule(module);
          if (module === 'unlocked') setUnlocked(true);
        }}
        unlocked={unlocked}
        onUnlock={() => {
          setUnlocked(true);
          setActiveModule('unlocked');
        }}
        selectedCountry={selectedCountry}
        onSelectCountry={setSelectedCountry}
        filters={filters}
        onFiltersChange={setFilters}
        companies={filteredCompanies}
      />
      <AnimatePresence>
        {booting && <BootSequence snapshot={snapshot} onSkip={() => setBooting(false)} />}
      </AnimatePresence>
    </main>
  );
}
