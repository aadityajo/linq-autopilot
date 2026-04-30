# Linq Autopilot QA

An autonomous integration testing framework for [Linq](https://linq.com) iMessage bots. Autopilot replays scripted conversation scenarios against a live bot, evaluates each reply with a mix of rule-based and LLM-powered assertions, and surfaces results in a real-time dashboard.

---

## How It Works

```
Scenario YAML ──► Runner sends messages to Linq hosted number
                       │
                       ▼
               Bot receives webhook, generates reply (LMStudio / Gemma)
                       │
                       ▼
               Assertions evaluated (contains, intent, react, latency)
                       │
                       ▼
               Results streamed to Next.js dashboard
```

1. **Scenarios** - Conversation scripts defined in YAML (`app/scenarios/`). Each step sends a user message and declares what the bot reply must satisfy.
2. **Runner** - Sends messages over the Linq API, waits for webhook events, and times each turn.
3. **Assertions** - Four types: `contains_any`, `contains_all`, `forbidden` (string matching), `intent` (LLM judge), `react` (Tapback reaction), `latency_under_ms`.
4. **Bot** - `Mia`, a Linq Bistro restaurant host powered by `pydantic-ai` + a local LMStudio model. Handles reservations, menu FAQs, cancellations, and Tapback reactions.
5. **Dashboard** - Next.js frontend that polls for run status and lets you trigger new runs from the browser.

---

## Setup

### Prerequisites

| Requirement | Notes |
|---|---|
| Python ≥ 3.13 | Managed via `uv` |
| Node.js ≥ 18 | For the frontend |
| [LMStudio](https://lmstudio.ai) | Running locally on `http://localhost:1234` with `google/gemma-4-e4b` loaded |
| Redis | Used for per-number conversation history |
| Linq account | API key + webhook secret |

### 1. Clone & install

```bash
git clone https://github.com/aadityajo/linq.git
cd linq

# Install Python deps with uv
pip install uv
uv sync
```

### 2. Configure environment

Copy the example and fill in your values:

```bash
cp .env.example .env
```

```env
LINQ_API_KEY=your_linq_api_key
LINQ_WEBHOOK_SECRET=your_webhook_signing_secret
BOT_NUMBER=+1xxxxxxxxxx     # Linq restaurant number — the bot sends FROM here
CALLER_NUMBER=+1xxxxxxxxxx  # Simulated user / tester — messages are sent TO here
LMSTUDIO_BASE_URL=http://localhost:1234/v1
DATABASE_URL=sqlite:///./autopilot.db   # or a postgres URL
```

### 3. Run with Docker Compose (recommended)

```bash
docker compose up --build
```

This starts the FastAPI backend on `:8000` and the Next.js dashboard on `:3000`.

### 4. Run locally (development)

```bash
# Terminal 1 — backend
uv run uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend && npm install && npm run dev
```

### 5. Expose the webhook

The Linq platform needs to reach your local server. Use [ngrok](https://ngrok.com) or a similar tunnel:

```bash
ngrok http 8000
```

Register the public URL as a webhook in your Linq dashboard (subscribe to `message.received`).

---

## Writing Scenarios

Scenarios live in `app/scenarios/` as YAML files.

```yaml
name: "Happy Path Reservation"
description: "Guest books a table in one shot."
timeout_ms: 30000
steps:
  - role: "user"
    message: "Table for 2 this Friday at 7pm please"
    assert:
      - type: "intent"
        value: "Confirm the reservation for 2 people on Friday at 7pm"
      - type: "contains_any"
        values: ["friday", "7pm", "7:00"]

  - role: "user"
    message: "Perfect, thanks!"
    delay_ms: 1000
    assert:
      - type: "react"
        values: ["love", "like"]
```

**Assertion types:**

| Type | Description |
|---|---|
| `contains_any` | Response includes at least one of the listed strings |
| `contains_all` | Response includes all listed strings |
| `forbidden` | Response must NOT include any listed strings |
| `intent` | LLM judge checks if response satisfies the described intent |
| `react` | Bot sent an iMessage Tapback of the specified type |
| `latency_under_ms` | Turn completed within the given millisecond budget |

---

## Dashboard

Open `http://localhost:3000` to:

- **View all runs** — status (passing/failing/running), timestamps, and step-level results.
- **Trigger a new run** — pick a scenario, set the from/to numbers, and click **Start Run**.

---

## Tech Stack

**Backend:** FastAPI · pydantic-ai · SQLModel (SQLite) · Redis · `linq-python`  
**Bot model:** LMStudio (local) · `google/gemma-4-e4b`  
**Frontend:** Next.js 15 · TypeScript · Tailwind CSS  
**Infra:** Docker Compose · ngrok (dev tunneling)
