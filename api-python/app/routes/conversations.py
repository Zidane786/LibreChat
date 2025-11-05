"""
Conversation routes for CRUD operations, forking, and management.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationsListResponse,
    DeleteConversationRequest,
    ForkConversationRequest,
    ForkConversationResponse,
    DuplicateConversationRequest,
    GenerateTitleRequest,
    GenerateTitleResponse,
)
from app.services.conversation_service import ConversationService
from app.models.user import User
from app.middleware.auth import get_current_active_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/convos", tags=["conversations"])


@router.get("/", response_model=ConversationsListResponse)
async def get_conversations(
    limit: int = Query(25, ge=1, le=100, description="Results per page"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    isArchived: Optional[bool] = Query(None, description="Filter by archive status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    search: Optional[str] = Query(None, description="Search query"),
    order: str = Query("desc", description="Sort order (asc/desc)"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get conversations with pagination and filters.
    """
    try:
        result = await ConversationService.get_conversations(
            user_id=current_user.id,
            cursor=cursor,
            limit=limit,
            is_archived=isArchived,
            tags=tags,
            search=search,
            order=order,
        )

        return ConversationsListResponse(**result)

    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching conversations",
        )


@router.get("/{conversationId}", response_model=ConversationResponse)
async def get_conversation(
    conversationId: str,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific conversation.
    """
    try:
        conversation = await ConversationService.get_conversation(
            user_id=current_user.id,
            conversation_id=conversationId,
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        return ConversationResponse(**conversation.dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching conversation",
        )


@router.post("/gen_title", response_model=GenerateTitleResponse)
async def generate_title(
    request: GenerateTitleRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate a title for a conversation using AI.

    Note: This is a placeholder. Real implementation would:
    1. Get conversation messages
    2. Call AI service to generate title
    3. Cache result in Redis
    4. Return title
    """
    try:
        # TODO: Implement title generation with AI
        # For now, return placeholder
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Title not found or method not implemented for the conversation's endpoint",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating title: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating title",
        )


@router.post("/update", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def update_conversation(
    arg: ConversationUpdate = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a conversation.
    """
    try:
        if not arg.conversationId:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conversationId is required",
            )

        conversation = await ConversationService.create_or_update_conversation(
            user_id=current_user.id,
            data=arg.dict(exclude_unset=True),
        )

        return ConversationResponse(**conversation.dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating conversation",
        )


@router.delete("/", status_code=status.HTTP_201_CREATED)
async def delete_conversations(
    arg: DeleteConversationRequest = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete specific conversation(s).
    """
    try:
        # Validate parameters
        if not any([arg.conversationId, arg.source, arg.thread_id, arg.endpoint]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="no parameters provided",
            )

        if arg.source == "button" and not arg.conversationId:
            return {"message": "No conversationId provided"}

        # TODO: Handle OpenAI thread deletion if endpoint is assistants
        # This would require OpenAI client integration

        result = await ConversationService.delete_conversations(
            user_id=current_user.id,
            conversation_id=arg.conversationId,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting conversations",
        )


@router.delete("/all", status_code=status.HTTP_201_CREATED)
async def delete_all_conversations(
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete all conversations for the current user.
    """
    try:
        result = await ConversationService.delete_conversations(
            user_id=current_user.id,
            conversation_id=None,
        )

        return result

    except Exception as e:
        logger.error(f"Error clearing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing conversations",
        )


@router.post("/fork", response_model=ForkConversationResponse)
async def fork_conversation(
    request: ForkConversationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Fork a conversation from a specific message.

    This creates a new conversation containing messages up to the target message.
    """
    try:
        result = await ConversationService.fork_conversation(
            user_id=current_user.id,
            conversation_id=request.conversationId,
            message_id=request.messageId,
            split_at_target=request.splitAtTarget,
            option=request.option,
            latest_message_id=request.latestMessageId,
        )

        return ForkConversationResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error forking conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error forking conversation",
        )


@router.post("/duplicate", status_code=status.HTTP_201_CREATED)
async def duplicate_conversation(
    request: DuplicateConversationRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Duplicate an entire conversation.
    """
    try:
        result = await ConversationService.duplicate_conversation(
            user_id=current_user.id,
            conversation_id=request.conversationId,
            title=request.title,
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error duplicating conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error duplicating conversation",
        )
