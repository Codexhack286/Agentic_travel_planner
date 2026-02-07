"""
Database seeding functions.
Seeds a welcome conversation for new users on first startup.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.db import crud


async def seed_welcome_conversation(db: AsyncSession) -> None:
    """
    Create a welcome conversation if the database is empty.
    This provides helpful context and example prompts for new users.
    """
    # Check if any conversations already exist
    existing = await crud.list_conversations(db)
    if existing:
        # Database already has conversations, skip seeding
        return

    # Create welcome conversation
    conversation = await crud.create_conversation(
        db,
        title="Welcome to Voyager AI ✈️"
    )

    # Add welcome message from assistant
    welcome_content = """Welcome to **Voyager AI**, your AI-powered travel planning assistant! 🌍

I can help you plan your perfect trip by:

- 🔍 **Searching flights** across multiple airlines and finding the best deals
- 🏨 **Finding hotels** that match your budget and preferences
- 🎯 **Creating custom itineraries** based on your interests
- 🌤️ **Checking weather forecasts** for your destination
- 💱 **Converting currencies** and estimating travel costs
- 🗺️ **Discovering attractions** and local experiences

### Try asking me:

- "Find me flights from New York to Tokyo next month"
- "I want to visit Paris for 5 days, help me plan an itinerary"
- "What's the weather like in Bali in December?"
- "Find affordable hotels near the Eiffel Tower"

Just type your travel question below and I'll help you plan your next adventure! 🚀

---
*Note: I'm currently running with mock data. Real flight search, hotel booking, and weather APIs will be integrated by the API Integration Engineer.*
"""

    await crud.add_message(
        db,
        conv_id=conversation.id,
        role="assistant",
        content=welcome_content,
        tool_results=None,
    )

    print(f"✅ Seeded welcome conversation (ID: {conversation.id})")
