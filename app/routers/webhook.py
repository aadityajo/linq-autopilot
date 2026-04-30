import os
import hmac
import hashlib
from fastapi import BackgroundTasks, Request, HTTPException, Header, APIRouter
from app.internals.linqClient import client
from app.core.bot import generate_reply

WEBHOOK_SECRET = os.environ.get("LINQ_WEBHOOK_SECRET")

if not WEBHOOK_SECRET:
    raise RuntimeError("LINQ_WEBHOOK_SECRET environment variable is not set")

router = APIRouter()


def verify_webhook(
    signing_secret: str, payload: bytes, timestamp: str, signature: str
) -> bool:
    """Verifies the HMAC-SHA256 signature of the incoming webhook."""
    message = f"{timestamp}.{payload.decode('utf-8')}"

    expected_signature = hmac.new(
        signing_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


@router.post("/webhook")
async def handle_linq_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_webhook_signature: str = Header(None),
    x_webhook_timestamp: str = Header(None),
    x_webhook_event: str = Header(None),
):
    if not x_webhook_signature or not x_webhook_timestamp:
        raise HTTPException(status_code=400, detail="Missing webhook headers")

    raw_payload = await request.body()

    if not verify_webhook(
        WEBHOOK_SECRET, raw_payload, x_webhook_timestamp, x_webhook_signature
    ):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    try:
        event = client.webhooks.events(payload=raw_payload.decode("utf-8"))

        if event.event_type == "message.received":
            message_data = event.data
            sender = message_data.sender_handle.handle
            print(f"Restaurant Bot Webhook: Received message from {sender}")

            parts = message_data.parts
            response_text = " ".join([p.value for p in parts if p.type == "text"])

            if response_text.strip():
                message_id = getattr(message_data, "id", "")

                background_tasks.add_task(
                    process_restaurant_reply, sender, response_text, message_id
                )

        return {"status": "success"}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_restaurant_reply(sender: str, text: str, message_id: str = ""):
    print(f"Generating Restaurant reply for: {text}")
    reply = await generate_reply(sender, text, message_id)
    if reply:
        try:
            from_number = os.environ.get("FROM_NUMBER")
            client.chats.create(
                from_=from_number,
                to=[sender],
                message={"parts": [{"type": "text", "value": reply}]},
            )
            print(f"Restaurant Bot sent reply: {reply}")
        except Exception as e:
            print(f"Error sending reply via Linq SDK: {e}")
