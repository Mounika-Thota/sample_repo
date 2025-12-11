from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class CategoryEnum(str, Enum):
    usg = "usg"
    testing = "testing"
    api_doc_testing = "api_doc_testing"
    performance_testing = "performance_testing"
    deployment = "deployment"


class AgentBase(BaseModel):
    slug: str
    display_name: str
    category: CategoryEnum
    description: str | None = None
    parent_id: str | None = None


class AgentCreate(AgentBase):
    parent_id: str | None = None


class AgentUpdate(BaseModel):
    slug: str | None = None
    display_name: str | None = None
    category: CategoryEnum | None = None
    description: str | None = None
    parent_id: str | None = None


class AgentOut(AgentBase):
    id: str
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None = None
    parent_id: str | None = None

    class Config:
        from_attributes = True
