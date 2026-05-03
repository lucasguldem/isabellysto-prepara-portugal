import type { MarketCountry, PersonaMetric, PresentationFocus, PresentationSnapshot, SegmentMetric } from '../types';
import { formatNumber, formatPercent } from './presentationData';

export type LiveSlideId =
  | 'challenge'
  | 'data'
  | 'market'
  | 'personas'
  | 'segments'
  | 'behavior'
  | 'barriers'
  | 'dashboard'
  | 'process'
  | 'recommendation';

export type LiveSlide = {
  id: LiveSlideId;
  label: string;
  kicker: string;
  title: string;
};

export const liveSlides: LiveSlide[] = [
  {
    id: 'challenge',
    label: 'Desafio',
    kicker: 'Resposta executiva',
    title: 'A hCaptcha deve se posicionar como alternativa anti-bot centrada em privacidade europeia',
  },
  {
    id: 'data',
    label: 'Dados',
    kicker: 'Base harmonizada',
    title: 'A planilha raw virou uma base gold pronta para decisao',
  },
  {
    id: 'market',
    label: 'Mercados',
    kicker: 'Onde entrar primeiro',
    title: 'A priorizacao por pais reduz dispersao comercial',
  },
  {
    id: 'personas',
    label: 'Personas',
    kicker: 'Quem influencia a compra',
    title: 'A venda precisa falar com tecnologia e compliance',
  },
  {
    id: 'segments',
    label: 'Porte',
    kicker: 'Tamanho das empresas',
    title: 'Enterprise valida a tese; mid-market amplia a escala',
  },
  {
    id: 'behavior',
    label: 'Sinais',
    kicker: 'Comportamento e interesses',
    title: 'A propensao aparece por proxies firmograficos',
  },
  {
    id: 'barriers',
    label: 'Barreiras',
    kicker: 'Riscos e oportunidades',
    title: 'Privacidade vira criterio de compra e diferenciacao',
  },
  {
    id: 'dashboard',
    label: 'Dashboard',
    kicker: 'Entrega interativa',
    title: 'O Power BI transforma os achados em decisao filtravel',
  },
  {
    id: 'process',
    label: 'Processo',
    kicker: 'Como foi construido',
    title: 'Do dado bruto a decisao comercial',
  },
  {
    id: 'recommendation',
    label: 'Recomendacao',
    kicker: 'Resposta final',
    title: 'Entrar com privacidade, provar valor e depois escalar',
  },
];

const countryDisplayNames: Record<string, string> = {
  Belgium: 'Belgica',
  Estonia: 'Estonia',
  France: 'Franca',
  Germany: 'Alemanha',
  Ireland: 'Irlanda',
  Italy: 'Italia',
  Lithuania: 'Lituania',
  Netherlands: 'Paises Baixos',
  Poland: 'Polonia',
  Portugal: 'Portugal',
  Spain: 'Espanha',
  Switzerland: 'Suica',
  'United Kingdom': 'Reino Unido',
};

export function displayCountry(country: string): string {
  return countryDisplayNames[country] ?? country;
}

export function stripSegment(value: string): string {
  return value.replace(/^\d+\.\s*/, '');
}

export function recommendationForMarket(market: MarketCountry): string {
  const country = displayCountry(market.company_country);
  const angle = market.messaging_angle.toLowerCase();

  if (angle.includes('privacy')) {
    return `A recomendacao e priorizar ${country} com uma mensagem privacy-first: protecao anti-bot, menor dependencia do reCAPTCHA e alinhamento com exigencias de privacidade europeias.`;
  }

  if (angle.includes('developer')) {
    return `A recomendacao e priorizar ${country} com uma mensagem scale-first: implementacao simples, desempenho tecnico e protecao anti-bot que reduz atrito para equipas de produto e engenharia.`;
  }

  return `A recomendacao e abordar ${country} com uma mensagem equilibrada: protecao anti-bot, conformidade pronta para conversas comerciais e eficiencia tecnica para acelerar a adocao.`;
}

