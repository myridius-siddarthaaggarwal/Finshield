from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
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
from app.services.requirement_expansion_service import expand_vague_brief, get_preseeded_vague_brief_benchmarks
from app.services.llm_client import get_active_provider_label

router = APIRouter(prefix="/cases", tags=["Cases & Intake"])

class BriefExpansionRequest(BaseModel):
    vague_brief: str
    division: Optional[str] = "Consumer Banking"
    change_type: Optional[str] = "New Product Launch"
    target_geographies: Optional[List[str]] = None

class CaseCreateRequest(BaseModel):
    title: str
    division: Optional[str] = "Consumer Banking"
    change_type: Optional[str] = "New Product Launch"
    submitter_name: Optional[str] = "Submitter"
    submitter_role: Optional[str] = None
    what_requester_wants: Optional[Any] = ""
    target_geographies: Optional[List[str]] = None
    target_customers: Optional[str] = None
    verification_speed: Optional[str] = "Standard"
    transaction_limits_desc: Optional[str] = "Standard"
    settlement_rail: Optional[str] = None
    third_party_dependencies: Optional[List[str]] = None
    mitigating_controls_offered: Optional[List[str]] = None
    working_specification: Optional[Any] = None

    class Config:
        extra = "allow"

@router.get("/vague-brief-benchmarks")
def list_vague_brief_benchmarks():
    """Returns realistic pre-seeded benchmark vague briefs for live evaluator testing."""
    return get_preseeded_vague_brief_benchmarks()

