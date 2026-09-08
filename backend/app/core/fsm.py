"""
FinShield Deterministic Workflow State Machine (FSM)
Enforces strictly deterministic, auditable business state transitions.
State progression cannot be probabilistically manipulated or bypassed.
"""

from typing import Set, Dict, List
from fastapi import HTTPException, status

class CaseStatus:
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    SCREENING_PASSED = "SCREENING_PASSED"
    SCREENING_FLAGGED = "SCREENING_FLAGGED"
    IN_REVIEW = "IN_REVIEW"                    # Analyst review
    REQUIRES_MANUAL_REVIEW = "REQUIRES_MANUAL_REVIEW" # Low AI confidence (<70%)
    COMMITTEE_PENDING = "COMMITTEE_PENDING"     # Escalated to 3-member committee
    APPROVED = "APPROVED"                       # Clean approval (e.g. Case 6)
    APPROVED_WITH_CONDITIONS = "APPROVED_WITH_CONDITIONS" # (Cases 1, 2, 5, 7)
    DEFERRED = "DEFERRED"                       # Pending EDD (Case 4)
    REJECTED = "REJECTED"                       # Regulatory blocker (Case 3)

VALID_TRANSITIONS: Dict[str, Set[str]] = {
    CaseStatus.DRAFT: {CaseStatus.SUBMITTED},
    CaseStatus.SUBMITTED: {CaseStatus.SCREENING_PASSED, CaseStatus.SCREENING_FLAGGED},
    CaseStatus.SCREENING_PASSED: {CaseStatus.IN_REVIEW, CaseStatus.REQUIRES_MANUAL_REVIEW, CaseStatus.APPROVED},
    CaseStatus.SCREENING_FLAGGED: {CaseStatus.IN_REVIEW, CaseStatus.REQUIRES_MANUAL_REVIEW},
    CaseStatus.REQUIRES_MANUAL_REVIEW: {CaseStatus.IN_REVIEW, CaseStatus.COMMITTEE_PENDING},
    CaseStatus.IN_REVIEW: {
        CaseStatus.APPROVED,                   # Fast-track low risk only
        CaseStatus.COMMITTEE_PENDING,
        CaseStatus.DEFERRED,
        CaseStatus.REJECTED
    },
    CaseStatus.COMMITTEE_PENDING: {
        CaseStatus.APPROVED,
        CaseStatus.APPROVED_WITH_CONDITIONS,
        CaseStatus.DEFERRED,
        CaseStatus.REJECTED
    },
    # Terminal states
    CaseStatus.APPROVED: set(),
    CaseStatus.APPROVED_WITH_CONDITIONS: set(),
    CaseStatus.DEFERRED: {CaseStatus.SUBMITTED}, # Can be resubmitted after EDD
    CaseStatus.REJECTED: {CaseStatus.SUBMITTED}  # Can be resubmitted after licensing
}

def validate_state_transition(current_status: str, target_status: str) -> bool:
    allowed = VALID_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Illegal workflow transition: Cannot transition from '{current_status}' to '{target_status}'. Allowed next states: {list(allowed)}"
        )
    return True

def get_allowed_next_states(current_status: str) -> List[str]:
    return list(VALID_TRANSITIONS.get(current_status, set()))
