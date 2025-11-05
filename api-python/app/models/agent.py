"""Agent model"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING, DESCENDING
from bson import ObjectId


class Agent(Document):
    """Agent document model"""
    id: str = Field(..., description="Unique agent ID")
    name: Optional[str] = Field(default=None, description="Agent name")
    description: Optional[str] = Field(default=None, description="Agent description")
    instructions: Optional[str] = Field(default=None, description="Agent instructions")

    # Avatar
    avatar: Optional[Dict[str, Any]] = Field(default=None, description="Avatar configuration")

    # Model configuration
    provider: str = Field(..., description="AI provider")
    model: str = Field(..., description="Model name")
    model_parameters: Optional[Dict[str, Any]] = Field(default=None, description="Model parameters")

    # Agent configuration
    artifacts: Optional[str] = Field(default=None, description="Artifacts configuration")
    access_level: Optional[int] = Field(default=None, description="Access level")
    recursion_limit: Optional[int] = Field(default=None, description="Recursion limit")

    # Tools and actions
    tools: Optional[List[str]] = Field(default=None, description="Enabled tools")
    tool_kwargs: Optional[List[Dict[str, Any]]] = Field(default=None, description="Tool keyword arguments")
    actions: Optional[List[str]] = Field(default=None, description="Enabled actions")

    # Authorship
    author: ObjectId = Field(..., description="Author user ID")
    author_name: Optional[str] = Field(default=None, description="Author name")

    # Behavior settings
    hide_sequential_outputs: Optional[bool] = Field(default=None, description="Hide sequential outputs")
    end_after_tools: Optional[bool] = Field(default=None, description="End after tools")

    # Collaboration
    agent_ids: Optional[List[str]] = Field(default=None, description="Collaborative agent IDs")
    is_collaborative: Optional[bool] = Field(default=None, description="Is collaborative agent")

    # Conversation starters
    conversation_starters: List[str] = Field(default_factory=list, description="Conversation starters")

    # Tool resources
    tool_resources: Dict[str, Any] = Field(default_factory=dict, description="Tool resources")

    # Project association
    project_ids: Optional[List[ObjectId]] = Field(default=None, description="Associated project IDs")

    # Versioning
    versions: List[Dict[str, Any]] = Field(default_factory=list, description="Agent versions")

    # Categorization
    category: str = Field(default="general", description="Agent category")

    # Support and promotion
    support_contact: Optional[Dict[str, Any]] = Field(default=None, description="Support contact info")
    is_promoted: bool = Field(default=False, description="Is promoted agent")

    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "agents"
        indexes = [
            IndexModel([("id", ASCENDING)], unique=True),
            IndexModel([("author", ASCENDING)]),
            IndexModel([("project_ids", ASCENDING)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("is_promoted", ASCENDING)]),
            IndexModel([("updated_at", DESCENDING), ("_id", ASCENDING)]),
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "agent-123",
                "name": "My Assistant",
                "provider": "openai",
                "model": "gpt-4",
                "description": "A helpful AI assistant"
            }
        }
