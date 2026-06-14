"""Hermes Agent API endpoints.

Provides two sets of endpoints:
1. Simple chat (for the demo playground)
2. Root cause analysis via Hermes (for the smart analysis page)
"""
from fastapi import APIRouter
from app.utils.response import success_response
from app.services.hermes_service import hermes_service

router = APIRouter()


@router.post("/chat")
async def hermes_chat(data: dict):
    """Simple stateless chat with Hermes Agent.

    Accepts:
        {"message": "用户的问题", "system_prompt": "可选系统提示"}
    Returns:
        {"code": 0, "message": "success", "data": {"reply": "..."}}
    """
    reply = await hermes_service.chat(
        message=data.get("message", ""),
        system_prompt=data.get("system_prompt"),
    )
    return success_response(data={"reply": reply})


@router.post("/analyze-root-cause")
async def hermes_root_cause_analysis(data: dict):
    """Root cause analysis via Hermes Agent.

    Hermes autonomously plans the analysis path, invokes skills/tools,
    and returns structured results matching the frontend display format.

    Accepts:
        {
            "task_id": "TASK-001",
            "problem_description": "可选问题描述",
            "acct_month": "可选账期"
        }
    Returns the same structure as the preset analysis data so the
    existing Analysis.tsx and TaskList.tsx can render it directly.
    """
    result = await hermes_service.analyze_root_cause(
        task_id=data.get("task_id", ""),
        problem_description=data.get("problem_description", ""),
        acct_month=data.get("acct_month", ""),
    )
    return success_response(data=result, message="Hermes Agent分析完成")


@router.get("/health")
async def hermes_health():
    """Check Hermes Agent connectivity."""
    try:
        reply = await hermes_service.chat("连通性测试，请回复OK", "你是一个测试助手")
        return success_response(data={
            "status": "ok" if "ok" in reply.lower() else "unknown",
            "reply": reply,
        })
    except Exception as e:
        return success_response(data={
            "status": "error",
            "error": str(e),
        })
