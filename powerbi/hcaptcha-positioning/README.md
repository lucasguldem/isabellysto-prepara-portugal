# hCaptcha Power BI Project

Este projeto foi estruturado em formato `PBIP` para desenvolvimento versionável.

## Como abrir

1. Abra [hcaptcha_report.pbip](hcaptcha_report.pbip) no Power BI Desktop.
2. Verifique o parâmetro `DataRoot` no Semantic Model.
3. Faça o refresh do modelo.
4. Se quiser o artefato monolítico, use `Save As` no Desktop para gerar um `.pbix`.

## Pré-visualização do relatório

As imagens abaixo deixam os principais resultados visíveis diretamente no GitHub. Elas são geradas em `reports/figures/`; o relatório interativo completo continua no projeto `PBIP`.

### Prioridade de mercado por país

<img src="../../reports/figures/01_market_overview_top_countries.png" alt="Top mercados europeus por volume de leads elegíveis" width="100%"/>

### Mix de personas por porte

<img src="../../reports/figures/02_icp_role_size_heatmap.png" alt="Mix de personas por porte de empresa" width="100%"/>

### Sinal de operação distribuída

<img src="../../reports/figures/03_cross_border_signal.png" alt="Mercados com maior sinal de operação distribuída" width="100%"/>

## Observações

- O modelo lê os CSVs processados pelo parâmetro `DataRoot`, apontando para `C:\Users\02luc\Documents\PowerBIData\hcaptcha\processed`.
- Esse diretório Windows é sincronizado a partir de `data/processed/` por `scripts/export_gateway_ready.py`.
- O relatório usa visuais nativos do Power BI para cards, barras, tabelas e filtros interativos.
- O dataset já inclui medidas para leads, empresas, países, cross-border share e segmentação por persona e porte.
