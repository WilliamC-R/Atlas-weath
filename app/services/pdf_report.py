
from __future__ import annotations

from io import BytesIO

from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

COLORS = {
    "Conservador": colors.HexColor("#84CC16"),
    "Moderado": colors.HexColor("#F59E0B"),
    "Sofisticado": colors.HexColor("#2563EB"),
}


def _money(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _scenario_chart(scenario_projection: dict) -> Drawing:
    series_map = scenario_projection["series"]
    drawing = Drawing(520, 260)
    chart = HorizontalLineChart()
    chart.x = 48
    chart.y = 48
    chart.height = 165
    chart.width = 430
    chart.data = [
        tuple(series_map["Conservador"]),
        tuple(series_map["Moderado"]),
        tuple(series_map["Sofisticado"]),
    ]
    chart.joinedLines = 1
    chart.categoryAxis.categoryNames = scenario_projection["annual_labels"]
    chart.categoryAxis.labels.boxAnchor = "n"
    chart.categoryAxis.labels.angle = 30
    chart.categoryAxis.labels.fontSize = 6
    chart.categoryAxis.labels.dy = -2
    chart.valueAxis.labels.fontSize = 7
    chart.valueAxis.valueMin = min(min(values) for values in series_map.values()) * 0.95
    chart.valueAxis.valueMax = max(max(values) for values in series_map.values()) * 1.06
    chart.valueAxis.valueStep = max((chart.valueAxis.valueMax - chart.valueAxis.valueMin) / 5, 1)
    chart.lines[0].strokeColor = COLORS["Conservador"]
    chart.lines[1].strokeColor = COLORS["Moderado"]
    chart.lines[2].strokeColor = COLORS["Sofisticado"]
    for idx in range(3):
        chart.lines[idx].strokeWidth = 2.4
    drawing.add(chart)

    legend_y = 233
    legend_x = 58
    for idx, name in enumerate(["Conservador", "Moderado", "Sofisticado"]):
        x = legend_x + idx * 140
        drawing.add(Line(x, legend_y, x + 18, legend_y, strokeColor=COLORS[name], strokeWidth=3))
        drawing.add(String(x + 24, legend_y - 4, name, fontSize=8, fillColor=colors.HexColor("#0F172A")))

    return drawing


def generate_plan_pdf(report_context: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=12 * mm, leftMargin=12 * mm, rightMargin=12 * mm, bottomMargin=12 * mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SmallMuted", parent=styles["BodyText"], fontSize=8.5, textColor=colors.HexColor("#475569"), leading=11))
    styles.add(ParagraphStyle(name="SectionLead", parent=styles["BodyText"], fontSize=10, leading=14, textColor=colors.HexColor("#0F172A")))
    story = []

    client = report_context["client"]
    summary = report_context["summary"]
    assumptions = report_context["assumptions"]
    scenario_projection = report_context["scenario_projection"]
    portfolio_diagnosis = report_context.get("portfolio_diagnosis", {})

    story.append(Paragraph("Atlas Wealth — Relatório de Wealth Planning", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Cliente: {client['client_name']}", styles["Heading2"]))
    story.append(Paragraph(
        f"Idade atual: {client['age']} | Idade alvo: {client['target_age']} | Estratégia de usufruto: {summary['retirement_mode_label']}",
        styles["BodyText"],
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Este relatório consolida diagnóstico patrimonial, cenários de investimento e proteção. Em Atlas Wealth, segurança de vida é tratada como base estrutural do plano, porque garante liquidez imediata para família, sucessão e continuidade da estratégia.",
        styles["SectionLead"],
    ))
    story.append(Spacer(1, 12))

    summary_data = [
        ["Indicador", "Valor"],
        ["Patrimônio atual", _money(summary["current_net_worth"])],
        ["Patrimônio projetado", _money(summary["future_value"])],
        ["Capital alvo estimado", _money(summary["retirement_target_capital"])],
        ["Gap de capital", _money(summary["capital_gap"])],
        ["Reserva de emergência ideal", _money(summary["emergency_reserve_target"])],
        ["Cobertura atual informada", _money(summary["current_insurance_coverage"])],
        ["Necessidade de segurança de vida", _money(summary["life_security_capital"])],
        ["Custo sucessório estimado", _money(summary["succession_cost_estimate"])],
        ["Proteção total sugerida", _money(summary["protection_capital_needed"])],
        ["Gap de proteção", _money(summary["protection_gap"])],
        ["Aderência projetada à meta", f"{summary['goal_readiness_percent']:.1f}%"],
        ["Status do termômetro", summary["thermometer_status"]],
    ]
    summary_table = Table(summary_data, colWidths=[255, 230])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    protection_data = [
        ["Pilar de proteção", "Leitura do plano"],
        ["Sucessão patrimonial", f"Aplicado custo de {assumptions['succession_cost_rate'] * 100:.0f}% sobre o patrimônio total para gerar liquidez sucessória."],
        ["Seguro de vida", "Na ausência de produto informado, a recomendação é automatizada com base em renda, custo de vida, metas familiares e sucessão."],
        ["Previdência", summary["pension_recommendation"]],
    ]
    protection_table = Table(protection_data, colWidths=[140, 345])
    protection_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14532D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0FDF4")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(Paragraph("Proteção e previdência", styles["Heading2"]))
    story.append(protection_table)
    story.append(Spacer(1, 10))


    if portfolio_diagnosis:
        story.append(Paragraph("Diagnóstico da carteira atual", styles["Heading2"]))
        story.append(Paragraph(
            f"Carteira informada: {_money(portfolio_diagnosis.get('total', 0))} | Perfil identificado: {portfolio_diagnosis.get('identified_profile', '-')} | Nota da carteira: {portfolio_diagnosis.get('investor_score', 0):.0f}/100 | Risco estimado: {portfolio_diagnosis.get('risk_score', 0) * 100:.1f}%.",
            styles["BodyText"],
        ))
        allocation_rows = [["Classe", "Valor", "% Atual"]]
        for classe, valor in portfolio_diagnosis.get("allocation_values", {}).items():
            pct = portfolio_diagnosis.get("allocation", {}).get(classe, 0)
            if valor > 0:
                allocation_rows.append([classe, _money(valor), f"{pct * 100:.1f}%"])
        if len(allocation_rows) == 1:
            allocation_rows.append(["Carteira não informada", _money(0), "0.0%"])
        allocation_table = Table(allocation_rows, colWidths=[220, 140, 100])
        allocation_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4C81")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(allocation_table)
        story.append(Spacer(1, 6))
        for item in portfolio_diagnosis.get("diagnostics", []):
            story.append(Paragraph(f"• {item}", styles["BodyText"]))
        story.append(Spacer(1, 4))
        story.append(Paragraph("Recomendações para a carteira", styles["Heading3"]))
        for item in portfolio_diagnosis.get("recommendations", []):
            story.append(Paragraph(f"• {item}", styles["BodyText"]))
        story.append(Spacer(1, 10))

    story.append(Paragraph("Premissas do estudo", styles["Heading2"]))
    story.append(Paragraph(
        f"Selic estrutural: {assumptions['selic_structural'] * 100:.2f}% ao ano | Banda: -{assumptions['selic_band_down'] * 100:.2f} p.p / +{assumptions['selic_band_up'] * 100:.2f} p.p | Taxa de usufruto: {assumptions['retirement_return_rate'] * 100:.2f}% | Horizontes: {assumptions['scenario_short_years']} e {assumptions['simulation_years']} anos.",
        styles["BodyText"],
    ))
    story.append(Paragraph(
        f"Ativos usados na simulação: CDI {assumptions['cdi_return'] * 100:.2f}%, Ouro {assumptions['gold_return'] * 100:.2f}%, NTN-B {assumptions['ntnb_return'] * 100:.2f}%, NTN-F {assumptions['ntnf_return'] * 100:.2f}%, Ibovespa {assumptions['ibovespa_return'] * 100:.2f}%, S&P 500 BRL {assumptions['sp500_brl_return'] * 100:.2f}%, FIIs {assumptions['fiis_return'] * 100:.2f}%.",
        styles["SmallMuted"],
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Cenários de investimento comparados", styles["Heading2"]))
    first_h = scenario_projection["horizons"][0]
    last_h = scenario_projection["horizons"][-1]
    scenario_rows = [["Perfil", f"{first_h} anos", f"{last_h} anos", "Retorno médio", "Volatilidade", "Pior ano"]]
    for card in scenario_projection["portfolio_cards"]:
        scenario_rows.append([
            card["name"],
            _money(card["value_10y"]),
            _money(card["value_20y"]),
            _pct(card["expected_return"]),
            _pct(card["volatility"]),
            _pct(card["worst_drawdown"]),
        ])
    scenario_table = Table(scenario_rows, colWidths=[78, 75, 75, 72, 72, 72])
    scenario_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D4ED8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#EFF6FF")),
    ]))
    story.append(scenario_table)
    story.append(Spacer(1, 8))
    story.append(_scenario_chart(scenario_projection))
    story.append(Spacer(1, 8))
    for highlight in scenario_projection["highlights"]:
        story.append(Paragraph(f"• {highlight}", styles["BodyText"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Linha do tempo financeira", styles["Heading2"]))
    for item in report_context["timeline"]:
        story.append(Paragraph(f"{item['year']} — {item['title']}: {item['detail']}", styles["BodyText"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Plano de ação", styles["Heading2"]))
    for idx, action in enumerate(report_context["action_plan"], start=1):
        story.append(Paragraph(f"{idx}. {action}", styles["BodyText"]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
