import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  Bot,
  ClipboardCheck,
  Database,
  FileText,
  Filter,
  Gauge,
  Globe2,
  Presentation,
  Route,
  ShieldCheck,
  Sparkles,
  Target,
  TestTube2,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import type { CSSProperties } from 'react';
import type { PresentationSnapshot, PresentationFilters } from './types';
import type { ActionPhase, AdoptionSignal, BarrierOpportunity, ChallengeCoverage, GlossaryTerm, MarketCountry, PersonaMetric, SegmentMetric } from './types';
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
  loadPresentationSnapshot,
} from './lib/presentationData';
import {
  getFilterHelp,
  getSlideAudienceText,
  liveSlides,
  recommendationForMarket,
  stripSegment,
} from './lib/presentationContent';
import type { LiveSlide, LiveSlideId } from './lib/presentationContent';

const defaultFilters: PresentationFilters = {
  country: ALL_FILTER,
  persona: ALL_FILTER,
  segment: ALL_FILTER,
};

type ChartBar = {
  label: string;
  value: number;
  detail: string;
  tone: 'blue' | 'aqua' | 'amber' | 'coral' | 'plum';
};

function SelectField({
  id,
  label,
  value,
  options,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="select-field" htmlFor={id}>
      <span>{label}</span>
      <select id={id} value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option === ALL_FILTER ? 'Todos' : option}
          </option>
        ))}
      </select>
    </label>
  );
}

function MetricCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

