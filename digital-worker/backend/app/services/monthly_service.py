"""Monthly service wrapping MockDataService."""
from typing import Any, Optional
from datetime import date
from app.config import settings
from app.services.database_service import DatabaseService


class MonthlyService:
    """Service for monthly module operations."""

    def __init__(self):
        if not settings.USE_MOCK:
            self.mock = DatabaseService()
        else:
            from app.services.mock_data import MockDataService
            self.mock = MockDataService()
        self._tasks_cache = None
        self._reports_cache = None

    @property
    def orchestration_tasks(self):
        if self._tasks_cache is None:
            data = self.mock.get_orchestration_tasks(page=1, page_size=200)
            self._tasks_cache = data["items"]
        return self._tasks_cache

    @property
    def daily_reports(self):
        if self._reports_cache is None:
            data = self.mock.get_daily_reports(page=1, page_size=200)
            self._reports_cache = data["items"]
        return self._reports_cache

    def get_progress(self, account_month=None):
        return self.mock.get_monthly_progress(account_month)

    def get_milestones(self, account_month=None):
        return self.mock.get_milestones(account_month)

    def get_running_tasks(self):
        return self.mock.get_running_tasks()

    def get_tasks(self, page=1, page_size=20):
        return self.mock.get_monthly_tasks(page, page_size)

    def get_task_logs(self, task_id: int):
        return self.mock.get_task_logs(task_id)

    def get_orchestration_tasks(self, page=1, page_size=20):
        return self.mock.get_orchestration_tasks(page, page_size)

    def create_orchestration_task(self, data: dict):
        return self.mock.create_item(self.orchestration_tasks, data)

    def update_orchestration_task(self, task_id: int, data: dict):
        return self.mock.update_item(self.orchestration_tasks, task_id, data)

    def delete_orchestration_task(self, task_id: int):
        return self.mock.delete_item(self.orchestration_tasks, task_id)

    def get_gantt(self):
        return self.mock.get_gantt_data()

    def get_dag(self):
        return self.mock.get_dag_data()

    def validate_orchestration(self):
        return {"is_valid": True, "issues": [], "warnings": [{"message": "任务依赖可能存在环路"}]}

    def generate_plan(self, data: dict):
        return {"task_id": f"plan_{hash(str(data)) % 10000}", "status": "completed", "tasks": []}

    def get_daily_reports(self, page=1, page_size=20, **filters):
        return self.mock.get_daily_reports(page, page_size, **filters)

    def get_daily_report(self, report_id: int):
        return self.mock.get_item(self.daily_reports, report_id)

    def create_daily_report(self, data: dict):
        return self.mock.create_item(self.daily_reports, data)

    def update_daily_report(self, report_id: int, data: dict):
        return self.mock.update_item(self.daily_reports, report_id, data)

    def export_daily_report(self, report_id: int, fmt: str = "pdf"):
        return {"url": f"/exports/daily_report_{report_id}.{fmt}", "format": fmt}

    def get_summary_reports(self, page=1, page_size=20):
        return self.mock.get_summary_reports(page, page_size)

    def get_summary_report(self, report_id: int):
        reports = self.mock.get_summary_reports(page=1, page_size=200)["items"]
        return self.mock.get_item(reports, report_id)

    def publish_report(self, report_id: int):
        report = self.get_summary_report(report_id)
        if report:
            report["status"] = "published"
            report["publisher"] = "系统管理员"
            from datetime import datetime
            report["publish_time"] = datetime.now().isoformat()
        return report

    def republish_report(self, report_id: int):
        report = self.get_summary_report(report_id)
        if report:
            report["status"] = "published"
            from datetime import datetime
            report["publish_time"] = datetime.now().isoformat()
        return report

    def handle_exception(self, report_id: int, data: dict):
        report = self.get_summary_report(report_id)
        if report:
            report["exception_flag"] = True
            report["exception_detail"] = data.get("detail", "已处理")
        return report

    def get_report_statistics(self):
        return {"total_reports": 24, "published": 18, "draft": 6,
                "with_exception": 3, "by_month": {"2025-01": 4, "2025-02": 4, "2025-03": 4, "2025-04": 4}}

    # ==================== Billing Progress Methods ====================

    def get_billing_cycles(self):
        return self.mock.get_billing_cycles()

    def get_billing_progress_gantt(self, cycle_id="202601"):
        return self.mock.get_billing_progress_gantt(cycle_id)

    def get_billing_progress_tasks(self, cycle_id="202601", page=1, page_size=200):
        return self.mock.get_billing_progress_tasks(cycle_id, page, page_size)

    def create_billing_progress_task(self, cycle_id, data):
        return self.mock.create_billing_progress_task(cycle_id, data)

    def update_billing_progress_task(self, task_id, data):
        return self.mock.update_billing_progress_task(task_id, data)

    def update_billing_progress_task_status(self, task_id, status, actual_end=None):
        return self.mock.update_billing_progress_task_status(task_id, status, actual_end)

    def generate_billing_brief(self, cycle_id="202601"):
        return self.mock.generate_billing_brief(cycle_id)

    def update_billing_progress_task_detail(self, task_id, data):
        return self.mock.update_billing_progress_task_detail(task_id, data)

    def delete_billing_progress_task(self, task_id):
        return self.mock.delete_billing_progress_task(task_id)

    def import_billing_progress_tasks(self, cycle_id, tasks_data):
        return self.mock.import_billing_progress_tasks(cycle_id, tasks_data)
