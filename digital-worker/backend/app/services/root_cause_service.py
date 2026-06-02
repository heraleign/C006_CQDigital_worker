"""Root cause service wrapping MockDataService."""
from typing import Any, Optional
from app.services.mock_data import MockDataService


class RootCauseService:
    """Service for root cause module operations."""

    def __init__(self):
        self.mock = MockDataService()
        self._cases_cache = None
        self._paths_cache = None
        self._analyses_cache = None

    @property
    def cases(self):
        if self._cases_cache is None:
            self._cases_cache = self.mock.get_problem_cases(page=1, page_size=200)["items"]
        return self._cases_cache

    @property
    def paths(self):
        if self._paths_cache is None:
            self._paths_cache = self.mock.get_analysis_paths(page=1, page_size=200)["items"]
        return self._paths_cache

    @property
    def analyses(self):
        if self._analyses_cache is None:
            self._analyses_cache = self.mock.get_root_cause_analyses(page=1, page_size=200)["items"]
        return self._analyses_cache

    def get_lineage(self, page=1, page_size=20):
        return self.mock.get_task_lineage(page, page_size)

    def batch_import_lineage(self, tasks: list[dict]):
        return {"imported": len(tasks), "status": "success"}

    def get_paths(self, page=1, page_size=20):
        return self.mock.get_analysis_paths(page, page_size)

    def get_path(self, path_id: int):
        return self.mock.get_item(self.paths, path_id)

    def create_path(self, data: dict):
        return self.mock.create_item(self.paths, data)

    def update_path(self, path_id: int, data: dict):
        return self.mock.update_item(self.paths, path_id, data)

    def delete_path(self, path_id: int):
        return self.mock.delete_item(self.paths, path_id)

    def create_analysis(self, data: dict):
        return self.mock.create_item(self.analyses, data)

    def get_analysis(self, analysis_id: int):
        return self.mock.get_item(self.analyses, analysis_id)

    def get_analysis_steps(self, analysis_id: int):
        return self.mock.get_analysis_steps(analysis_id)

    def get_analyses_records(self, page=1, page_size=20):
        return self.mock.get_root_cause_analyses(page, page_size)

    def add_feedback(self, data: dict):
        feedbacks = self.mock.get_user_feedback(page=1, page_size=200)["items"]
        return self.mock.create_item(feedbacks, data)

    def save_as_case(self, analysis_id: int):
        analysis = self.get_analysis(analysis_id)
        if analysis:
            analysis["is_saved_as_case"] = True
            return {"success": True, "case_id": analysis_id}
        return {"success": False}

    def get_cases(self, page=1, page_size=20, **filters):
        return self.mock.get_problem_cases(page, page_size, **filters)

    def get_case(self, case_id: int):
        return self.mock.get_item(self.cases, case_id)

    def create_case(self, data: dict):
        return self.mock.create_item(self.cases, data)

    def update_case(self, case_id: int, data: dict):
        return self.mock.update_item(self.cases, case_id, data)

    def delete_case(self, case_id: int):
        return self.mock.delete_item(self.cases, case_id)

    def get_case_statistics(self):
        return self.mock.get_case_statistics()

    def match_cases(self, problem_description: str, top_k: int = 5):
        from app.services.ai_service import ai_service
        matches = ai_service._mock_case_matching(problem_description, self.cases, top_k)
        return matches

    def get_suggestions(self, page=1, page_size=20):
        return self.mock.get_suggestions(page, page_size)

    def get_suggestion_statistics(self):
        return self.mock.get_suggestion_statistics()

    def generate_suggestions(self, data: dict):
        return {"task_id": f"sug_gen_{hash(str(data)) % 10000}", "status": "completed"}

    def update_suggestion(self, suggestion_id: int, data: dict):
        suggestions = self.mock.get_suggestions(page=1, page_size=200)["items"]
        return self.mock.update_item(suggestions, suggestion_id, data)
