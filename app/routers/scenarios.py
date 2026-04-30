from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.core.scenario_parser import list_scenarios, ScenarioConfig

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])

class ScenarioListResponse(BaseModel):
    scenarios: List[dict]

@router.get("", response_model=ScenarioListResponse)
def get_scenarios():
    scenarios = list_scenarios()
    return ScenarioListResponse(scenarios=scenarios)

@router.post("/validate")
def validate_scenario(payload: dict):
    try:
        scenario = ScenarioConfig(**payload)
        return {"status": "valid", "parsed": scenario.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
