from app.schemas.plans import ComparisonInput, PlanCreate
from app.services.planner import build_report


def test_build_report_generates_summary_and_scenarios() -> None:
    payload = PlanCreate(
        client_name="Cliente Teste",
        age=35,
        dependents=1,
        monthly_income=20000,
        monthly_expenses=9000,
        monthly_contribution=3000,
        invested_assets=250000,
        real_estate_assets=150000,
        cash_reserves=50000,
        company_equity=0,
        target_age=60,
        desired_monthly_income_future=25000,
        comparison=ComparisonInput(
            property_value=400000,
            property_expected_sale_value=550000,
            property_monthly_rent=2200,
            property_monthly_costs=500,
            auction_discount_rate=0.20,
            investment_initial=400000,
            investment_monthly=2200,
            investment_years=10,
            long_term_rate=0.12,
            business_expected_roi=0.16,
        ),
    )

    calc = build_report(payload)

    assert calc.summary["current_net_worth"] > 0
    assert calc.summary["future_value"] > calc.summary["current_net_worth"]
    assert calc.comparison["best_scenario"]
    assert len(calc.scenario_projection["portfolio_cards"]) == 3
    assert len(calc.scenario_projection["series"]["Conservador"]) == max(calc.scenario_projection["horizons"]) + 1


def test_protection_includes_succession_cost() -> None:
    payload = PlanCreate(
        client_name="Cliente Protecao",
        age=40,
        dependents=2,
        monthly_income=15000,
        monthly_expenses=7000,
        monthly_contribution=2000,
        invested_assets=100000,
        real_estate_assets=300000,
        cash_reserves=20000,
        company_equity=80000,
        target_age=65,
        desired_monthly_income_future=18000,
        comparison=ComparisonInput(),
    )
    calc = build_report(payload)
    assert calc.summary["succession_cost_estimate"] == 100000.0
    assert calc.summary["protection_capital_needed"] > calc.summary["succession_cost_estimate"]

def test_portfolio_diagnosis_defaults() -> None:
    calc = build_report(PlanCreate(client_name="Sem Carteira", age=35, target_age=60))
    assert calc.portfolio_diagnosis["identified_profile"] == "Não informado"
    assert calc.portfolio_diagnosis["investor_score"] == 0
