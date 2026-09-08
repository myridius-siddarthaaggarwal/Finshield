import json
from fastapi import APIRouter, HTTPException
from pathlib import Path
from app.core.config import settings

router = APIRouter(prefix="/data-layer", tags=["Governed Data Layer"])

def read_json_file(filename: str):
    path = settings.DATA_LAYER_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Governed data file '{filename}' not found.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/geography-risk")
def get_geography_risk_table():
    return read_json_file("geography_risk_table.json")

@router.get("/regulatory-frameworks")
def get_regulatory_frameworks():
    return read_json_file("regulatory_frameworks.json")

@router.get("/control-library")
def get_control_library():
    return read_json_file("control_library.json")

@router.get("/risk-taxonomies")
def get_risk_taxonomies():
    return read_json_file("risk_taxonomies.json")
