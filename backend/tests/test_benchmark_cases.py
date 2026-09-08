import pytest
from app.db.session import SessionLocal
from app.models.case import RiskCase, RiskDimensionScore, CommitteeVote, DecisionCondition

def test_all_seven_benchmark_cases_exist_and_are_valid():
    db = SessionLocal()
    try:
        cases = db.query(RiskCase).order_by(RiskCase.case_number.asc()).all()
        assert len(cases) >= 7, f"Expected 7 benchmark cases, found {len(cases)}"

        case_map = {c.case_number: c for c in cases if c.case_number is not None}
        
        # Case 1: QuickAccount (Approved w/ Conditions)
        c1 = case_map[1]
        assert "QuickAccount" in c1.title
        assert c1.status == "APPROVED_WITH_CONDITIONS"
        assert c1.inherent_risk_score == 8.4
        assert c1.residual_risk_score == 7.8
        assert c1.is_audit_locked is True

        # Case 2: PayAnywhere (Approved w/ Conditions)
        c2 = case_map[2]
        assert "PayAnywhere" in c2.title
        assert c2.status == "APPROVED_WITH_CONDITIONS"
        assert c2.inherent_risk_score == 8.3

        # Case 3: CryptoConnect (Rejected)
        c3 = case_map[3]
        assert "CryptoConnect" in c3.title
        assert c3.status == "REJECTED"
        assert c3.final_outcome == "REJECTED"

        # Case 4: TradeLink (Deferred)
        c4 = case_map[4]
        assert "TradeLink" in c4.title
        assert c4.status == "DEFERRED"

        # Case 5: WealthGlobal (Approved w/ Conditions)
        c5 = case_map[5]
        assert "WealthGlobal" in c5.title
        assert c5.status == "APPROVED_WITH_CONDITIONS"

        # Case 6: GreenHome (Approved Clean)
        c6 = case_map[6]
        assert "GreenHome" in c6.title
        assert c6.status == "APPROVED"
        assert c6.inherent_risk_tier == "LOW"

        # Case 7: AlertSmart (Meta Case)
        c7 = case_map[7]
        assert "AlertSmart" in c7.title
        assert c7.status == "APPROVED_WITH_CONDITIONS"
        assert c7.division == "FCRM / Compliance"

        # Verify each case has exactly 4 dimensions and 3 committee votes
        for num in range(1, 8):
            c = case_map[num]
            dims = db.query(RiskDimensionScore).filter(RiskDimensionScore.case_id == c.id).all()
            assert len(dims) == 4, f"Case #{num} has {len(dims)} dimensions, expected 4"

            votes = db.query(CommitteeVote).filter(CommitteeVote.case_id == c.id).all()
            assert len(votes) >= 3, f"Case #{num} has {len(votes)} committee votes, expected at least 3"

    finally:
        db.close()
