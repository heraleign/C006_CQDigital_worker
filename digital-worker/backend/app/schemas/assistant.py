from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChatRequest(BaseModel):
    session_id: Optional[int] = None
    message: str
    session_type: str = "general"


class ChatResponse(BaseModel):
    session_id: int
    message_id: int
    reply: str
    tokens_used: Optional[int] = None
    ai_model: Optional[str] = None


class SessionCreate(BaseModel):
    session_title: Optional[str] = None
    session_type: str = "general"


class SessionResponse(BaseModel):
    id: int
    session_title: Optional[str] = None
    session_type: str = "general"
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    message_count: int = 0
    status: str = "active"
    is_pinned: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    content_type: str = "text"
    tokens_used: Optional[int] = None
    ai_model: Optional[str] = None
    message_metadata: Optional[Any] = Field(None, alias="metadata")
    feedback_score: Optional[int] = None
    created_at: Optional[datetime] = None
