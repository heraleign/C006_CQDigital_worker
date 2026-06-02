"""Dashboard service wrapping MockDataService."""
from typing import Any
from app.services.mock_data import MockDataService


class DashboardService:
    """Service for dashboard aggregate operations."""

    def __init__(self):
        self.mock = MockDataService()

    def get_summary(self) -> dict:
        return self.mock.get_dashboard_summary()

    def get_trends(self) -> dict:
        return self.mock.get_dashboard_trends()

    def get_recent_alerts(self) -> list:
        return self.mock.get_dashboard_recent_alerts()
