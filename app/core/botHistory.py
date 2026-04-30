from pydantic_ai.messages import ModelMessagesTypeAdapter
from app.internals.redisClient import redis_client

CONVERSATION_TTL_SECONDS = 60 * 60


def _history_key(sender_number: str) -> str:
    return f"bot:history:{sender_number}"


async def _load_history(sender_number: str) -> list:
    redis = redis_client.get_client()
    if redis is None:
        return []
    raw = await redis.get(_history_key(sender_number))
    if not raw:
        return []
    return ModelMessagesTypeAdapter.validate_json(raw)


async def _delete_history(sender_number: str) -> None:
    redis = redis_client.get_client()
    if redis is None:
        return
    await redis.delete(_history_key(sender_number))


async def _save_history(sender_number: str, messages: list) -> None:
    redis = redis_client.get_client()
    if redis is None:
        return
    serialized = ModelMessagesTypeAdapter.dump_json(messages)
    await redis.setex(_history_key(sender_number), CONVERSATION_TTL_SECONDS, serialized)
