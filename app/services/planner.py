
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime

from app.schemas.plans import ComparisonInput, PlanCreate

CURRENT_YEAR = datetime.now().year
RET_CYCLE = [0.35, -0.45, 0.60, -0.20, 0.15, -0.10, 0.45, -0.35, 0.20, -0.05]
HISTORICAL_YEARS = list(range(2015, 2025))

PORTFOLIO_MODELS = {
    "conservador": {
        "name": "Conservador",
        "level": "Baixo risco",
        "allocation": {"Caixa": 0.61, "Renda Fixa": 0.28, "Renda Variável": 0.11},
        "assets": [
            {"name": "Liquidez", "weight": 0.545, "bucket": "Caixa"},
            {"name": "Ouro", "weight": 0.060, "bucket": "Caixa"},
            {"name": "Inflação Longo", "weight": 0.020, "bucket": "Renda Fixa"},
            {"name": "Inflação Médio", "weight": 0.065, "bucket": "Renda Fixa"},
            {"name": "Inflação Curto", "weight": 0.145, "bucket": "Renda Fixa"},
            {"name": "Pré-Fixado Longo", "weight": 0.000, "bucket": "Renda Fixa"},
            {"name": "Pré-Fixado Médio", "weight": 0.015, "bucket": "Renda Fixa"},
            {"name": "Pré-Fixado Curto", "weight": 0.030, "bucket": "Renda Fixa"},
            {"name": "ETFs Internacionais", "weight": 0.045, "bucket": "Renda Variável"},
            {"name": "BDRs", "weight": 0.000, "bucket": "Renda Variável"},
            {"name": "Brasil Passivo", "weight": 0.025, "bucket": "Renda Variável"},
            {"name": "Brasil Ativo", "weight": 0.000, "bucket": "Renda Variável"},
            {"name": "FIIs", "weight": 0.040, "bucket": "Renda Variável"},
        ],
        "volatility_key": "conservative_volatility",
    },
    "moderado": {
        "name": "Moderado",
        "level": "Risco equilibrado",
        "allocation": {"Caixa": 0.45, "Renda Fixa": 0.30, "Renda Variável": 0.26},
        "assets": [
            {"name": "Liquidez", "weight": 0.300, "bucket": "Caixa"},
            {"name": "Ouro", "weight": 0.150, "bucket": "Caixa"},
            {"name": "Inflação Longo", "weight": 0.100, "bucket": "Renda Fixa"},
            {"name": "Inflação Médio", "weight": 0.110, "bucket": "Renda Fixa"},
            {"name": "Inflação Curto", "weight": 0.000, "bucket": "Renda Fixa"},
            {"name": "Pré-Fixado Longo", "weight": 0.040, "bucket": "Renda Fixa"},
            {"name": "Pré-Fixado Médio", "weight": 0.045, "bucket": "Renda Fixa"},
            {"name": "Pré-Fixado Curto", "weight": 0.000, "bucket": "Renda Fixa"},
            {"name": "ETFs Internacionais", "weight": 0.040, "bucket": "Renda Variável"},
            {"name": "BDRs", "weight": 0.055, "bucket": "Renda Variável"},
            {"name": "Brasil Passivo", "weight": 0.025, "bucket": "Renda Variável"},
            {"name": "Brasil Ativo", "weight": 0.025, "bucket": "Renda Variável"},
            {"name": "FIIs", "weight": 0.110, "bucket": "Renda Variável"},
        ],
        "volatility_key": "moderate_volatility",
    },
    "sofisticado": {
        "name": "Sofisticado",
        "level": "Maior crescimento",
        "allocation": {"Caixa": 0.41, "Renda Fixa": 0.23, "Renda Variável": 0.37},
        "assets": [
            {"name": "Liquidez", "weight": 0.185, "bucket": "Caixa"},
            {"name": "Ouro", "weight": 0.220, "bucket": "Caixa"},
            {"name": "Inflação Longo", "weight": 0.150, "bucket": "Renda Fixa"},
            {"name": "Inflação Médio", "weight": 0.000, "bucket": "Renda Fixa"},
            {"name": "Inflação Curto", "weight": 0.000, "bucket": "Renda Fixa"},
            {"name": "Pré-Fixado Longo", "weight": 0.075, "bucket": "Renda Fixa"},
            {"name": "Pré-Fixado Médio", "weight": 0.000, "bucket": "Renda Fixa"},
            {"name": "Pré-Fixado Curto", "weight": 0.000, "bucket": "Renda Fixa"},
            {"name": "ETFs Internacionais", "weight": 0.070, "bucket": "Renda Variável"},
            {"name": "BDRs", "weight": 0.090, "bucket": "Renda Variável"},
            {"name": "Brasil Passivo", "weight": 0.040, "bucket": "Renda Variável"},
            {"name": "Brasil Ativo", "weight": 0.040, "bucket": "Renda Variável"},
            {"name": "FIIs", "weight": 0.130, "bucket": "Renda Variável"},
        ],
        "volatility_key": "sophisticated_volatility",
    },
}


