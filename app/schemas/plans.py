
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class GoalInput(BaseModel):
    name: str
    target_amount: float = Field(default=0, ge=0)
    target_year: int = Field(default=2026, ge=2026)


class LifeEventInput(BaseModel):
    year: int = Field(default=2026, ge=2026)
    title: str
    impact_amount: float = 0
    recurring: bool = False


class ComparisonInput(BaseModel):
    property_value: float = 0
    property_expected_sale_value: float = 0
    property_monthly_rent: float = 0
    property_monthly_costs: float = 0
    auction_discount_rate: float = 0
    investment_initial: float = 0
    investment_monthly: float = 0
    investment_years: int = 10
    long_term_rate: float = 0.12
    business_expected_roi: float = 0.15



class PortfolioInput(BaseModel):
    cash: float = 0
    fixed_income: float = 0
    equities_br: float = 0
    equities_global: float = 0
    fiis: float = 0
    alternatives: float = 0
    pension: float = 0
    others: float = 0
    perceived_profile: Literal["conservador", "moderado", "sofisticado", "nao_sei"] = "nao_sei"
    notes: str = ""

class ExistingInsuranceInput(BaseModel):
    provider: str = ""
    product_type: str = ""
    coverage_amount: float = 0
    death_coverage: float = 0
    disability_coverage: float = 0
    serious_illness_coverage: float = 0
    dit_monthly: float = 0
    monthly_premium: float = 0
    redeemable: Literal["sim", "nao"] = "nao"
    notes: str = ""


class ExistingPensionInput(BaseModel):
    provider: str = ""
    plan_type: Literal["pgbl", "vgbl", "nao_sabe", "nenhum"] = "nenhum"
    balance: float = 0
    annual_contribution: float = 0
    taxation_table: Literal["progressiva", "regressiva", "nao_sabe", "nenhuma"] = "nenhuma"
    notes: str = ""


class AssumptionsInput(BaseModel):
    simulation_years: int = 40
    scenario_short_years: int = 20
    selic_structural: float = 0.055
    selic_band_up: float = 0.02
    selic_band_down: float = 0.01
    inflation_assumption: float = 0.05
    post_fixed_spread: float = 0.0
    inflation_plus_rate: float = 0.05
    pre_fixed_real_rate: float = 0.03
    rebalance_annually: bool = True
    withdrawal_rate: float = 0.04
    retirement_years: int = 40
    retirement_return_rate: float = 0.08
    succession_cost_rate: float = 0.20
    family_protection_years: int = 10
    income_multiple: float = 5.0
    cdi_return: float = 0.0950        # Média 9,2% + ajuste ciclo atual
    gold_return: float = 0.1300       # Média 18,5% descontado efeito câmbio extremo
    ntnb_return: float = 0.0550       # Carry médio NTN-B, não marcação
    ntnf_return: float = 0.0900       # Carry médio NTN-F
    ibovespa_return: float = 0.1000   # Média geométrica 9,8%, levemente arredondado
    sp500_brl_return: float = 0.1500
    moderate_volatility: float = 0.10   # Média 22,4% descontado câmbio estrutural
    fiis_return: float = 0.0800       # IFIX médio 7,1% + ajuste dividend yield atual
    conservative_volatility: float = 0.05
    sophisticated_volatility: float = 0.16

    @model_validator(mode="after")
    def normalize_percent_inputs(self) -> "AssumptionsInput":
        percent_fields = [
            "selic_structural",
            "selic_band_up",
            "selic_band_down",
            "inflation_assumption",
            "post_fixed_spread",
            "inflation_plus_rate",
            "pre_fixed_real_rate",
            "withdrawal_rate",
            "retirement_return_rate",
            "succession_cost_rate",
            "cdi_return",
            "gold_return",
            "ntnb_return",
            "ntnf_return",
            "ibovespa_return",
            "sp500_brl_return",
            "fiis_return",
            "conservative_volatility",
            "moderate_volatility",
            "sophisticated_volatility",
        ]

        for field in percent_fields:
            value = getattr(self, field)
            if abs(value) > 1:
                setattr(self, field, value / 100)
        return self


