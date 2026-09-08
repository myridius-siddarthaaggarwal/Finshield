import pytest
from app.services.scoring_engine import calculate_inherent_score, calculate_residual_score, get_risk_tier, evaluate_confidence_gate, simulate_what_if

def test_inherent_score_weighted_math():
    # money_laundering (0.35), terrorist_financing (0.20), fraud (0.25), compliance (0.20)
    dimensions = {
        "money_laundering": 9.2,
        "terrorist_financing": 8.0,
        "fraud": 8.5,
        "compliance": 8.0
    }
    score, tier = calculate_inherent_score(dimensions)
    assert round(score, 1) == 8.5
    assert tier == "CRITICAL"

def test_residual_score_controls_reduction():
    inherent = 8.4
    # Single weak control 15% effective -> reduces from 8.4 to ~7.46 (HIGH)
    res_1, tier_1 = calculate_residual_score(inherent, [0.15])
    assert res_1 < inherent
    assert tier_1 == "HIGH"

    # Multiple strong controls (15%, 65%, 55%, 60%) -> drops into LOW/MEDIUM
    res_multi, tier_multi = calculate_residual_score(inherent, [0.15, 0.65, 0.55, 0.60])
    assert res_multi < 4.0
    assert tier_multi in ["LOW", "MEDIUM"]

def test_confidence_gate_routing():
    # High confidence >= 70%
    gate_pass = evaluate_confidence_gate(0.85)
    assert gate_pass["passed_gate"] is True
    assert gate_pass["status"] == "IN_REVIEW"
    assert gate_pass["show_ai_score_to_analyst"] is True

    # Low confidence < 70%
    gate_fail = evaluate_confidence_gate(0.62)
    assert gate_fail["passed_gate"] is False
    assert gate_fail["status"] == "REQUIRES_MANUAL_REVIEW"
    assert gate_fail["show_ai_score_to_analyst"] is False

def test_what_if_simulation_calculation():
    sim = simulate_what_if(
        current_inherent=8.4,
        current_controls=[0.15],
        additional_controls=[
            {"name": "Transaction Limits", "effectiveness": 0.55},
            {"name": "Real-Time Monitoring", "effectiveness": 0.60}
        ]
    )
    assert sim["simulated_residual"] < sim["baseline_residual"]
    assert sim["risk_delta"] > 0
    assert "summary" in sim
