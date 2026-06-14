"""Hermes Agent API endpoints.

Provides:
1. Simple chat (for the demo playground)
2. Root cause analysis via Hermes (for the smart analysis page)
3. Skill execution — Hermes calls individual skills by code
4. Project registration — register all skills as a project in Hermes
"""
from fastapi import APIRouter
from app.utils.response import success_response
from app.config import settings
from app.services.hermes_service import hermes_service
from app.services.skill_engine import skill_engine

if not settings.USE_MOCK:
    from app.services.database_service import DatabaseService
    tool_db = DatabaseService()
else:
    from app.services.mock_data import MockDataService
    tool_db = MockDataService()

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
    """Root cause analysis via Hermes Agent (async).

    Submits the analysis task to a background worker and returns
    immediately with a task_id. Poll GET /hermes/analysis/{task_id}
    for the completed result.

    Accepts:
        {
            "task_id": "TASK-001",
            "problem_description": "可选问题描述",
            "acct_month": "可选账期"
        }
    Returns:
        {"task_id": "ASYNC_1_...", "status": "processing"}
    """
    task_ref = data.get("task_id", "") or data.get("problem_description", "unknown")
    task_id = await hermes_service.start_async_analysis(
        task_ref=task_ref,
        problem_description=data.get("problem_description", ""),
        acct_month=data.get("acct_month", ""),
    )
    return success_response(data={
        "task_id": task_id,
        "status": "processing",
        "message": "分析任务已提交，请稍后查询结果",
    }, message="分析任务已提交")


@router.get("/analysis/{task_id}")
async def get_analysis_status(task_id: str):
    """Get the status and result of an async analysis task.

    - While processing: {"status": "processing", "progress": 45}
    - When completed: {"status": "completed", "result": {...}}
    - When failed: {"status": "failed", "error": "..."}
    """
    task = hermes_service.get_analysis_result(task_id)
    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="分析任务不存在")
    return success_response(data=task)


@router.post("/execute-skill")
async def execute_skill(data: dict):
    """Execute a registered skill by its code.

    Hermes Agent calls this during root cause analysis to invoke
    individual skills (data source APIs). Currently returns mock data;
    in production it routes to the real backend.

    Accepts:
        {
            "skill_code": "rca/task/trace",
            "params": {"task_id": "TASK-001"}
        }
    Returns:
        {"success": true, "data": {...}}
    """
    result = skill_engine.execute(
        skill_code=data.get("skill_code", ""),
        params=data.get("params", {}),
    )
    return success_response(data=result)


@router.get("/project/definition")
async def get_project_definition():
    """Get the full project definition for Hermes Agent.

    Returns all 46 skills as OpenAI-compatible function tools,
    grouped by category, ready to be registered in Hermes.
    """
    return success_response(data=hermes_service.get_project_definition())


@router.get("/project/skills")
async def get_project_skills():
    """Get all skills as OpenAI-compatible function tool definitions."""
    return success_response(data={
        "project": "CQ数据运维数字员工",
        "total_skills": len(hermes_service.get_skill_tools_json()),
        "tools": hermes_service.get_skill_tools_json(),
    })


@router.get("/profile/{profile_name}")
async def get_profile(profile_name: str):
    """Get skills for a named Hermes profile.

    Built-in profiles:
    - ``cqdigitalworker`` — 根因分析 (rca/* + ops/*) = 15 skills

    Returns OpenAI-compatible function tools that can be registered
    as a Hermes agent profile.
    """
    tools = hermes_service.get_profile_skills(profile_name)
    return success_response(data={
        "profile": profile_name,
        "total_skills": len(tools),
        "tools": tools,
        "execute_endpoint": "/api/v1/hermes/execute-skill",
    })


@router.post("/register-skill")
async def register_skill(data: dict):
    """Register a single skill as a callable tool in Hermes Agent.

    Accepts:
        {"skill_code": "rca/task/trace"}

    Builds the OpenAI function tool definition for this skill and sends
    it to Hermes so it becomes a callable tool in Hermes's toolset.
    Also persists the registration status in the database.
    """
    skill_code = data.get("skill_code", "")
    result = await hermes_service.register_skill_to_hermes(skill_code)
    if result.get("success"):
        tool_db.mark_tool_registered(skill_code)
    return success_response(data=result)


@router.post("/unregister-skill")
async def unregister_skill(data: dict):
    """Unregister a skill from Hermes Agent.

    Accepts:
        {"skill_code": "rca/task/trace"}

    Removes the tool registration from Hermes and clears the
    hermes_registered flag in the database.
    """
    skill_code = data.get("skill_code", "")
    tool_db.mark_tool_unregistered(skill_code)
    return success_response(data={
        "success": True,
        "skill_code": skill_code,
    })


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
