from typing import Optional, Literal
from pydantic import BaseModel
from app.core.botHistory import _load_history, _save_history
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.config import settings
from datetime import datetime


SYSTEM_PROMPT = """You are Mia, the friendly host at Linq Bistro, a modern American restaurant in Atlanta.
<current_data>
Date & time right now: {date_time}
Figure out the date for the user from the day request made. Don't ask what day or date they are talking about.
</current_data>


<business_basics>
Our job is to make the restaurant more accessible and cater to request. We are very congenial and polite.
Your job is to help guests with reservations, answer questions about the menu and hours, and provide a warm experience over text.
Keep your replies brief and conversational — this is SMS/iMessage, not an email.
</business_basics>

<restaurant_info>
- Hours: Mon-Thu 5-10pm, Fri-Sat 5-11pm, Sunday brunch 11am-3pm (closed Sunday dinner)
- Address: 123 Peachtree St NW, Atlanta, GA 30303
- Phone: (404) 555-0192
- Cuisine: Modern American with Southern influences
- Popular dishes: Shrimp & Grits, Cast Iron Chicken, Wagyu Burger, Seasonal Tasting Menu (Fri/Sat only)
- Dietary: Full vegetarian and vegan menu available, gluten-free options on request
- Max party size: 10. Larger groups need to call the restaurant directly.
- Reservations: Available up to 30 days in advance
</restaurant_info>

<reservation_flow>
When a guest wants a reservation, collect: preferred date, time, and party size.
Once you have all three, confirm the reservation with a summary (e.g. "Great! I've booked a table for 4 on Friday at 7pm.").
If a date/time is fully booked, offer 2 alternatives within 1 hour either side.
</reservation_flow>

<cancellation_flow>
Ask the guest to confirm they want to cancel, then confirm the cancellation.
</cancellation_flow>

<out_of_scope>
If asked something outside your remit (e.g. directions to another restaurant, personal advice), politely redirect to what you can help with.
</out_of_scope>

DO NOT USE emojis

Respond using the output schema:
- Set "reply" with your text response for normal messages.
- Set "tapback" (one of: love, like, dislike, laugh, emphasize, question) INSTEAD of reply to send a silent Tapback reaction. Use this for short acknowledgements like "Thanks!" or "Got it!".
- Never set both reply and tapback. Never set neither — always set exactly one.
"""


class BotOutput(BaseModel):
    reply: Optional[str] = None
    tapback: Optional[
        Literal["love", "like", "dislike", "laugh", "emphasize", "question"]
    ] = None


model = OpenAIChatModel(
    "google/gemma-4-e4b",
    provider=OpenAIProvider(
        base_url=settings.lmstudio_base_url,
        api_key="lm-studio",
    ),
)

agent = Agent(
    model,
    output_type=BotOutput,
    model_settings={"thinking": "low"},
)


@agent.system_prompt
def dynamic_system_prompt() -> str:
    return SYSTEM_PROMPT.format(date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


async def generate_reply(
    sender_number: str, message_text: str, message_id: str = ""
) -> str:
    """Passes the incoming message through the agent, maintaining history."""

    history = await _load_history(sender_number)

    try:
        result = await agent.run(message_text, message_history=history)
        output: BotOutput = result.output

        await _save_history(sender_number, result.all_messages())

        if output.tapback:
            try:
                from app.internals.linqClient import client

                client.messages.add_reaction(
                    message_id=message_id, operation="add", type=output.tapback
                )
            except Exception as e:
                print(f"Failed to send Tapback reaction: {e}")
            return ""  # No text reply to send

        return output.reply or ""
    except Exception as e:
        print(f"Agent error generating reply: {e}")
        return ""
