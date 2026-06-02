"""Dashboard service wrapping MockDataService."""
from typing import Any
from app.config import settings
from app.services.database_service import DatabaseService


class DashboardService:
    """Service for dashboard aggregate operations."""

    def __init__(self):
        if not settings.USE_MOCK:
            self.mock = DatabaseService()
        else:
            from app.services.mock_data import MockDataService
            self.mock = MockDataService()

    def get_summary(self) -> dict:
        return self.mock.get_dashboard_summary()

    def get_trends(self) -> dict:
        return self.mock.get_dashboard_trends()

    def get_recent_alerts(self) -> list:
        return self.mock.get_dashboard_recent_alerts()
