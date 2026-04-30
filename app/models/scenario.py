from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class AssertionType(str, Enum):
    contains_any = "contains_any"
    contains_all = "contains_all"
    forbidden = "forbidden"
    latency_under_ms = "latency_under_ms"
    intent = "intent"
    react = "react"


class AssertionConfig(BaseModel):
    type: AssertionType
    values: list[str] | None = None
    value: str | int | None = None
    reason: str | None = None


class StepConfig(BaseModel):
    role: Literal["user"]
    message: str
    assert_: list[AssertionConfig] = Field(alias="assert", default_factory=list)
    delay_ms: int = 0


class ScenarioConfig(BaseModel):
    name: str
    description: str
    timeout_ms: int = 10000
    steps: list[StepConfig]
    metadata: dict = {}
