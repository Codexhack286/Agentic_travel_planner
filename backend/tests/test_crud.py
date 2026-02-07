"""
Tests for database CRUD operations.
"""

import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud


@pytest.mark.asyncio
async def test_create_conversation_inserts_row(db_session: AsyncSession):
    """Test that create_conversation properly inserts a row in the database."""
    # Create a conversation
    conversation = await crud.create_conversation(db_session, title="Test Title")
    await db_session.commit()

    # Verify it was inserted
    assert conversation.id is not None
    assert conversation.title == "Test Title"
    assert conversation.created_at is not None
    assert conversation.updated_at is not None

    # Verify we can retrieve it
    retrieved = await crud.get_conversation(db_session, conversation.id)
    assert retrieved is not None
    assert retrieved.id == conversation.id
    assert retrieved.title == "Test Title"


@pytest.mark.asyncio
async def test_add_message_creates_message_and_updates_timestamp(
    db_session: AsyncSession,
):
    """Test that add_message creates a message and updates conversation timestamp."""
    # Create a conversation
    conversation = await crud.create_conversation(db_session, title="Chat")
    await db_session.commit()
    original_updated_at = conversation.updated_at

    # Wait a moment to ensure timestamp will be different
    await asyncio.sleep(0.01)

    # Add a message
    message = await crud.add_message(
        db_session,
        conv_id=conversation.id,
        role="user",
        content="Hello!",
        tool_results=None,
    )
    await db_session.commit()

    # Verify message was created
    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.role == "user"
    assert message.content == "Hello!"
    assert message.tool_results is None
    assert message.created_at is not None

    # Verify conversation's updated_at was updated
    await db_session.refresh(conversation)
    # Compare using timestamp() to handle both timezone-aware and naive datetimes
    assert conversation.updated_at.replace(tzinfo=None) > original_updated_at.replace(tzinfo=None)

    # Verify we can retrieve the message
    messages = await crud.get_messages(db_session, conversation.id)
    assert len(messages) == 1
    assert messages[0].id == message.id


@pytest.mark.asyncio
async def test_delete_conversation_cascades_to_messages(db_session: AsyncSession):
    """Test that deleting a conversation cascades to delete messages."""
    # Create a conversation
    conversation = await crud.create_conversation(db_session, title="To Delete")
    await db_session.commit()

    # Add some messages
    await crud.add_message(
        db_session,
        conv_id=conversation.id,
        role="user",
        content="Message 1",
    )
    await crud.add_message(
        db_session,
        conv_id=conversation.id,
        role="assistant",
        content="Message 2",
    )
    await db_session.commit()

    # Verify messages exist
    messages = await crud.get_messages(db_session, conversation.id)
    assert len(messages) == 2

    # Delete the conversation
    deleted = await crud.delete_conversation(db_session, conversation.id)
    await db_session.commit()
    assert deleted is True

    # Verify conversation is gone
    retrieved = await crud.get_conversation(db_session, conversation.id)
    assert retrieved is None

    # Verify messages are also gone (cascade delete)
    messages = await crud.get_messages(db_session, conversation.id)
    assert len(messages) == 0


@pytest.mark.asyncio
async def test_list_conversations_ordered_by_updated_at(db_session: AsyncSession):
    """Test that list_conversations returns results ordered by updated_at DESC."""
    # Create three conversations
    conv1 = await crud.create_conversation(db_session, title="First")
    await db_session.commit()

    await asyncio.sleep(0.01)

    conv2 = await crud.create_conversation(db_session, title="Second")
    await db_session.commit()

    await asyncio.sleep(0.01)

    conv3 = await crud.create_conversation(db_session, title="Third")
    await db_session.commit()

    # List should be in DESC order (newest first)
    conversations = await crud.list_conversations(db_session)
    assert len(conversations) == 3
    assert conversations[0].id == conv3.id  # Most recent
    assert conversations[1].id == conv2.id
    assert conversations[2].id == conv1.id  # Oldest

    # Update conv1 by adding a message (should bump it to top)
    await asyncio.sleep(0.01)
    await crud.add_message(
        db_session,
        conv_id=conv1.id,
        role="user",
        content="Update!",
    )
    await db_session.commit()

    # Now conv1 should be first
    conversations = await crud.list_conversations(db_session)
    assert conversations[0].id == conv1.id  # Just updated
    assert conversations[1].id == conv3.id
    assert conversations[2].id == conv2.id