export function getSlideAudienceText(
  slideId: LiveSlideId,
  snapshot: PresentationSnapshot,
  focus: PresentationFocus,
  selectedMarket: MarketCountry,
  selectedPersona: PersonaMetric,
  selectedSegment: SegmentMetric,
): string {
  const country = displayCountry(selectedMarket.company_country);
  const segment = stripSegment(selectedSegment.company_size_segment);

  if (slideId === 'challenge') {
    return `Tese principal: a hCaptcha deve entrar na Europa como alternativa anti-bot privacy-first, sustentada por GDPR, soberania de dados e menor dependencia do ecossistema Google. A leitura parte de uma base gold com ${formatNumber(snapshot.metadata.source_rows)} leads em ${formatNumber(snapshot.metadata.unique_companies)} empresas, conectando volume comercial, perfil comprador e risco regulatorio em uma recomendacao unica.`;
  }

  if (slideId === 'data') {
    return `A base raw foi reduzida e qualificada ate chegar a ${formatNumber(snapshot.metadata.source_rows)} leads europeus elegiveis em ${formatNumber(snapshot.metadata.unique_companies)} empresas. O tratamento separou pais da empresa e pais do contato, agrupou cargos em personas comerciais, criou buckets de porte e removeu duplicidades antes de qualquer leitura estrategica.`;
  }

  if (slideId === 'market') {
    return `${country} concentra ${formatNumber(selectedMarket.lead_count)} leads em ${formatNumber(selectedMarket.company_count)} empresas e sustenta o primeiro foco comercial do recorte. A decisao nao e apenas escolher o pais com mais contatos; e reduzir dispersao, priorizar mercados Tier 1 e adaptar a mensagem entre privacy-first, scale-first e expansao balanceada.`;
  }

  if (slideId === 'personas') {
    return `${selectedPersona.role_category} lidera o recorte com ${formatPercent(selectedPersona.lead_share)} dos leads comparaveis. A leitura mostra que a venda precisa falar com dois centros de decisao: tecnologia, que avalia integracao e performance, e dados/compliance, que avalia privacidade, risco regulatorio e dependencia de fornecedores.`;
  }

  if (slideId === 'segments') {
    return `${segment} indica onde a tese tem maior impacto comercial antes de expandir para outros portes de empresa. Empresas maiores tendem a ter mais trafego, maior exposicao a bots e governanca mais madura; mid-market e startups funcionam como expansao depois que a proposta estiver provada.`;
  }

  if (slideId === 'behavior') {
    return 'A base nao traz cliques, visitas, stack atual ou intencao declarada de compra. Por isso, a propensao foi lida por proxies firmograficos: cargo como poder de influencia, pais como pressao regulatoria, porte como maturidade de compra e cross-border como sinal de operacao distribuida.';
  }

  if (slideId === 'barriers') {
    return 'As principais barreiras sao diligencia de privacidade, inercia do reCAPTCHA, risco de friccao na experiencia do usuario e ausencia de sinal direto de intencao. A oportunidade e transformar cada barreira em argumento comercial: compliance, migracao simples, baixa friccao e pilotos controlados por mercado.';
  }

  if (slideId === 'dashboard') {
    return 'A entrega cobre dashboard interativo em Power BI, relatorio executivo, PDF publico, roteiro privado, glossario tecnico e testes de qualidade. O dashboard e o artefato central de decisao; o site e os PDFs traduzem a analise para defesa e consulta.';
  }

  if (slideId === 'process') {
    return 'A recomendacao foi construida por uma trilha reproduzivel: pergunta de negocio, diagnostico exploratorio, base gold, modelo BI, validacao e sintese comercial. Essa sequencia mostra governanca de dados e reduz o risco de defender uma conclusao baseada apenas em graficos soltos.';
  }

  return `Recorte atual: ${focus.filteredLeadCount} ${focus.filteredLeadCount === 1 ? 'lead' : 'leads'} em ${focus.filteredCompanyCount} ${focus.filteredCompanyCount === 1 ? 'empresa' : 'empresas'}. A estrategia recomendada e entrar por mercados prioritarios, adaptar mensagem por persona e porte, provar valor em contas de maior impacto e depois escalar com um playbook validado.`;
}

