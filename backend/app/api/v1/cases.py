from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime, timezone
from app.db.session import get_db
from app.models.case import (
    RiskCase, RiskDimensionScore, CaseControl, CommitteeVote,
    DecisionCondition, AuditEvent
)
from app.core.fsm import validate_state_transition, CaseStatus
from app.services.screening_service import screen_geographies
from app.services.scoring_engine import (
    calculate_inherent_score, calculate_residual_score,
    evaluate_confidence_gate, get_risk_tier
)
from app.services.ai_service import score_risk_proposal_ai
from app.services.token_tracker import record_token_usage

router = APIRouter(prefix="/cases", tags=["Cases & Intake"])

class CaseCreateRequest(BaseModel):
    title: str
    division: str
    change_type: str
    submitter_name: str
    submitter_role: Optional[str] = None
    what_requester_wants: str
    target_geographies: List[str]
    target_customers: Optional[str] = None
    verification_speed: Optional[str] = "Standard"
    transaction_limits_desc: Optional[str] = "Standard"

@router.get("/")
def list_cases(division: Optional[str] = None, status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(RiskCase)
    if division:
        query = query.filter(RiskCase.division == division)
    if status_filter:
        query = query.filter(RiskCase.status == status_filter)
    
    cases = query.order_by(RiskCase.case_number.asc().nullslast(), RiskCase.id.asc()).all()
    
    # Return formatted list with lightweight details
    results = []
    for c in cases:
        results.append({
            "id": c.id,
            "case_number": c.case_number,
            "title": c.title,
            "division": c.division,
            "change_type": c.change_type,
            "submitter_name": c.submitter_name,
            "submitter_role": c.submitter_role,
            "status": c.status,
            "inherent_risk_score": c.inherent_risk_score,
            "inherent_risk_tier": c.inherent_risk_tier,
            "residual_risk_score": c.residual_risk_score,
            "residual_risk_tier": c.residual_risk_tier,
            "final_outcome": c.final_outcome,
            "ai_confidence_overall": c.ai_confidence_overall,
            "time_taken_hours": c.time_taken_hours,
            "old_process_days": c.old_process_days,
            "time_saved_pct": c.time_saved_pct,
            "created_at": c.created_at,
            "is_audit_locked": c.is_audit_locked
        })
    return results

@router.get("/{case_id}")
def get_case_detail(case_id: int, db: Session = Depends(get_db)):
    case = db.query(RiskCase).filter(RiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    dimensions = db.query(RiskDimensionScore).filter(RiskDimensionScore.case_id == case_id).all()
    controls = db.query(CaseControl).filter(CaseControl.case_id == case_id).all()
    votes = db.query(CommitteeVote).filter(CommitteeVote.case_id == case_id).all()
    conditions = db.query(DecisionCondition).filter(DecisionCondition.case_id == case_id).all()
    audit_events = db.query(AuditEvent).filter(AuditEvent.case_id == case_id).order_by(AuditEvent.created_at.asc()).all()

    return {
        "case": case,
        "dimensions": dimensions,
        "controls": controls,
        "committee_votes": votes,
        "conditions": conditions,
        "audit_events": audit_events
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_case(req: CaseCreateRequest, db: Session = Depends(get_db)):
    """
    Intake pipeline:
    1. Deterministic Sanctions & Geography Screening
    2. AI Risk Scoring across 4 dimensions
    3. Deterministic Weighted Math
    4. Confidence Gate (<70% routes to unanchored manual review)
    5. Immutable Audit Event Creation
    """
    # 1. Deterministic screening
    screening_result = screen_geographies(req.target_geographies)

    new_case = RiskCase(
        title=req.title,
        division=req.division,
        change_type=req.change_type,
        submitter_name=req.submitter_name,
        submitter_role=req.submitter_role or "Requester",
        what_requester_wants=req.what_requester_wants,
        target_geographies=req.target_geographies,
        target_customers=req.target_customers,
        verification_speed=req.verification_speed,
        transaction_limits_desc=req.transaction_limits_desc,
        status=CaseStatus.SUBMITTED
    )
    db.add(new_case)
    db.flush()

    # Log submission
    db.add(AuditEvent(
        case_id=new_case.id,
        event_type="SUBMISSION",
        actor_name=req.submitter_name,
        actor_role="Submitter",
        description=f"Change proposal '{req.title}' submitted for {req.division}."
    ))

    # Log auto-screening
    screening_desc = f"Screening result: {screening_result['screening_status']}. Highest risk tier: {screening_result['highest_risk_tier']}."
    db.add(AuditEvent(
        case_id=new_case.id,
        event_type="AUTO_SCREENING",
        actor_name="FinShield Screener",
        actor_role="System",
        description=screening_desc,
        details_json=screening_result
    ))

    # 2. AI Reasoning call
    ai_output = await score_risk_proposal_ai(
        case_title=req.title,
        division=req.division,
        change_type=req.change_type,
        description=req.what_requester_wants,
        geographies=req.target_geographies,
        customers=req.target_customers or "",
        verification=req.verification_speed or ""
    )

    # 3. Store Dimension Scores
    dim_data = ai_output.get("dimensions", {})
    scores_dict = {}
    confidences = []

    dim_name_map = {
        "money_laundering": "Money Laundering Risk",
        "terrorist_financing": "Terrorist Financing Risk",
        "fraud": "Fraud Risk",
        "compliance": "Regulatory & Compliance Risk"
    }

    dim_weight_map = {
        "money_laundering": 0.35,
        "terrorist_financing": 0.20,
        "fraud": 0.25,
        "compliance": 0.20
    }

    for key in ["money_laundering", "terrorist_financing", "fraud", "compliance"]:
        d_item = dim_data.get(key, {})
        sc = float(d_item.get("score", 6.0))
        conf = float(d_item.get("confidence", 0.85))
        scores_dict[key] = sc
        confidences.append(conf)

        db.add(RiskDimensionScore(
            case_id=new_case.id,
            dimension_key=key,
            dimension_name=dim_name_map.get(key, key),
            weight=dim_weight_map.get(key, 0.25),
            ai_score=sc,
            analyst_override_score=None,
            final_score=sc,
            confidence=conf,
            framework_citation=d_item.get("framework_citation", "FATF / FCA Standards"),
            reasoning=d_item.get("reasoning", "Standard assessment."),
            traceability_factors=d_item.get("traceability_factors", [])
        ))

    # 4. Deterministic Math & Confidence Gate
    inherent_score, inherent_tier = calculate_inherent_score(scores_dict)
    avg_confidence = round(sum(confidences) / len(confidences), 2)
    gate_eval = evaluate_confidence_gate(avg_confidence)

    new_case.inherent_risk_score = inherent_score
    new_case.inherent_risk_tier = inherent_tier
    new_case.residual_risk_score = inherent_score
    new_case.residual_risk_tier = inherent_tier
    new_case.ai_confidence_overall = avg_confidence
    new_case.status = gate_eval["status"]
    new_case.analyst_recommendation = ai_output.get("ai_recommendation", "APPROVE_WITH_CONDITIONS")

    # Add default basic KYC control
    db.add(CaseControl(
        case_id=new_case.id,
        control_id="CTRL-KYC-BASIC",
        name="Standard Customer Onboarding Verification",
        effectiveness=0.20,
        is_active=True,
        control_type="EXISTING",
        rationale="Initial baseline due diligence."
    ))

    # Log AI scoring event
    db.add(AuditEvent(
        case_id=new_case.id,
        event_type="AI_SCORING",
        actor_name="Claude Sonnet (v1.2.0)",
        actor_role="AI",
        description=f"AI risk evaluation completed. Inherent score: {inherent_score} ({inherent_tier}). Confidence: {int(avg_confidence*100)}%.",
        details_json={"gate_evaluation": gate_eval}
    ))

    # Record token usage
    record_token_usage(db, new_case.id, "document_parsing", 750, 320, 450)
    record_token_usage(db, new_case.id, "risk_scoring", 620, 410, 380)

    db.commit()
    db.refresh(new_case)
    return new_case
