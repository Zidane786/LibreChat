"""
Tests for message routes.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_message(client: AsyncClient, auth_headers, test_user):
    """Test creating a message."""
    response = await client.post(
        "/api/messages/test-conversation-id",
        headers=auth_headers,
        json={
            "conversationId": "test-conversation-id",
            "text": "Hello, this is a test message",
            "isCreatedByUser": True,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Hello, this is a test message"
    assert data["conversationId"] == "test-conversation-id"
    assert "messageId" in data


@pytest.mark.asyncio
async def test_get_messages(client: AsyncClient, auth_headers):
    """Test getting messages."""
    # First create a message
    await client.post(
        "/api/messages/test-convo",
        headers=auth_headers,
        json={
            "conversationId": "test-convo",
            "text": "Test message",
            "isCreatedByUser": True,
        },
    )

    # Then retrieve messages
    response = await client.get(
        "/api/messages/?conversationId=test-convo",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) > 0


@pytest.mark.asyncio
async def test_update_message(client: AsyncClient, auth_headers):
    """Test updating a message."""
    # Create a message first
    create_response = await client.post(
        "/api/messages/test-convo",
        headers=auth_headers,
        json={
            "conversationId": "test-convo",
            "text": "Original text",
            "isCreatedByUser": True,
        },
    )

    message_id = create_response.json()["messageId"]

    # Update the message
    response = await client.put(
        f"/api/messages/test-convo/{message_id}",
        headers=auth_headers,
        json={"text": "Updated text"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Updated text"


@pytest.mark.asyncio
async def test_delete_message(client: AsyncClient, auth_headers):
    """Test deleting a message."""
    # Create a message first
    create_response = await client.post(
        "/api/messages/test-convo",
        headers=auth_headers,
        json={
            "conversationId": "test-convo",
            "text": "To be deleted",
            "isCreatedByUser": True,
        },
    )

    message_id = create_response.json()["messageId"]

    # Delete the message
    response = await client.delete(
        f"/api/messages/test-convo/{message_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
