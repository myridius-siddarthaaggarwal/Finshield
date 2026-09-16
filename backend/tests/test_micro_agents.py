import pytest
from app.services.agents.aml_agent import AMLSpecialistAgent
from app.services.agents.cft_agent import CFTSpecialistAgent
from app.services.agents.fraud_agent import FraudSpecialistAgent
from app.services.agents.compliance_agent import ComplianceSpecialistAgent
from app.services.agents.orchestrator import RiskAssessmentOrchestrator

@pytest.mark.asyncio
async def test_aml_specialist_agent():
    agent = AMLSpecialistAgent()
    res, inp_tok, outp_tok = await agent.evaluate_aml(
        title="Instant Global P2P Wallet",
        target_customers="Retail consumers",
        limits_desc="No limits proposed",
        geographies=["United Kingdom", "Nigeria"]
    )
    assert "score" in res
    assert "confidence" in res
    assert "framework_citation" in res
    assert "FATF" in res["framework_citation"]
    assert inp_tok > 0
    assert outp_tok > 0

@pytest.mark.asyncio
async def test_cft_specialist_agent():
    agent = CFTSpecialistAgent()
    res, inp_tok, outp_tok = await agent.evaluate_cft(
        title="Crypto Debit Card with USDT",
        geographies=["United Kingdom", "UAE"]
    )
    assert "score" in res
    assert res["score"] >= 8.0
    assert "FATF R.15" in res["framework_citation"]

@pytest.mark.asyncio
async def test_fraud_specialist_agent():
    agent = FraudSpecialistAgent()
    res, inp_tok, outp_tok = await agent.evaluate_fraud(
        title="Faster Payments 24/7",
        verification_speed="Instant 60-seconds",
        limits_desc="None"
    )
    assert "score" in res
    assert "PSR APP Fraud" in res["framework_citation"] or "FCA Consumer Duty" in res["framework_citation"]

@pytest.mark.asyncio
async def test_compliance_specialist_agent():
    agent = ComplianceSpecialistAgent()
    res, inp_tok, outp_tok = await agent.evaluate_compliance(
        title="In-App Crypto Wallet",
        division="Payments",
        change_type="New Product Launch"
    )
    assert "score" in res
    assert "MiCA" in res["framework_citation"] or "FCA" in res["framework_citation"]

@pytest.mark.asyncio
async def test_orchestrator_parallel_execution():
    orchestrator = RiskAssessmentOrchestrator()
    assessment = await orchestrator.run_parallel_assessment(
        case_title="Instant Cross-Border P2P",
        division="Payments",
        change_type="New Product Launch",
        description="Instant transfers via phone numbers between UK and Nigeria.",
        geographies=["United Kingdom", "Nigeria"],
        customers="Retail",
        verification="Instant 60s"
    )
    
    dims = assessment["dimensions"]
    assert "money_laundering" in dims
    assert "terrorist_financing" in dims
    assert "fraud" in dims
    assert "compliance" in dims

    telemetry = assessment["agent_telemetry"]
    assert "agent_aml" in telemetry
    assert "agent_cft" in telemetry
    assert "agent_fraud" in telemetry
    assert "agent_compliance" in telemetry
    assert telemetry["total_tokens"] > 0
    assert telemetry["saved_tokens"] > 0
    assert telemetry["efficiency_gain_pct"] > 35.0

@pytest.mark.asyncio
async def test_conditional_cross_agent_consultation_and_hardstop():
    orchestrator = RiskAssessmentOrchestrator()
    # This case has both P2P instant transfer AND crypto indicators which trigger cross-consultation
    assessment = await orchestrator.run_parallel_assessment(
        case_title="Instant P2P Crypto Wallet",
        division="Payments",
        change_type="New Product Launch",
        description="Instant P2P transfers and USDT crypto wallet.",
        geographies=["United Kingdom", "Nigeria"],
        customers="Retail",
        verification="Instant 60s"
    )
    
    interactions = assessment.get("cross_agent_interactions", {})
    assert "consultations" in interactions
    assert "circuit_breaker_hardstops" in interactions
    assert interactions["max_allowed_depth"] == 1
    assert interactions["loop_guard_status"] == "ACTIVE_GUARDED"

    # Verify at least one consultation occurred
    assert len(interactions["consultations"]) >= 1
    first_consult = interactions["consultations"][0]
    assert first_consult["status"] == "COMPLETED"
    assert "peer_advisory" in first_consult
    assert "score_adjustment_delta" in first_consult

    # Verify hardstop circuit breaker triggered to prevent infinite loop
    # Total consultations must strictly NOT exceed MAX_INTERACTION_DEPTH (1)
    assert len(interactions["consultations"]) <= 1
    assert len(interactions["circuit_breaker_hardstops"]) >= 1
    hardstop = interactions["circuit_breaker_hardstops"][0]
    assert hardstop["status"] == "HARDSTOP_ENFORCED"
    assert "prevented" in hardstop["action"]
