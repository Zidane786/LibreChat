"""
Message service for business logic.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
from beanie.operators import In, Eq
from app.models.message import Message
from app.models.conversation import Conversation
from app.utils.logger import logger


class MessageService:
    """Service for managing messages."""

    @staticmethod
    async def get_messages(
        user_id: str,
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        cursor: Optional[str] = None,
        sort_by: str = "createdAt",
        sort_direction: str = "desc",
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Get messages with pagination.

        Args:
            user_id: User ID
            conversation_id: Optional conversation ID filter
            message_id: Optional specific message ID
            cursor: Pagination cursor
            sort_by: Field to sort by
            sort_direction: Sort direction (asc/desc)
            page_size: Page size

        Returns:
            Dict with messages and nextCursor
        """
        # Validate sort field
        if sort_by not in ["endpoint", "createdAt", "updatedAt"]:
            sort_by = "createdAt"

        sort_order = 1 if sort_direction == "asc" else -1

        # Get specific message
        if conversation_id and message_id:
            message = await Message.find_one(
                Message.conversationId == conversation_id,
                Message.messageId == message_id,
                Message.user == user_id,
            )
            return {
                "messages": [message.dict()] if message else [],
                "nextCursor": None
            }

        # Get conversation messages
        if conversation_id:
            query = Message.find(
                Message.conversationId == conversation_id,
                Message.user == user_id,
            )

            # Apply cursor pagination
            if cursor:
                if sort_direction == "asc":
                    query = query.find({sort_by: {"$gt": cursor}})
                else:
                    query = query.find({sort_by: {"$lt": cursor}})

            # Sort and limit
            query = query.sort((sort_by, sort_order)).limit(page_size + 1)
            messages = await query.to_list()

            # Determine next cursor
            next_cursor = None
            if len(messages) > page_size:
                next_cursor = getattr(messages.pop(), sort_by)

            return {
                "messages": [msg.dict() for msg in messages],
                "nextCursor": next_cursor
            }

        return {"messages": [], "nextCursor": None}

    @staticmethod
    async def create_message(
        user_id: str,
        conversation_id: str,
        data: Dict[str, Any],
    ) -> Message:
        """
        Create a new message.

        Args:
            user_id: User ID
            conversation_id: Conversation ID
            data: Message data

        Returns:
            Created message
        """
        # Generate message ID if not provided
        if "messageId" not in data or not data["messageId"]:
            data["messageId"] = str(uuid.uuid4())

        # Create message
        message = Message(
            user=user_id,
            conversationId=conversation_id,
            **data
        )
        await message.insert()

        logger.info(f"Message created: {message.messageId} in conversation {conversation_id}")
        return message

    @staticmethod
    async def update_message(
        user_id: str,
        message_id: str,
        data: Dict[str, Any],
    ) -> Optional[Message]:
        """
        Update a message.

        Args:
            user_id: User ID
            message_id: Message ID
            data: Update data

        Returns:
            Updated message or None
        """
        message = await Message.find_one(
            Message.messageId == message_id,
            Message.user == user_id,
        )

        if not message:
            return None

        # Update fields
        for key, value in data.items():
            if hasattr(message, key) and value is not None:
                setattr(message, key, value)

        message.updatedAt = datetime.utcnow()
        await message.save()

        logger.info(f"Message updated: {message_id}")
        return message

    @staticmethod
    async def update_message_feedback(
        user_id: str,
        message_id: str,
        feedback: Optional[str],
    ) -> Optional[Message]:
        """
        Update message feedback.

        Args:
            user_id: User ID
            message_id: Message ID
            feedback: Feedback value

        Returns:
            Updated message or None
        """
        message = await Message.find_one(
            Message.messageId == message_id,
            Message.user == user_id,
        )

        if not message:
            return None

        message.feedback = feedback
        message.updatedAt = datetime.utcnow()
        await message.save()

        logger.info(f"Message feedback updated: {message_id}")
        return message

    @staticmethod
    async def delete_message(
        user_id: str,
        message_id: str,
    ) -> bool:
        """
        Delete a message.

        Args:
            user_id: User ID
            message_id: Message ID

        Returns:
            True if deleted, False otherwise
        """
        message = await Message.find_one(
            Message.messageId == message_id,
            Message.user == user_id,
        )

        if not message:
            return False

        await message.delete()
        logger.info(f"Message deleted: {message_id}")
        return True

    @staticmethod
    async def search_messages(
        user_id: str,
        query: str,
    ) -> List[Dict[str, Any]]:
        """
        Search messages using Meilisearch.

        Args:
            user_id: User ID
            query: Search query

        Returns:
            List of search results with conversation data
        """
        # TODO: Implement Meilisearch integration
        # For now, return empty list
        logger.warning("Meilisearch not implemented, returning empty results")
        return []

    @staticmethod
    async def update_artifact(
        user_id: str,
        message_id: str,
        artifact_index: int,
        original: str,
        updated: str,
    ) -> Optional[Message]:
        """
        Update artifact content in a message.

        Args:
            user_id: User ID
            message_id: Message ID
            artifact_index: Artifact index
            original: Original content
            updated: Updated content

        Returns:
            Updated message or None
        """
        message = await Message.find_one(
            Message.messageId == message_id,
            Message.user == user_id,
        )

        if not message:
            return None

        # Find and replace artifact content
        # TODO: Implement artifact finding and replacement logic
        # This requires parsing message content/text for artifact markers

        message.updatedAt = datetime.utcnow()
        await message.save()

        logger.info(f"Artifact updated in message: {message_id}")
        return message
