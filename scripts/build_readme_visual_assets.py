from __future__ import annotations

import os
from pathlib import Path
from textwrap import fill

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Rectangle


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

BG = "#FFF7DC"
PANEL = "#FFFDF4"
PANEL_ALT = "#FFF9E8"
INK = "#182126"
SHADOW = "#0D1215"
MUTED = "#40545C"
GRID = "#D7CBB6"
TEAL = "#24A99A"
ORANGE = "#F0B429"
BLUE = "#2E68D6"
PURPLE = "#7252B8"
RED = "#DF5A44"
LEAF = "#94BD3F"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans Mono",
        "axes.titleweight": "bold",
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
    }
)


def _load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    gold = pd.read_csv(PROCESSED_DIR / "hcaptcha_europe_gold.csv")
    country = pd.read_csv(PROCESSED_DIR / "dim_country_priority.csv")
    role = pd.read_csv(PROCESSED_DIR / "dim_role_category.csv")
    size = pd.read_csv(PROCESSED_DIR / "dim_company_size.csv")
    return gold, country, role, size


def _add_pixel_grid(fig: plt.Figure) -> None:
    for x in [i / 18 for i in range(1, 18)]:
        fig.lines.append(
            plt.Line2D([x, x], [0, 1], transform=fig.transFigure, color=INK, alpha=0.045, linewidth=0.8, zorder=-20)
        )
    for y in [i / 14 for i in range(1, 14)]:
        fig.lines.append(
            plt.Line2D([0, 1], [y, y], transform=fig.transFigure, color="#FFFFFF", alpha=0.24, linewidth=0.8, zorder=-20)
        )


def _add_pixel_mosaic(fig: plt.Figure, x: float = 0.86, y: float = 0.88, scale: float = 1.0, alpha: float = 0.92) -> None:
    size = 0.012 * scale
    gap = 0.003 * scale
    pattern = [
        (0, 0, BLUE),
        (1, 0, ORANGE),
        (2, 0, TEAL),
        (0.5, -1, RED),
        (1.5, -1, PURPLE),
        (2.5, -1, LEAF),
        (1, -2, INK),
        (2, -2, BLUE),
    ]
    for col, row, color in pattern:
        fig.patches.append(
            Rectangle(
                (x + col * (size + gap), y + row * (size + gap)),
                size,
                size,
                transform=fig.transFigure,
                facecolor=color,
                edgecolor="none",
                alpha=alpha,
                zorder=-2,
            )
        )


def _panel_shadow(fig: plt.Figure, ax: plt.Axes, dx: float = 0.006, dy: float = -0.008) -> None:
    bbox = ax.get_position()
    fig.patches.extend(
        [
            Rectangle(
                (bbox.x0 + dx, bbox.y0 + dy),
                bbox.width,
                bbox.height,
                transform=fig.transFigure,
                facecolor=SHADOW,
                edgecolor="none",
                zorder=-7,
            ),
            Rectangle(
                (bbox.x0, bbox.y0),
                bbox.width,
                bbox.height,
                transform=fig.transFigure,
                facecolor=PANEL,
                edgecolor=INK,
                linewidth=2.2,
                zorder=-6,
            ),
        ]
    )


def _style_axis(ax: plt.Axes, fig: plt.Figure | None = None, *, grid_axis: str = "x") -> None:
    if fig is not None:
        _panel_shadow(fig, ax)
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_color(INK)
        spine.set_linewidth(2.1)
    ax.tick_params(colors=INK, labelsize=9, width=1.6)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.9)
    ax.set_axisbelow(True)


def _add_title(fig: plt.Figure, title: str, subtitle: str | None = None) -> None:
    fig.patch.set_facecolor(BG)
    _add_pixel_grid(fig)
    _add_pixel_mosaic(fig)
    fig.text(0.04, 0.94, title.upper(), fontsize=20, fontweight="black", color=INK)
    if subtitle:
        fig.text(0.04, 0.895, subtitle, fontsize=10.5, color=MUTED)


