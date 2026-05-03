# Notas do Modelo Semântico

## Fontes Físicas

O pipeline gera quatro CSVs em `data/processed/` e sincroniza os mesmos arquivos para o mirror Windows usado pelo Power BI:

- `hcaptcha_europe_gold.csv`
- `dim_country_priority.csv`
- `dim_role_category.csv`
- `dim_company_size.csv`

No modelo PBIP, o parâmetro `DataRoot` aponta para `C:\Users\02luc\Documents\PowerBIData\hcaptcha\processed`.

## Tabelas do Modelo

### `Leads`

Tabela fato principal, em granularidade de lead limpo, carregada de `hcaptcha_europe_gold.csv`.

**Chaves analíticas:**
- `Country`
- `Role`
- `Segment`
- `Mismatch`

### `Country Priority`

Dimensão/resumo por país, carregada de `dim_country_priority.csv`.

**Relacionamento:**
- `Leads[Country]` -> `Country Priority[Country]`

Essa tabela é usada diretamente na página de próximas ações, com ranking, tier e recomendação comercial por país.

### `Role Category`

Dimensão/resumo por categoria de cargo, carregada de `dim_role_category.csv`.

**Relacionamento:**
- `Leads[Role]` -> `Role Category[Role]`

Os visuais de persona usam `Leads[Role]` diretamente para preservar a interatividade com a tabela fato.

### `Company Size`

Dimensão/resumo por porte da empresa, carregada de `dim_company_size.csv`.

**Relacionamento:**
- `Leads[Segment]` -> `Company Size[Segment]`

Os visuais de porte usam `Leads[Segment]` diretamente para preservar a interatividade com a tabela fato.

### `About`

Tabela técnica de metadados do modelo. Não precisa ser apresentada nos slides.

## Medidas no Power BI

- `Leads = COUNTROWS('Leads')`
- `Companies = DISTINCTCOUNT('Leads'[company_name])`
- `Countries In Scope = DISTINCTCOUNT('Leads'[Country])`
- `Cross-Border Contacts = CALCULATE([Leads], 'Leads'[Mismatch] = TRUE())`
- `Cross-Border Share = DIVIDE([Cross-Border Contacts], [Leads])`
- `Executive Leads = CALCULATE([Leads], 'Leads'[Role] = "Executive / Technical Decision Maker")`
- `Compliance Leads = CALCULATE([Leads], 'Leads'[Role] = "Data / Compliance")`
- `Enterprise Leads = CALCULATE([Leads], 'Leads'[Segment] = "3. Enterprise")`
- `Mid-Market Leads = CALCULATE([Leads], 'Leads'[Segment] = "2. Mid-Market")`
- `Startup / SMB Leads = CALCULATE([Leads], 'Leads'[Segment] = "1. Startup / SMB")`
