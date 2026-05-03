# Blueprint do Dashboard Power BI

Este dashboard foi desenvolvido em formato `PBIP` e usa o parâmetro `DataRoot` para carregar os CSVs processados do mirror Windows:

`C:\Users\02luc\Documents\PowerBIData\hcaptcha\processed`

## Página 1: Market Command

**Objetivo:** mostrar onde existe massa crítica de leads e empresas para priorização comercial.

**Visuais:**
- Card: medida `Leads`
- Card: medida `Companies`
- Card: medida `Countries In Scope`
- Barra horizontal: `Leads[Country]` por medida `Leads`
- Tabela: `Leads[Country]`, `Leads`, `Companies`, `Cross-Border Share`, `Executive Leads`
- Filtro interativo: `Leads[Country]`

**Mensagem para apresentação:**
Alemanha, Reino Unido, França, Espanha e Portugal concentram a maior parte da oportunidade inicial.

## Página 2: Buyer Intelligence

**Objetivo:** identificar quem compra e como a mensagem muda por porte de empresa.

**Visuais:**
- Barra horizontal: `Leads[Role]` por medida `Leads`
- Colunas: `Leads[Segment]` por medida `Leads`
- Barra empilhada: `Leads[Role]` x `Leads[Segment]`
- Tabela: `Leads[Role]`, `Leads`, `Companies`
- Filtro interativo: `Leads[Segment]`

**Mensagem para apresentação:**
Os perfis mais relevantes são decisores técnicos e áreas de dados/compliance; por isso, a narrativa deve combinar eficiência técnica com privacidade e conformidade.

## Página 3: Border Signal

**Objetivo:** evidenciar operação distribuída e oportunidade de posicionamento para empresas com presença internacional.

**Visuais:**
- Card: medida `Cross-Border Contacts`
- Card: medida `Cross-Border Share`
- Barra horizontal: `Leads[Country]` por `Cross-Border Share`
- Tabela: `Leads[Country]`, `Leads`, `Cross-Border Contacts`, `Cross-Border Share`
- Filtro interativo: `Leads[Mismatch]`

**Mensagem para apresentação:**
O sinal cross-border indica empresas com contatos e sedes em países diferentes, sugerindo maior necessidade de proteção consistente, baixa fricção e discurso regulatório claro.

## Página 4: Action Map

**Objetivo:** transformar leitura descritiva em priorização comercial.

**Visuais:**
- Barra: `Country Priority[Tier]` por soma de `Country Priority[Leads]`
- Tabela: `Country Priority[Rank]`, `Country Priority[Country]`, `Country Priority[Tier]`, `Country Priority[Leads]`, `Country Priority[Companies]`

**Mensagem para apresentação:**
Priorizar Tier 1 com mensagens segmentadas: privacy-first para Alemanha e França; eficiência técnica e escala para Reino Unido; mensagem híbrida para Espanha e Portugal.

## Modelo Semântico

**Tabelas físicas geradas pelo pipeline:**
- `hcaptcha_europe_gold.csv`
- `dim_country_priority.csv`
- `dim_role_category.csv`
- `dim_company_size.csv`

**Tabelas no Power BI:**
- `Leads`
- `Country Priority`
- `Role Category`
- `Company Size`
- `About`

`Leads` e `Country Priority` são usadas diretamente nos visuais. `Role Category` e `Company Size` apoiam a modelagem e mantêm a documentação analítica das dimensões.

## Materialização

Para gerar o arquivo standalone:

1. Abra [hcaptcha_report.pbip](/home/lucasguldem/dev/data-science/isabellysto-data-analytics/powerbi/hcaptcha-positioning/hcaptcha_report.pbip) no Power BI Desktop.
2. Verifique o parâmetro `DataRoot`.
3. Faça o refresh.
4. Use `Save As` para gerar o `.pbix`.
