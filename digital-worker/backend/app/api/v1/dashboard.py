"""Dashboard API endpoints - aggregate overview."""
from fastapi import APIRouter, Query
from app.utils.response import success_response
from app.services.dashboard_service import DashboardService

router = APIRouter()
dashboard_service = DashboardService()


@router.get("/summary")
async def get_summary():
    """Overview stats including progress, alerts, quality score."""
    data = dashboard_service.get_summary()
    return success_response(data=data)


@router.get("/trends")
async def get_trends():
    """Trend data for charts (quality, task, alert trends)."""
    data = dashboard_service.get_trends()
    return success_response(data=data)


@router.get("/recent-alerts")
async def get_recent_alerts(limit: int = Query(default=10, le=50)):
    """Recent alerts list."""
    alerts = dashboard_service.get_recent_alerts()
    return success_response(data=alerts[:limit])