@dataclass
class PlanCalculation:
    summary: dict
    comparison: dict
    scenario_projection: dict
    portfolio_diagnosis: dict
    timeline: list[dict]
    action_plan: list[str]
    report_context: dict


def future_value_lump_sum(value: float, annual_rate: float, years: int) -> float:
    return value * ((1 + annual_rate) ** max(years, 0))


def future_value_series(monthly: float, annual_rate: float, years: int) -> float:
    months = max(years * 12, 0)
    if months == 0:
        return 0.0
    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1
    if monthly_rate == 0:
        return monthly * months
    return monthly * (((1 + monthly_rate) ** months - 1) / monthly_rate)


def retirement_target_capital(monthly_income: float, years: int, annual_rate: float, mode: str) -> float:
    annual_need = monthly_income * 12
    annual_rate = max(annual_rate, 0.0001)
    if mode == "somente_rentabilidade":
        return annual_need / annual_rate
    if mode == "somente_principal":
        return annual_need * years
    # rentabilidade + principal
    return annual_need * (1 - (1 + annual_rate) ** (-years)) / annual_rate


def retirement_mode_label(mode: str) -> str:
    return {
        "somente_rentabilidade": "Somente rentabilidade",
        "rentabilidade_e_principal": "Rentabilidade + principal",
        "somente_principal": "Somente principal",
    }.get(mode, "Rentabilidade + principal")


def tax_drag_for_regime(regime: str) -> float:
    mapping = {
        "pf_completa": 0.10,
        "pf_simplificada": 0.12,
        "pj": 0.13,
        "nao_informado": 0.10,
        "simples": 0.06,
        "lucro_presumido": 0.10,
        "lucro_real": 0.13,
    }
    return mapping.get(regime, 0.10)


def compare_scenarios(comp: ComparisonInput, annual_rate: float) -> dict:
    years = comp.investment_years
    property_growth = future_value_lump_sum(comp.property_expected_sale_value or comp.property_value, 0.08, years)
    property_net = property_growth - (comp.property_monthly_costs * 12 * years)

    rent_and_invest = future_value_lump_sum(comp.investment_initial or comp.property_value, annual_rate, years) + future_value_series(
        max(comp.property_monthly_rent - comp.property_monthly_costs, 0) + comp.investment_monthly,
        annual_rate,
        years,
    )

    auction_entry = comp.property_value * (1 - comp.auction_discount_rate)
    auction_profit = future_value_lump_sum(max(comp.property_expected_sale_value - auction_entry, 0), 0.10, years)
    auction_net = auction_entry + auction_profit

    business_future = future_value_lump_sum(comp.investment_initial or comp.property_value, comp.business_expected_roi, years)
    long_term = future_value_lump_sum(comp.investment_initial or comp.property_value, comp.long_term_rate, years) + future_value_series(
        comp.investment_monthly,
        comp.long_term_rate,
        years,
    )

    scenarios = {
        "buy_property_future_value": round(property_net, 2),
        "rent_and_invest_future_value": round(rent_and_invest, 2),
        "auction_property_future_value": round(auction_net, 2),
        "invest_in_business_future_value": round(business_future, 2),
        "long_term_investment_future_value": round(long_term, 2),
    }
    scenarios["best_scenario"] = max(scenarios, key=scenarios.get)
    return scenarios


def asset_return_map(payload: PlanCreate) -> dict[str, float]:
    a = payload.assumptions
    return {
        "Liquidez": a.cdi_return,
        "Ouro": a.gold_return,
        "Inflação Longo": a.ntnb_return,
        "Inflação Médio": a.ntnb_return,
        "Inflação Curto": a.ntnb_return,
        "Pré-Fixado Longo": a.ntnf_return,
        "Pré-Fixado Médio": a.ntnf_return,
        "Pré-Fixado Curto": a.ntnf_return,
        "ETFs Internacionais": a.sp500_brl_return,
        "BDRs": a.sp500_brl_return,
        "Brasil Passivo": a.ibovespa_return,
        "Brasil Ativo": a.ibovespa_return,
        "FIIs": a.fiis_return,
    }


