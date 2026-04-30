from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.config import settings
import os

class IntentJudgment(BaseModel):
    passed: bool
    reason: str
    confidence: float

LMSTUDIO_MODEL = "google/gemma-4-e4b"

model = OpenAIChatModel(
    LMSTUDIO_MODEL,
    provider=OpenAIProvider(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
    ),
)

agent = Agent(
   model,
   output_type=IntentJudgment,
    system_prompt=(
        "You are a QA judge for a messaging bot. "
        "Given a bot response and an expected intent, determine if the response "
        "satisfies the intent. Be strict - partial matches should fail."
    ),
    model_settings={'thinking': 'low'}
)


async def judge_intent(response: str, expected_intent: str) -> IntentJudgment:
    result = await agent.run(
        f"Bot response: {response}\nExpected intent: {expected_intent}"
    )
    return result.output