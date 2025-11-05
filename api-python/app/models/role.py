"""Role and permission models"""
from typing import Optional
from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel, ASCENDING


class PermissionSet(BaseModel):
    """Permission set for a specific resource type"""
    use: Optional[bool] = Field(default=None, description="Use permission")
    create: Optional[bool] = Field(default=None, description="Create permission")
    update: Optional[bool] = Field(default=None, description="Update permission")
    read: Optional[bool] = Field(default=None, description="Read permission")
    delete: Optional[bool] = Field(default=None, description="Delete permission")
    shared_global: Optional[bool] = Field(default=None, description="Access shared global resources")
    opt_out: Optional[bool] = Field(default=None, description="Opt out permission")
    view_users: Optional[bool] = Field(default=None, description="View users")
    view_groups: Optional[bool] = Field(default=None, description="View groups")
    view_roles: Optional[bool] = Field(default=None, description="View roles")


class RolePermissions(BaseModel):
    """All permissions for a role"""
    bookmarks: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    prompts: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    memories: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    agents: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    multi_convo: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    temporary_chat: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    run_code: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    web_search: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    people_picker: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    marketplace: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    file_search: Optional[PermissionSet] = Field(default_factory=PermissionSet)
    file_citations: Optional[PermissionSet] = Field(default_factory=PermissionSet)


class Role(Document):
    """Role document model for RBAC"""
    name: str = Field(..., description="Role name")
    permissions: RolePermissions = Field(default_factory=RolePermissions, description="Role permissions")

    class Settings:
        name = "roles"
        indexes = [
            IndexModel([("name", ASCENDING)], unique=True),
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "USER",
                "permissions": {
                    "prompts": {"use": True, "create": True},
                    "agents": {"use": True, "create": False}
                }
            }
        }