export function getSlidePresenterText(
  slideId: LiveSlideId,
  snapshot: PresentationSnapshot,
  focus: PresentationFocus,
  selectedMarket: MarketCountry,
  selectedPersona: PersonaMetric,
  selectedSegment: SegmentMetric,
): string {
  const country = displayCountry(selectedMarket.company_country);
  const segment = stripSegment(selectedSegment.company_size_segment);
  const recommendation = recommendationForMarket(selectedMarket);

if (slideId === 'challenge') {
    return 'A resposta ao desafio é que a hCaptcha deve entrar na Europa como uma alternativa anti-bot com privacidade no centro da mensagem. O mercado europeu valoriza conformidade com GDPR (General Data Protection Regulation), soberania de dados e redução de dependência do ecossistema Google. A análise foi baseada em uma base gold de 882 leads europeus elegíveis em 748 empresas, processados através de um pipeline ETL com deduplicação, harmonização e validação de qualidade. A narrativa deve combinar proteção contra bots, segurança para conversas de compliance e facilidade de adoção técnica para times de engenharia.';
  }

if (slideId === 'data') {
    return `A análise partiu de uma base raw de 1.027 registros e chegou a ${formatNumber(snapshot.metadata.source_rows)} leads europeus elegíveis em ${formatNumber(snapshot.metadata.unique_companies)} empresas. O pipeline de tratamento incluiu: normalização geográfica (distinguindo país da empresa do país do contato), harmonização de cargos em categorias de decisão (Executive / Technical, Data / Compliance, Security / Risk, IT Management, Individual Contributor), bucketização de porte (Startup / SMB até 50, Mid-Market até 250, Enterprise acima de 250), deduplicação por E-mail + Nome da empresa, e filtragem por empresas europeias. O status do e-mail foi preservado como atributo de qualidade, não como filtro rígido da análise. A redução de ruído total foi de 14,1%, o que evita conclusões tiradas de uma planilha bruta sem tratamento.`;
  }

if (slideId === 'market') {
    return `${country} é o mercado de referência neste recorte, com ${formatNumber(selectedMarket.lead_count)} leads e ${formatNumber(selectedMarket.company_count)} empresas mapeadas. A análise identificou que os 5 maiores mercados concentram 88,4% dos leads elegíveis (Germany, UK, France, Spain, Portugal), permitindo uma estratégia focada sem dispersão comercial. Os países foram classificados em Tier 1 (prioridade para validação), Tier 2 (expansão) e Tier 3 (residual). A prioridade não é escolher qualquer país europeu, mas concentrar esforço onde existe massa crítica para outbound e ABM (Account-Based Marketing). ${recommendation}`;
  }

if (slideId === 'personas') {
    return `A persona em maior evidência neste recorte é ${selectedPersona.role_category}, responsável por ${formatPercent(selectedPersona.lead_share)} dos leads comparáveis. As duas categorias principais representam 78% do total (Executive / Technical: 41,3% + Data / Compliance: 36,7%). A venda da hCaptcha precisa ter mensagens duplas: uma técnica para CTOs e Heads de Engineering (foco em performance, integração, baixa fricção), e outra de compliance para DPOs e responsáveis por privacidade (foco em GDPR, soberania de dados, redução de risco regulatório). A hierarquia de personas varia por porte: em Enterprise, Data / Compliance lidera; em SMB, Executive / Technical lidera.`;
  }

  if (slideId === 'segments') {
    return `O segmento em foco e ${segment}. Esta leitura mostra onde a proposta tende a ter mais impacto: empresas maiores validam a tese por volume, risco e maturidade tecnica; mid-market e startups funcionam melhor como expansao depois que a mensagem principal estiver provada.`;
  }

if (slideId === 'behavior') {
    const topSignal = snapshot.adoption_signals[0];
    return `A planilha não contém eventos comportamentais diretos (cliques, visitas, intenção declarada, stack tecnológico), então a propensão foi estimada por proxies firmográficos. Os sinais utilizados: cargo (role_category) como proxy de capacidade de influência na decisão; país como proxy de pressão regulatória e maturidade digital; porte (company_size_segment) como proxy de complexidade operacional e maturidade de compra; e divergência entre país do contato e país da empresa (cross-border signal) como proxy de operação internacional. O sinal mais forte é ${topSignal.signal.toLowerCase()}: ${topSignal.value}, indicando foco comercial sem dispersão. Importante: esta análise deve ser apresentada como inferência baseada em dados firmográficos, não como medição de comportamento real.`;
  }

if (slideId === 'barriers') {
    return 'As barreiras principais são: diligência de privacidade (empresas europeias são rigorosas com GDPR e soberania de dados), inércia de troca (reCAPTCHA tem alta penetração e familiaridade), preocupação com fricção de UX (desafios frequentes geram atrito), e ausência de sinal direto de intenção na base. A oportunidade é transformar essas barreiras em narrativa: privacy-first como porta de entrada para mercados regulatórios (Germany, France, Belgium), migração técnica simples como redutor de risco (compatibilidade com API do Google), modos de baixa fricção (invisible, passive) como resposta a preocupações de UX, e pilotos por mercado para validar interesse antes de escalar.';
  }

  if (slideId === 'dashboard') {
    return 'A entrega principal do desafio e o dashboard interativo em Power BI, apoiado por relatorio, PDF e apresentacao. O dashboard permite filtrar mercado, persona e porte para transformar os numeros em uma decisao comercial defensavel, em vez de apresentar apenas tabelas estaticas.';
  }

  if (slideId === 'process') {
    return 'O projeto seguiu uma trilha de decisao: primeiro veio a pergunta de negocio, depois a exploracao dos dados, a criacao da base gold, o modelo Power BI, os testes e a sintese final. Essa sequencia mostra que a recomendacao nao saiu de graficos soltos; ela foi construida a partir de um processo reproduzivel.';
  }

  return `A recomendacao final e entrar com foco em mercados prioritarios, adaptar a mensagem por pais e persona, e provar valor nas contas de maior impacto antes de escalar. Para o recorte atual, existem ${focus.filteredLeadCount} ${focus.filteredLeadCount === 1 ? 'lead' : 'leads'} em ${focus.filteredCompanyCount} ${focus.filteredCompanyCount === 1 ? 'empresa' : 'empresas'}; o argumento comercial deve ser: ${recommendation}`;
}

