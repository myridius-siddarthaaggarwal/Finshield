import pytest
from app.services.public_compliance_api import check_public_sanctions_and_compliance, get_calibrated_public_record
from app.services.requirement_expansion_service import expand_vague_brief, get_preseeded_vague_brief_benchmarks

@pytest.mark.asyncio
async def test_public_compliance_lookup():
    # Test Sanctioned Corridor
    res_sanction = await check_public_sanctions_and_compliance("Iran", category="jurisdiction")
    assert res_sanction["status"] == "CRITICAL_BLOCKED"
    assert "FATF Black List" in res_sanction["source"]

    # Test Monitored Corridor
    res_grey = await check_public_sanctions_and_compliance("Nigeria", category="jurisdiction")
    assert res_grey["status"] == "FLAGGED_MONITORED"
    assert "FATF" in res_grey["source"]

    # Test Crypto / Stablecoin
    res_crypto = await check_public_sanctions_and_compliance("USDT", category="asset")
    assert res_crypto["status"] == "REGULATORY_FLAG"
    assert "CASP" in res_crypto["mandatory_action"]

@pytest.mark.asyncio
async def test_expand_vague_brief_structure():
    brief = "Launch instant P2P transfers using phone numbers between UK and Nigeria with no limits."
    expanded = await expand_vague_brief(
        vague_brief=brief,
        division="Payments",
        change_type="New Product Launch",
        target_geographies=["United Kingdom", "Nigeria"]
    )
    
    assert "expanded_title" in expanded
    assert "technical_mechanics" in expanded
    assert "regulatory_matrix" in expanded
    assert len(expanded["regulatory_matrix"]) >= 2
    assert "identified_gaps" in expanded
    assert len(expanded["identified_gaps"]) >= 1
    assert "suggested_mitigations" in expanded
    assert "public_api_checks" in expanded
    assert expanded["context_confidence_score"] > 0.8

def test_vague_benchmarks():
    benchmarks = get_preseeded_vague_brief_benchmarks()
    assert len(benchmarks) >= 3
    assert benchmarks[0]["id"] == "brief-1"
