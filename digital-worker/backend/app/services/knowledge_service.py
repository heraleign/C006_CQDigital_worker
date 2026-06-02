"""Knowledge service for root cause case library operations."""
from typing import Any, Optional
from app.config import settings
from app.services.database_service import DatabaseService


class KnowledgeService:
    """Service for knowledge/case library operations."""

    def __init__(self):
        if not settings.USE_MOCK:
            self.mock = DatabaseService()
        else:
            from app.services.mock_data import MockDataService
            self.mock = MockDataService()
        self._cases_cache = None

    @property
    def cases(self):
        if self._cases_cache is None:
            self._cases_cache = self.mock.get_problem_cases(page=1, page_size=200)["items"]
        return self._cases_cache

    def search_cases(self, keyword: str, page=1, page_size=20):
        all_cases = self.mock.get_problem_cases(page=1, page_size=200)["items"]
        filtered = [
            c for c in all_cases
            if keyword.lower() in str(c.get("case_title", "")).lower()
            or keyword.lower() in str(c.get("description", "")).lower()
            or keyword.lower() in str(c.get("tags", "")).lower()
        ]
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "items": filtered[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }

    def get_case(self, case_id: int):
        return self.mock.get_item(self.cases, case_id)
