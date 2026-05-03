# hCaptcha Power BI Project

Este projeto foi estruturado em formato `PBIP` para desenvolvimento versionável.

## Como abrir

1. Abra [hcaptcha_report.pbip](hcaptcha_report.pbip) no Power BI Desktop.
2. Verifique o parâmetro `DataRoot` no Semantic Model.
3. Faça o refresh do modelo.
4. Se quiser o artefato monolítico, use `Save As` no Desktop para gerar um `.pbix`.

## Observações

- O modelo lê os CSVs processados pelo parâmetro `DataRoot`, apontando para `C:\Users\02luc\Documents\PowerBIData\hcaptcha\processed`.
- Esse diretório Windows é sincronizado a partir de `data/processed/` por `scripts/export_gateway_ready.py`.
- O relatório usa visuais nativos do Power BI para cards, barras, tabelas e filtros interativos.
- O dataset já inclui medidas para leads, empresas, países, cross-border share e segmentação por persona e porte.
