from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# --- User ---
class UserCreate(BaseModel):
    username: str
    password: str = Field(default="123456", min_length=6)
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    position: Optional[str] = None
    role_ids: Optional[list[int]] = None
    remark: Optional[str] = None


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[int] = None
    position: Optional[str] = None
    status: Optional[int] = None
    role_ids: Optional[list[int]] = None
    remark: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    position: Optional[str] = None
    status: int = 1
    is_admin: bool = False
    roles: Optional[list[dict]] = None
    last_login_time: Optional[datetime] = None
    remark: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Role ---
class RoleCreate(BaseModel):
    role_name: str
    role_code: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[list[int]] = None


class RoleUpdate(RoleCreate):
    role_name: Optional[str] = None


class RoleResponse(BaseModel):
    id: int
    role_name: str
    role_code: Optional[str] = None
    description: Optional[str] = None
    status: int = 1
    permissions: Optional[list[dict]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Permission ---
class PermissionResponse(BaseModel):
    id: int
    permission_name: str
    permission_code: Optional[str] = None
    menu_path: Optional[str] = None
    parent_id: Optional[int] = None
    permission_type: str = "menu"
    icon: Optional[str] = None
    sort_order: int = 0
    description: Optional[str] = None
    status: int = 1
    children: Optional[list["PermissionResponse"]] = None
    created_at: Optional[datetime] = None


# --- Department ---
class DepartmentResponse(BaseModel):
    id: int
    dept_name: str
    dept_code: Optional[str] = None
    parent_id: Optional[int] = None
    dept_level: int = 1
    dept_type: Optional[str] = None
    manager: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    sort_order: int = 0
    status: int = 1
    children: Optional[list["DepartmentResponse"]] = None
    created_at: Optional[datetime] = None


# --- Config ---
class SystemConfigCreate(BaseModel):
    config_key: str
    config_value: str
    config_type: Optional[str] = "system"
    description: Optional[str] = None
    is_encrypted: bool = False


class SystemConfigUpdate(SystemConfigCreate):
    config_key: Optional[str] = None


class SystemConfigResponse(BaseModel):
    id: int
    config_key: str
    config_value: Optional[str] = None
    config_type: str = "system"
    description: Optional[str] = None
    is_encrypted: bool = False
    status: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Data Dict ---
class DataDictResponse(BaseModel):
    id: int
    dict_key: Optional[str] = None
    dict_value: str
    dict_type: str
    parent_id: Optional[int] = None
    sort_order: int = 0
    status: int = 1
    remark: Optional[str] = None
    created_at: Optional[datetime] = None


# --- Notification ---
class NotificationResponse(BaseModel):
    id: int
    notification_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    receiver_id: Optional[int] = None
    receiver_name: Optional[str] = None
    channel: Optional[str] = None
    is_read: bool = False
    read_time: Optional[datetime] = None
    status: str = "sent"
    send_time: Optional[datetime] = None
    created_at: Optional[datetime] = None


# --- Prompt Config (Tool/Prompt management) ---
class ToolConfigCreate(BaseModel):
    config_name: str
    config_code: Optional[str] = None
    config_type: str = "tool"
    config_value: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Any] = None


class ToolConfigUpdate(ToolConfigCreate):
    config_name: Optional[str] = None


class ToolConfigResponse(BaseModel):
    id: int
    config_name: str
    config_code: Optional[str] = None
    config_type: str
    config_value: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Any] = None
    status: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
