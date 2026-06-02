"""Audit service wrapping MockDataService for all audit-related operations."""
from typing import Any, Optional
from app.config import settings
from app.services.database_service import DatabaseService


class AuditService:
    """Service for audit module operations."""

    def __init__(self):
        if not settings.USE_MOCK:
            self.mock = DatabaseService()
        else:
            from app.services.mock_data import MockDataService
            self.mock = MockDataService()
        self._fields_cache = None
        self._rules_cache = None
        self._tasks_cache = None
        self._reports_cache = None

    @property
    def fields(self):
        if self._fields_cache is None:
            self._fields_cache = self.mock.get_audit_fields(page=1, page_size=200)["items"]
        return self._fields_cache

    @property
    def rules(self):
        if self._rules_cache is None:
            self._rules_cache = self.mock.get_audit_rules(page=1, page_size=200)["items"]
        return self._rules_cache

    @property
    def tasks(self):
        if self._tasks_cache is None:
            self._tasks_cache = self.mock.get_audit_tasks(page=1, page_size=200)["items"]
        return self._tasks_cache

    @property
    def reports(self):
        if self._reports_cache is None:
            self._reports_cache = self.mock.get_audit_reports(page=1, page_size=200)["items"]
        return self._reports_cache

    def get_fields(self, page=1, page_size=20, **filters):
        return self.mock.get_audit_fields(page, page_size, **filters)

    def get_field(self, field_id: int):
        return self.mock.get_item(self.fields, field_id)

    def create_field(self, data: dict):
        return self.mock.create_item(self.fields, data)

    def update_field(self, field_id: int, data: dict):
        return self.mock.update_item(self.fields, field_id, data)

    def delete_field(self, field_id: int):
        return self.mock.delete_item(self.fields, field_id)

    def get_rules(self, page=1, page_size=20, **filters):
        return self.mock.get_audit_rules(page, page_size, **filters)

    def get_rule(self, rule_id: int):
        return self.mock.get_item(self.rules, rule_id)

    def create_rule(self, data: dict):
        return self.mock.create_item(self.rules, data)

    def update_rule(self, rule_id: int, data: dict):
        return self.mock.update_item(self.rules, rule_id, data)

    def delete_rule(self, rule_id: int):
        return self.mock.delete_item(self.rules, rule_id)

    def get_datasources(self):
        return self.mock.get_datasources()

    def get_schemas(self, datasource_id=None):
        return self.mock.get_schemas(datasource_id)

    def get_tables(self, schema_name=None):
        return self.mock.get_tables(schema_name)

    def get_fields_by_table(self, table_name=None):
        return self.mock.get_fields_by_table(table_name)

    def get_tasks(self, page=1, page_size=20, **filters):
        return self.mock.get_audit_tasks(page, page_size, **filters)

    def get_task(self, task_id: int):
        return self.mock.get_item(self.tasks, task_id)

    def create_task(self, data: dict):
        return self.mock.create_item(self.tasks, data)

    def delete_task(self, task_id: int):
        return self.mock.delete_item(self.tasks, task_id)

    def get_executions(self, task_id=None, page=1, page_size=20):
        return self.mock.get_audit_executions(task_id, page, page_size)

    def get_exceptions(self, execution_id=None, page=1, page_size=20):
        return self.mock.get_audit_exceptions(execution_id, page, page_size)

    def get_alerts(self, page=1, page_size=20):
        return self.mock.get_audit_exceptions(None, page, page_size)

    def handle_alert(self, alert_id: int, data: dict):
        alerts = self.mock.get_audit_exceptions(page=1, page_size=200)["items"]
        return self.mock.update_item(alerts, alert_id, data)

    def get_reports(self, page=1, page_size=20):
        return self.mock.get_audit_reports(page, page_size)

    def get_report(self, report_id: int):
        return self.mock.get_item(self.reports, report_id)

    def create_report(self, data: dict):
        return self.mock.create_item(self.reports, data)

    def get_importance_configs(self):
        return self.mock.get_importance_configs()

    def create_importance_config(self, data: dict):
        configs = self.mock.get_importance_configs()
        return self.mock.create_item(configs, data)

    def update_importance_config(self, config_id: int, data: dict):
        configs = self.mock.get_importance_configs()
        return self.mock.update_item(configs, config_id, data)

    def delete_importance_config(self, config_id: int):
        configs = self.mock.get_importance_configs()
        return self.mock.delete_item(configs, config_id)

    def get_upgrade_rules(self):
        return self.mock.get_upgrade_rules()

    def create_upgrade_rule(self, data: dict):
        rules = self.mock.get_upgrade_rules()
        return self.mock.create_item(rules, data)

    def update_upgrade_rule(self, rule_id: int, data: dict):
        rules = self.mock.get_upgrade_rules()
        return self.mock.update_item(rules, rule_id, data)

    def delete_upgrade_rule(self, rule_id: int):
        rules = self.mock.get_upgrade_rules()
        return self.mock.delete_item(rules, rule_id)

    def get_statistics(self):
        execs = self.mock.get_audit_executions(page=1, page_size=200)["items"]
        exceptions = self.mock.get_audit_exceptions(page=1, page_size=200)["items"]
        total_ex = len(execs)
        total_exc = len(exceptions)
        avg_pass = sum(e.get("pass_rate", 0) for e in execs) / total_ex if total_ex > 0 else 0
        active_alerts = len([e for e in exceptions if e.get("status") == "open"])
        by_severity = {}
        by_type = {}
        for e in exceptions:
            sev = e.get("severity", "medium")
            by_severity[sev] = by_severity.get(sev, 0) + 1
            tp = e.get("exception_type", "其他")
            by_type[tp] = by_type.get(tp, 0) + 1
        return {
            "total_executions": total_ex,
            "total_exceptions": total_exc,
            "avg_pass_rate": round(avg_pass, 2),
            "total_tasks": len(self.tasks),
            "active_alerts": active_alerts,
            "by_severity": by_severity,
            "by_type": by_type,
        }

    def get_trend(self):
        execs = self.mock.get_audit_executions(page=1, page_size=200)["items"][:30]
        dates = []
        rates = []
        counts = []
        for e in execs:
            dates.append(str(e.get("execute_time", ""))[:10])
            rates.append(e.get("pass_rate", 100))
            counts.append(e.get("failed_records", 0))
        return {"dates": dates, "pass_rates": rates, "exception_counts": counts}

    def get_distribution(self):
        exceptions = self.mock.get_audit_exceptions(page=1, page_size=200)["items"]
        by_type = {}
        by_severity = {}
        by_table = {}
        by_status = {}
        for e in exceptions:
            tp = e.get("exception_type", "其他")
            by_type[tp] = by_type.get(tp, 0) + 1
            sev = e.get("severity", "medium")
            by_severity[sev] = by_severity.get(sev, 0) + 1
            tbl = e.get("table_name", "unknown")
            by_table[tbl] = by_table.get(tbl, 0) + 1
            st = e.get("status", "open")
            by_status[st] = by_status.get(st, 0) + 1
        return {"by_type": by_type, "by_severity": by_severity, "by_table": by_table, "by_status": by_status}
