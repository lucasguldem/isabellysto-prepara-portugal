# hCaptcha Power BI Project

Este projeto foi estruturado em formato `PBIP` para desenvolvimento versionável.

## Como abrir

1. Abra [hcaptcha_report.pbip](hcaptcha_report.pbip) no Power BI Desktop.
2. Verifique o parâmetro `DataRoot` no Semantic Model.
3. Faça o refresh do modelo.
4. Se quiser o artefato monolítico, use `Save As` no Desktop para gerar um `.pbix`.

## Pré-visualização do relatório Power BI

As imagens abaixo deixam as páginas do relatório visíveis diretamente no GitHub. Elas são geradas em `reports/figures/` a partir dos mesmos CSVs processados usados pelo projeto `PBIP`; a exploração interativa continua no Power BI Desktop gratuito.

### Market Command

<img src="../../reports/figures/04_powerbi_market_command.png" alt="Prévia estática da página Market Command" width="100%"/>

### Buyer Intelligence

<img src="../../reports/figures/05_powerbi_buyer_intelligence.png" alt="Prévia estática da página Buyer Intelligence" width="100%"/>

### Border Signal

<img src="../../reports/figures/06_powerbi_border_signal.png" alt="Prévia estática da página Border Signal" width="100%"/>

### Action Map

<img src="../../reports/figures/07_powerbi_action_map.png" alt="Prévia estática da página Action Map" width="100%"/>

## Figuras analíticas complementares

### Prioridade de mercado por país

<img src="../../reports/figures/01_market_overview_top_countries.png" alt="Top mercados europeus por volume de leads elegíveis" width="100%"/>

### Mix de personas por porte

<img src="../../reports/figures/02_icp_role_size_heatmap.png" alt="Mix de personas por porte de empresa" width="100%"/>

### Sinal de operação distribuída

<img src="../../reports/figures/03_cross_border_signal.png" alt="Mercados com maior sinal de operação distribuída" width="100%"/>

## Observações

- O modelo lê os CSVs processados pelo parâmetro `DataRoot`, apontando para `C:\Users\02luc\Documents\PowerBIData\hcaptcha\processed`.
- Esse diretório Windows funciona como espelho local dos arquivos de `data/processed/`.
- O relatório usa visuais nativos do Power BI para cards, barras, tabelas e filtros interativos.
- O dataset já inclui medidas para leads, empresas, países, cross-border share e segmentação por persona e porte.
