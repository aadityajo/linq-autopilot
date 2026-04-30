from enum import Enum
from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON

class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    passed = "passed"
    failed = "failed"
    timeout = "timeout"

class TestRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    scenario_name: str
    scenario_file: str
    status: RunStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    from_number: str
    to_number: str

class StepResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    test_run_id: Optional[int] = Field(default=None, foreign_key="testrun.id")
    step_index: int
    message_sent: str
    response_received: Optional[str] = None
    response_latency_ms: Optional[int] = None
    assertions_passed: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    assertions_failed: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    failure_reasons: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    linq_trace_id: Optional[str] = None
    status: RunStatus
