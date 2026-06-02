"""Assistant module API endpoints - 5 endpoints."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional
from app.utils.response import success_response, paginated_response
from app.services.assistant_service import AssistantService
from app.schemas.assistant import ChatRequest, SessionCreate

router = APIRouter()
service = AssistantService()


@router.post("/chat")
async def chat(request: ChatRequest):
    """Send chat message to AI assistant."""
    result = await service.chat(
        session_id=request.session_id,
        message=request.message,
        session_type=request.session_type,
    )
    return success_response(data=result)


@router.get("/sessions")
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List chat sessions."""
    data = service.get_sessions(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/sessions")
async def create_session(session: SessionCreate):
    """Create a new chat session."""
    data = service.create_session(session.model_dump(exclude_unset=True))
    return success_response(data=data, message="会话创建成功")


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Get messages for a session."""
    data = service.get_messages(session_id, page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int):
    """Delete a chat session."""
    data = service.delete_session(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="会话不存在")
    return success_response(data=data, message="会话删除成功")
