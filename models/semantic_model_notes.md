# Notas do Modelo Semântico

## Tabelas

### `hcaptcha_europe_gold`

Tabela fato principal em granularidade de lead limpo.

**Chaves analíticas:**
- `company_country`
- `role_category`
- `company_size_segment`

### `dim_country_priority`

Resumo por país para priorização comercial.

**Relacionamento sugerido:**
- `hcaptcha_europe_gold[company_country]` -> `dim_country_priority[company_country]`

### `dim_role_category`

Resumo por categoria de cargo.

**Relacionamento sugerido:**
- `hcaptcha_europe_gold[role_category]` -> `dim_role_category[role_category]`

### `dim_company_size`

Resumo por segmento de porte.

**Relacionamento sugerido:**
- `hcaptcha_europe_gold[company_size_segment]` -> `dim_company_size[company_size_segment]`

## Medidas sugeridas no Power BI

- `Leads = COUNTROWS(hcaptcha_europe_gold)`
- `Empresas = DISTINCTCOUNT(hcaptcha_europe_gold[company_name])`
- `% Enterprise = DIVIDE(CALCULATE([Leads], hcaptcha_europe_gold[company_size_segment] = "3. Enterprise"), [Leads])`
- `% Operação Distribuída = DIVIDE(CALCULATE([Leads], hcaptcha_europe_gold[contact_company_country_mismatch] = TRUE()), [Leads])`
- `% Decision Makers = DIVIDE(CALCULATE([Leads], hcaptcha_europe_gold[role_category] = "Executive / Technical Decision Maker"), [Leads])`