export function getFilterHelp(slideId: LiveSlideId, focus: PresentationFocus): string {
  const base = `Recorte atual: ${focus.filterSummary}`;
  if (slideId === 'market') {
    return `${base} A leitura principal e escolher onde concentrar esforco comercial sem perder o contexto de persona e porte.`;
  }
  if (slideId === 'personas') {
    return `${base} A leitura principal e entender quem deve receber a mensagem tecnica, de privacidade e de risco.`;
  }
  if (slideId === 'segments') {
    return `${base} A leitura principal e decidir se a entrada deve comecar por enterprise, mid-market ou startup/SMB.`;
  }
  if (slideId === 'behavior') {
    return `${base} A leitura principal e observar sinais indiretos de propensao: decisor, compliance, porte e operacao distribuida.`;
  }
  if (slideId === 'barriers') {
    return `${base} A leitura principal e transformar riscos de compra em mensagens e mitigacoes comerciais.`;
  }
  if (slideId === 'dashboard') {
    return `${base} A leitura principal e conferir se cada pergunta do desafio aparece em um artefato defensavel.`;
  }
  if (slideId === 'process') {
    return `${base} O processo tecnico e o mesmo para todos os recortes; o que muda e a interpretacao comercial sustentada por ele.`;
  }
  return `${base} Os filtros mudam os graficos e a leitura final sem expor uma lista nominal de contas na apresentacao.`;
}
