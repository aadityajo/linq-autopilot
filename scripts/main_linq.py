import os
from linq import LinqAPIV3

client = LinqAPIV3(api_key=os.environ["LINQ_API_KEY"])


def test_webhook():
    subscription = client.webhook_subscriptions.create(
        target_url="https://upchuck-unscented-steed.ngrok-free.dev/?version=2026-02-03",
        subscribed_events=[
            "message.sent",
            "message.received",
            "message.delivered",
            "message.read",
            "message.failed",
        ],
    )
    print(subscription.id)
    print(subscription.signing_secret)
    print(subscription.dict())


def main():
    chatResponse = client.chats.create(
        from_=os.environ["BOT_NUMBER"],
        to=[os.environ["CALLER_NUMBER"]],
        message={"parts": [{"type": "text", "value": "Hello from Linq!"}]},
    )
    print(chatResponse)
    print(f"Chat created: {chatResponse.chat.id}")
    message = client.chats.messages.send(
        chatResponse.chat.id,
        message={"parts": [{"type": "text", "value": "Following up!"}]},
    )
    # print(f"Message ID: {chat.last_message.id}")
    test_webhook()


if __name__ == "__main__":
    main()
