import os
import yaml
from app.models.scenario import ScenarioConfig

SCENARIOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scenarios")

def load_scenario(filename: str) -> ScenarioConfig:
    filepath = os.path.join(SCENARIOS_DIR, filename)
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
    return ScenarioConfig(**data)

def list_scenarios() -> list[dict]:
    scenarios = []
    if not os.path.exists(SCENARIOS_DIR):
        return scenarios
    for file in os.listdir(SCENARIOS_DIR):
        if file.endswith(".yaml") or file.endswith(".yml"):
            try:
                scenario = load_scenario(file)
                scenarios.append({
                    "filename": file,
                    "name": scenario.name,
                    "description": scenario.description,
                    "step_count": len(scenario.steps)
                })
            except Exception as e:
                print(f"Error loading {file}: {e}")
    return scenarios
