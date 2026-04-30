from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class FinancialPlan(Base):
    __tablename__ = "financial_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    dependents: Mapped[int] = mapped_column(Integer, default=0)
    monthly_income: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_expenses: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_contribution: Mapped[float] = mapped_column(Float, nullable=False)
    invested_assets: Mapped[float] = mapped_column(Float, nullable=False)
    real_estate_assets: Mapped[float] = mapped_column(Float, default=0.0)
    cash_reserves: Mapped[float] = mapped_column(Float, default=0.0)
    company_equity: Mapped[float] = mapped_column(Float, default=0.0)
    target_age: Mapped[int] = mapped_column(Integer, nullable=False)
    desired_monthly_income_future: Mapped[float] = mapped_column(Float, nullable=False)
    tax_regime: Mapped[str] = mapped_column(String(60), default="lucro_presumido")
    has_life_insurance: Mapped[str] = mapped_column(String(10), default="nao")
    has_emergency_reserve: Mapped[str] = mapped_column(String(10), default="nao")
    goals_json: Mapped[dict] = mapped_column(JSON, default=dict)
    life_events_json: Mapped[list] = mapped_column(JSON, default=list)
    comparison_json: Mapped[dict] = mapped_column(JSON, default=dict)
    report_json: Mapped[dict] = mapped_column(JSON, default=dict)
    advisor_notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
