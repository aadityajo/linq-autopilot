from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from app.config import settings

SYSTEM_PROMPT = """You are a helpful and polite receptionist for a Linq dental office. 
Your job is to help patients schedule appointments, answer basic questions about the clinic, and provide a welcoming experience.
Keep your answers brief and suitable for a text message (SMS/iMessage).

If user is trying to reschedule an appointment, ask them what date/time they want it to be rescheduled to. 
Once they reply, confirm that the appointment has been rescheduled.

DO NOT USE emojis
You have access to a tool to send Tapback reactions to the user's message. Feel free to use it to acknowledge their messages instead of always replying with text!
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
    model_settings={'thinking': 'low'}
)

@agent.tool
def react_to_message(ctx: RunContext[str], reaction_type: str) -> str:
    """
    Sends a reaction (Tapback) to the user's last message. Use this to acknowledge messages without sending a text reply.
    reaction_type must be exactly one of: love, like, dislike, laugh, emphasize, question.
    """
    valid_reactions = ['love', 'like', 'dislike', 'laugh', 'emphasize', 'question']
    if reaction_type not in valid_reactions:
        return f"Invalid reaction. Must be one of: {valid_reactions}"
        
    message_id = ctx.deps
    if not message_id:
        return "Error: No message ID available to react to."
        
    try:
        from app.internals.linqClient import client
        client.messages.add_reaction(
            message_id=message_id,
            operation="add",
            type=reaction_type
        )
        return f"Successfully sent '{reaction_type}' reaction."
    except Exception as e:
        return f"Failed to send reaction: {e}"

# In-memory dictionary tracking conversation history per phone number
# Format: { "+14041234567": [ ... messages ... ] }
conversation_histories = {}

async def generate_reply(sender_number: str, message_text: str, message_id: str = "", clear_history: bool = False) -> str:
    """Passes the incoming message through the agent, maintaining history."""
    if clear_history:
        conversation_histories[sender_number] = []
        
    history = conversation_histories.get(sender_number, [])
    
    try:
        # Run inference via the agent
        result = await agent.run(message_text, message_history=history, deps=message_id)
        reply_text = result.output
        if "NO_TEXT" in reply_text:
            reply_text = ""
        
        # Save updated conversation history
        conversation_histories[sender_number] = result.all_messages()
        
        return reply_text
    except Exception as e:
        print(f"Agent error generating reply: {e}")
        return ""
