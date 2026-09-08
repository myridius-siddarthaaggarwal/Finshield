import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "FinShield" in data["system"]

def test_data_layer_geography_risk():
    response = client.get("/api/v1/data-layer/geography-risk")
    assert response.status_code == 200
    data = response.json()
    assert "jurisdictions" in data
    assert len(data["jurisdictions"]) >= 10

def test_data_layer_regulatory_frameworks():
    response = client.get("/api/v1/data-layer/regulatory-frameworks")
    assert response.status_code == 200
    data = response.json()
    assert "frameworks" in data
    assert len(data["frameworks"]) >= 10

def test_data_layer_control_library():
    response = client.get("/api/v1/data-layer/control-library")
    assert response.status_code == 200
    data = response.json()
    assert "controls" in data
    assert len(data["controls"]) >= 10

def test_evaluation_judgement_matrix():
    response = client.get("/api/v1/evaluation/judgement-matrix")
    assert response.status_code == 200
    matrix = response.json()
    assert len(matrix) >= 8
    # Ensure both Deterministic and AI approaches are present
    approaches = [item["approach"] for item in matrix]
    assert any("Deterministic" in a for a in approaches)
    assert any("AI" in a for a in approaches)

def test_evaluation_benchmarks():
    response = client.get("/api/v1/evaluation/benchmarks")
    assert response.status_code == 200
    benchmarks = response.json()
    assert benchmarks["tested_cases_count"] == 7
    assert "85.7%" in benchmarks["overall_accuracy_rate"]
