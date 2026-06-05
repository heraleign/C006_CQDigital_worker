"""Central router that includes all v1 routers."""
from fastapi import APIRouter
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.audit import router as audit_router
from app.api.v1.root_cause import router as root_cause_router
from app.api.v1.monthly import router as monthly_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.system import router as system_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(
    dashboard_router, prefix="/dashboard",
    tags=["📊 Dashboard — 首页看板"],
)
api_v1_router.include_router(
    audit_router, prefix="/audit",
    tags=["🔍 Audit — 数据质量稽核"],
)
api_v1_router.include_router(
    root_cause_router, prefix="/root-cause",
    tags=["🧬 Root Cause — 根因分析"],
)
api_v1_router.include_router(
    monthly_router, prefix="/monthly",
    tags=["📅 Monthly — 月账监控"],
)
api_v1_router.include_router(
    assistant_router, prefix="/assistant",
    tags=["🤖 Assistant — AI助手"],
)
api_v1_router.include_router(
    system_router, prefix="/settings",
    tags=["⚙️ Settings — 系统设置"],
)
