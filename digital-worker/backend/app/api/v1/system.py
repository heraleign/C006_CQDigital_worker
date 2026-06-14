"""System/Settings module API endpoints - 8+ endpoints for tools, prompts, users."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional
from app.utils.response import success_response, paginated_response
from app.config import settings
from app.services.database_service import DatabaseService
from app.schemas.system import (
    UserCreate, UserUpdate, UserResponse,
    ToolConfigCreate, ToolConfigUpdate,
    PromptConfigCreate, PromptConfigUpdate,
)

router = APIRouter()
if not settings.USE_MOCK:
    mock = DatabaseService()
else:
    from app.services.mock_data import MockDataService
    mock = MockDataService()


# ==================== Tools Config Endpoints ====================

@router.get("/tools")
async def list_tools(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List tool configurations."""
    data = mock.get_tool_configs(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/tools")
async def create_tool(config: dict):
    """Create tool configuration."""
    new_item = mock.create_tool(config)
    return success_response(data=new_item, message="技能创建成功")


@router.put("/tools/{tool_id}")
async def update_tool(tool_id: str, config: dict):
    """Update tool configuration."""
    data = mock.update_tool(tool_id, config)
    if not data:
        raise HTTPException(status_code=404, detail="技能不存在")
    return success_response(data=data, message="更新成功")


@router.delete("/tools/{tool_id}")
async def delete_tool(tool_id: str):
    """Delete tool configuration."""
    data = mock.delete_tool(tool_id)
    if not data:
        raise HTTPException(status_code=404, detail="技能不存在")
    return success_response(data=data, message="删除成功")


# ==================== Prompts Config Endpoints ====================

@router.get("/prompts")
async def list_prompts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List prompt configurations."""
    data = mock.get_prompt_configs(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/prompts")
async def create_prompt(config: PromptConfigCreate):
    """Create prompt configuration."""
    prompts = mock.get_prompt_configs(page=1, page_size=200)["items"]
    new_item = mock.create_item(prompts, config.model_dump(exclude_unset=True))
    return success_response(data=new_item, message="提示词配置创建成功")


@router.put("/prompts/{prompt_id}")
async def update_prompt(prompt_id: str, config: PromptConfigUpdate):
    """Update prompt configuration."""
    prompts = mock.get_prompt_configs(page=1, page_size=200)["items"]
    data = mock.update_item(prompts, prompt_id, config.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="提示词配置不存在")
    return success_response(data=data, message="更新成功")


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """Delete prompt configuration."""
    prompts = mock.get_prompt_configs(page=1, page_size=200)["items"]
    data = mock.delete_item(prompts, prompt_id)
    if not data:
        raise HTTPException(status_code=404, detail="提示词配置不存在")
    return success_response(data=data, message="删除成功")


# ==================== Users & Roles Endpoints ====================

@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List system users."""
    data = mock.get_users(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/users")
async def create_user(user: UserCreate):
    """Create system user."""
    users = mock.get_users(page=1, page_size=200)["items"]
    new_user = mock.create_item(users, user.model_dump(exclude_unset=True))
    return success_response(data=new_user, message="用户创建成功")


@router.put("/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    """Update system user."""
    users = mock.get_users(page=1, page_size=200)["items"]
    data = mock.update_item(users, user_id, user.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="用户不存在")
    return success_response(data=data, message="更新成功")


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete system user."""
    users = mock.get_users(page=1, page_size=200)["items"]
    data = mock.delete_item(users, user_id)
    if not data:
        raise HTTPException(status_code=404, detail="用户不存在")
    return success_response(data=data, message="删除成功")


# ==================== Roles Endpoints ====================

@router.get("/roles")
async def list_roles():
    """List system roles."""
    data = mock.get_roles()
    return success_response(data=data)


@router.post("/roles")
async def create_role(data: dict):
    """Create system role."""
    roles = mock.get_roles()
    new_role = mock.create_item(roles, data)
    return success_response(data=new_role, message="角色创建成功")


@router.put("/roles/{role_id}")
async def update_role(role_id: int, data: dict):
    """Update system role."""
    roles = mock.get_roles()
    updated = mock.update_item(roles, role_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="角色不存在")
    return success_response(data=updated, message="更新成功")


@router.delete("/roles/{role_id}")
async def delete_role(role_id: int):
    """Delete system role."""
    roles = mock.get_roles()
    data = mock.delete_item(roles, role_id)
    if not data:
        raise HTTPException(status_code=404, detail="角色不存在")
    return success_response(data=data, message="删除成功")


# ==================== Permissions Endpoints ====================

@router.get("/permissions")
async def list_permissions():
    """List all permissions."""
    data = mock.get_permissions()
    return success_response(data=data)


# ==================== Departments Endpoints ====================

@router.get("/departments")
async def list_departments():
    """List departments."""
    data = mock.get_departments()
    return success_response(data=data)


# ==================== System Config Endpoints ====================

@router.get("/configs")
async def list_system_configs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List system configurations."""
    data = mock.get_system_configs(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


# ==================== Notifications Endpoints ====================

@router.get("/notifications")
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List notifications."""
    data = mock.get_notifications(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


# ==================== Audit Logs Endpoints ====================

@router.get("/audit-logs")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List audit logs."""
    data = mock.get_audit_logs(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


# ==================== Data Dict Endpoints ====================

@router.get("/data-dicts")
async def list_data_dicts(dict_type: Optional[str] = None):
    """List data dictionaries."""
    data = mock.get_data_dicts(dict_type)
    return success_response(data=data)
