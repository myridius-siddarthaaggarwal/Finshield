"""
FinShield Hybrid Risk Scoring Engine
Combines probabilistic AI domain reasoning with deterministic mathematical formulas,
confidence threshold gating, and what-if simulation capabilities.
"""

from typing import Dict, List, Any, Tuple
from app.core.config import settings

DIMENSION_WEIGHTS = {
    "money_laundering": 0.35,
    "terrorist_financing": 0.20,
    "fraud": 0.25,
    "compliance": 0.20
}

def calculate_inherent_score(dimension_scores: Dict[str, float]) -> Tuple[float, str]:
    """
    DETERMINISTIC: Computes weighted average inherent score across all 4 dimensions.
    """
    total_score = 0.0
    total_weight = 0.0

    for key, weight in DIMENSION_WEIGHTS.items():
        score = dimension_scores.get(key, 5.0)
        total_score += score * weight
        total_weight += weight

    inherent = round(total_score / total_weight, 2)
    tier = get_risk_tier(inherent)
    return inherent, tier

def calculate_residual_score(inherent_score: float, controls_effectiveness: List[float]) -> Tuple[float, str]:
    """
    DETERMINISTIC: Applies controls reduction formula.
    Controls mitigate but NEVER eliminate inherent risk (minimum floor: 1.0).
    """
    if not controls_effectiveness:
        return inherent_score, get_risk_tier(inherent_score)

    # Diminishing returns formula for multiple controls:
    # effective_reduction = 1 - product(1 - e_i)
    multiplier = 1.0
    for eff in controls_effectiveness:
        multiplier *= (1.0 - min(eff, 0.90))

    overall_reduction = 1.0 - multiplier
    # Residual cannot drop below 15% of inherent risk floor
    residual = max(round(inherent_score * (1.0 - (overall_reduction * 0.75)), 2), 1.0)
    tier = get_risk_tier(residual)
    return residual, tier

def get_risk_tier(score: float) -> str:
    """Deterministic lookup against policy bands."""
    if score <= 3.0:
        return "LOW"
    elif score <= 6.0:
        return "MEDIUM"
    elif score <= 8.0:
        return "HIGH"
    else:
        return "CRITICAL"

def evaluate_confidence_gate(overall_confidence: float) -> Dict[str, Any]:
    """
    ENGINEERING JUDGEMENT: Confidence Threshold Gate.
    If AI confidence is below 70%, block auto-display to prevent anchoring bias.
    """
    threshold = settings.CONFIDENCE_THRESHOLD
    if overall_confidence < threshold:
        return {
            "passed_gate": False,
            "status": "REQUIRES_MANUAL_REVIEW",
            "reason": f"AI confidence ({round(overall_confidence * 100, 1)}%) is below governing threshold ({round(threshold * 100)}%). Routing to unanchored manual assessment.",
            "show_ai_score_to_analyst": False
        }
    return {
        "passed_gate": True,
        "status": "IN_REVIEW",
        "reason": "AI confidence meets enterprise threshold.",
        "show_ai_score_to_analyst": True
    }

def simulate_what_if(
    current_inherent: float,
    current_controls: List[float],
    additional_controls: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Sandbox simulation allowing analyst to test impact of adding 1-5 proposed controls.
    """
    current_residual, current_tier = calculate_residual_score(current_inherent, current_controls)
    
    combined_controls = list(current_controls)
    for c in additional_controls:
        combined_controls.append(c.get("effectiveness", 0.0))

    simulated_residual, simulated_tier = calculate_residual_score(current_inherent, combined_controls)
    delta = round(current_residual - simulated_residual, 2)
    pct_reduction = round((delta / current_residual) * 100, 1) if current_residual > 0 else 0.0

    return {
        "baseline_residual": current_residual,
        "baseline_tier": current_tier,
        "simulated_residual": simulated_residual,
        "simulated_tier": simulated_tier,
        "risk_delta": delta,
        "percentage_reduction": pct_reduction,
        "is_approvable_tier": simulated_tier in ["LOW", "MEDIUM"],
        "summary": f"Adding {len(additional_controls)} controls reduces risk score by {delta} pts ({pct_reduction}%), moving status to {simulated_tier}."
    }
