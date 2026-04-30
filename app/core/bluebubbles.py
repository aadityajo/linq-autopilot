import uuid
import requests
from urllib.parse import quote

class BlueBubblesClient:
    def __init__(self, base_url: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.password = password

    def _params(self, **extra):
        return {"password": self.password, **extra}

    def _check(self, response: requests.Response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"BlueBubbles API Error: {response.text}")
            raise
        
        data = response.json()
        if data.get("status") not in (200, 201):
            raise RuntimeError(data)
        return data.get("data")

    def ping(self):
        r = requests.get(
            f"{self.base_url}/api/v1/ping",
            params=self._params(),
            timeout=10,
        )
        return self._check(r)

    def list_chats(self, limit=100):
        r = requests.post(
            f"{self.base_url}/api/v1/chat/query",
            params=self._params(),
            json={
                "limit": limit,
                "offset": 0,
                "with": ["lastMessage", "participants"],
            },
            timeout=20,
        )
        return self._check(r)

    def get_chat_messages(self, chat_guid: str, limit=20):
        encoded_guid = quote(chat_guid, safe="")
        r = requests.get(
            f"{self.base_url}/api/v1/chat/{encoded_guid}/message",
            params=self._params(limit=limit, offset=0, sort="DESC"),
            timeout=20,
        )
        return self._check(r)

    def send_text(self, chat_guid: str, text: str, method="apple-script"):
        payload = {
            "chatGuid": chat_guid,
            "tempGuid": f"temp-{uuid.uuid4()}",
            "message": text,
            "text": text,
            "method": method,
        }

        r = requests.post(
            f"{self.base_url}/api/v1/message/text",
            params=self._params(),
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        return self._check(r)

def find_chat_by_number(client: BlueBubblesClient, target_number: str):
    chats = client.list_chats(limit=100)
    target_digits = "".join(filter(str.isdigit, target_number))
    if target_digits.startswith("1") and len(target_digits) == 11:
        target_digits = target_digits[1:]

    for chat in chats:
        for participant in chat.get("participants", []):
            addr = participant.get("address", "")
            addr_digits = "".join(filter(str.isdigit, addr))
            if addr_digits.endswith(target_digits):
                return chat
    return None
