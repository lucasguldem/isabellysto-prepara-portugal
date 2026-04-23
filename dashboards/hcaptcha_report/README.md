# hCaptcha Power BI Project

Este projeto foi estruturado em formato `PBIP` para desenvolvimento versionável.

## Como abrir

1. Abra [hcaptcha_report.pbip](hcaptcha_report.pbip) no Power BI Desktop.
2. Verifique o parâmetro `DataRoot` no Semantic Model.
3. Faça o refresh do modelo.
4. Se quiser o artefato monolítico, use `Save As` no Desktop para gerar um `.pbix`.

## Observações

- O modelo lê os CSVs processados em `data/processed/` via caminho UNC do WSL.
- O relatório usa as figuras geradas no notebook como blueprint visual inicial.
- O dataset já inclui medidas para leads, empresas, países, cross-border share e segmentação por persona e porte.
- O arquivo `.pbix` final é um artefato local e não deve ser versionado; o repositório mantém o `PBIP` como fonte de verdade.
