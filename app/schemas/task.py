
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# 1. Task lifecycle
class TaskStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


# 2. Shared validation configuration
class SchemaBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


# 3. Request: Create a new task
class TaskCreate(SchemaBase):
    title: str = Field(min_length=1, max_length=255)


# 4. Request: Publish task progress
class TaskContextUpdate(SchemaBase):
    status: TaskStatus

    completed_steps: list[str] = Field(
        default_factory=list,
    )

    current_step: str | None = None
    next_step: str | None = None

    updated_by: str = Field(
        min_length=1,
        max_length=100,
    )


# 5. Response: Complete task state
class TaskStateResponse(SchemaBase):
    task_id: UUID
    title: str
    status: TaskStatus

    completed_steps: list[str]
    current_step: str | None
    next_step: str | None

    updated_by: str
    version: int

    updated_at: datetime
