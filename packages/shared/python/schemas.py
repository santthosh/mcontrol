"""
Auto-generated Pydantic models from TypeScript Zod schemas.
DO NOT EDIT MANUALLY - run 'pnpm generate:pydantic' to regenerate.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# Enums

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AutonomyLevel(str, Enum):
    """Level of autonomy for AI agents."""
    SUPERVISED = "supervised"
    SEMI = "semi"
    AUTONOMOUS = "autonomous"


class Provider(str, Enum):
    """LLM Provider."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    CUSTOM = "custom"


class CredentialType(str, Enum):
    """Credential type."""
    API_KEY = "api_key"
    OAUTH = "oauth"
    SERVICE_ACCOUNT = "service_account"


# Schemas

class Task(BaseModel):
    """Task schema - represents a unit of work for an AI agent."""
    id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus
    team_member_id: UUID = Field(..., alias="teamMemberId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    started_at: datetime | None = Field(None, alias="startedAt")
    completed_at: datetime | None = Field(None, alias="completedAt")
    metadata: dict[str, Any] | None = None

    class Config:
        populate_by_name = True


class TeamMember(BaseModel):
    """Team Member schema - represents an AI agent configuration."""
    id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    model_id: UUID = Field(..., alias="modelId")
    autonomy_level: AutonomyLevel = Field(..., alias="autonomyLevel")
    system_prompt: str | None = Field(None, alias="systemPrompt")
    tools: list[str] = Field(default_factory=list)
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True


class Model(BaseModel):
    """Model schema - represents an LLM model configuration."""
    id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    provider: Provider
    model_id: str = Field(..., min_length=1, alias="modelId")
    max_tokens: int = Field(4096, gt=0, alias="maxTokens")
    temperature: float = Field(1.0, ge=0, le=2)
    credential_id: UUID | None = Field(None, alias="credentialId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True


class Credential(BaseModel):
    """Credential schema - represents stored API credentials."""
    id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    type: CredentialType
    provider: Provider
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True


class UserSettings(BaseModel):
    """User Settings schema."""
    id: UUID
    user_id: UUID = Field(..., alias="userId")
    theme: str = Field("system", pattern="^(light|dark|system)$")
    default_autonomy_level: AutonomyLevel = Field(
        AutonomyLevel.SUPERVISED, alias="defaultAutonomyLevel"
    )
    notifications_enabled: bool = Field(True, alias="notificationsEnabled")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True


class HealthResponse(BaseModel):
    """API Health Response."""
    status: str = Field(..., pattern="^(ok|error)$")
    version: str
