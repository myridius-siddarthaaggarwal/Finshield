"""
FinShield Deterministic Screening Service
Performs instant lookup against FATF lists, OFAC sanctioned jurisdictions, and high-risk corridors.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from app.core.config import settings

def load_geography_risk_table() -> List[Dict[str, Any]]:
    geo_path = settings.DATA_LAYER_DIR / "geography_risk_table.json"
    if geo_path.exists():
        with open(geo_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("jurisdictions", [])
    return []

def screen_geographies(geographies: List[str]) -> Dict[str, Any]:
    """
    DETERMINISTIC: Evaluates a list of countries against the Governed Data Layer.
    """
    jurisdictions = load_geography_risk_table()
    geo_map = {j["country_name"].lower(): j for j in jurisdictions}
    # Also index by code
    code_map = {j["country_code"].lower(): j for j in jurisdictions}

    flags = []
    max_multiplier = 1.0
    highest_risk_tier = "LOW"
    tier_rank = {"LOW": 1, "LOW-MEDIUM": 2, "MEDIUM": 3, "MEDIUM-HIGH": 4, "HIGH": 5, "CRITICAL_SANCTIONED": 6}

    for geo in geographies:
        geo_clean = geo.strip().lower()
        matched = geo_map.get(geo_clean) or code_map.get(geo_clean)
        
        # Fuzzy match for regional corridors
        if not matched:
            for k, v in geo_map.items():
                if geo_clean in k or k in geo_clean:
                    matched = v
                    break

        if matched:
            tier = matched.get("risk_tier", "LOW")
            multiplier = matched.get("risk_multiplier", 1.0)
            if multiplier > max_multiplier:
                max_multiplier = multiplier

            if tier_rank.get(tier, 1) > tier_rank.get(highest_risk_tier, 1):
                highest_risk_tier = tier

            if tier in ["HIGH", "CRITICAL_SANCTIONED"]:
                flags.append({
                    "jurisdiction": matched["country_name"],
                    "risk_tier": tier,
                    "multiplier": multiplier,
                    "fatf_status": matched.get("fatf_status"),
                    "action_required": "Enhanced Due Diligence Mandatory" if tier == "HIGH" else "IMMEDIATE REJECTION (Sanctions Policy)"
                })
        else:
            # Default unlisted country
            pass

    is_sanctioned = highest_risk_tier == "CRITICAL_SANCTIONED"
    has_high_risk = len(flags) > 0

    return {
        "screened_count": len(geographies),
        "highest_risk_tier": highest_risk_tier,
        "max_multiplier": max_multiplier,
        "is_sanctioned_blocked": is_sanctioned,
        "requires_edd": has_high_risk,
        "flags": flags,
        "screening_status": "SANCTIONS_BLOCKED" if is_sanctioned else ("FLAGGED_FOR_EDD" if has_high_risk else "CLEARED")
    }
