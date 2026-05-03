import { chromium } from 'playwright';
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const siteRoot = path.resolve(__dirname, '..');
const repoRoot = path.resolve(siteRoot, '..', '..');
const publicRoot = path.join(siteRoot, 'public');
const dataPath = path.join(publicRoot, 'data', 'presentation-snapshot.json');
const htmlPath = path.join(publicRoot, 'hcaptcha-positioning-deck.html');
const pdfPath = path.join(publicRoot, 'hcaptcha-positioning-deck.pdf');
const glossaryHtmlPath = path.join(publicRoot, 'glossario-termos-tecnicos.html');
const glossaryPdfPath = path.join(publicRoot, 'glossario-termos-tecnicos.pdf');
const presenterNotesHtmlPath = path.join(repoRoot, 'reports', 'hcaptcha_roteiro_apresentador.html');
const presenterNotesPdfPath = path.join(repoRoot, 'reports', 'hcaptcha_roteiro_apresentador.pdf');
const glossaryReportHtmlPath = path.join(repoRoot, 'reports', 'glossario_termos_tecnicos.html');
const glossaryReportPdfPath = path.join(repoRoot, 'reports', 'glossario_termos_tecnicos.pdf');

const formatNumber = (value) => new Intl.NumberFormat('en-US').format(value);
const formatPercent = (value) => `${(value * 100).toFixed(1)}%`;
const escapeHtml = (value) =>
  String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');

const cleanHtml = (value) => `${value.replace(/[ \t]+$/gm, '').trimEnd()}\n`;

function barRows(rows, maxValue, labelKey, valueKey) {
  return rows
    .map((row) => {
      const width = Math.max(4, Math.round((row[valueKey] / maxValue) * 100));
      return `
        <div class="bar-row">
          <span>${escapeHtml(row[labelKey])}</span>
          <div><i style="width:${width}%"></i></div>
          <strong>${formatNumber(row[valueKey])}</strong>
        </div>
      `;
    })
    .join('');
}

function stat(label, value, detail = '') {
  return `
    <article class="stat">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <small>${escapeHtml(detail)}</small>
    </article>
  `;
}

function slide({ page, kicker, title, copy, stats = '', visual = '', accent = 'mint' }) {
  return `
    <section class="slide ${accent}">
      <header>
        <p>${escapeHtml(kicker)}</p>
        <b>${String(page).padStart(2, '0')}</b>
      </header>
      <main>
        <div class="story">
          <h1>${escapeHtml(title)}</h1>
          <p>${escapeHtml(copy)}</p>
          <div class="stats">${stats}</div>
        </div>
        <aside>${visual}</aside>
      </main>
    </section>
  `;
}

