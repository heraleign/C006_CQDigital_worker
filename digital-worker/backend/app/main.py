"""FastAPI application entry point."""
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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
    description="Data Operations Digital Employee Platform API",
    lifespan=lifespan,
)

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