function EvidenceCard({ icon: Icon, label, value, detail }: { icon: LucideIcon; label: string; value: string; detail: string }) {
  return (
    <article className="evidence-card">
      <Icon size={18} />
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

function ChartBars({ bars, formatter = formatNumber }: { bars: ChartBar[]; formatter?: (value: number) => string }) {
  const maxValue = Math.max(...bars.map((bar) => bar.value), 1);

  if (!bars.length) {
    return (
      <div className="empty-chart">
        <strong>Sem dados para este recorte</strong>
        <span>Altere Pais, Persona ou Porte para comparar outro segmento.</span>
      </div>
    );
  }

  return (
    <div className="chart-bars" aria-label="Grafico de barras">
      {bars.map((bar) => {
        const width = Math.max(6, Math.round((bar.value / maxValue) * 100));
        return (
          <div className="chart-row" key={`${bar.label}-${bar.detail}`}>
            <div className="chart-label">
              <strong>{bar.label}</strong>
              <small>{bar.detail}</small>
            </div>
            <div className="bar-track">
              <span
                className={`bar-fill is-${bar.tone}`}
                style={{ '--bar-width': `${width}%` } as CSSProperties}
              />
            </div>
            <b>{formatter(bar.value)}</b>
          </div>
        );
      })}
    </div>
  );
}

function SignalBoard({ signals }: { signals: AdoptionSignal[] }) {
  return (
    <div className="signal-board">
      {signals.map((signal) => (
        <article key={signal.signal}>
          <div>
            <ShieldCheck size={18} />
            <span>{signal.strength}</span>
          </div>
          <strong>{signal.value}</strong>
          <b>{signal.signal}</b>
          <p>{signal.detail}</p>
          <small>{signal.interpretation}</small>
        </article>
      ))}
    </div>
  );
}

function BarrierBoard({ barriers }: { barriers: BarrierOpportunity[] }) {
  return (
    <div className="barrier-board">
      {barriers.map((barrier) => (
        <article key={barrier.theme}>
          <span>{barrier.theme}</span>
          <div>
            <AlertTriangle size={18} />
            <p>{barrier.barrier}</p>
          </div>
          <div>
            <Sparkles size={18} />
            <p>{barrier.opportunity}</p>
          </div>
          <strong>{barrier.move}</strong>
        </article>
      ))}
    </div>
  );
}

function CoverageBoard({ coverage }: { coverage: ChallengeCoverage[] }) {
  return (
    <div className="coverage-board">
      {coverage.map((item, index) => (
        <article key={item.requirement}>
          <span>{String(index + 1).padStart(2, '0')}</span>
          <div>
            <strong>{item.requirement}</strong>
            <p>{item.evidence}</p>
            <small>{item.status} · {item.artifact}</small>
          </div>
        </article>
      ))}
    </div>
  );
}

function ActionRoadmap({ phases }: { phases: ActionPhase[] }) {
  return (
    <div className="action-roadmap">
      {phases.map((phase) => (
        <article key={phase.phase}>
          <span>{phase.phase}</span>
          <strong>{phase.focus}</strong>
          <dl>
            <div>
              <dt>Mercados</dt>
              <dd>{phase.markets}</dd>
            </div>
            <div>
              <dt>Comprador</dt>
              <dd>{phase.buyer}</dd>
            </div>
            <div>
              <dt>KPI</dt>
              <dd>{phase.kpi}</dd>
            </div>
          </dl>
          <p>{phase.message}</p>
        </article>
      ))}
    </div>
  );
}

function GlossarySection({ terms }: { terms: GlossaryTerm[] }) {
  return (
    <section className="glossary-section" aria-label="Glossario tecnico do projeto">
      <div className="section-heading">
        <BookOpen size={20} />
        <div>
          <p className="eyebrow">Material de apoio</p>
          <h2>Glossario tecnico</h2>
        </div>
      </div>
      <p>
        Estes termos explicam a linguagem tecnica usada no dashboard, no relatorio e na defesa. O objetivo e permitir que a banca acompanhe a analise sem depender de conhecimento previo em dados, BI ou estrategia comercial B2B.
      </p>
      <div className="glossary-grid">
        {terms.map((term) => (
          <article key={term.term}>
            <span>{term.category}</span>
            <strong>{term.term}</strong>
            <p>{term.definition}</p>
            <small>{term.in_project}</small>
          </article>
        ))}
      </div>
      <div className="glossary-preview">
        <iframe title="Previa HTML do glossario tecnico" src="/glossario-termos-tecnicos.html" />
        <a className="pdf-link" href={GLOSSARY_PDF_PATH} target="_blank" rel="noreferrer">
          <FileText size={18} />
          Abrir glossario
        </a>
      </div>
    </section>
  );
}

function DecisionFlow() {
  const steps = [
    { icon: FileText, title: 'Enunciado', text: 'Transformei a pergunta em criterio de decisao: escolher mercados, perfis compradores e argumento comercial.' },
    { icon: BarChart3, title: 'Diagnostico', text: 'Li a base no Jupyter para entender volume, pais, cargo, porte de empresa e sinais de oportunidade.' },
    { icon: Database, title: 'Base gold', text: 'Padronizei e dedupliquei os dados com Python para trabalhar com uma base consistente e defensavel.' },
    { icon: Presentation, title: 'Modelo BI', text: 'Modelei medidas e paginas no Power BI para comparar mercado, persona, porte e recomendacao.' },
    { icon: TestTube2, title: 'Validacao', text: 'Testei pipeline, snapshot, PBIP e interface para reduzir erro antes da apresentacao.' },
    { icon: Sparkles, title: 'Recomendacao', text: 'Conectei os achados em uma resposta comercial: privacidade como entrada e eficiencia tecnica como escala.' },
  ];

  return (
    <ol className="decision-flow" aria-label="Fluxo de decisao do projeto">
      {steps.map(({ icon: Icon, title, text }, index) => (
        <li key={title}>
          <span className="flow-index">{String(index + 1).padStart(2, '0')}</span>
          <Icon size={18} />
          <strong>{title}</strong>
          <p>{text}</p>
        </li>
      ))}
    </ol>
  );
}

function slideNumber(slide: LiveSlide, index: number) {
  return `${String(index + 1).padStart(2, '0')} · ${slide.label}`;
}

function countryBars(markets: MarketCountry[]): ChartBar[] {
  return markets.slice(0, 5).map((market, index) => ({
    label: market.company_country,
    value: market.lead_count,
    detail: `${formatNumber(market.company_count)} empresas · ${market.priority_tier}`,
    tone: index === 0 ? 'blue' : index === 1 ? 'aqua' : index === 2 ? 'amber' : index === 3 ? 'coral' : 'plum',
  }));
}

function personaBars(personas: PersonaMetric[]): ChartBar[] {
  const tones: ChartBar['tone'][] = ['plum', 'blue', 'aqua', 'amber', 'coral'];
  return personas.slice(0, 5).map((persona, index) => ({
    label: persona.role_category,
    value: persona.lead_count,
    detail: `${formatPercent(persona.lead_share)} da base`,
    tone: tones[index] ?? 'blue',
  }));
}

function segmentBars(segments: SegmentMetric[]): ChartBar[] {
  const tones: ChartBar['tone'][] = ['coral', 'amber', 'aqua', 'plum', 'blue'];
  return segments.map((segment, index) => ({
    label: stripSegment(segment.company_size_segment),
    value: segment.lead_count,
    detail: `${formatPercent(segment.lead_share)} da base`,
    tone: tones[index] ?? 'blue',
  }));
}

function LiveSlideVisual({
  slideId,
  snapshot,
  selectedMarket,
  selectedPersona,
  selectedSegment,
  countryBars,
  personaChartBars,
  segmentChartBars,
  keySeed,
}: {
  slideId: LiveSlideId;
  snapshot: PresentationSnapshot;
  selectedMarket: MarketCountry;
  selectedPersona: PersonaMetric;
  selectedSegment: SegmentMetric;
  countryBars: ChartBar[];
  personaChartBars: ChartBar[];
  segmentChartBars: ChartBar[];
  keySeed: string;
}) {
  if (slideId === 'challenge') {
    return (
      <div className="challenge-proof" key={keySeed}>
        <EvidenceCard icon={Globe2} label="Mercado em foco" value={selectedMarket.company_country} detail={selectedMarket.messaging_angle} />
        <EvidenceCard icon={Target} label="Prioridade" value={selectedMarket.priority_tier} detail={`${formatNumber(selectedMarket.lead_count)} leads no mercado`} />
        <EvidenceCard icon={Bot} label="Tese de produto" value="anti-bot + privacidade" detail="alternativa ao reCAPTCHA na Europa" />
      </div>
    );
  }

  if (slideId === 'data') {
    return (
      <div className="data-ledger" key={keySeed}>
        <div><span>Raw Snov.io</span><strong>1,027</strong><small>linhas originais</small></div>
        <div><span>Gold</span><strong>{formatNumber(snapshot.metadata.source_rows)}</strong><small>leads europeus elegiveis</small></div>
        <div><span>Duplicidade gold</span><strong>0</strong><small>email + empresa</small></div>
        <div><span>Status</span><strong>{snapshot.metadata.quality_decision ?? 'approved'}</strong><small>{snapshot.metadata.privacy_level}</small></div>
      </div>
    );
  }

  if (slideId === 'market') {
    return <ChartBars key={keySeed} bars={countryBars} />;
  }

  if (slideId === 'personas') {
    return <ChartBars key={keySeed} bars={personaChartBars} />;
  }

  if (slideId === 'segments') {
    return <ChartBars key={keySeed} bars={segmentChartBars} />;
  }

  if (slideId === 'behavior') {
    return <SignalBoard key={keySeed} signals={snapshot.adoption_signals} />;
  }

  if (slideId === 'barriers') {
    return <BarrierBoard key={keySeed} barriers={snapshot.barriers} />;
  }

  if (slideId === 'dashboard') {
    return <CoverageBoard key={keySeed} coverage={snapshot.challenge_coverage} />;
  }

  if (slideId === 'process') {
    return <DecisionFlow key={keySeed} />;
  }

  return (
    <div className="recommendation-board action-summary" key={keySeed}>
      <EvidenceCard icon={Route} label="Plano comercial" value="30-60-90" detail={`${selectedMarket.company_country} · ${selectedMarket.priority_tier}`} />
      <EvidenceCard icon={ClipboardCheck} label="Perfil abordado" value={selectedPersona.role_category} detail="traduzir valor tecnico em risco reduzido" />
      <EvidenceCard icon={Target} label="Segmento" value={stripSegment(selectedSegment.company_size_segment)} detail="validar, provar valor e escalar" />
      <ActionRoadmap phases={snapshot.action_plan} />
    </div>
  );
}

function LoadingState() {
  return (
    <main className="loading-screen">
      <div className="pixel-loader" />
      <p>Carregando dados harmonizados...</p>
    </main>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <main className="loading-screen">
      <section className="error-box">
        <h1>Snapshot indisponivel</h1>
        <p>{message}</p>
        <code>python scripts/build_presentation_snapshot.py</code>
      </section>
    </main>
  );
}

export default function App() {
  const [snapshot, setSnapshot] = useState<PresentationSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<PresentationFilters>(defaultFilters);
  const [activeLiveSlide, setActiveLiveSlide] = useState<LiveSlideId>('challenge');

  useEffect(() => {
    loadPresentationSnapshot()
      .then(setSnapshot)
      .catch((cause: Error) => setError(cause.message));
  }, []);

  const options = useMemo(() => (snapshot ? getPresentationOptions(snapshot) : null), [snapshot]);
  const focus = useMemo(
    () => (snapshot ? getPresentationFocus(snapshot, filters) : null),
    [filters, snapshot],
  );

  if (error) return <ErrorState message={error} />;
  if (!snapshot || !options || !focus) return <LoadingState />;

  const topMarket = snapshot.market[0];
  const filteredCountryMetrics = getFilteredCountryMetrics(snapshot, filters);
  const selectedMarket = filters.country === ALL_FILTER ? (filteredCountryMetrics[0] ?? topMarket) : (focus.market ?? topMarket);
  const selectedPersona = focus.persona ?? snapshot.personas[0];
  const selectedSegment = focus.segment ?? snapshot.segments[0];
  const privacyTrack = snapshot.recommendations.find((item) => item.track === 'Privacy-first');
  const scaleTrack = snapshot.recommendations.find((item) => item.track === 'Scale-first');
  const liveSlide = liveSlides.find((slide) => slide.id === activeLiveSlide) ?? liveSlides[0];
  const selectedSlideIndex = liveSlides.findIndex((slide) => slide.id === liveSlide.id);
  const filterSignature = `${activeLiveSlide}-${filters.country}-${filters.persona}-${filters.segment}`;
  const countryChartBars = countryBars(filteredCountryMetrics.length ? filteredCountryMetrics : snapshot.market);
  const personaChartBars = personaBars(getFilteredPersonaMetrics(snapshot, filters));
  const segmentChartBars = segmentBars(getFilteredSegmentMetrics(snapshot, filters));
  const audienceText = getSlideAudienceText(activeLiveSlide, snapshot, focus, selectedMarket, selectedPersona, selectedSegment);
  const filterHelp = getFilterHelp(activeLiveSlide, focus);
  const selectedRecommendation = recommendationForMarket(selectedMarket);

  return (
    <main className="presentation-app">
      <header className="hero-strip">
        <div>
          <p className="eyebrow">Prepara Portugal · Analise de Dados e TI aplicado a Gestao</p>
          <h1>Posicionamento europeu da hCaptcha</h1>
          <p>
            A hCaptcha deve se posicionar como alternativa anti-bot centrada em privacidade, conformidade europeia e eficiencia tecnica.
            Esta apresentacao mostra a trilha completa: dados tratados, leitura de mercado, personas, porte das empresas e recomendacao comercial.
          </p>
        </div>
        <a className="pdf-link" href={DECK_PDF_PATH} target="_blank" rel="noreferrer">
          <FileText size={18} />
          PDF final
        </a>
      </header>

      <section className="live-deck" aria-label="Apresentacao interativa do projeto">
        <nav className="live-slide-nav" aria-label="Slides da apresentacao">
          {liveSlides.map((slide, index) => (
            <button
              key={slide.id}
              className={slide.id === activeLiveSlide ? 'is-active' : ''}
              onClick={() => setActiveLiveSlide(slide.id)}
              type="button"
            >
              <span>{slideNumber(slide, index)}</span>
              <strong>{slide.title}</strong>
            </button>
          ))}
        </nav>

        <div className="presentation-controls">
          <div>
            <Filter size={18} />
            <strong>Filtros da apresentacao</strong>
            <span>Pais, persona e porte recalculam a leitura comercial do recorte.</span>
          </div>
          <SelectField
            id="country"
            label="Pais"
            value={filters.country}
            options={options.countries}
            onChange={(country) => setFilters((current) => ({ ...current, country }))}
          />
          <SelectField
            id="persona"
            label="Persona"
            value={filters.persona}
            options={options.personas}
            onChange={(persona) => setFilters((current) => ({ ...current, persona }))}
          />
          <SelectField
            id="segment"
            label="Porte"
            value={filters.segment}
            options={options.segments}
            onChange={(segment) => setFilters((current) => ({ ...current, segment }))}
          />
        </div>

        <aside className="filter-help" key={`${filterSignature}-help`}>
          <strong>Leitura do recorte</strong>
          <p>{filterHelp}</p>
        </aside>

        <section className="live-stage" key={`${filterSignature}-stage`}>
          <div className="slide-copy">
            <p className="eyebrow">{liveSlide.kicker}</p>
            <span className="slide-count">{String(selectedSlideIndex + 1).padStart(2, '0')} / {String(liveSlides.length).padStart(2, '0')}</span>
            <h2>{liveSlide.title}</h2>
            <p>{audienceText}</p>
          </div>

          <div className="slide-visual">
            <LiveSlideVisual
              slideId={activeLiveSlide}
              snapshot={snapshot}
              selectedMarket={selectedMarket}
              selectedPersona={selectedPersona}
              selectedSegment={selectedSegment}
              countryBars={countryChartBars}
              personaChartBars={personaChartBars}
              segmentChartBars={segmentChartBars}
              keySeed={filterSignature}
            />
          </div>
        </section>
      </section>

      <section className="summary-grid" aria-label="Indicadores chave do projeto">
        <MetricCard label="Base gold" value={formatNumber(snapshot.metadata.source_rows)} detail="leads europeus elegiveis depois da harmonizacao" />
        <MetricCard label="Empresas" value={formatNumber(snapshot.metadata.unique_companies)} detail="contas para priorizacao comercial" />
        <MetricCard label="Top mercado" value={topMarket.company_country} detail={`${formatNumber(topMarket.lead_count)} leads mapeados`} />
        <MetricCard label="Quality gate" value={snapshot.metadata.quality_decision ?? 'unknown'} detail="dados prontos para apresentacao sem PII no site" />
      </section>

      <section className="answer-strip" aria-label="Resposta estrategica resumida">
        <div>
          <Gauge size={22} />
          <h2>Resposta final</h2>
        </div>
        <p>
          A hCaptcha deve posicionar-se como uma alternativa de protecao anti-bot com forte apelo de privacidade para a Europa.
          O plano recomendado e entrar por mercados prioritarios, adaptar a mensagem por perfil comprador e provar valor em segmentos de maior impacto antes de expandir.
        </p>
        <dl>
          <div>
            <dt>Privacy-first</dt>
            <dd>{privacyTrack?.countries.join(', ') || 'Germany, France'}</dd>
          </div>
          <div>
            <dt>Scale-first</dt>
            <dd>{scaleTrack?.countries.join(', ') || 'United Kingdom'}</dd>
          </div>
          <div>
            <dt>ICP inicial</dt>
            <dd>{selectedPersona.role_category} em empresas {stripSegment(selectedSegment.company_size_segment)}.</dd>
          </div>
        </dl>
      </section>

      <section className="process-exhibit" aria-label="Trilha completa de decisao do projeto">
        <div className="section-heading">
          <WorkflowIcon />
          <div>
            <p className="eyebrow">Trilha de decisao do projeto</p>
            <h2>Do dado bruto a decisao comercial</h2>
          </div>
        </div>
        <DecisionFlow />
      </section>

      <section className="appendix-grid" aria-label="Materiais de defesa e recorte selecionado">
        <article className="focus-box">
          <div className="focus-title">
            <Target size={18} />
            <h3>Recorte selecionado</h3>
          </div>
          <p>{focus.headline}</p>
          <dl>
            <div>
              <dt>Mercado</dt>
              <dd>{selectedMarket.company_country} · {selectedMarket.priority_tier}</dd>
            </div>
            <div>
              <dt>Mensagem</dt>
              <dd>{selectedMarket.messaging_angle}</dd>
            </div>
            <div>
              <dt>Persona</dt>
              <dd>{selectedPersona.role_category} · {formatPercent(selectedPersona.lead_share)}</dd>
            </div>
            <div>
              <dt>Porte</dt>
              <dd>{stripSegment(selectedSegment.company_size_segment)} · {formatNumber(selectedSegment.lead_count)} leads no recorte comparavel</dd>
            </div>
          </dl>
          <strong className="recommendation">{selectedRecommendation}</strong>
        </article>

        <article className="pdf-card">
          <div>
            <Presentation size={18} />
            <h3>PDF final exportado</h3>
          </div>
          <p>
            O PDF registra a versao estatica da narrativa final. O deck vivo acima complementa o arquivo com recortes dinamicos por pais, persona e porte.
          </p>
          <iframe title="Previa HTML do PDF final" src="/hcaptcha-positioning-deck.html" />
          <a className="pdf-link" href={DECK_PDF_PATH} target="_blank" rel="noreferrer">
            <FileText size={18} />
            Abrir PDF
          </a>
        </article>
      </section>

      <GlossarySection terms={snapshot.glossary_terms} />
    </main>
  );
}

function WorkflowIcon() {
  return <Sparkles size={20} />;
}
