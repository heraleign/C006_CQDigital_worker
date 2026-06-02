"""Assistant service for chat and session management."""
from typing import Any, Optional
from datetime import datetime
from app.services.mock_data import MockDataService
from app.services.ai_service import ai_service


class AssistantService:
    """Service for assistant module operations."""

    def __init__(self):
        self.mock = MockDataService()
        self._sessions_cache = None

    @property
    def sessions(self):
        if self._sessions_cache is None:
            data = self.mock.get_chat_sessions(page=1, page_size=200)
            self._sessions_cache = data["items"]
        return self._sessions_cache

    async def chat(self, session_id: Optional[int], message: str, session_type: str = "general"):
        if not session_id:
            session = self.mock.create_item(self.sessions, {
                "session_title": message[:50],
                "session_type": session_type,
                "user_id": 1,
                "user_name": "管理员",
                "context_summary": "",
                "message_count": 1,
                "status": "active",
                "is_pinned": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            })
            session_id = session["id"]

        # Get AI response
        ai_result = await ai_service.chat_completion(
            messages=[{"role": "user", "content": message}]
        )

        try:
            reply = ai_result["choices"][0]["message"]["content"]
            tokens = ai_result["usage"]["total_tokens"]
        except (KeyError, IndexError):
            reply = "您好，我是数据运维数字员工助手。请描述您的问题，我将为您提供帮助。"
            tokens = 0

        msg_id = hash(f"{session_id}_{datetime.now()}") % 1000000
        # Update session
        session = self.mock.get_item(self.sessions, session_id)
        if session:
            session["message_count"] = session.get("message_count", 0) + 1
            session["updated_at"] = datetime.now().isoformat()

        return {
            "session_id": session_id,
            "message_id": abs(msg_id),
            "reply": reply,
            "tokens_used": tokens,
            "ai_model": "gpt-4",
        }

    def get_sessions(self, page=1, page_size=20):
        return self.mock.get_chat_sessions(page, page_size)

    def create_session(self, data: dict):
        return self.mock.create_item(self.sessions, {
            **data,
            "user_id": 1,
            "user_name": "管理员",
            "message_count": 0,
            "status": "active",
            "is_pinned": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        })

    def delete_session(self, session_id: int):
        return self.mock.delete_item(self.sessions, session_id)

    def get_messages(self, session_id: int, page=1, page_size=50):
        return self.mock.get_chat_messages(session_id, page, page_size)
