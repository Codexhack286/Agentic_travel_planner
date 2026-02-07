"""
Tests for conversation API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_conversations(test_client: AsyncClient):
    """Test listing all conversations."""
    # Initially empty
    response = await test_client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

    # Create a conversation
    create_response = await test_client.post(
        "/api/conversations",
        json={"title": "Test Conversation"}
    )
    assert create_response.status_code == 200

    # List should now have 1 conversation
    response = await test_client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Conversation"


@pytest.mark.asyncio
async def test_create_conversation(test_client: AsyncClient):
    """Test creating a new conversation."""
    # Create with custom title
    response = await test_client.post(
        "/api/conversations",
        json={"title": "My Trip to Paris"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Trip to Paris"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data

    # Create with default title
    response = await test_client.post("/api/conversations", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New conversation"


@pytest.mark.asyncio
async def test_update_conversation_title(test_client: AsyncClient):
    """Test updating a conversation's title."""
    # Create a conversation
    create_response = await test_client.post(
        "/api/conversations",
        json={"title": "Original Title"}
    )
    assert create_response.status_code == 200
    conversation_id = create_response.json()["id"]

    # Update the title
    response = await test_client.patch(
        f"/api/conversations/{conversation_id}",
        json={"title": "Updated Title"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["id"] == conversation_id

    # Verify update with GET
    response = await test_client.get(f"/api/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

    # Test updating non-existent conversation
    response = await test_client.patch(
        "/api/conversations/00000000-0000-0000-0000-000000000000",
        json={"title": "Will Fail"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation(test_client: AsyncClient):
    """Test deleting a conversation."""
    # Create a conversation
    create_response = await test_client.post(
        "/api/conversations",
        json={"title": "To Be Deleted"}
    )
    assert create_response.status_code == 200
    conversation_id = create_response.json()["id"]

    # Delete the conversation
    response = await test_client.delete(f"/api/conversations/{conversation_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    # Verify it's gone
    response = await test_client.get(f"/api/conversations/{conversation_id}")
    assert response.status_code == 404

    # Try deleting again (should fail)
    response = await test_client.delete(f"/api/conversations/{conversation_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_messages_for_conversation(test_client: AsyncClient):
    """Test getting messages for a conversation."""
    # Create a conversation
    create_response = await test_client.post(
        "/api/conversations",
        json={"title": "Chat Test"}
    )
    assert create_response.status_code == 200
    conversation_id = create_response.json()["id"]

    # Get messages (should be empty initially)
    response = await test_client.get(f"/api/conversations/{conversation_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

    # Test getting messages from non-existent conversation
    response = await test_client.get(
        "/api/conversations/00000000-0000-0000-0000-000000000000/messages"
    )
    assert response.status_code == 404
