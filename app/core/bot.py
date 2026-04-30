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
You have access to a tool to send Tapback reactions to the user's message. Use it to acknowledge short messages like "Thanks!" instead of always replying with text.
IMPORTANT: If you use the reaction tool, DO NOT output any text response. You MUST output exactly 'NO_TEXT' to end the conversation.
"""

model = OpenAIChatModel(
    "google/gemma-4-e4b",
    provider=OpenAIProvider(
        base_url=settings.lmstudio_base_url,
        api_key="lm-studio",
    ),
)

agent = Agent(
    model,
    deps_type=str,
    system_prompt=SYSTEM_PROMPT,
    model_settings={"thinking": "low"},
)


@agent.tool
def react_to_message(ctx: RunContext[str], reaction_type: str) -> str:
    """
    Sends a reaction (Tapback) to the user's last message. Use this to acknowledge messages without sending a text reply.
    reaction_type must be exactly one of: love, like, dislike, laugh, emphasize, question.
    """
    valid_reactions = ["love", "like", "dislike", "laugh", "emphasize", "question"]
    if reaction_type not in valid_reactions:
        return f"Invalid reaction. Must be one of: {valid_reactions}"

    message_id = ctx.deps
    if not message_id:
        return "Error: No message ID available to react to."

    try:
        from app.internals.linqClient import client

        client.messages.add_reaction(
            message_id=message_id, operation="add", type=reaction_type
        )
        return f"Successfully sent '{reaction_type}' reaction."
    except Exception as e:
        return f"Failed to send reaction: {e}"


async def generate_reply(
    sender_number: str, message_text: str, message_id: str = ""
) -> str:
    """Passes the incoming message through the agent, maintaining history."""

    history = await _load_history(sender_number)

    try:
        agent.system_prompt = SYSTEM_PROMPT.format(
            date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        result = await agent.run(message_text, message_history=history, deps=message_id)
        reply_text = result.output
        if "NO_TEXT" in reply_text:
            reply_text = ""

        await _save_history(sender_number, result.all_messages())

        return reply_text
    except Exception as e:
        print(f"Agent error generating reply: {e}")
        return ""
