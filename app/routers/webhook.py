import os
import hmac
import hashlib
from fastapi import Request, HTTPException, Header, APIRouter
from app.internals.linqClient import client

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

        # if x_webhook_event == "message.received":
        #     print(f"New message received: {event}")
        #     # Add your custom business logic here

        # elif x_webhook_event == "message.sent":
        #     print(f"Message was sent: {event}")
        return {"status": "success"}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