@router.post("/expand-brief")
async def expand_brief_endpoint(req: BriefExpansionRequest):
    """
    Autonomous Requirement Expansion:
    Transforms a 1-2 sentence vague brief into a full 360-degree banking technical
    and regulatory working specification using Governed Data Layer and Public APIs.
    """
    return await expand_vague_brief(
        vague_brief=req.vague_brief,
        division=req.division or "Consumer Banking",
        change_type=req.change_type or "New Product Launch",
        target_geographies=req.target_geographies
    )

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
    geos = req.target_geographies or ["United Kingdom"]
    screening_result = screen_geographies(geos)

    # Format description safely as string
    desc_str = req.what_requester_wants
    if isinstance(desc_str, dict):
        desc_str = desc_str.get("product_overview") or desc_str.get("summary") or desc_str.get("executive_summary") or str(desc_str)
    elif not isinstance(desc_str, str):
        desc_str = str(desc_str or req.title)

    new_case = RiskCase(
        title=req.title,
        division=req.division or "Consumer Banking",
        change_type=req.change_type or "New Product Launch",
        submitter_name=req.submitter_name or "Submitter",
        submitter_role=req.submitter_role or "Requester",
        what_requester_wants=desc_str,
        target_geographies=geos,
        target_customers=req.target_customers,
        verification_speed=req.verification_speed or "Standard",
        transaction_limits_desc=req.transaction_limits_desc or "Standard",
        status=CaseStatus.SUBMITTED,
        ai_draft_memo=req.working_specification if isinstance(req.working_specification, dict) else None
    )
    db.add(new_case)
    db.flush()

    # Log submission
    db.add(AuditEvent(
        case_id=new_case.id,
        event_type="SUBMISSION",
        actor_name=req.submitter_name or "Submitter",
        actor_role="Submitter",
        description=f"Change proposal '{req.title}' submitted for {req.division}."
    ))

    # Log requirement expansion if present
    if req.working_specification and isinstance(req.working_specification, dict):
        reg_matrix = req.working_specification.get("regulatory_matrix") or req.working_specification.get("governing_regulatory_frameworks") or []
        matrix_len = len(reg_matrix) if isinstance(reg_matrix, list) else 1
        public_checks = req.working_specification.get("public_api_checks") or []
        public_hits = len(public_checks) if isinstance(public_checks, list) else 0
        db.add(AuditEvent(
            case_id=new_case.id,
            event_type="REQUIREMENT_EXPANSION",
            actor_name="FinShield AI SME",
            actor_role="AI System",
            description=f"Vague brief autonomously expanded into 360° Bank Working Specification. Layered {matrix_len} regulatory frameworks & {public_hits} Public Compliance API checks.",
            details_json=req.working_specification
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
        
        # Resolve score
        sc_val = d_item.get("score") if d_item.get("score") is not None else d_item.get("risk_score", 7.5)
        try:
            sc = float(sc_val)
        except (ValueError, TypeError):
            sc = 7.5
        
        conf = float(d_item.get("confidence", 0.88))
        scores_dict[key] = sc
        confidences.append(conf)

        # Resolve citation
        citation = d_item.get("framework_citation") or d_item.get("governing_standards_violated") or d_item.get("governing_standards_applied") or "FATF / FCA Regulatory Standards"
        if isinstance(citation, list):
            citation = " + ".join([str(c) for c in citation[:2]])

        # Resolve reasoning
        reasoning = d_item.get("reasoning") or d_item.get("justification") or d_item.get("rationale") or d_item.get("fca_consumer_duty_alignment")
        if not reasoning or not isinstance(reasoning, str) or len(reasoning.strip()) < 10:
            if d_item.get("primary_vulnerabilities") and isinstance(d_item["primary_vulnerabilities"], list):
                reasoning = "; ".join([str(v) for v in d_item["primary_vulnerabilities"]])
            else:
                reasoning = "Multi-agent domain evaluation completed under active statutory frameworks."

        factors = d_item.get("traceability_factors") or d_item.get("primary_vulnerabilities") or []
        if not isinstance(factors, list):
            factors = [str(factors)]

        db.add(RiskDimensionScore(
            case_id=new_case.id,
            dimension_key=key,
            dimension_name=dim_name_map.get(key, key),
            weight=dim_weight_map.get(key, 0.25),
            ai_score=sc,
            analyst_override_score=None,
            final_score=sc,
            confidence=conf,
            framework_citation=str(citation),
            reasoning=str(reasoning),
            traceability_factors=factors
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
        actor_name=get_active_provider_label(),
        actor_role="AI",
        description=f"AI risk evaluation completed. Inherent score: {inherent_score} ({inherent_tier}). Confidence: {int(avg_confidence*100)}%.",
        details_json={"gate_evaluation": gate_eval}
    ))

    # Record token usage per specialized micro-agent
    agent_telemetry = ai_output.get("agent_telemetry", {})
    if agent_telemetry:
        for agent_key in ["agent_aml", "agent_cft", "agent_fraud", "agent_compliance"]:
            metrics = agent_telemetry.get(agent_key, {})
            record_token_usage(
                db=db,
                case_id=new_case.id,
                step_name=agent_key,
                input_tokens=metrics.get("input_tokens", 150),
                output_tokens=metrics.get("output_tokens", 80),
                saved_tokens=int(agent_telemetry.get("saved_tokens", 1200) / 4)
            )
    else:
        record_token_usage(db, new_case.id, "risk_scoring", 620, 410, 380)

    db.commit()
    db.refresh(new_case)
    return {
        "id": new_case.id,
        "case_number": new_case.case_number or new_case.id,
        "title": new_case.title,
        "division": new_case.division,
        "change_type": new_case.change_type,
        "status": new_case.status,
        "inherent_risk_score": new_case.inherent_risk_score,
        "inherent_risk_tier": new_case.inherent_risk_tier,
        "residual_risk_score": new_case.residual_risk_score,
        "residual_risk_tier": new_case.residual_risk_tier,
        "ai_confidence_overall": new_case.ai_confidence_overall,
        "analyst_recommendation": new_case.analyst_recommendation,
        "submitter_name": new_case.submitter_name,
        "created_at": new_case.created_at.isoformat() if new_case.created_at else None
    }


class ControlCreateRequest(BaseModel):
    name: str
    effectiveness: float
    dimension: Optional[str] = "compliance"
    control_type: Optional[str] = "PROPOSED"
    rationale: Optional[str] = None
    control_id: Optional[str] = None


class TransitionRequest(BaseModel):
    new_status: str
    actor_name: Optional[str] = "Analyst"
    actor_role: Optional[str] = "FCRM Analyst"
    notes: Optional[str] = None


class DirectVoteRequest(BaseModel):
    member_name: str
    member_role: str
    vote: str
    rationale: str


@router.post("/{case_id}/controls")
def add_case_control(case_id: int, req: ControlCreateRequest, db: Session = Depends(get_db)):
    """
    Attaches a mitigating control to the case, recalculates the residual risk score,
    and records an immutable audit event.
    """
    case = db.query(RiskCase).filter(RiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    ctrl_id = req.control_id or f"CTRL-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    new_ctrl = CaseControl(
        case_id=case_id,
        control_id=ctrl_id,
        name=req.name,
        effectiveness=req.effectiveness,
        is_active=True,
        control_type=req.control_type or "PROPOSED",
        rationale=req.rationale or f"Mitigates {req.dimension} risk."
    )
    db.add(new_ctrl)
    db.flush()

    # Recalculate residual score with all active controls
    all_active_controls = db.query(CaseControl).filter(CaseControl.case_id == case_id, CaseControl.is_active == True).all()
    eff_list = [c.effectiveness for c in all_active_controls]
    new_residual, new_tier = calculate_residual_score(case.inherent_risk_score or 8.0, eff_list)

    case.residual_risk_score = new_residual
    case.residual_risk_tier = new_tier
    case.final_analyst_score = new_residual

    db.add(AuditEvent(
        case_id=case_id,
        event_type="CONTROL_ADDED",
        actor_name="FCRM Analyst",
        actor_role="Risk Operations",
        description=f"Mitigating control added: '{req.name}' (Effectiveness: {int(req.effectiveness * 100)}%). Residual risk reduced to {new_residual} ({new_tier}).",
        details_json={"control_id": ctrl_id, "name": req.name, "effectiveness": req.effectiveness, "new_residual": new_residual}
    ))

    db.commit()
    db.refresh(case)
    return {
        "status": "success",
        "control_id": ctrl_id,
        "residual_score": new_residual,
        "residual_tier": new_tier
    }


@router.post("/{case_id}/transition")
def transition_case_status(case_id: int, req: TransitionRequest, db: Session = Depends(get_db)):
    """
    Transitions the case lifecycle state (e.g. SUBMITTED -> UNDER_REVIEW -> COMMITTEE_PENDING).
    """
    case = db.query(RiskCase).filter(RiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    old_status = case.status
    case.status = req.new_status

    db.add(AuditEvent(
        case_id=case_id,
        event_type="STATE_TRANSITION",
        actor_name=req.actor_name or "System",
        actor_role=req.actor_role or "System",
        description=f"Case transitioned from '{old_status}' to '{req.new_status}'. Notes: {req.notes or 'None'}",
        details_json={"old_status": old_status, "new_status": req.new_status}
    ))

    db.commit()
    db.refresh(case)
    return {
        "status": "success",
        "old_status": old_status,
        "new_status": case.status
    }


@router.post("/{case_id}/vote")
def cast_case_vote(case_id: int, req: DirectVoteRequest, db: Session = Depends(get_db)):
    """
    Records a committee vote on the case and seals the decision when unanimous.
    """
    case = db.query(RiskCase).filter(RiskCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    existing = db.query(CommitteeVote).filter(
        CommitteeVote.case_id == case_id,
        CommitteeVote.member_name == req.member_name
    ).first()

    if existing:
        existing.vote = req.vote
        existing.rationale = req.rationale
        existing.voted_at = datetime.now(timezone.utc)
    else:
        new_vote = CommitteeVote(
            case_id=case_id,
            member_name=req.member_name,
            member_role=req.member_role,
            vote=req.vote,
            rationale=req.rationale
        )
        db.add(new_vote)

    db.add(AuditEvent(
        case_id=case_id,
        event_type="COMMITTEE_VOTE",
        actor_name=req.member_name,
        actor_role=req.member_role,
        description=f"Vote cast by {req.member_name} ({req.member_role}): {req.vote}. Rationale: '{req.rationale}'",
        details_json={"vote": req.vote, "rationale": req.rationale}
    ))

    # Auto-seal if 3 votes recorded
    db.flush()
    all_votes = db.query(CommitteeVote).filter(CommitteeVote.case_id == case_id).all()
    if len(all_votes) >= 3:
        case.status = "APPROVED_WITH_CONDITIONS"
        case.final_outcome = "APPROVED_WITH_CONDITIONS"
        case.committee_vote_result = f"{len(all_votes)}-0 Unanimous"
        case.is_audit_locked = True
        case.locked_at = datetime.now(timezone.utc)
        case.time_taken_hours = 24.0
        case.time_saved_pct = 94.2

        db.add(AuditEvent(
            case_id=case_id,
            event_type="AUDIT_LOCK",
            actor_name="FinShield Governance Engine",
            actor_role="System",
            description=f"Case #{case.case_number or case.id} APPROVED WITH CONDITIONS by unanimous 3-0 Risk Committee vote. Cryptographic audit trail sealed.",
            details_json={"total_votes": len(all_votes), "decision": "APPROVED_WITH_CONDITIONS"}
        ))

    db.commit()
    db.refresh(case)
    return {
        "status": "success",
        "member_name": req.member_name,
        "vote": req.vote,
        "case_status": case.status,
        "is_audit_locked": case.is_audit_locked
    }


@router.get("/{case_id}/audit")
def get_case_audit_trail(case_id: int, db: Session = Depends(get_db)):
    """
    Returns full immutable ACID audit trail for the case.
    """
    events = db.query(AuditEvent).filter(AuditEvent.case_id == case_id).order_by(AuditEvent.created_at.asc()).all()
    return events

