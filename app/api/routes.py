from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.plans import FinancialPlan
from app.schemas.plans import PlanCreate, PlanResponse
from app.services.pdf_report import generate_plan_pdf
from app.services.planner import build_report

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@router.post("/api/plans", response_model=PlanResponse)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)) -> PlanResponse:
    calc = build_report(payload)
    plan = FinancialPlan(
        client_name=payload.client_name,
        age=payload.age,
        dependents=payload.dependents,
        monthly_income=payload.monthly_income,
        monthly_expenses=payload.monthly_expenses,
        monthly_contribution=payload.monthly_contribution,
        invested_assets=payload.invested_assets,
        real_estate_assets=payload.real_estate_assets,
        cash_reserves=payload.cash_reserves,
        company_equity=payload.company_equity,
        target_age=payload.target_age,
        desired_monthly_income_future=payload.desired_monthly_income_future,
        tax_regime=payload.tax_regime,
        has_life_insurance=payload.has_life_insurance,
        has_emergency_reserve=payload.has_emergency_reserve,
        goals_json=[goal.model_dump() for goal in payload.goals],
        life_events_json=[event.model_dump() for event in payload.life_events],
        comparison_json=payload.comparison.model_dump(),
        report_json=calc.report_context,
        advisor_notes=payload.advisor_notes,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return PlanResponse(
        id=plan.id,
        client_name=plan.client_name,
        summary=calc.summary,
        comparison=calc.comparison,
        scenario_projection=calc.scenario_projection,
        portfolio_diagnosis=calc.portfolio_diagnosis,
        timeline=calc.timeline,
        action_plan=calc.action_plan,
    )


@router.get("/api/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)) -> PlanResponse:
    plan = db.get(FinancialPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado.")
    report = plan.report_json
    return PlanResponse(
        id=plan.id,
        client_name=plan.client_name,
        summary=report["summary"],
        comparison=report["comparison"],
        scenario_projection=report["scenario_projection"],
        portfolio_diagnosis=report.get("portfolio_diagnosis", {
            "total": 0,
            "allocation": {},
            "allocation_values": {},
            "identified_profile": "Não informado",
            "perceived_profile": "Não informado",
            "risk_score": 0,
            "investor_score": 0,
            "concentration_alert": "Carteira não informada.",
            "diagnostics": ["Carteira atual não informada."],
            "recommendations": ["Mapear a carteira atual antes de propor realocação."],
            "comparison_table": [],
        }),
        timeline=report["timeline"],
        action_plan=report["action_plan"],
    )


@router.get("/api/plans/{plan_id}/pdf")
def get_plan_pdf(plan_id: int, db: Session = Depends(get_db)) -> Response:
    plan = db.get(FinancialPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado.")
    pdf_bytes = generate_plan_pdf(plan.report_json)
    filename = f"atlas-wealth-plano-{plan.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/api/plans")
def list_plans(db: Session = Depends(get_db)) -> JSONResponse:
    plans = db.query(FinancialPlan).order_by(FinancialPlan.created_at.desc()).limit(20).all()
    payload = [
        {
            "id": plan.id,
            "client_name": plan.client_name,
            "created_at": plan.created_at.isoformat(),
            "future_value": plan.report_json.get("summary", {}).get("future_value"),
            "capital_gap": plan.report_json.get("summary", {}).get("capital_gap"),
        }
        for plan in plans
    ]
    return JSONResponse(content=payload)