function buildHtml(snapshot) {
  const market = snapshot.market;
  const personas = snapshot.personas;
  const segments = snapshot.segments;
  const topCountries = market.slice(0, 5);
  const maxCountryLeads = Math.max(...topCountries.map((row) => row.lead_count));
  const maxPersonaLeads = Math.max(...personas.map((row) => row.lead_count));
  const maxSegmentLeads = Math.max(...segments.map((row) => row.lead_count));
  const topCountry = market[0];
  const topPersona = personas[0];
  const topSegment = segments[0];
  const totalLeads = Math.max(snapshot.metadata.source_rows, 1);
  const topFiveLeads = topCountries.reduce((sum, row) => sum + row.lead_count, 0);
  const topFiveShare = topFiveLeads / totalLeads;
  const enterpriseSegment = segments.find((row) => row.company_size_segment.toLowerCase().includes('enterprise'));
  const midMarketSegment = segments.find((row) => row.company_size_segment.toLowerCase().includes('mid'));
  const startupSegment = segments.find((row) => row.company_size_segment.toLowerCase().includes('startup'));
  const expansionShare = ((midMarketSegment?.lead_share ?? 0) + (startupSegment?.lead_share ?? 0));
  const crossBorderShare = topCountries.reduce((sum, row) => sum + row.mismatch_share, 0) / topCountries.length;
  const privacyCountries = market
    .filter((row) => row.messaging_angle.toLowerCase().includes('privacy'))
    .slice(0, 4)
    .map((row) => row.company_country)
    .join(', ');
  const scaleCountries = market
    .filter((row) => row.messaging_angle.toLowerCase().includes('developer'))
    .slice(0, 4)
    .map((row) => row.company_country)
    .join(', ');

  const slides = [
    slide({
      page: 1,
      kicker: 'Resposta ao desafio',
      title: 'A hCaptcha deve se posicionar como alternativa anti-bot centrada em privacidade',
      copy: 'A resposta ao desafio e que a hCaptcha deve entrar na Europa com privacidade, conformidade e eficiencia tecnica como mensagem central. O mercado europeu valoriza protecao contra bots, reducao de dependencia do reCAPTCHA e seguranca para conversas sobre GDPR.',
      stats:
        stat('Base gold', `${formatNumber(snapshot.metadata.source_rows)} leads`, 'dados processados') +
        stat('Empresas', formatNumber(snapshot.metadata.unique_companies), 'contas sem PII exposta') +
        stat('Mercados', `${market.length} paises`, 'recorte Europa'),
      visual: '<div class="pixel-tower"><i></i><i></i><i></i><i></i></div>',
      accent: 'blue',
    }),
    slide({
      page: 2,
      kicker: 'Trilha de decisao',
      title: 'Do dado bruto a decisao comercial',
      copy: 'O projeto seguiu uma sequencia defensavel: pergunta de negocio, exploracao, base gold, modelo Power BI, validacao e recomendacao. Assim, a conclusao nao depende de opiniao solta; ela nasce de um processo reproduzivel.',
      stats:
        stat('Exploracao', 'Jupyter', 'entendimento inicial') +
        stat('Automacao', 'Python', 'pipeline e snapshot') +
        stat('Entrega', 'PBIP + PDF', 'dashboard e defesa'),
      visual:
        '<ol class="flow"><li>Enunciado</li><li>Diagnostico</li><li>Base gold</li><li>Modelo BI</li><li>Validacao</li><li>Recomendacao</li></ol>',
      accent: 'mint',
    }),
    slide({
      page: 3,
      kicker: 'Dados e qualidade',
      title: 'Raw virou gold antes da leitura de negocio',
      copy: 'A base original precisava ser tratada antes de sustentar uma recomendacao. O pipeline padronizou pais, cargo, porte e empresa, removeu duplicidades e gerou tabelas prontas para analise, dashboard e apresentacao.',
      stats:
        stat('Raw', '1,027', 'linhas originais') +
        stat('Gold', '882', 'leads europeus elegiveis') +
        stat('Quality gate', snapshot.metadata.quality_decision || 'approved', 'carga validada'),
      visual:
        '<ol class="pipeline"><li>CSV original</li><li>ETL Python</li><li>Gold + dimensoes</li><li>Power BI</li></ol>',
      accent: 'yellow',
    }),
    slide({
      page: 4,
      kicker: 'Mercados prioritarios',
      title: `${topCountry.company_country} lidera a oportunidade inicial`,
      copy: 'A entrada deve comecar pelos mercados com maior massa critica. Eles permitem concentrar outbound e ABM onde ja existe volume suficiente para testar mensagem, aprender rapido e criar prova comercial.',
      stats:
        stat('Top pais', topCountry.company_country, `${formatNumber(topCountry.lead_count)} leads`) +
        stat('Top 5', formatPercent(topFiveShare), 'dos leads elegiveis') +
        stat('Tese', 'foco', 'menos dispersao'),
      visual: `<div class="bars">${barRows(topCountries, maxCountryLeads, 'company_country', 'lead_count')}</div>`,
      accent: 'blue',
    }),
    slide({
      page: 5,
      kicker: 'Perfis de compradores',
      title: 'A decisao combina tecnologia e compliance',
      copy: 'Os cargos mostram que a venda precisa falar com tecnologia e compliance ao mesmo tempo. Para decisores tecnicos, o argumento e performance e facilidade de implementacao; para dados, seguranca e risco, o argumento e privacidade e conformidade.',
      stats:
        stat('Persona lider', topPersona.role_category, formatPercent(topPersona.lead_share)) +
        stat('Compliance', formatPercent(personas.find((row) => row.role_category === 'Data / Compliance')?.lead_share ?? 0), 'sinal regulatorio') +
        stat('Abordagem', 'dupla', 'tecnica + privacidade'),
      visual: `<div class="bars">${barRows(personas, maxPersonaLeads, 'role_category', 'lead_count')}</div>`,
      accent: 'violet',
    }),
    slide({
      page: 6,
      kicker: 'Porte das empresas',
      title: `${topSegment.company_size_segment.replace(/^[0-9]+\\.\\s*/, '')} puxa a tese enterprise`,
      copy: 'Empresas maiores tendem a ter mais trafego, maior exposicao a bots e mais maturidade para discutir troca de solucao. Mid-market e SMB entram como expansao depois que a proposta for validada nos segmentos de maior impacto.',
      stats:
        stat('Enterprise', formatPercent(enterpriseSegment?.lead_share ?? topSegment.lead_share), 'maior segmento') +
        stat('Mid + SMB', formatPercent(expansionShare), 'expansao comercial') +
        stat('Prioridade', 'contas maiores', 'alto impacto'),
      visual: `<div class="bars">${barRows(segments, maxSegmentLeads, 'company_size_segment', 'lead_count')}</div>`,
      accent: 'red',
    }),
    slide({
      page: 7,
      kicker: 'Comportamento por proxy',
      title: 'O sinal cross-border indica operacao distribuida',
      copy: 'A planilha nao traz cliques, visitas ou intencao declarada. Por isso, comportamento e interesse foram lidos por proxies firmograficos: cargo, pais, porte e divergencia entre pais do contato e pais da empresa.',
      stats:
        stat('Cross-border', '10.1%', 'base limpa') +
        stat('Top 5 media', formatPercent(crossBorderShare), 'mercados lideres') +
        stat('Uso', 'proxy', 'sem evento comportamental'),
      visual: '<div class="pixel-map"><span>Contato</span><b></b><span>Empresa</span></div>',
      accent: 'mint',
    }),
    slide({
      page: 8,
      kicker: 'Barreiras e oportunidades',
      title: 'Privacidade vira diferenciacao competitiva',
      copy: 'Na Europa, privacidade, GDPR e dependencia do ecossistema Google podem virar barreiras para concorrentes e oportunidade para a hCaptcha. A diferenciacao precisa ser concreta: menos exposicao de dados, protecao anti-bot e adocao tecnica simples.',
      stats:
        stat('Privacy-first', privacyCountries || 'Germany, France', 'mensagem GDPR') +
        stat('Scale-first', scaleCountries || 'United Kingdom', 'eficiencia tecnica') +
        stat('Concorrencia', 'reCAPTCHA', 'alternativa mais privada'),
      visual: '<div class="versus"><b>hCaptcha</b><span>vs</span><b>reCAPTCHA</b><small>privacidade · soberania · UX</small></div>',
      accent: 'blue',
    }),
    slide({
      page: 9,
      kicker: 'Dashboard interativo',
      title: 'O Power BI transforma a analise em decisao filtravel',
      copy: 'A entrega principal do desafio e o dashboard interativo em Power BI. Ele organiza mercado, persona, porte, sinal cross-border e proxima acao em paginas filtraveis, apoiadas por relatorio executivo, PDF publico e roteiro privado.',
      stats:
        stat('Power BI', '4 paginas', 'visuais nativos') +
        stat('Relatorio', 'executivo', 'analise e recomendacao') +
        stat('Defesa', '2 PDFs', 'publico + apresentador'),
      visual:
        '<ul class="script-list"><li>Market Command</li><li>Buyer Intelligence</li><li>Border Signal</li><li>Action Map</li><li>Relatorio + apresentacao</li></ul>',
      accent: 'violet',
    }),
    slide({
      page: 10,
      kicker: 'Plano comercial',
      title: 'Entrar com privacidade, provar valor e depois escalar',
      copy: 'A recomendacao final e iniciar por mercados prioritarios, adaptar a mensagem por pais e persona, validar o ICP em segmentos de maior impacto e depois ampliar para regioes adjacentes. A hCaptcha deve vender privacidade como entrada e eficiencia tecnica como escala.',
      stats:
        stat('Fase 1', 'DE + FR', 'privacy-first') +
        stat('Fase 2', 'UK + IE', 'scale-first') +
        stat('Tese', 'ABM', 'contas priorizadas'),
      visual:
        '<ol class="pipeline roadmap"><li>Priorizar contas</li><li>Adaptar mensagem</li><li>Validar ICP</li><li>Escalar outbound</li></ol>',
      accent: 'yellow',
    }),
  ].join('');

  return `<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>Posicionamento europeu da hCaptcha</title>
  <style>
    @page { size: 13.333in 7.5in; margin: 0; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #182126; color: #182126; font-family: "Cascadia Code", "JetBrains Mono", "Courier New", monospace; }
    .slide { width: 13.333in; height: 7.5in; padding: .38in; page-break-after: always; background: linear-gradient(135deg, #fff7dc 0 34%, #dff5ee 34% 64%, #ffe0d5 64% 100%); border: 12px solid #182126; position: relative; overflow: hidden; }
    .slide:before { content: ""; position: absolute; inset: 0; background: repeating-linear-gradient(90deg, rgba(24,33,38,.08) 0 1px, transparent 1px 18px), repeating-linear-gradient(0deg, rgba(255,255,255,.22) 0 1px, transparent 1px 8px); pointer-events: none; }
    header { display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 1; }
    header p { margin: 0; font-weight: 700; text-transform: uppercase; color: #2e68d6; }
    header b { border: 4px solid #182126; padding: 8px 12px; background: #fffdf4; box-shadow: 5px 5px 0 #182126; }
    main { display: grid; grid-template-columns: 1.05fr .95fr; gap: .34in; height: calc(100% - .55in); align-items: center; position: relative; z-index: 1; }
    h1 { margin: 0 0 .18in; font-size: .52in; line-height: .94; text-transform: uppercase; }
    p { font-size: .18in; line-height: 1.45; }
    aside { border: 6px solid #182126; background: #fffdf4; box-shadow: 10px 10px 0 #182126; padding: .22in; min-height: 4.4in; display: grid; place-items: center; }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: .12in; margin-top: .28in; }
    .stat { border: 5px solid #182126; background: #fffdf4; padding: .13in; min-height: .9in; box-shadow: 6px 6px 0 #182126; }
    .stat span, .stat small { display: block; font-size: .1in; text-transform: uppercase; font-weight: 700; }
    .stat strong { display: block; margin: .05in 0; font-size: .22in; }
    .bars { width: 100%; display: grid; gap: .11in; }
    .bar-row { display: grid; grid-template-columns: 1.55in 1fr .55in; gap: .12in; align-items: center; font-weight: 700; font-size: .13in; }
    .bar-row div { height: .25in; border: 4px solid #182126; background: #fff; }
    .bar-row i { display: block; height: 100%; background: #2e68d6; }
    .pipeline { width: 100%; margin: 0; padding: 0; list-style: none; display: grid; gap: .18in; }
    .pipeline li { border: 5px solid #182126; background: #24a99a; padding: .16in; font-weight: 700; box-shadow: 6px 6px 0 #182126; }
    .flow { width: 100%; margin: 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(2, 1fr); gap: .14in; }
    .flow li, .script-list li { border: 5px solid #182126; background: #fffdf4; padding: .13in; font-weight: 700; box-shadow: 5px 5px 0 #182126; }
    .flow li:nth-child(2n), .script-list li:nth-child(2n) { background: #ffe0d5; }
    .flow li:nth-child(3n), .script-list li:nth-child(3n) { background: #dff5ee; }
    .script-list { width: 100%; margin: 0; padding: 0; list-style: none; display: grid; gap: .12in; font-size: .13in; }
    .roadmap li { background: #f0b429; }
    .pixel-tower { display: grid; grid-template-columns: repeat(2, 1.2in); gap: .2in; }
    .pixel-tower i { display: block; width: 1.2in; height: 1.2in; border: 6px solid #182126; box-shadow: 8px 8px 0 #182126; }
    .pixel-tower i:nth-child(1) { background: #2e68d6; } .pixel-tower i:nth-child(2) { background: #df5a44; } .pixel-tower i:nth-child(3) { background: #24a99a; } .pixel-tower i:nth-child(4) { background: #7252b8; }
    .pixel-map, .versus { width: 100%; display: grid; gap: .18in; text-align: center; font-weight: 700; }
    .pixel-map b { height: .18in; background: repeating-linear-gradient(90deg, #182126 0 20px, transparent 20px 34px); }
    .pixel-map span, .versus b, .versus small { border: 5px solid #182126; background: #fffdf4; padding: .18in; box-shadow: 6px 6px 0 #182126; }
    .versus span { font-size: .34in; color: #df5a44; }
    .mint aside, .mint .bar-row i { background: #bcefe6; } .blue aside, .blue .bar-row i { background: #c8dcff; } .yellow aside, .yellow .bar-row i { background: #ffe7a3; } .violet aside, .violet .bar-row i { background: #e4ddff; } .red aside, .red .bar-row i { background: #ffd3c8; }
  </style>
</head>
<body>${slides}</body>
</html>`;
}