def build_scenario_projection(payload: PlanCreate) -> dict:
    assumptions = payload.assumptions
    returns_map = asset_return_map(payload)
    starting_capital = max(payload.invested_assets + payload.cash_reserves + payload.international_assets + payload.previdence_assets, 0)
    annual_contribution = max(payload.monthly_contribution * 12, 0)
    horizons = sorted({max(int(assumptions.scenario_short_years),1), max(int(assumptions.simulation_years),1)})
    years = max(horizons)
    annual_labels = [str(CURRENT_YEAR + idx) for idx in range(years + 1)]

    series: dict[str, list[float]] = {}
    cards: list[dict] = []

    for profile in PORTFOLIO_MODELS.values():
        value = starting_capital
        path = [round(value, 2)]
        weighted_returns: list[float] = []
        base_vol = getattr(assumptions, profile["volatility_key"])

        for year_index in range(years):
            portfolio_base = 0.0
            for asset in profile["assets"]:
                if asset["weight"] <= 0:
                    continue
                portfolio_base += asset["weight"] * returns_map[asset["name"]]
            cycle_factor = RET_CYCLE[year_index % len(RET_CYCLE)]
            portfolio_return = portfolio_base + (base_vol * cycle_factor)
            weighted_returns.append(portfolio_return)
            value = (value * (1 + portfolio_return)) + annual_contribution
            path.append(round(value, 2))

        series[profile["name"]] = path
        expected_return = sum(weighted_returns) / len(weighted_returns)
        variance = sum((item - expected_return) ** 2 for item in weighted_returns) / len(weighted_returns)
        cards.append({
            "name": profile["name"],
            "level": profile["level"],
            "allocation": profile["allocation"],
            "assets": profile["assets"],
            "value_10y": round(path[min(horizons[0], len(path)-1)], 2),
            "value_20y": round(path[min(horizons[-1], len(path)-1)], 2),
            "expected_return": round(expected_return, 4),
            "volatility": round(math.sqrt(variance), 4),
            "worst_drawdown": round(min(weighted_returns), 4),
        })

    ordered = sorted(cards, key=lambda item: item["value_20y"])
    highlights = [
        f"As curvas combinam retornos editáveis dos ativos com volatilidade crescente por perfil para mostrar altos e baixos visíveis no horizonte de {horizons[-1]} anos.",
        f"Em {horizons[-1]} anos, a carteira {ordered[-1]['name'].lower()} projeta o maior patrimônio entre os três cenários nas premissas atuais.",
        f"A carteira {ordered[0]['name'].lower()} preserva maior estabilidade, com volatilidade projetada de {ordered[0]['volatility'] * 100:.1f}% ao ano.",
        "Os três cenários mantêm os pesos oficiais da casa e assumem rebalanceamento interno anual.",
    ]

    return {
        "horizons": horizons,
        "annual_labels": annual_labels,
        "series": series,
        "portfolio_cards": cards,
        "highlights": highlights,
        "historical_window": {"start": HISTORICAL_YEARS[0], "end": HISTORICAL_YEARS[-1]},
    }


