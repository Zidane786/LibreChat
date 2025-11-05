"""
Message routes for CRUD operations, search, and feedback.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.schemas.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
    MessageFeedback,
    MessagesListResponse,
    ArtifactUpdate,
)
from app.services.message_service import MessageService
from app.services.conversation_service import ConversationService
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("/", response_model=MessagesListResponse)
async def get_messages(
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    sortBy: str = Query("createdAt", description="Sort field"),
    sortDirection: str = Query("desc", description="Sort direction"),
    pageSize: int = Query(25, ge=1, le=100, description="Page size"),
    conversationId: Optional[str] = Query(None, description="Conversation ID filter"),
    messageId: Optional[str] = Query(None, description="Specific message ID"),
    search: Optional[str] = Query(None, description="Search query"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get messages with pagination and filters.

    Supports:
    - Getting all messages in a conversation
    - Getting a specific message
    - Searching messages (via Meilisearch)
    """
    try:
        if search:
            # Search messages
            messages = await MessageService.search_messages(
                user_id=current_user.id,
                query=search,
            )
            return MessagesListResponse(messages=messages, nextCursor=None)

        # Get messages
        result = await MessageService.get_messages(
            user_id=current_user.id,
            conversation_id=conversationId,
            message_id=messageId,
            cursor=cursor,
            sort_by=sortBy,
            sort_direction=sortDirection,
            page_size=pageSize,
        )

        return MessagesListResponse(
            messages=result["messages"],
            nextCursor=result["nextCursor"],
        )

    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching messages",
        )


@router.get("/{conversationId}", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversationId: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all messages in a conversation.
    """
    try:
        result = await MessageService.get_messages(
            user_id=current_user.id,
            conversation_id=conversationId,
            page_size=1000,  # Get all messages
        )

        return result["messages"]

    except Exception as e:
        logger.error(f"Error fetching conversation messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching messages",
        )


@router.post("/{conversationId}", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversationId: str,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new message in a conversation.
    """
    try:
        # Create message
        message = await MessageService.create_message(
            user_id=current_user.id,
            conversation_id=conversationId,
            data=message_data.dict(exclude_unset=True),
        )

        # Update conversation
        await ConversationService.create_or_update_conversation(
            user_id=current_user.id,
            data={
                "conversationId": conversationId,
                "title": message_data.text[:50] if message_data.text else "New conversation",
            },
        )

        return MessageResponse(**message.dict())

    except Exception as e:
        logger.error(f"Error creating message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating message",
        )


@router.get("/{conversationId}/{messageId}", response_model=MessageResponse)
async def get_message(
    conversationId: str,
    messageId: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific message.
    """
    try:
        result = await MessageService.get_messages(
            user_id=current_user.id,
            conversation_id=conversationId,
            message_id=messageId,
        )

        if not result["messages"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        return result["messages"][0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching message",
        )


@router.put("/{conversationId}/{messageId}", response_model=MessageResponse)
async def update_message(
    conversationId: str,
    messageId: str,
    update_data: MessageUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a message.

    Supports:
    - Updating text
    - Updating specific content part by index
    - Token count updates
    """
    try:
        updated_message = await MessageService.update_message(
            user_id=current_user.id,
            message_id=messageId,
            data=update_data.dict(exclude_unset=True),
        )

        if not updated_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        return MessageResponse(**updated_message.dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating message",
        )


@router.put("/{conversationId}/{messageId}/feedback")
async def update_message_feedback(
    conversationId: str,
    messageId: str,
    feedback_data: MessageFeedback,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update message feedback (thumbs up/down, etc.).
    """
    try:
        updated_message = await MessageService.update_message_feedback(
            user_id=current_user.id,
            message_id=messageId,
            feedback=feedback_data.feedback,
        )

        if not updated_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        return {
            "messageId": messageId,
            "conversationId": conversationId,
            "feedback": updated_message.feedback,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating message feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update feedback",
        )


@router.post("/artifact/{messageId}")
async def update_artifact(
    messageId: str,
    artifact_data: ArtifactUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update artifact content within a message.
    """
    try:
        updated_message = await MessageService.update_artifact(
            user_id=current_user.id,
            message_id=messageId,
            artifact_index=artifact_data.index,
            original=artifact_data.original,
            updated=artifact_data.updated,
        )

        if not updated_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        return {
            "conversationId": updated_message.conversationId,
            "content": updated_message.content,
            "text": updated_message.text,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing artifact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error editing artifact",
        )


@router.delete("/{conversationId}/{messageId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    conversationId: str,
    messageId: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a message.
    """
    try:
        deleted = await MessageService.delete_message(
            user_id=current_user.id,
            message_id=messageId,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting message",
        )
