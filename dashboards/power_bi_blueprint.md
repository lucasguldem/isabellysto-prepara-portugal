# Blueprint do Dashboard Power BI

## Página 1: Market Overview

**Objetivo:** mostrar onde existe massa crítica de leads e empresas para priorização comercial.

**Visuais:**
- Card: `COUNTROWS(hcaptcha_europe_gold)`
- Card: `DISTINCTCOUNT(hcaptcha_europe_gold[company_name])`
- Card: `DISTINCTCOUNT(hcaptcha_europe_gold[company_country])`
- Barra horizontal: `lead_count` por `company_country`
- Tabela: `company_country`, `lead_count`, `company_count`, `priority_tier`, `messaging_angle`

**Campos principais:**
- `hcaptcha_europe_gold[company_country]`
- `dim_country_priority[lead_count]`
- `dim_country_priority[company_count]`
- `dim_country_priority[priority_tier]`
- `dim_country_priority[messaging_angle]`

## Página 2: ICP e Personas

**Objetivo:** identificar quem compra e como a mensagem muda por porte de empresa.

**Visuais:**
- Barra horizontal: `lead_count` por `role_category`
- Matriz: `role_category` x `company_size_segment`
- Barra: setores mais recorrentes com foco em `Executive / Technical Decision Maker`, `Data / Compliance` e `Security / Risk`

**Campos principais:**
- `hcaptcha_europe_gold[role_category]`
- `hcaptcha_europe_gold[company_size_segment]`
- `hcaptcha_europe_gold[company_industry]`
- `dim_role_category[lead_count]`
- `dim_company_size[lead_count]`

## Página 3: Go-to-Market

**Objetivo:** transformar leitura descritiva em priorização comercial.

**Visuais:**
- Scatter: `lead_count` x `mismatch_share`
- Matriz: `company_country` x `company_size_segment`
- Tabela Tier 1 / Tier 2 / Tier 3 com `strategic_recommendation`

**Campos principais:**
- `dim_country_priority[priority_tier]`
- `dim_country_priority[mismatch_share]`
- `dim_country_priority[strategic_recommendation]`
- `hcaptcha_europe_gold[contact_company_country_mismatch]`

## Página 4: Executive Summary

**Objetivo:** condensar os insights acionáveis para o relatório final.

**Mensagens recomendadas:**
- `Germany` e `France`: posicionamento `privacy-first`, alternativa GDPR-safe ao reCAPTCHA.
- `United Kingdom`, `Ireland`, `Estonia`, `Lithuania`: foco em eficiência, velocidade de implementação e escala.
- `Spain` e `Portugal`: mensagem híbrida de performance anti-bot com aderência regulatória.

**KPIs sugeridos:**
- `% enterprise`
- `% Data / Compliance`
- `% Executive / Technical Decision Maker`
- `% de operação distribuída`

## Materialização

Este dashboard foi desenvolvido em formato `PBIP`.

Para gerar o arquivo standalone:

1. Abra [hcaptcha_report.pbip](/home/lucasguldem/dev/data-science/isabellysto-data-analytics/dashboards/hcaptcha_report/hcaptcha_report.pbip) no Power BI Desktop.
2. Verifique o parâmetro `DataRoot` do modelo semântico.
3. Faça o refresh.
4. Use `Save As` para gerar o `.pbix`.
