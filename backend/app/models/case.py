from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base


class RiskCase(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(Integer, unique=True, index=True, nullable=True) # e.g. 1 to 7
    title = Column(String, nullable=False, index=True)
    division = Column(String, nullable=False) # Consumer Banking, Payments, Commercial Banking, Wealth Management, FCRM / Compliance
    change_type = Column(String, nullable=False) # New Product Launch, New Feature Launch, New Vendor Onboarding, Process Change - INTERNAL
    
    # Submitter info
    submitter_id = Column(Integer, nullable=True)
    submitter_name = Column(String, nullable=False)
    submitter_role = Column(String, nullable=True)
    
    # Description and structured intake
    what_requester_wants = Column(Text, nullable=False)
    target_geographies = Column(JSON, default=list) # e.g. ["UK", "EU", "Nigeria"]
    target_customers = Column(String, nullable=True)
    verification_speed = Column(String, nullable=True) # e.g. "60 seconds", "Standard in-branch"
    transaction_limits_desc = Column(String, nullable=True)
    
    # Real-world Context & Precedent
    real_world_context = Column(Text, nullable=True) # Precedents like Monzo £21M, Nationwide £44M, TD Bank $3B, OKX $504M
    
    # Workflow & State
    status = Column(String, default="SUBMITTED", nullable=False, index=True)
    
    # AI & Deterministic Scoring
    inherent_risk_score = Column(Float, nullable=True)
    inherent_risk_tier = Column(String, nullable=True) # LOW, MEDIUM, HIGH, CRITICAL
    residual_risk_score = Column(Float, nullable=True)
    residual_risk_tier = Column(String, nullable=True)
    final_analyst_score = Column(Float, nullable=True)
    ai_confidence_overall = Column(Float, nullable=True) # e.g. 0.87 (87%)
    
    # Recommendations & Outcomes
    analyst_recommendation = Column(String, nullable=True) # APPROVE, APPROVE_WITH_CONDITIONS, DEFER, REJECT
    final_outcome = Column(String, nullable=True)           # APPROVE, APPROVE_WITH_CONDITIONS, DEFER, REJECT
    committee_vote_result = Column(String, nullable=True)  # e.g. "3-0 Unanimous"
    
    # Metrics & Governance
    time_taken_hours = Column(Float, nullable=True)
    old_process_days = Column(Integer, default=15)
    time_saved_pct = Column(Float, nullable=True)          # e.g. 93.0
    
    # AI Generated Narrative / Draft Memo
    ai_draft_memo = Column(JSON, nullable=True)
    rejection_or_deferral_notice = Column(Text, nullable=True)
    
    # Audit & Locking
    is_audit_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    locked_at = Column(DateTime, nullable=True)

    # Relationships
    dimension_scores = relationship("RiskDimensionScore", back_populates="case", cascade="all, delete-orphan")
    controls = relationship("CaseControl", back_populates="case", cascade="all, delete-orphan")
    committee_votes = relationship("CommitteeVote", back_populates="case", cascade="all, delete-orphan")
    conditions = relationship("DecisionCondition", back_populates="case", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="case", cascade="all, delete-orphan")
    token_logs = relationship("TokenLog", back_populates="case", cascade="all, delete-orphan")


class RiskDimensionScore(Base):
    __tablename__ = "risk_dimension_scores"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    dimension_key = Column(String, nullable=False) # money_laundering, terrorist_financing, fraud, compliance
    dimension_name = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    
    # Scores
    ai_score = Column(Float, nullable=False)
    analyst_override_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=False)
    
    confidence = Column(Float, nullable=False) # 0.0 to 1.0
    framework_citation = Column(String, nullable=False) # e.g. "FATF R.10 — Customer Due Diligence"
    reasoning = Column(Text, nullable=False)
    traceability_factors = Column(JSON, default=list) # Breakdown of points added/reduced
    
    case = relationship("RiskCase", back_populates="dimension_scores")


class CaseControl(Base):
    __tablename__ = "case_controls"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    control_id = Column(String, nullable=True) # CTRL-KYC-BASIC, etc.
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    effectiveness = Column(Float, nullable=False) # e.g. 0.20 (20%)
    is_active = Column(Boolean, default=True)
    control_type = Column(String, default="EXISTING") # EXISTING, PROPOSED_BY_AI, ADDED_BY_ANALYST, MANDATED_BY_COMMITTEE
    rationale = Column(Text, nullable=True)
    
    case = relationship("RiskCase", back_populates="controls")


class CommitteeVote(Base):
    __tablename__ = "committee_votes"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    member_name = Column(String, nullable=False) # Sunita Rao, James Lee, Anita Patel
    member_role = Column(String, nullable=False) # CRO, CCO, Legal
    vote = Column(String, nullable=False)        # APPROVE, APPROVE_WITH_CONDITIONS, DEFER, REJECT
    rationale = Column(Text, nullable=False)
    voted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    case = relationship("RiskCase", back_populates="committee_votes")


class DecisionCondition(Base):
    __tablename__ = "decision_conditions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    condition_text = Column(String, nullable=False)
    is_mandatory = Column(Boolean, default=True)
    is_met = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    
    case = relationship("RiskCase", back_populates="conditions")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String, nullable=False) # SUBMISSION, AUTO_SCREENING, AI_SCORING, ANALYST_OVERRIDE, COMMITTEE_VOTE, AUDIT_LOCK
    actor_name = Column(String, nullable=False)
    actor_role = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    case = relationship("RiskCase", back_populates="audit_events")


class TokenLog(Base):
    __tablename__ = "token_logs"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True)
    step_name = Column(String, nullable=False) # document_parsing, risk_scoring, draft_generation, what_if_simulation
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    saved_tokens = Column(Integer, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    case = relationship("RiskCase", back_populates="token_logs")