def build_timeline(payload: PlanCreate, future_value: float, target_capital: float, succession_cost: float) -> list[dict]:
    timeline = [{
        "year": CURRENT_YEAR,
        "title": "Diagnóstico inicial",
        "detail": f"Patrimônio atual estimado em R$ {(payload.invested_assets + payload.real_estate_assets + payload.cash_reserves + payload.company_equity + payload.vehicles_assets + payload.previdence_assets + payload.insurance_reserve_assets + payload.international_assets + payload.other_assets):,.2f}",
    }]
    for event in payload.life_events:
        timeline.append({
            "year": event.year,
            "title": event.title,
            "detail": f"Impacto financeiro estimado em R$ {event.impact_amount:,.2f}",
        })
    timeline.extend([
        {
            "year": CURRENT_YEAR + 1,
            "title": "Estrutura de proteção",
            "detail": f"Organizar liquidez sucessória estimada em R$ {succession_cost:,.2f} e revisar proteção de vida.",
        },
        {
            "year": CURRENT_YEAR + max((payload.target_age - payload.age) // 2, 1),
            "title": "Revisão intermediária",
            "detail": f"Checar aderência da carteira para alcançar R$ {target_capital:,.2f}",
        },
        {
            "year": CURRENT_YEAR + (payload.target_age - payload.age),
            "title": "Meta principal",
            "detail": f"Projeção patrimonial em R$ {future_value:,.2f}",
        },
    ])
    return sorted(timeline, key=lambda item: item["year"])


def build_action_plan(payload: PlanCreate, summary: dict, comparison: dict, scenario_projection: dict) -> list[str]:
    actions: list[str] = []
    actions.append("Tratar proteção e previdência como pilares da estratégia, e não como complemento opcional.")
    if payload.has_emergency_reserve == "nao":
        actions.append(f"Construir reserva de emergência até R$ {summary['emergency_reserve_target']:,.2f}.")
    if payload.has_life_insurance == "nao":
        actions.append(f"Cliente sem seguro informado. Estruturar cobertura próxima de R$ {summary['protection_capital_needed']:,.2f}.")
    elif summary["protection_gap"] > 0:
        actions.append(f"Seguro existente insuficiente. Gap de proteção estimado em R$ {summary['protection_gap']:,.2f}.")
    else:
        actions.append("Cobertura informada parece suficiente nas premissas atuais, mas deve ser revisada periodicamente.")
    actions.append(f"Preparar liquidez sucessória estimada em R$ {summary['succession_cost_estimate']:,.2f}.")
    if summary["capital_gap"] > 0:
        actions.append("Aumentar aporte mensal, alongar prazo ou assumir mais risco para reduzir o gap de capital.")
    else:
        actions.append("As premissas atuais já colocam o cliente em boa direção para o objetivo principal.")
    if payload.has_pension == "nao":
        actions.append(summary["pension_recommendation"])
    best_20y = max(scenario_projection["portfolio_cards"], key=lambda item: item["value_20y"])
    actions.append(f"No comparativo do horizonte principal, a carteira {best_20y['name'].lower()} oferece o maior patrimônio projetado.")
    return actions



def _pct(value: float, total: float) -> float:
    return (value / total) if total else 0.0


def _recommended_allocation_for(profile_name: str) -> dict[str, float]:
    key = (profile_name or "moderado").lower()
    if "conserv" in key:
        model = PORTFOLIO_MODELS["conservador"]
    elif "sofistic" in key or "agress" in key:
        model = PORTFOLIO_MODELS["sofisticado"]
    else:
        model = PORTFOLIO_MODELS["moderado"]

    rv_assets = {"Ações Brasil": 0.0, "Ações Exterior": 0.0, "FIIs": 0.0, "Alternativos": 0.0}
    rf = 0.0
    cash = 0.0
    for asset in model["assets"]:
        name = asset["name"]
        weight = float(asset["weight"])
        bucket = asset["bucket"]
        if bucket == "Caixa":
            if name == "Ouro":
                rv_assets["Alternativos"] += weight
            else:
                cash += weight
        elif bucket == "Renda Fixa":
            rf += weight
        else:
            if name in ("ETFs Internacionais", "BDRs"):
                rv_assets["Ações Exterior"] += weight
            elif name == "FIIs":
                rv_assets["FIIs"] += weight
            else:
                rv_assets["Ações Brasil"] += weight

    return {
        "Caixa / Liquidez": cash,
        "Renda Fixa": rf,
        "Ações Brasil": rv_assets["Ações Brasil"],
        "Ações Exterior": rv_assets["Ações Exterior"],
        "FIIs": rv_assets["FIIs"],
        "Alternativos": rv_assets["Alternativos"],
        "Previdência": 0.0,
        "Outros": 0.0,
    }


def build_portfolio_diagnosis(payload: PlanCreate) -> dict:
    portfolio = payload.current_portfolio
    values = {
        "Caixa / Liquidez": portfolio.cash,
        "Renda Fixa": portfolio.fixed_income,
        "Ações Brasil": portfolio.equities_br,
        "Ações Exterior": portfolio.equities_global,
        "FIIs": portfolio.fiis,
        "Alternativos": portfolio.alternatives,
        "Previdência": portfolio.pension,
        "Outros": portfolio.others,
    }
    total = sum(max(v, 0) for v in values.values())
    allocation = {k: round(_pct(max(v, 0), total), 4) for k, v in values.items()}

    risk_score = (
        allocation["Caixa / Liquidez"] * 0.05
        + allocation["Renda Fixa"] * 0.20
        + allocation["Ações Brasil"] * 0.85
        + allocation["Ações Exterior"] * 0.80
        + allocation["FIIs"] * 0.55
        + allocation["Alternativos"] * 0.90
        + allocation["Previdência"] * 0.35
        + allocation["Outros"] * 0.50
    )
    if total <= 0:
        identified_profile = "Não informado"
    elif risk_score < 0.30:
        identified_profile = "Conservador"
    elif risk_score < 0.58:
        identified_profile = "Moderado"
    else:
        identified_profile = "Sofisticado"

    positive_classes = sum(1 for value in values.values() if value > 0)
    max_class = max(allocation.values()) if allocation else 0
    has_global = allocation["Ações Exterior"] > 0.05
    has_liquidity = allocation["Caixa / Liquidez"] >= 0.05
    has_risk_asset = allocation["Ações Brasil"] + allocation["Ações Exterior"] + allocation["FIIs"] + allocation["Alternativos"] > 0.10

    investor_score = 40
    investor_score += min(positive_classes, 5) * 7
    investor_score += 10 if has_global else 0
    investor_score += 10 if has_liquidity else 0
    investor_score += 10 if has_risk_asset else 0
    investor_score -= 15 if max_class > 0.70 else 0
    investor_score = max(0, min(100, investor_score if total > 0 else 0))

    diagnostics: list[str] = []
    recommendations: list[str] = []
    if total <= 0:
        diagnostics.append("Carteira atual não informada. Preencha a alocação para gerar diagnóstico.")
        recommendations.append("Mapear a carteira atual antes de propor qualquer realocação.")
    else:
        if max_class > 0.70:
            concentration_name = max(allocation, key=allocation.get)
            concentration_alert = f"Concentração elevada em {concentration_name}."
            diagnostics.append(concentration_alert)
            recommendations.append("Reduzir concentração excessiva e redistribuir risco entre classes.")
        else:
            concentration_alert = "Concentração controlada entre classes."
            diagnostics.append(concentration_alert)

        if not has_global:
            diagnostics.append("Baixa exposição internacional informada.")
            recommendations.append("Avaliar exposição internacional para diversificação cambial e geográfica.")
        if allocation["Caixa / Liquidez"] < 0.05:
            diagnostics.append("Liquidez imediata aparentemente baixa.")
            recommendations.append("Reforçar caixa/reserva para evitar venda forçada de ativos.")
        if allocation["Renda Fixa"] > 0.75:
            diagnostics.append("Carteira muito concentrada em renda fixa.")
            recommendations.append("Avaliar se a carteira acompanha os objetivos de crescimento patrimonial.")
        if risk_score > 0.65:
            diagnostics.append("Exposição relevante a ativos de maior volatilidade.")
            recommendations.append("Confirmar se o risco atual está alinhado ao prazo, objetivo e perfil emocional do cliente.")
        if not recommendations:
            recommendations.append("Manter acompanhamento periódico e rebalanceamento anual conforme objetivos.")

    if total <= 0:
        concentration_alert = "Carteira não informada."

    recommended = _recommended_allocation_for(identified_profile if identified_profile != "Não informado" else "Moderado")
    comparison_table = []
    for name, pct_value in allocation.items():
        comparison_table.append({
            "classe": name,
            "atual": round(pct_value, 4),
            "referencia_atlas": round(recommended.get(name, 0.0), 4),
        })

    return {
        "total": round(total, 2),
        "allocation": allocation,
        "allocation_values": {k: round(v, 2) for k, v in values.items()},
        "identified_profile": identified_profile,
        "perceived_profile": portfolio.perceived_profile.replace("_", " ").title(),
        "risk_score": round(risk_score, 4),
        "investor_score": round(investor_score, 2),
        "concentration_alert": concentration_alert,
        "diagnostics": diagnostics,
        "recommendations": recommendations,
        "comparison_table": comparison_table,
    }


def build_report(payload: PlanCreate) -> PlanCalculation:
    years = max(payload.target_age - payload.age, 1)
    assumptions = payload.assumptions
    tax_drag = tax_drag_for_regime(payload.tax_regime)
    base_nominal_return = assumptions.selic_structural + assumptions.inflation_plus_rate
    effective_return = max(base_nominal_return - tax_drag, 0.01)

    current_net_worth = (
        payload.invested_assets
        + payload.real_estate_assets
        + payload.cash_reserves
        + payload.company_equity
        + payload.vehicles_assets
        + payload.previdence_assets
        + payload.insurance_reserve_assets
        + payload.international_assets
        + payload.other_assets
    )
    future_value = future_value_lump_sum(current_net_worth, effective_return, years) + future_value_series(
        payload.monthly_contribution,
        effective_return,
        years,
    )
    target_capital = retirement_target_capital(
        payload.desired_monthly_income_future,
        assumptions.retirement_years,
        assumptions.retirement_return_rate,
        payload.retirement_mode,
    )
    capital_gap = max(target_capital - future_value, 0)
    emergency_target = payload.monthly_expenses * 6
    succession_cost = current_net_worth * assumptions.succession_cost_rate
    family_income_protection = max(payload.monthly_income * 12 * assumptions.income_multiple, 0)
    family_maintenance = payload.monthly_expenses * 12 * assumptions.family_protection_years
    family_goal_cost = sum(goal.target_amount for goal in payload.goals if goal.target_amount > 0)
    current_coverage = payload.existing_insurance.coverage_amount + payload.existing_insurance.death_coverage + payload.existing_insurance.disability_coverage
    protection_needed = succession_cost + max(family_income_protection, family_maintenance) + family_goal_cost
    protection_gap = max(protection_needed - current_coverage, 0)

    if payload.has_pension == "sim":
        pension_recommendation = "Cliente já possui previdência informada. Revisar aderência entre tipo do plano, tabela tributária e objetivo de longo prazo."
    elif payload.tax_regime == "pf_completa":
        pension_recommendation = "Sem previdência informada. Há espaço para avaliar PGBL como ferramenta de longo prazo e eficiência tributária."
    else:
        pension_recommendation = "Sem previdência informada. Avaliar VGBL ou outra estrutura de acumulação conforme perfil tributário e sucessório."

    readiness_ratio = (future_value / target_capital) if target_capital else 1
    if readiness_ratio >= 1:
        thermometer_status = "Objetivo coberto"
    elif readiness_ratio >= 0.75:
        thermometer_status = "Boa direção"
    elif readiness_ratio >= 0.45:
        thermometer_status = "Ajuste necessário"
    else:
        thermometer_status = "Distante da meta"

    summary = {
        "current_net_worth": round(current_net_worth, 2),
        "future_value": round(future_value, 2),
        "retirement_target_capital": round(target_capital, 2),
        "capital_gap": round(capital_gap, 2),
        "emergency_reserve_target": round(emergency_target, 2),
        "protection_capital_needed": round(protection_needed, 2),
        "protection_gap": round(protection_gap, 2),
        "succession_cost_estimate": round(succession_cost, 2),
        "life_security_capital": round(max(family_income_protection, family_maintenance), 2),
        "current_insurance_coverage": round(current_coverage, 2),
        "effective_tax_drag": round(tax_drag, 4),
        "goal_readiness_ratio": round(readiness_ratio, 4),
        "goal_readiness_percent": round(min(readiness_ratio * 100, 999), 2),
        "remaining_percent": round(max(100 - (readiness_ratio * 100), 0), 2),
        "years_to_goal": years,
        "monthly_capacity": round(max(payload.monthly_income - payload.monthly_expenses, 0), 2),
        "retirement_mode_label": retirement_mode_label(payload.retirement_mode),
        "thermometer_status": thermometer_status,
        "pension_recommendation": pension_recommendation,
        "total_income_considered": round(payload.monthly_income, 2),
        "total_expenses_considered": round(payload.monthly_expenses, 2),
        "monthly_contribution_selected": round(payload.monthly_contribution, 2),
    }
    comparison = compare_scenarios(payload.comparison, effective_return)
    scenario_projection = build_scenario_projection(payload)
    portfolio_diagnosis = build_portfolio_diagnosis(payload)
    timeline = build_timeline(payload, future_value, target_capital, succession_cost)
    action_plan = build_action_plan(payload, summary, comparison, scenario_projection)

    report_context = {
        "client": payload.model_dump(),
        "summary": summary,
        "comparison": comparison,
        "scenario_projection": scenario_projection,
        "portfolio_diagnosis": portfolio_diagnosis,
        "timeline": timeline,
        "goals": [goal.model_dump() for goal in payload.goals],
        "assumptions": assumptions.model_dump(),
        "action_plan": action_plan,
    }
    return PlanCalculation(
        summary=summary,
        comparison=comparison,
        scenario_projection=scenario_projection,
        portfolio_diagnosis=portfolio_diagnosis,
        timeline=timeline,
        action_plan=action_plan,
        report_context=report_context,
    )