def _save(fig: plt.Figure, filename: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / filename
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def _card(ax: plt.Axes, label: str, value: str, detail: str = "", color: str = TEAL) -> None:
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(Rectangle((0.08, 0.04), 0.88, 0.78, facecolor=SHADOW, edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((0.02, 0.12), 0.88, 0.78, facecolor=PANEL, edgecolor=INK, linewidth=2.6, zorder=1))
    ax.add_patch(Rectangle((0.76, 0.14), 0.15, 0.20, facecolor=color, edgecolor=INK, linewidth=2.0, zorder=2))
    ax.text(0.09, 0.66, label.upper(), fontsize=8.5, color=MUTED, fontweight="black", zorder=3)
    ax.text(0.09, 0.37, value, fontsize=22, color=color, fontweight="black", zorder=3)
    if detail:
        ax.text(0.09, 0.18, detail, fontsize=8.5, color=MUTED, zorder=3)


def _prepare_table_panel(fig: plt.Figure, ax: plt.Axes) -> None:
    _panel_shadow(fig, ax)
    ax.axis("off")


def _render_table_image(
    rows: list[list[str]],
    columns: list[str],
    title: str,
    subtitle: str,
    filename: str,
    *,
    widths: list[float] | None = None,
    height: float = 5.2,
) -> Path:
    wrapped_rows = [[fill(str(value), width=34) for value in row] for row in rows]
    fig, ax = plt.subplots(figsize=(13.5, height))
    fig.subplots_adjust(left=0.04, right=0.98, top=0.80, bottom=0.05)
    _add_title(fig, title, subtitle)
    ax.axis("off")
    ax.add_patch(Rectangle((0.012, -0.012), 1, 1, transform=ax.transAxes, facecolor=SHADOW, edgecolor="none", zorder=-3, clip_on=False))
    ax.add_patch(Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor=PANEL, edgecolor=INK, linewidth=2.8, zorder=-2, clip_on=False))
    table = ax.table(
        cellText=wrapped_rows,
        colLabels=columns,
        cellLoc="left",
        loc="center",
        colWidths=widths,
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)

    for (row_idx, _col_idx), cell in table.get_celld().items():
        cell.set_edgecolor(INK)
        cell.set_linewidth(1.35)
        cell.get_text().set_va("center")
        if row_idx == 0:
            cell.set_facecolor(INK)
            cell.get_text().set_color("#FFFFFF")
            cell.get_text().set_fontweight("black")
        else:
            cell.set_facecolor(PANEL if row_idx % 2 else PANEL_ALT)
            cell.get_text().set_color(INK)

    return _save(fig, filename)


def build_documentation_tables(gold: pd.DataFrame, country: pd.DataFrame, role: pd.DataFrame, size: pd.DataFrame) -> list[Path]:
    top5_share = country.head(5)["lead_count"].sum() / len(gold)
    cross_border = int(gold["contact_company_country_mismatch"].sum())
    email_status = gold["email_status"].value_counts().to_dict()
    enterprise_share = (gold["company_size_segment"] == "3. Enterprise").mean()
    mid_share = (gold["company_size_segment"] == "2. Mid-Market").mean()
    smb_share = (gold["company_size_segment"] == "1. Startup / SMB").mean()

    return [
        _render_table_image(
            [
                ["Planilha raw", "1.027", "24 colunas originais", "Atributos profissionais e empresariais da exportação."],
                ["Base gold", f"{len(gold):,}".replace(",", "."), "27 colunas harmonizadas", "Dados deduplicados, normalizados e filtrados para empresas europeias."],
                ["Empresas no escopo", f"{gold['company_name'].nunique():,}".replace(",", "."), "Empresas únicas", "Base para leitura de contas e priorização comercial."],
                ["Dimensão de país", str(len(country)), "Ranking de mercado e tiers", "Usada pelo Power BI e pelo snapshot da apresentação."],
            ],
            ["Camada", "Linhas", "Colunas / escopo", "Observações"],
            "Descrição do dataset",
            "Visão executiva da passagem da planilha original para a base analítica.",
            "00_readme_dataset_overview.png",
            widths=[0.18, 0.12, 0.24, 0.46],
        ),
        _render_table_image(
            [
                ["Padronização", "Mapeia colunas originais para nomes analíticos estáveis.", "Mantém Power BI, notebook e scripts no mesmo schema."],
                ["Deduplicação", "Mantém a melhor linha por E-mail + Nome da empresa.", "Evita dupla contagem do mesmo contato na mesma empresa."],
                ["Geografia", "Usa País da empresa como lente de mercado.", "Define o país correto para posicionamento comercial."],
                ["Filtro europeu", "Mantém empresas de países europeus normalizados.", "Alinha a análise ao desafio de entrada na Europa."],
                ["Personas", "Agrupa cargos em categorias de compra.", "Transforma cargos ruidosos em inteligência comercial."],
                ["Porte", "SMB até 50; Mid-Market até 250; Enterprise acima de 250.", "Permite comparar empresas com faixas raw inconsistentes."],
                ["E-mail", "Preserva status valid, unknown e not valid.", "Status é atributo de qualidade, não filtro rígido da análise."],
            ],
            ["Etapa", "O que acontece", "Motivo analítico"],
            "Tratamento e harmonização",
            "Regras reais aplicadas pelo pipeline, notebook, Power BI e apresentação.",
            "00_readme_treatment_harmonization.png",
            widths=[0.18, 0.42, 0.40],
            height=7.0,
        ),
        _render_table_image(
            [
                ["Linhas raw", "1.027", "Ponto de partida da planilha original."],
                ["Linhas gold", str(len(gold)), "Após deduplicação e filtro por empresa europeia."],
                ["Linhas removidas", str(1027 - len(gold)), "Redução de 14,1% da base raw para a gold."],
                ["Duplicadas contato/empresa", "203", "Warning de qualidade monitorado pelo pipeline."],
                ["Duplicadas exatas", "2", "Registros totalmente duplicados na planilha original."],
                ["Sem país europeu da empresa", "33", "Registros fora da lente europeia."],
                ["Cross-border", f"{cross_border} ({cross_border / len(gold):.1%})", "Proxy de operação distribuída ou internacional."],
                ["Status do e-mail", f"{email_status.get('valid', 0)} valid / {email_status.get('unknown', 0)} unknown / {email_status.get('not valid', 0)} not valid", "Contexto de qualidade preservado."],
            ],
            ["Métrica", "Valor", "Interpretação"],
            "Qualidade e linhagem",
            "Quality gate aprovado e dados consistentes entre data/processed e mirror do Power BI.",
            "00_readme_quality_lineage.png",
            widths=[0.28, 0.24, 0.48],
            height=7.2,
        ),
        _render_table_image(
            [
                ["Concentração geográfica", f"Top 5 mercados concentram {top5_share:.1%}", "GTM inicial focado em Tier 1."],
                ["Personas claras", f"{role.iloc[0]['role_category']} ({role.iloc[0]['lead_share']:.1%}) e {role.iloc[1]['role_category']} ({role.iloc[1]['lead_share']:.1%})", "Mensagem técnica + privacidade/compliance."],
                ["Enterprise lidera", f"Enterprise {enterprise_share:.1%}; Mid-Market {mid_share:.1%}; SMB {smb_share:.1%}", "Provar valor em contas maiores e escalar depois."],
                ["Comportamento por proxy", "Sem cliques, stack, visitas ou eventos de intenção.", "Usar proxies firmográficos com limitação declarada."],
            ],
            ["Achado", "Evidência", "Implicação"],
            "Principais achados estratégicos",
            "Leitura executiva para posicionamento da hCaptcha na Europa.",
            "00_readme_strategic_findings.png",
            widths=[0.24, 0.40, 0.36],
            height=4.8,
        ),
        _render_table_image(
            [
                ["Python + pandas", "ETL, qualidade, dimensoes e snapshots", "scripts/hcaptcha_pipeline.py"],
                ["Jupyter", "EDA e geração das figuras analíticas", "notebooks/hcaptcha_europe_positioning.ipynb"],
                ["Power BI PBIP/TMDL", "Modelo semântico versionável e dashboard", "powerbi/hcaptcha-positioning"],
                ["Matplotlib + seaborn", "Gráficos e previews estáticos do README", "reports/figures"],
                ["React + Vite", "Apresentação pública interativa", "apps/hcaptcha-course-presentation"],
                ["pytest + Vitest", "Validação do pipeline, PBIP e apresentação", "tests/ e src/*.test.ts"],
            ],
            ["Ferramenta", "Uso no projeto", "Evidência"],
            "Ferramentas utilizadas",
            "Stack completa demonstrada por código, artefatos e validações automatizadas.",
            "00_readme_tool_stack.png",
            widths=[0.24, 0.42, 0.34],
            height=5.8,
        ),
    ]


def build_market_dashboard(gold: pd.DataFrame, country: pd.DataFrame) -> Path:
    fig = plt.figure(figsize=(15.2, 8.8), constrained_layout=False)
    _add_title(fig, "Power BI - Market Command", "Prévia estática gerada dos CSVs processados usados pelo PBIP.")
    gs = fig.add_gridspec(
        3,
        4,
        height_ratios=[0.82, 2.35, 2.0],
        left=0.07,
        right=0.97,
        top=0.84,
        bottom=0.07,
        hspace=0.42,
        wspace=0.35,
    )

    _card(fig.add_subplot(gs[0, 0]), "Leads", str(len(gold)), "base gold", TEAL)
    _card(fig.add_subplot(gs[0, 1]), "Empresas", str(gold["company_name"].nunique()), "únicas", ORANGE)
    _card(fig.add_subplot(gs[0, 2]), "Países", str(gold["company_country"].nunique()), "em escopo", BLUE)
    _card(fig.add_subplot(gs[0, 3]), "Top 5", f"{country.head(5)['lead_count'].sum() / len(gold):.1%}", "dos leads", PURPLE)

    ax_bar = fig.add_subplot(gs[1:, :2])
    top = country.head(10).sort_values("lead_count")
    colors = [TEAL if tier == "Tier 1" else "#4267D5" for tier in top["priority_tier"]]
    ax_bar.barh(top["company_country"], top["lead_count"], color=colors, edgecolor=INK, linewidth=1.6)
    ax_bar.set_title("Top mercados por leads elegíveis", loc="left", color=INK, fontweight="bold")
    ax_bar.set_xlabel("Leads")
    _style_axis(ax_bar, fig)

    ax_table = fig.add_subplot(gs[1:, 2:])
    _prepare_table_panel(fig, ax_table)
    table_data = country.head(8)[["company_country", "lead_count", "company_count", "priority_tier"]]
    table = ax_table.table(
        cellText=table_data.values,
        colLabels=["País", "Leads", "Empresas", "Tier"],
        cellLoc="left",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (row, _col), cell in table.get_celld().items():
        cell.set_edgecolor(INK)
        cell.set_linewidth(1.25)
        cell.set_facecolor(INK if row == 0 else (PANEL if row % 2 else PANEL_ALT))
        cell.get_text().set_color("#FFFFFF" if row == 0 else INK)
        if row == 0:
            cell.get_text().set_fontweight("bold")
    ax_table.set_title("Tabela executiva por país", loc="left", color=INK, fontweight="bold")

    return _save(fig, "04_powerbi_market_command.png")


def build_buyer_dashboard(gold: pd.DataFrame, role: pd.DataFrame, size: pd.DataFrame) -> Path:
    fig = plt.figure(figsize=(15.2, 8.8), constrained_layout=False)
    _add_title(fig, "Power BI - Buyer Intelligence", "Personas, porte empresarial e mix de compradores.")
    gs = fig.add_gridspec(
        3,
        4,
        height_ratios=[0.82, 2.35, 2.0],
        left=0.07,
        right=0.97,
        top=0.84,
        bottom=0.07,
        hspace=0.48,
        wspace=0.42,
    )

    _card(fig.add_subplot(gs[0, 0]), "Top persona", "41,3%", "Executive / Technical", TEAL)
    _card(fig.add_subplot(gs[0, 1]), "Compliance", "36,7%", "Data / Compliance", ORANGE)
    _card(fig.add_subplot(gs[0, 2]), "Enterprise", "42,7%", "dos leads", BLUE)
    _card(fig.add_subplot(gs[0, 3]), "SMB + Mid", "56,7%", "escala futura", PURPLE)

    ax_role = fig.add_subplot(gs[1:, :2])
    role_plot = role.sort_values("lead_count")
    ax_role.barh(role_plot["role_category"], role_plot["lead_count"], color=TEAL, edgecolor=INK, linewidth=1.6)
    ax_role.set_title("Leads por persona", loc="left", color=INK, fontweight="bold")
    ax_role.set_xlabel("Leads")
    _style_axis(ax_role, fig)

    ax_size = fig.add_subplot(gs[1, 2:])
    ax_size.bar(size["company_size_segment"], size["lead_count"], color=[ORANGE, TEAL, BLUE, PURPLE], edgecolor=INK, linewidth=1.6)
    ax_size.set_title("Leads por porte", loc="left", color=INK, fontweight="bold")
    ax_size.set_ylabel("Leads")
    ax_size.tick_params(axis="x", labelrotation=15)
    _style_axis(ax_size, fig, grid_axis="y")

    ax_heat = fig.add_subplot(gs[2, 2:])
    matrix = pd.crosstab(gold["role_category"], gold["company_size_segment"])
    role_order = [
        "Executive / Technical Decision Maker",
        "Data / Compliance",
        "Security / Risk",
        "IT / Engineering Management",
        "Individual Contributor / Specialist",
        "Other",
    ]
    size_order = ["1. Startup / SMB", "2. Mid-Market", "3. Enterprise", "4. Unknown"]
    matrix = matrix.reindex(index=role_order, columns=size_order, fill_value=0)
    matrix = matrix.rename(
        index={
            "Executive / Technical Decision Maker": "Exec / Tech",
            "Data / Compliance": "Data / Compliance",
            "Security / Risk": "Security / Risk",
            "IT / Engineering Management": "IT Mgmt",
            "Individual Contributor / Specialist": "IC / Specialist",
            "Other": "Other",
        },
        columns={
            "1. Startup / SMB": "Startup / SMB",
            "2. Mid-Market": "Mid-Market",
            "3. Enterprise": "Enterprise",
            "4. Unknown": "Unknown",
        },
    )
    _panel_shadow(fig, ax_heat)
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap=sns.color_palette([PANEL_ALT, "#DFF5EE", TEAL, BLUE], as_cmap=True),
        cbar=False,
        linewidths=1.2,
        linecolor=INK,
        ax=ax_heat,
    )
    ax_heat.set_title("Mix persona x porte", loc="left", color=INK, fontweight="bold")
    ax_heat.set_xlabel("")
    ax_heat.set_ylabel("")
    ax_heat.tick_params(axis="x", labelrotation=15)
    ax_heat.tick_params(axis="y", labelsize=8)

    return _save(fig, "05_powerbi_buyer_intelligence.png")


def build_border_dashboard(gold: pd.DataFrame) -> Path:
    fig = plt.figure(figsize=(15.2, 8.8), constrained_layout=False)
    _add_title(fig, "Power BI - Border Signal", "Sinal de operação distribuída por divergência entre país do contato e país da empresa.")
    gs = fig.add_gridspec(
        3,
        4,
        height_ratios=[0.82, 2.35, 2.0],
        left=0.07,
        right=0.97,
        top=0.84,
        bottom=0.07,
        hspace=0.42,
        wspace=0.35,
    )

    cross_border = int(gold["contact_company_country_mismatch"].sum())
    _card(fig.add_subplot(gs[0, 0]), "Cross-border", str(cross_border), "contatos", ORANGE)
    _card(fig.add_subplot(gs[0, 1]), "Share", f"{cross_border / len(gold):.1%}", "da base gold", TEAL)
    _card(fig.add_subplot(gs[0, 2]), "Maior massa", "UK", "32 contatos", BLUE)
    _card(fig.add_subplot(gs[0, 3]), "Proxy", "Firmográfico", "não comportamental", PURPLE)

    mismatch = (
        gold.groupby("company_country")
        .agg(
            lead_count=("email", "count"),
            mismatch_count=("contact_company_country_mismatch", "sum"),
            mismatch_rate=("contact_company_country_mismatch", "mean"),
        )
        .reset_index()
        .query("lead_count >= 10")
        .sort_values("mismatch_rate", ascending=True)
    )

    ax_bar = fig.add_subplot(gs[1:, :2])
    ax_bar.barh(mismatch["company_country"], mismatch["mismatch_rate"], color=ORANGE, edgecolor=INK, linewidth=1.6)
    ax_bar.set_title("Taxa cross-border por país", loc="left", color=INK, fontweight="bold")
    ax_bar.set_xlabel("Share")
    ax_bar.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
    _style_axis(ax_bar, fig)

    ax_scatter = fig.add_subplot(gs[1:, 2:])
    ax_scatter.scatter(mismatch["lead_count"], mismatch["mismatch_rate"], s=145, color=RED, edgecolor=INK, linewidth=1.4)
    for row in mismatch.itertuples(index=False):
        ax_scatter.text(row.lead_count + 1, row.mismatch_rate + 0.003, row.company_country, fontsize=8, color=INK)
    ax_scatter.set_title("Volume x sinal distribuído", loc="left", color=INK, fontweight="bold")
    ax_scatter.set_xlabel("Leads elegíveis")
    ax_scatter.set_ylabel("Taxa cross-border")
    ax_scatter.set_xlim(0, mismatch["lead_count"].max() + 32)
    ax_scatter.set_ylim(max(0, mismatch["mismatch_rate"].min() - 0.01), mismatch["mismatch_rate"].max() + 0.015)
    ax_scatter.yaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
    _style_axis(ax_scatter, fig)

    return _save(fig, "06_powerbi_border_signal.png")


def build_action_dashboard(country: pd.DataFrame) -> Path:
    fig = plt.figure(figsize=(15.2, 8.8), constrained_layout=False)
    _add_title(fig, "Power BI - Action Map", "Priorização comercial por tier, mercado e mensagem recomendada.")
    gs = fig.add_gridspec(
        2,
        4,
        height_ratios=[1.5, 2.6],
        left=0.07,
        right=0.97,
        top=0.84,
        bottom=0.08,
        hspace=0.45,
        wspace=0.35,
    )

    tier = country.groupby("priority_tier", as_index=False)["lead_count"].sum()
    ax_tier = fig.add_subplot(gs[0, :2])
    ax_tier.bar(tier["priority_tier"], tier["lead_count"], color=[TEAL, BLUE, PURPLE], edgecolor=INK, linewidth=1.6)
    ax_tier.set_title("Leads por tier", loc="left", color=INK, fontweight="bold")
    ax_tier.set_ylabel("Leads")
    _style_axis(ax_tier, fig, grid_axis="y")

    ax_rec = fig.add_subplot(gs[0, 2:])
    _prepare_table_panel(fig, ax_rec)
    recommendations = [
        ("Privacy-first", "Germany, France, Belgium", "GDPR, soberania e menor dependência do Google"),
        ("Scale-first", "United Kingdom, Ireland, Lithuania, Estonia", "eficiência técnica e implementação rápida"),
        ("Balanced", "Spain, Portugal, Poland", "performance anti-bot com prontidão regulatória"),
    ]
    y = 0.84
    for label, markets, message in recommendations:
        ax_rec.text(0.02, y, label, fontsize=11, fontweight="bold", color=TEAL)
        ax_rec.text(0.02, y - 0.11, markets, fontsize=9.4, color=INK)
        ax_rec.text(0.02, y - 0.21, message, fontsize=8.4, color=MUTED)
        y -= 0.30

    ax_table = fig.add_subplot(gs[1, :])
    _prepare_table_panel(fig, ax_table)
    table_data = country.head(10)[["country_rank", "company_country", "priority_tier", "lead_count", "company_count"]]
    table = ax_table.table(
        cellText=table_data.values,
        colLabels=["Rank", "País", "Tier", "Leads", "Empresas"],
        cellLoc="left",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (row, _col), cell in table.get_celld().items():
        cell.set_edgecolor(INK)
        cell.set_linewidth(1.25)
        cell.set_facecolor(INK if row == 0 else (PANEL if row % 2 else PANEL_ALT))
        cell.get_text().set_color("#FFFFFF" if row == 0 else INK)
        if row == 0:
            cell.get_text().set_fontweight("bold")
    ax_table.set_title("Mapa de ação por mercado", loc="left", color=INK, fontweight="bold")

    return _save(fig, "07_powerbi_action_map.png")


def build_assets() -> list[Path]:
    sns.set_theme(style="whitegrid")
    gold, country, role, size = _load_data()
    paths = []
    paths.extend(build_documentation_tables(gold, country, role, size))
    paths.append(build_market_dashboard(gold, country))
    paths.append(build_buyer_dashboard(gold, role, size))
    paths.append(build_border_dashboard(gold))
    paths.append(build_action_dashboard(country))
    return paths


def main() -> int:
    paths = build_assets()
    for path in paths:
        print(path.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
