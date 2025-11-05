"""
Conversation service for business logic.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
from beanie import PydanticObjectId
from beanie.operators import In, Eq
from app.models.conversation import Conversation
from app.models.message import Message
from app.utils.logger import logger


class ConversationService:
    """Service for managing conversations."""

    @staticmethod
    async def get_conversations(
        user_id: str,
        cursor: Optional[str] = None,
        limit: int = 25,
        is_archived: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
        order: str = "desc",
    ) -> Dict[str, Any]:
        """
        Get conversations with pagination and filters.

        Args:
            user_id: User ID
            cursor: Pagination cursor
            limit: Results limit
            is_archived: Filter by archive status
            tags: Filter by tags
            search: Search query
            order: Sort order (asc/desc)

        Returns:
            Dict with conversations and pagination info
        """
        query = Conversation.find(Conversation.user == user_id)

        # Apply filters
        if is_archived is not None:
            query = query.find(Conversation.isArchived == is_archived)

        if tags:
            query = query.find(In(Conversation.tags, tags))

        if search:
            # Simple title search (can be enhanced with Meilisearch)
            query = query.find({"title": {"$regex": search, "$options": "i"}})

        # Apply cursor pagination
        if cursor:
            try:
                cursor_id = PydanticObjectId(cursor)
                if order == "asc":
                    query = query.find({"_id": {"$gt": cursor_id}})
                else:
                    query = query.find({"_id": {"$lt": cursor_id}})
            except Exception:
                logger.warning(f"Invalid cursor: {cursor}")

        # Sort
        sort_direction = 1 if order == "asc" else -1
        query = query.sort([("createdAt", sort_direction)])

        # Fetch with limit + 1 to check for more pages
        conversations = await query.limit(limit + 1).to_list()

        # Calculate pagination
        has_more = len(conversations) > limit
        if has_more:
            conversations = conversations[:limit]

        next_cursor = str(conversations[-1].id) if has_more and conversations else None

        return {
            "conversations": [conv.dict() for conv in conversations],
            "pageNumber": 1,
            "pageSize": limit,
            "pages": 1,
            "nextCursor": next_cursor,
        }

    @staticmethod
    async def get_conversation(
        user_id: str,
        conversation_id: str,
    ) -> Optional[Conversation]:
        """
        Get a specific conversation.

        Args:
            user_id: User ID
            conversation_id: Conversation ID

        Returns:
            Conversation or None
        """
        return await Conversation.find_one(
            Conversation.conversationId == conversation_id,
            Conversation.user == user_id,
        )

    @staticmethod
    async def create_or_update_conversation(
        user_id: str,
        data: Dict[str, Any],
    ) -> Conversation:
        """
        Create or update a conversation.

        Args:
            user_id: User ID
            data: Conversation data

        Returns:
            Conversation
        """
        conversation_id = data.get("conversationId")

        if conversation_id:
            # Update existing conversation
            conversation = await Conversation.find_one(
                Conversation.conversationId == conversation_id,
                Conversation.user == user_id,
            )

            if conversation:
                # Update fields
                for key, value in data.items():
                    if hasattr(conversation, key) and key != "conversationId":
                        setattr(conversation, key, value)

                conversation.updatedAt = datetime.utcnow()
                await conversation.save()
                logger.info(f"Conversation updated: {conversation_id}")
                return conversation

        # Create new conversation
        if not conversation_id:
            data["conversationId"] = str(uuid.uuid4())

        conversation = Conversation(
            user=user_id,
            **data
        )
        await conversation.insert()

        logger.info(f"Conversation created: {conversation.conversationId}")
        return conversation

    @staticmethod
    async def delete_conversations(
        user_id: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Delete conversations.

        Args:
            user_id: User ID
            conversation_id: Optional specific conversation ID

        Returns:
            Deletion result
        """
        if conversation_id:
            # Delete specific conversation
            conversation = await Conversation.find_one(
                Conversation.conversationId == conversation_id,
                Conversation.user == user_id,
            )

            if conversation:
                # Delete associated messages
                await Message.find(
                    Message.conversationId == conversation_id,
                    Message.user == user_id,
                ).delete()

                await conversation.delete()
                logger.info(f"Conversation deleted: {conversation_id}")
                return {"deleted": 1, "conversationId": conversation_id}

            return {"deleted": 0}
        else:
            # Delete all conversations
            delete_result = await Conversation.find(
                Conversation.user == user_id
            ).delete()

            # Delete all messages
            await Message.find(Message.user == user_id).delete()

            logger.info(f"All conversations deleted for user: {user_id}")
            return {"deleted": delete_result.deleted_count}

    @staticmethod
    async def fork_conversation(
        user_id: str,
        conversation_id: str,
        message_id: str,
        split_at_target: bool = False,
        option: Optional[str] = None,
        latest_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fork a conversation from a specific message.

        Args:
            user_id: User ID
            conversation_id: Source conversation ID
            message_id: Target message ID to fork from
            split_at_target: Whether to split at target
            option: Fork option
            latest_message_id: Latest message ID

        Returns:
            Forked conversation data
        """
        # Get source conversation
        source_conv = await Conversation.find_one(
            Conversation.conversationId == conversation_id,
            Conversation.user == user_id,
        )

        if not source_conv:
            raise ValueError("Source conversation not found")

        # Get messages up to target
        messages = await Message.find(
            Message.conversationId == conversation_id,
            Message.user == user_id,
        ).sort("createdAt", 1).to_list()

        # Find target message index
        target_index = next(
            (i for i, msg in enumerate(messages) if msg.messageId == message_id),
            None
        )

        if target_index is None:
            raise ValueError("Target message not found")

        # Determine which messages to copy
        if split_at_target:
            messages_to_copy = messages[:target_index + 1]
        else:
            messages_to_copy = messages[:target_index]

        # Create new conversation
        new_conv_id = str(uuid.uuid4())
        new_conv = Conversation(
            user=user_id,
            conversationId=new_conv_id,
            title=f"{source_conv.title} (forked)",
            endpoint=source_conv.endpoint,
            model=source_conv.model,
            agentOptions=source_conv.agentOptions,
        )
        await new_conv.insert()

        # Copy messages
        new_message_ids = []
        for msg in messages_to_copy:
            new_msg_id = str(uuid.uuid4())
            new_msg = Message(
                user=user_id,
                conversationId=new_conv_id,
                messageId=new_msg_id,
                parentMessageId=msg.parentMessageId,
                text=msg.text,
                content=msg.content,
                endpoint=msg.endpoint,
                model=msg.model,
                isCreatedByUser=msg.isCreatedByUser,
            )
            await new_msg.insert()
            new_message_ids.append(new_msg_id)

        logger.info(f"Conversation forked: {conversation_id} -> {new_conv_id}")

        return {
            "conversationId": new_conv_id,
            "title": new_conv.title,
            "messages": new_message_ids,
        }

    @staticmethod
    async def duplicate_conversation(
        user_id: str,
        conversation_id: str,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Duplicate an entire conversation.

        Args:
            user_id: User ID
            conversation_id: Source conversation ID
            title: Optional new title

        Returns:
            Duplicated conversation data
        """
        # Get source conversation
        source_conv = await Conversation.find_one(
            Conversation.conversationId == conversation_id,
            Conversation.user == user_id,
        )

        if not source_conv:
            raise ValueError("Source conversation not found")

        # Get all messages
        messages = await Message.find(
            Message.conversationId == conversation_id,
            Message.user == user_id,
        ).sort("createdAt", 1).to_list()

        # Create new conversation
        new_conv_id = str(uuid.uuid4())
        new_conv = Conversation(
            user=user_id,
            conversationId=new_conv_id,
            title=title or f"{source_conv.title} (copy)",
            endpoint=source_conv.endpoint,
            model=source_conv.model,
            agentOptions=source_conv.agentOptions,
        )
        await new_conv.insert()

        # Copy all messages
        for msg in messages:
            new_msg = Message(
                user=user_id,
                conversationId=new_conv_id,
                messageId=str(uuid.uuid4()),
                parentMessageId=msg.parentMessageId,
                text=msg.text,
                content=msg.content,
                endpoint=msg.endpoint,
                model=msg.model,
                isCreatedByUser=msg.isCreatedByUser,
                tokenCount=msg.tokenCount,
            )
            await new_msg.insert()

        logger.info(f"Conversation duplicated: {conversation_id} -> {new_conv_id}")

        return {
            "conversationId": new_conv_id,
            "title": new_conv.title,
            "messageCount": len(messages),
        }
