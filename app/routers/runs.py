from app.core.botHistory import _delete_history
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlmodel import Session, select

from app.core.runner import execute_run
from app.database import get_session
from app.models.run import RunStatus, StepResult, TestRun
from app.redis import get_redis

router = APIRouter(prefix="/api/runs", tags=["runs"])


class RunStartRequest(BaseModel):
    scenario_file: str
    from_number: str
    to_number: str


class RunStartResponse(BaseModel):
    id: int


@router.post("", response_model=RunStartResponse)
async def start_run(
    request: RunStartRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    scenario_name = request.scenario_file.replace(".yaml", "").replace(".yml", "")

    run = TestRun(
        scenario_name=scenario_name,
        scenario_file=request.scenario_file,
        status=RunStatus.pending,
        started_at=datetime.now(timezone.utc),
        from_number=request.from_number,
        to_number=request.to_number,
    )
    session.add(run)
    session.commit()
    await _delete_history(request.to_number)
    await _delete_history(request.from_number)
    background_tasks.add_task(execute_run, run.id)

    return RunStartResponse(id=run.id)


@router.get("")
def list_runs(session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    runs = session.exec(
        select(TestRun).order_by(TestRun.started_at.desc()).offset(skip).limit(limit)
    ).all()
    return runs


@router.get("/{run_id}")
def get_run(run_id: int, session: Session = Depends(get_session)):
    run = session.get(TestRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    steps = session.exec(
        select(StepResult)
        .where(StepResult.test_run_id == run_id)
        .order_by(StepResult.step_index)
    ).all()
    return {"run": run.model_dump(), "steps": [step.model_dump() for step in steps]}
