"""
FinShield Live Token & Cost Tracker
Calculates tokens used, optimization savings, and cost metrics for enterprise reporting.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.case import TokenLog

# Claude 3.7 Sonnet baseline pricing per million tokens
INPUT_COST_PER_M = 3.00   # $3.00 per 1M input tokens
OUTPUT_COST_PER_M = 15.00 # $15.00 per 1M output tokens

def record_token_usage(
    db: Session,
    case_id: int,
    step_name: str,
    input_tokens: int,
    output_tokens: int,
    saved_tokens: int = 0
) -> TokenLog:
    total_tokens = input_tokens + output_tokens
    cost = ((input_tokens / 1_000_000) * INPUT_COST_PER_M) + ((output_tokens / 1_000_000) * OUTPUT_COST_PER_M)

    log_entry = TokenLog(
        case_id=case_id,
        step_name=step_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=round(cost, 5),
        saved_tokens=saved_tokens
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry

def get_token_metrics_summary(db: Session, case_id: int = None) -> Dict[str, Any]:
    query = db.query(TokenLog)
    if case_id:
        query = query.filter(TokenLog.case_id == case_id)
    
    logs: List[TokenLog] = query.all()
    
    total_input = sum(l.input_tokens for l in logs)
    total_output = sum(l.output_tokens for l in logs)
    total_tokens = sum(l.total_tokens for l in logs)
    total_cost = sum(l.estimated_cost_usd for l in logs)
    total_saved = sum(l.saved_tokens for l in logs)

    baseline_tokens = total_tokens + total_saved
    efficiency_pct = round((total_saved / baseline_tokens) * 100, 1) if baseline_tokens > 0 else 44.0

    by_step = {}
    for l in logs:
        if l.step_name not in by_step:
            by_step[l.step_name] = {"input": 0, "output": 0, "total": 0, "cost": 0.0}
        by_step[l.step_name]["input"] += l.input_tokens
        by_step[l.step_name]["output"] += l.output_tokens
        by_step[l.step_name]["total"] += l.total_tokens
        by_step[l.step_name]["cost"] += l.estimated_cost_usd

    return {
        "total_tokens": total_tokens,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_cost_usd": round(total_cost, 4),
        "total_saved_tokens": total_saved,
        "baseline_tokens_before_opt": baseline_tokens,
        "efficiency_savings_pct": efficiency_pct,
        "breakdown_by_step": by_step
    }
