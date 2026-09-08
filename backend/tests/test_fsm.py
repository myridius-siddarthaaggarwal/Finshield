import pytest
from fastapi import HTTPException
from app.core.fsm import validate_state_transition, CaseStatus

def test_valid_state_transitions():
    assert validate_state_transition(CaseStatus.DRAFT, CaseStatus.SUBMITTED) is True
    assert validate_state_transition(CaseStatus.SUBMITTED, CaseStatus.SCREENING_PASSED) is True
    assert validate_state_transition(CaseStatus.IN_REVIEW, CaseStatus.COMMITTEE_PENDING) is True
    assert validate_state_transition(CaseStatus.COMMITTEE_PENDING, CaseStatus.APPROVED_WITH_CONDITIONS) is True
    assert validate_state_transition(CaseStatus.COMMITTEE_PENDING, CaseStatus.REJECTED) is True

def test_invalid_state_transitions_raise_exception():
    with pytest.raises(HTTPException):
        # Cannot jump from SUBMITTED directly to APPROVED without review
        validate_state_transition(CaseStatus.SUBMITTED, CaseStatus.APPROVED)

    with pytest.raises(HTTPException):
        # Cannot modify an already approved terminal case
        validate_state_transition(CaseStatus.APPROVED, CaseStatus.IN_REVIEW)