const countryDisplayNames = {
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

function displayCountry(country) {
  return countryDisplayNames[country] ?? country;
}

function stripSegment(value) {
  return value.replace(/^\d+\.\s*/, '');
}

function speakerRecommendation(market) {
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

function speakerSection({ page, title, visible, say }) {
  return `
    <section class="note">
      <div class="note-number">${String(page).padStart(2, '0')}</div>
      <div>
        <p class="kicker">No site fica</p>
        <h2>${escapeHtml(title)}</h2>
        <p class="visible">${escapeHtml(visible)}</p>
        <p class="kicker talk">Fala do apresentador</p>
        <p class="say">${escapeHtml(say)}</p>
      </div>
    </section>
  `;
}

function buildPresenterNotesHtml(snapshot) {
  const topMarket = snapshot.market[0];
  const topPersona = snapshot.personas[0];
  const topSegment = [...snapshot.segments].sort((left, right) => right.lead_count - left.lead_count)[0];
  const segment = stripSegment(topSegment.company_size_segment);
  const country = displayCountry(topMarket.company_country);
  const recommendation = speakerRecommendation(topMarket);
  const focusLine = `Europa soma ${formatNumber(snapshot.metadata.source_rows)} leads em ${formatNumber(snapshot.metadata.unique_companies)} empresas no recorte europeu.`;

  const sections = [
    speakerSection({
      page: 1,
      title: 'A hCaptcha deve se posicionar como alternativa anti-bot centrada em privacidade',
      visible: 'Tese principal: privacidade, conformidade europeia e eficiencia tecnica como diferenciais contra solucoes anti-bot tradicionais.',
      say: 'Eu comeco respondendo diretamente ao desafio: a hCaptcha deve entrar na Europa como alternativa anti-bot com privacidade no centro da mensagem. O mercado europeu valoriza conformidade, soberania de dados e reducao de dependencia do ecossistema Google. Por isso, a narrativa precisa combinar protecao contra bots, seguranca para GDPR e facilidade de adocao tecnica.',
    }),
    speakerSection({
      page: 2,
      title: 'A planilha raw virou uma base gold pronta para decisao',
      visible: `${formatNumber(snapshot.metadata.source_rows)} leads europeus elegiveis em ${formatNumber(snapshot.metadata.unique_companies)} empresas, tratados sem expor nomes de contas no site.`,
      say: `A analise partiu de uma base raw e chegou a ${formatNumber(snapshot.metadata.source_rows)} leads europeus elegiveis em ${formatNumber(snapshot.metadata.unique_companies)} empresas. Antes de defender qualquer recomendacao, os dados foram limpos, deduplicados e harmonizados por pais, persona e porte. Isso torna a leitura comercial mais confiavel e evita conclusoes tiradas de uma planilha bruta.`,
    }),
    speakerSection({
      page: 3,
      title: 'A priorizacao por pais reduz dispersao comercial',
      visible: `${country} concentra ${formatNumber(topMarket.lead_count)} leads em ${formatNumber(topMarket.company_count)} empresas e sustenta o primeiro foco comercial do recorte.`,
      say: `${country} e o mercado de referencia neste recorte, com ${formatNumber(topMarket.lead_count)} leads e ${formatNumber(topMarket.company_count)} empresas mapeadas. A prioridade nao e escolher qualquer pais europeu, mas concentrar esforco onde existe massa critica para outbound e ABM. ${recommendation}`,
    }),
    speakerSection({
      page: 4,
      title: 'A venda precisa falar com tecnologia e compliance',
      visible: `${topPersona.role_category} lidera o recorte com ${formatPercent(topPersona.lead_share)} dos leads comparaveis.`,
      say: `A persona em maior evidencia neste recorte e ${topPersona.role_category}, responsavel por ${formatPercent(topPersona.lead_share)} dos leads comparaveis. A venda da hCaptcha precisa conversar com decisores tecnicos, mas tambem traduzir privacidade, seguranca e risco regulatorio para quem influencia a compra.`,
    }),
    speakerSection({
      page: 5,
      title: 'Enterprise valida a tese; mid-market amplia a escala',
      visible: `${segment} indica onde a tese tem maior impacto comercial antes de expandir para outros portes de empresa.`,
      say: `O segmento em foco e ${segment}. Esta leitura mostra onde a proposta tende a ter mais impacto: empresas maiores validam a tese por volume, risco e maturidade tecnica; mid-market e startups funcionam melhor como expansao depois que a mensagem principal estiver provada.`,
    }),
    speakerSection({
      page: 6,
      title: 'A propensao aparece por proxies firmograficos',
      visible: 'A base nao traz cliques ou intencao declarada; por isso, a propensao foi lida por cargo, pais, porte e operacao distribuida.',
      say: `Aqui eu deixo claro o limite metodologico: a planilha nao mede comportamento real, como clique, visita ou uso atual de CAPTCHA. Entao eu uso proxies defensaveis. O sinal mais forte e ${snapshot.adoption_signals[0].signal.toLowerCase()}, com ${snapshot.adoption_signals[0].value}; depois entram compradores qualificados, maturidade enterprise e operacao distribuida. Isso mostra propensao, mas deve ser apresentado como inferencia, nao como certeza.`,
    }),
    speakerSection({
      page: 7,
      title: 'Privacidade vira criterio de compra e diferenciacao',
      visible: 'As barreiras principais sao GDPR, inercia do reCAPTCHA, friccao de UX e falta de sinal direto de intencao.',
      say: 'Nesta parte eu transformo risco em oportunidade. Na Europa, privacidade e GDPR podem travar uma compra se a solucao parecer invasiva, mas tambem podem abrir espaco para a hCaptcha. A inercia do reCAPTCHA deve ser vencida com uma mensagem de migracao simples. A preocupacao com UX deve ser respondida com modos de baixa friccao. E a falta de intencao direta vira uma recomendacao de validar rapidamente por outbound.',
    }),
    speakerSection({
      page: 8,
      title: 'O Power BI transforma os achados em decisao filtravel',
      visible: 'A entrega cobre dashboard interativo, relatorio executivo, PDF publico, roteiro privado e testes de qualidade.',
      say: 'Eu reforco que o objetivo final do desafio nao era apenas contar leads. Era criar um dashboard interativo para apoiar decisao. O Power BI cobre mercado, perfil comprador, porte, operacao distribuida e mapa de acao. O site e o PDF sao materiais de defesa; o dashboard e o artefato principal para tomada de decisao.',
    }),
    speakerSection({
      page: 9,
      title: 'Do dado bruto a decisao comercial',
      visible: 'Trilha reproduzivel: pergunta de negocio, diagnostico, base gold, modelo BI, validacao e sintese comercial.',
      say: 'O projeto seguiu uma trilha de decisao: primeiro veio a pergunta de negocio, depois a exploracao dos dados, a criacao da base gold, o modelo Power BI, os testes e a sintese final. Essa sequencia mostra que a recomendacao nao saiu de graficos soltos; ela foi construida a partir de um processo reproduzivel.',
    }),
    speakerSection({
      page: 10,
      title: 'Entrar com privacidade, provar valor e depois escalar',
      visible: 'Prioridade: entrar com privacidade, provar valor nas contas de maior impacto e escalar para mercados adjacentes.',
      say: `A recomendacao final e entrar com foco em mercados prioritarios, adaptar a mensagem por pais e persona, e provar valor nas contas de maior impacto antes de escalar. ${focusLine} O argumento comercial deve ser: ${recommendation}`,
    }),
  ].join('');

  return `<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>Roteiro do apresentador - hCaptcha Europa</title>
  <style>
    @page { size: A4; margin: 14mm; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: #182126;
      background: #fffdf4;
      font-family: "Cascadia Code", "JetBrains Mono", "Courier New", monospace;
    }
    header {
      border: 4px solid #182126;
      background: linear-gradient(135deg, #fff7dc, #dff5ee 58%, #ffe0d5);
      box-shadow: 6px 6px 0 #182126;
      padding: 18px;
      margin-bottom: 18px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1;
      text-transform: uppercase;
    }
    header p {
      margin: 0;
      line-height: 1.45;
    }
    .note {
      display: grid;
      grid-template-columns: 52px 1fr;
      gap: 14px;
      border: 3px solid #182126;
      background: #fff9e8;
      box-shadow: 5px 5px 0 #182126;
      padding: 14px;
      margin-bottom: 16px;
      break-inside: avoid;
    }
    .note-number {
      display: grid;
      width: 42px;
      height: 42px;
      place-items: center;
      border: 3px solid #182126;
      background: #f0b429;
      box-shadow: 4px 4px 0 #182126;
      font-weight: 900;
    }
    .kicker {
      margin: 0 0 6px;
      color: #2e68d6;
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .talk {
      color: #7252b8;
      margin-top: 12px;
    }
    h2 {
      margin: 0 0 8px;
      font-size: 17px;
      line-height: 1.15;
    }
    .visible,
    .say {
      margin: 0;
      font-size: 12.5px;
      line-height: 1.55;
    }
    .visible {
      border-left: 5px solid #24a99a;
      padding-left: 10px;
    }
    .say {
      border-left: 5px solid #7252b8;
      padding-left: 10px;
    }
  </style>
</head>
<body>
  <header>
    <h1>Roteiro do apresentador</h1>
    <p>Use este PDF como material privado de fala. O site mostra apenas a versao resumida para a audiencia.</p>
  </header>
  ${sections}
</body>
</html>`;
}

function glossaryTerm(term) {
  return `
    <article class="term-card">
      <span>${escapeHtml(term.category)}</span>
      <h2>${escapeHtml(term.term)}</h2>
      <p>${escapeHtml(term.definition)}</p>
      <dl>
        <div>
          <dt>No projeto</dt>
          <dd>${escapeHtml(term.in_project)}</dd>
        </div>
        <div>
          <dt>Por que importa</dt>
          <dd>${escapeHtml(term.why_it_matters)}</dd>
        </div>
      </dl>
    </article>
  `;
}

function buildGlossaryHtml(snapshot) {
  const terms = snapshot.glossary_terms ?? [];
  const categories = Array.from(new Set(terms.map((term) => term.category)));
  const categorySections = categories
    .map((category) => {
      const cards = terms.filter((term) => term.category === category).map(glossaryTerm).join('');
      return `
        <section>
          <h1>${escapeHtml(category)}</h1>
          <div class="term-grid">${cards}</div>
        </section>
      `;
    })
    .join('');

  return `<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>Glossario tecnico - hCaptcha Europa</title>
  <style>
    @page { size: A4; margin: 13mm; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: #182126;
      background: #fffdf4;
      font-family: "Cascadia Code", "JetBrains Mono", "Courier New", monospace;
    }
    header {
      border: 4px solid #182126;
      background: linear-gradient(135deg, #fff7dc, #dff5ee 58%, #ffe0d5);
      box-shadow: 6px 6px 0 #182126;
      padding: 18px;
      margin-bottom: 18px;
    }
    header h1 {
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1;
      text-transform: uppercase;
    }
    header p {
      margin: 0;
      line-height: 1.45;
    }
    section {
      break-inside: avoid;
      margin-bottom: 18px;
    }
    section > h1 {
      width: max-content;
      margin: 0 0 12px;
      border: 3px solid #182126;
      background: #f0b429;
      box-shadow: 4px 4px 0 #182126;
      padding: 6px 10px;
      font-size: 15px;
      text-transform: uppercase;
    }
    .term-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .term-card {
      border: 3px solid #182126;
      background: #fff9e8;
      box-shadow: 5px 5px 0 #182126;
      padding: 13px;
      break-inside: avoid;
    }
    .term-card span {
      display: block;
      margin-bottom: 6px;
      color: #2e68d6;
      font-size: 10px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .term-card h2 {
      margin: 0 0 8px;
      font-size: 17px;
      line-height: 1.1;
    }
    .term-card p,
    .term-card dd {
      margin: 0;
      font-size: 11px;
      line-height: 1.45;
    }
    .term-card dl {
      display: grid;
      gap: 8px;
      margin: 10px 0 0;
    }
    .term-card dt {
      margin-bottom: 3px;
      color: #7252b8;
      font-size: 10px;
      font-weight: 900;
      text-transform: uppercase;
    }
  </style>
</head>
<body>
  <header>
    <h1>Glossario tecnico</h1>
    <p>Material de apoio para explicar os termos usados no dashboard, no relatorio e na apresentacao da estrategia de posicionamento da hCaptcha na Europa.</p>
  </header>
  ${categorySections}
</body>
</html>`;
}

async function renderPdfArtifacts(page, artifacts) {
  for (const artifact of artifacts) {
    await page.goto(pathToFileURL(artifact.htmlPath).href, { waitUntil: 'load' });
    await page.pdf(artifact.pdfOptions);
  }
}

async function main() {
  if (!existsSync(dataPath)) {
    throw new Error(`Missing snapshot at ${dataPath}`);
  }

  const snapshot = JSON.parse(await readFile(dataPath, 'utf8'));
  const html = buildHtml(snapshot);
  const presenterNotesHtml = buildPresenterNotesHtml(snapshot);
  const glossaryHtml = buildGlossaryHtml(snapshot);

  await mkdir(path.dirname(presenterNotesHtmlPath), { recursive: true });
  await Promise.all([
    writeFile(htmlPath, cleanHtml(html), 'utf8'),
    writeFile(presenterNotesHtmlPath, cleanHtml(presenterNotesHtml), 'utf8'),
    writeFile(glossaryHtmlPath, cleanHtml(glossaryHtml), 'utf8'),
    writeFile(glossaryReportHtmlPath, cleanHtml(glossaryHtml), 'utf8'),
  ]);

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
  await renderPdfArtifacts(page, [
    {
      htmlPath,
      pdfOptions: {
        path: pdfPath,
        width: '13.333in',
        height: '7.5in',
        printBackground: true,
        preferCSSPageSize: true,
      },
    },
    {
      htmlPath: presenterNotesHtmlPath,
      pdfOptions: {
        path: presenterNotesPdfPath,
        format: 'A4',
        printBackground: true,
        preferCSSPageSize: true,
      },
    },
    {
      htmlPath: glossaryHtmlPath,
      pdfOptions: {
        path: glossaryPdfPath,
        format: 'A4',
        printBackground: true,
        preferCSSPageSize: true,
      },
    },
  ]);
  await browser.close();
  await copyFile(glossaryPdfPath, glossaryReportPdfPath);

  console.log(`Wrote ${pdfPath}`);
  console.log(`Wrote ${presenterNotesPdfPath}`);
  console.log(`Wrote ${glossaryPdfPath}`);
  console.log(`Wrote ${glossaryReportPdfPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
