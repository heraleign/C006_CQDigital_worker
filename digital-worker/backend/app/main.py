"""FastAPI application entry point."""
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.utils.logger import logger
from app.utils.response import error_response, server_error_response
from app.api.v1.router import api_v1_router

# Frontend dist path
FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"
INDEX_HTML = FRONTEND_DIST / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Mock mode: {settings.USE_MOCK}")
    if INDEX_HTML.exists():
        logger.info(f"Serving frontend from {FRONTEND_DIST}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="数据运维数字员工平台 — 数据质量稽核、根因分析、月账监控一体化运维平台",
    lifespan=lifespan,
    contact={
        "name": "CQ Digital Worker Team",
        "email": "support@example.com",
    },
    license_info={
        "name": "Proprietary",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="数据运维数字员工平台 API",
        version=settings.APP_VERSION,
        description="""# 数据运维数字员工平台

## 模块概览

| 模块 | 路径 | 说明 |
|------|------|------|
| 📊 Dashboard | `/api/v1/dashboard` | 首页看板：任务概览、质量评分、趋势图表 |
| 🔍 Audit | `/api/v1/audit` | 数据质量稽核：指标配置、AI规则生成、规则确认、告警管理、结果查看 |
| 🧬 Root Cause | `/api/v1/root-cause` | 根因分析：智能分析、知识库、任务诊断、案例库 |
| 📅 Monthly | `/api/v1/monthly` | 月账监控：进度跟踪、任务监控、日报报告 |
| 🤖 Assistant | `/api/v1/assistant` | AI助手：对话会话、消息管理 |
| ⚙️ Settings | `/api/v1/settings` | 系统设置：用户管理、角色权限、配置管理 |

## 运行模式

- **USE_MOCK=true**: 后端 Mock 模式，无需数据库
- **USE_MOCK=false**: 数据库模式，需 MySQL + 种子数据（当前模式）
""",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": ""
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.error(f"[{request_id}] Unhandled error: {e}")
        return JSONResponse(
            status_code=500,
            content=server_error_response(message=str(e)).model_dump(),
        )


# Include routers (API routes take precedence)
app.include_router(api_v1_router)


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mock_mode": settings.USE_MOCK,
    }

# Serve frontend static files (SPA: all non-API routes serve index.html)
if INDEX_HTML.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend SPA - all non-API routes return index.html."""
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(INDEX_HTML))