class PlanCreate(BaseModel):
    client_name: str = "Cliente"
    age: int = Field(default=35, ge=18, le=100)
    dependents: int = Field(ge=0, default=0)
    monthly_income: float = Field(default=0, ge=0)
    monthly_expenses: float = Field(default=0, ge=0)
    monthly_contribution: float = Field(default=0, ge=0)
    invested_assets: float = Field(default=0, ge=0)
    real_estate_assets: float = Field(default=0, ge=0)
    cash_reserves: float = Field(default=0, ge=0)
    company_equity: float = Field(default=0, ge=0)
    vehicles_assets: float = Field(default=0, ge=0)
    previdence_assets: float = Field(default=0, ge=0)
    insurance_reserve_assets: float = Field(default=0, ge=0)
    international_assets: float = Field(default=0, ge=0)
    other_assets: float = Field(default=0, ge=0)
    target_age: int = Field(default=60, ge=19, le=110)
    desired_monthly_income_future: float = Field(default=0, ge=0)
    retirement_mode: Literal["somente_rentabilidade", "rentabilidade_e_principal", "somente_principal"] = "rentabilidade_e_principal"
    tax_regime: str = "nao_informado"
    has_life_insurance: Literal["sim", "nao"] = "nao"
    has_emergency_reserve: Literal["sim", "nao"] = "nao"
    has_pension: Literal["sim", "nao"] = "nao"
    goals: list[GoalInput] = Field(default_factory=list)
    life_events: list[LifeEventInput] = Field(default_factory=list)
    comparison: ComparisonInput = Field(default_factory=ComparisonInput)
    assumptions: AssumptionsInput = Field(default_factory=AssumptionsInput)
    existing_insurance: ExistingInsuranceInput = Field(default_factory=ExistingInsuranceInput)
    existing_pension: ExistingPensionInput = Field(default_factory=ExistingPensionInput)
    current_portfolio: PortfolioInput = Field(default_factory=PortfolioInput)
    advisor_notes: str = ""

    @model_validator(mode="after")
    def validate_target_age(self) -> "PlanCreate":
        if self.target_age <= self.age:
            raise ValueError("A idade alvo deve ser maior que a idade atual.")
        return self


class PlanSummary(BaseModel):
    current_net_worth: float
    future_value: float
    retirement_target_capital: float
    capital_gap: float
    emergency_reserve_target: float
    protection_capital_needed: float
    protection_gap: float
    succession_cost_estimate: float
    life_security_capital: float
    current_insurance_coverage: float
    effective_tax_drag: float
    goal_readiness_ratio: float
    goal_readiness_percent: float
    remaining_percent: float
    years_to_goal: int
    monthly_capacity: float
    retirement_mode_label: str
    thermometer_status: str
    pension_recommendation: str
    total_income_considered: float
    total_expenses_considered: float
    monthly_contribution_selected: float


class ScenarioComparison(BaseModel):
    buy_property_future_value: float
    rent_and_invest_future_value: float
    auction_property_future_value: float
    invest_in_business_future_value: float
    long_term_investment_future_value: float
    best_scenario: str


class ScenarioPortfolioSummary(BaseModel):
    name: str
    level: str
    allocation: dict[str, float]
    assets: list[dict[str, float | str]]
    value_10y: float
    value_20y: float
    expected_return: float
    volatility: float
    worst_drawdown: float


class ScenarioProjection(BaseModel):
    horizons: list[int]
    annual_labels: list[str]
    series: dict[str, list[float]]
    portfolio_cards: list[ScenarioPortfolioSummary]
    highlights: list[str]
    historical_window: dict[str, int]



class PortfolioDiagnosis(BaseModel):
    total: float
    allocation: dict[str, float]
    allocation_values: dict[str, float]
    identified_profile: str
    perceived_profile: str
    risk_score: float
    investor_score: float
    concentration_alert: str
    diagnostics: list[str]
    recommendations: list[str]
    comparison_table: list[dict[str, float | str]]

class PlanResponse(BaseModel):
    id: int
    client_name: str
    summary: PlanSummary
    comparison: ScenarioComparison
    scenario_projection: ScenarioProjection
    portfolio_diagnosis: PortfolioDiagnosis
    timeline: list[dict]
    action_plan: list[str]
