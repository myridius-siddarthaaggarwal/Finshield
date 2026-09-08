from app.services.screening_service import screen_geographies

def test_screen_clean_domestic_geography():
    res = screen_geographies(["United Kingdom"])
    assert res["is_sanctioned_blocked"] is False
    assert res["requires_edd"] is False
    assert res["screening_status"] == "CLEARED"

def test_screen_high_risk_jurisdiction_flagged_for_edd():
    res = screen_geographies(["Nigeria", "United Arab Emirates"])
    assert res["is_sanctioned_blocked"] is False
    assert res["requires_edd"] is True
    assert res["screening_status"] == "FLAGGED_FOR_EDD"
    assert len(res["flags"]) >= 2

def test_screen_sanctioned_jurisdiction_blocked():
    res = screen_geographies(["Democratic People's Republic of Korea"])
    assert res["is_sanctioned_blocked"] is True
    assert res["screening_status"] == "SANCTIONS_BLOCKED"
