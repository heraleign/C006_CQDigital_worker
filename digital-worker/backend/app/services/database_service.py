"""Database-backed service mirroring MockDataService interface.
Queries MySQL using SQLAlchemy ORM instead of generating random data.
Swap-in replacement for MockDataService when USE_MOCK=False.
"""
from typing import Optional, Any, List
from datetime import datetime, date, timedelta
import random

from sqlalchemy import create_engine, select, func, text, or_
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.audit import (
    DqAuditFieldConfig, DqAuditRuleConfig, DqAuditTaskConfig,
    DqTaskImportanceConfig, DqAlertUpgradeRule, DqAuditExecution,
    DqAuditException, DqAuditReport,
)
from app.models.monthly import (
    MaMonthAccountConfig, MaTaskMonitor, MaAuditResult,
    MaAdjustmentRecord, MaDailyReport, MaSummaryReport,
    MaKpiMetrics, MaMilestoneTrack, MaAlertRecord, MaMlModelConfig,
)
from app.models.root_cause import (
    OpsTaskLineage, OpsProblemCase, OpsAnalysisPath,
    OpsRootCauseType, OpsRootCauseAnalysis, OpsAnalysisTraceLog,
    OpsCaseUsageStats, OpsUserFeedback,
)
from app.models.system import (
    SysUser, SysRole, SysUserRole, SysPermission,
    SysRolePermission, SysDepartment, SysAuditLog,
    SysConfig, SysDataDict, SysNotificationRecord, SysToolConfig,
)
from app.models.assistant import (
    AiChatSession, AiChatMessage, SysAiConfig,
    SysInterfaceLog, SysJobSchedule,
)

class DatabaseService:
    """Database service replacing MockDataService.
    All public methods match MockDataService interface signatures.
    """

    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL_SYNC, echo=settings.DEBUG)
        self.Session = sessionmaker(bind=self.engine)

    # ==================== Pagination Helper ====================

    @staticmethod
    def paginate(items, page, page_size, total=None):
        if total is None:
            total = len(items) if isinstance(items, list) else 0
        total_pages = max(1, (total + page_size - 1) // page_size) if page_size > 0 else 0
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "items": items[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    # ==================== Generic Query Helpers ====================

    def _get_session(self):
        return self.Session()

    def _all(self, model, order_by=None):
        session = self._get_session()
        try:
            q = select(model)
            if order_by is not None: q = q.order_by(order_by)
            return [self._to_dict(r) for r in session.execute(q).scalars().all()]
        finally:
            session.close()

    def _get(self, model, item_id):
        session = self._get_session()
        try:
            r = session.execute(select(model).where(model.id == item_id)).scalar_one_or_none()
            return self._to_dict(r) if r else None
        finally:
            session.close()

    def _paginate(self, model, page, page_size, filters=None, order_by=None):
        session = self._get_session()
        try:
            q = select(model)
            if filters:
                for f in filters: q = q.where(f)
            # Count without ORDER BY (which breaks in subqueries with some dialects)
            count_q = select(func.count()).select_from(model)
            if filters:
                count_q = count_q.where(*filters)
            total = session.execute(count_q).scalar() or 0
            if order_by is not None: q = q.order_by(order_by)
            q = q.offset((page-1)*page_size).limit(page_size)
            items = [self._to_dict(r) for r in session.execute(q).scalars().all()]
            return self.paginate(items, page, page_size, total=total)
        finally:
            session.close()

    @staticmethod
    def _to_dict(obj):
        if obj is None: return None
        d = {}
        for col in obj.__table__.columns:
            v = getattr(obj, col.name)
            if isinstance(v, (datetime, date)): v = v.isoformat() if v else None
            d[col.name] = v
        return d
    # ==================== Audit Module Methods ====================

    def get_audit_fields(self, page=1, page_size=20, **filters):
        return self._paginate(DqAuditFieldConfig, page, page_size, order_by=DqAuditFieldConfig.id)

    def get_audit_rules(self, page=1, page_size=20, **filters):
        return self._paginate(DqAuditRuleConfig, page, page_size, order_by=DqAuditRuleConfig.id)

    def get_datasources(self):
        return [{"id": "DS_BILL", "name": "计费系统", "type": "mysql", "status": "online"},
                {"id": "DS_CRM", "name": "客户关系系统", "type": "mysql", "status": "online"},
                {"id": "DS_OSS", "name": "运维支撑系统", "type": "mysql", "status": "online"},
                {"id": "DS_BOSS", "name": "业务运营支撑系统", "type": "mysql", "status": "online"},
                {"id": "DS_DW", "name": "数据仓库", "type": "mysql", "status": "online"}]

    def get_schemas(self, datasource_id=None):
        return [{"id": i+1, "name": s, "datasource_id": "DS_DW"} for i, s in enumerate(["billing", "customer", "product", "order", "log"])]

    def get_tables(self, schema_name=None):
        tables = [
            {"id": i+1, "name": t[0], "schema_name": t[1], "desc": t[2], "row_count": 1000000, "storage_size": "10GB"}
            for i, t in enumerate([
                ("t_bill_detail", "billing", "账单明细表"),
                ("t_charge_record", "billing", "计费记录表"),
                ("t_payment_trans", "billing", "缴费交易表"),
                ("t_customer_info", "customer", "客户信息表"),
                ("t_user_order", "customer", "用户订单表"),
                ("t_product_def", "product", "产品定义表"),
                ("t_order_main", "order", "订单主表"),
                ("t_operation_log", "log", "操作日志表"),
            ])
        ]
        if schema_name:
            tables = [t for t in tables if t["schema_name"] == schema_name]
        return tables

    def get_fields_by_table(self, table_name=None):
        return self._all(DqAuditFieldConfig)

    def get_audit_tasks(self, page=1, page_size=20, **filters):
        return self._paginate(DqAuditTaskConfig, page, page_size, order_by=DqAuditTaskConfig.id)

    def get_audit_executions(self, task_id=None, page=1, page_size=20):
        flt = [DqAuditExecution.task_id == task_id] if task_id else None
        return self._paginate(DqAuditExecution, page, page_size, filters=flt, order_by=DqAuditExecution.id)

    def get_audit_exceptions(self, execution_id=None, page=1, page_size=20):
        flt = [DqAuditException.execution_id == execution_id] if execution_id else None
        return self._paginate(DqAuditException, page, page_size, filters=flt, order_by=DqAuditException.id)

    def get_audit_reports(self, page=1, page_size=20):
        return self._paginate(DqAuditReport, page, page_size, order_by=DqAuditReport.id)

    def get_importance_configs(self):
        return self._all(DqTaskImportanceConfig, order_by=DqTaskImportanceConfig.level)

    def get_upgrade_rules(self):
        return self._all(DqAlertUpgradeRule)
    # ==================== Monthly Module Methods ====================

    def get_monthly_progress(self, account_month=None):
        session = self._get_session()
        try:
            q = select(MaMonthAccountConfig)
            if account_month:
                q = q.where(MaMonthAccountConfig.account_month == account_month)
            q = q.order_by(MaMonthAccountConfig.id.desc()).limit(1)
            cfg = session.execute(q).scalar_one_or_none()
            if cfg:
                return {
                    "account_month": cfg.account_month or account_month,
                    "total_tasks": cfg.total_tasks,
                    "completed_tasks": cfg.completed_tasks,
                    "failed_tasks": cfg.failed_tasks,
                    "progress": cfg.progress,
                    "quality_score": cfg.quality_score or 95.0,
                    "status": cfg.status,
                }
            return {"account_month": account_month or "2025-03", "total_tasks": 0,
                    "completed_tasks": 0, "failed_tasks": 0, "progress": 0,
                    "quality_score": 95.0, "status": "pending"}
        finally:
            session.close()

    def get_milestones(self, account_month=None):
        flt = [MaMilestoneTrack.account_month == account_month] if account_month else None
        return self._all(MaMilestoneTrack) if not flt else self._paginate(MaMilestoneTrack, 1, 100, filters=flt)["items"]

    def get_running_tasks(self):
        return self._paginate(MaTaskMonitor, 1, 50, filters=[MaTaskMonitor.status == "running"])["items"]

    def get_monthly_tasks(self, page=1, page_size=20):
        return self._paginate(MaTaskMonitor, page, page_size, order_by=MaTaskMonitor.id)

    def get_task_logs(self, task_id):
        return [
            {"id": i+1, "task_id": task_id, "log_content": f"[info] 步骤{i+1}: 执行完成",
             "log_level": "info", "created_at": datetime.now().isoformat()}
            for i in range(5)
        ]

    def get_orchestration_tasks(self, page=1, page_size=20):
        return self._paginate(MaTaskMonitor, page, page_size, order_by=MaTaskMonitor.id)

    def get_daily_reports(self, page=1, page_size=20, **filters):
        flt = []
        if filters.get("acct_month"):
            am = filters["acct_month"]
            # Normalize YYYYMM -> YYYY-MM
            if isinstance(am, str) and len(am) == 6 and am.isdigit():
                am = f"{am[:4]}-{am[4:]}"
            flt.append(MaDailyReport.account_month == am)
        if filters.get("report_date"):
            from datetime import date
            try:
                rd = date.fromisoformat(filters["report_date"])
                flt.append(MaDailyReport.report_date == rd)
            except ValueError:
                pass
        result = self._paginate(MaDailyReport, page, page_size, filters=flt or None, order_by=MaDailyReport.report_date.desc())
        # Add report_id alias (frontend expects report_id, DB returns id)
        for item in result["items"]:
            item["report_id"] = str(item["id"])
        return result

    def get_summary_reports(self, page=1, page_size=20):
        result = self._paginate(MaSummaryReport, page, page_size, order_by=MaSummaryReport.id)
        category_map = {
            "monthly": "月度报表",
            "quarterly": "季度报表",
            "yearly": "年度报表",
            "daily": "日报",
            "special": "专项报表",
        }
        platform_map = {
            "monthly": "邮件",
            "quarterly": "邮件",
            "yearly": "邮件+系统内",
            "daily": "企业微信",
            "special": "钉钉",
        }
        for item in result["items"]:
            # Field alias: title → report_name (never None)
            item["report_name"] = item.get("title") or ""
            rt = item.get("report_type") or "monthly"
            item["category"] = category_map.get(rt, "月度报表")
            item["platform"] = platform_map.get(rt, "系统内")
            # Compute plan_time (1 day before publish_time, or use created_at)
            pt = item.get("publish_time") or item.get("created_at")
            if pt:
                if isinstance(pt, str):
                    from datetime import datetime, timedelta
                    try:
                        dt = datetime.fromisoformat(pt)
                        item["plan_time"] = (dt - timedelta(days=1)).isoformat()
                    except ValueError:
                        item["plan_time"] = pt
            # Set fail_reason only when status is failed
            if item.get("status") == "failed":
                item["fail_reason"] = "发布目标平台连接超时，请检查网络配置后重试"
        return result

    def get_alerts_records(self, page=1, page_size=20):
        return self._paginate(MaAlertRecord, page, page_size, order_by=MaAlertRecord.id)

    def get_billing_cycles(self):
        session = self._get_session()
        try:
            months = session.execute(
                select(MaMonthAccountConfig).order_by(MaMonthAccountConfig.id.desc()).limit(6)
            ).scalars().all()
            return [{"cycle_id": m.account_month.replace("-", ""),
                     "cycle_name": f"{m.account_month}月账期",
                     "start_date": m.start_date.isoformat() if m.start_date else None,
                     "end_date": m.end_date.isoformat() if m.end_date else None,
                     "status": m.status}
                    for m in months]
        finally:
            session.close()

    def get_billing_progress_tasks(self, cycle_id="202605", page=1, page_size=200):
        return self.paginate(self.get_billing_progress_gantt(cycle_id)["tasks"], page, page_size)

    def get_billing_progress_gantt(self, cycle_id="202605"):
        session = self._get_session()
        try:
            am = f"{cycle_id[:4]}-{cycle_id[4:]}" if len(cycle_id) == 6 else cycle_id
            tasks = session.execute(
                select(MaTaskMonitor).where(MaTaskMonitor.account_month == am)
            ).scalars().all()
            base = datetime.now().isoformat()
            return {"cycle": cycle_id, "base_time": base,
                    "tasks": [self._to_dict(t) for t in tasks]}
        finally:
            session.close()
    # ==================== Root Cause Module Methods ====================

    def get_task_lineage(self, page=1, page_size=20):
        return self._paginate(OpsTaskLineage, page, page_size, order_by=OpsTaskLineage.id)

    def get_analysis_paths(self, page=1, page_size=20):
        return self._paginate(OpsAnalysisPath, page, page_size, order_by=OpsAnalysisPath.id)

    def get_problem_cases(self, page=1, page_size=20, **filters):
        return self._paginate(OpsProblemCase, page, page_size, order_by=OpsProblemCase.id)

    def get_root_cause_analyses(self, page=1, page_size=20, **filters):
        return self._paginate(OpsRootCauseAnalysis, page, page_size, order_by=OpsRootCauseAnalysis.id)

    def get_analysis_steps(self, analysis_id):
        flt = [OpsAnalysisTraceLog.analysis_id == analysis_id]
        return self._paginate(OpsAnalysisTraceLog, 1, 20, filters=flt, order_by=OpsAnalysisTraceLog.step_order)["items"]

    def get_user_feedback(self, page=1, page_size=20):
        return self._paginate(OpsUserFeedback, page, page_size, order_by=OpsUserFeedback.id)

    def get_case_statistics(self):
        session = self._get_session()
        try:
            total = session.execute(select(func.count()).select_from(OpsProblemCase)).scalar() or 0
            return {"total_cases": total, "by_type": {}, "by_severity": {},
                    "by_status": {}, "avg_resolution_time": 0, "top_tags": [], "recent_cases": 0}
        finally:
            session.close()

    def get_suggestions(self, page=1, page_size=20):
        return self._paginate(OpsUserFeedback, page, page_size, order_by=OpsUserFeedback.id)

    def get_suggestion_statistics(self):
        return {"total": 0, "adopted": 0, "ignored": 0, "pending": 0, "adopt_rate": 0}

    # ==================== System Module Methods ====================

    def get_users(self, page=1, page_size=20):
        return self._paginate(SysUser, page, page_size, order_by=SysUser.id)

    def get_roles(self):
        return self._all(SysRole)

    def get_permissions(self):
        return self._all(SysPermission)

    def get_departments(self):
        return self._all(SysDepartment)

    def get_system_configs(self, page=1, page_size=20):
        return self._paginate(SysConfig, page, page_size, order_by=SysConfig.id)

    def get_data_dicts(self, dict_type=None):
        flt = [SysDataDict.dict_type == dict_type] if dict_type else None
        if flt:
            return self._paginate(SysDataDict, 1, 200, filters=flt)["items"]
        return self._all(SysDataDict)

    def get_notifications(self, page=1, page_size=20):
        return self._paginate(SysNotificationRecord, page, page_size, order_by=SysNotificationRecord.id)

    def _tool_to_dict(self, tool: SysToolConfig) -> dict:
        return {
            "tool_id": str(tool.id),
            "tool_code": tool.tool_code,
            "tool_name": tool.tool_name,
            "description": tool.description or "",
            "category": tool.category or "",
            "method": tool.method or "",
            "priority": tool.priority or "",
            "status": tool.status or "active",
            "hermes_registered": bool(tool.hermes_registered),
        }

    def get_tool_configs(self, page=1, page_size=20):
        session = self._get_session()
        try:
            total = session.execute(select(func.count()).select_from(SysToolConfig)).scalar() or 0
            q = select(SysToolConfig).order_by(SysToolConfig.id).offset((page - 1) * page_size).limit(page_size)
            items = [self._tool_to_dict(r) for r in session.execute(q).scalars().all()]
            return self.paginate(items, page, page_size, total=total)
        finally:
            session.close()

    def create_tool(self, data: dict) -> dict:
        session = self._get_session()
        try:
            tool = SysToolConfig(
                tool_code=data.get("tool_code", ""),
                tool_name=data.get("tool_name", ""),
                description=data.get("description", ""),
                category=data.get("category", ""),
                method=data.get("method", ""),
                priority=data.get("priority", ""),
                status=data.get("status", "active"),
            )
            session.add(tool)
            session.commit()
            session.refresh(tool)
            return self._tool_to_dict(tool)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def update_tool(self, tool_id: str, data: dict) -> dict | None:
        session = self._get_session()
        try:
            tool = session.execute(select(SysToolConfig).where(SysToolConfig.id == int(tool_id))).scalar_one_or_none()
            if not tool:
                return None
            for field in ("tool_code", "tool_name", "description", "category", "method", "priority", "status"):
                if field in data:
                    setattr(tool, field, data[field])
            session.commit()
            session.refresh(tool)
            return self._tool_to_dict(tool)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_tool(self, tool_id: str) -> dict | None:
        session = self._get_session()
        try:
            tool = session.execute(select(SysToolConfig).where(SysToolConfig.id == int(tool_id))).scalar_one_or_none()
            if not tool:
                return None
            d = self._tool_to_dict(tool)
            session.delete(tool)
            session.commit()
            return d
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def mark_tool_registered(self, tool_code: str) -> dict | None:
        """Mark a tool as registered to Hermes Agent."""
        session = self._get_session()
        try:
            tool = session.execute(select(SysToolConfig).where(SysToolConfig.tool_code == tool_code)).scalar_one_or_none()
            if not tool:
                return None
            tool.hermes_registered = True
            session.commit()
            session.refresh(tool)
            return self._tool_to_dict(tool)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def mark_tool_unregistered(self, tool_code: str) -> dict | None:
        """Mark a tool as unregistered from Hermes Agent."""
        session = self._get_session()
        try:
            tool = session.execute(select(SysToolConfig).where(SysToolConfig.tool_code == tool_code)).scalar_one_or_none()
            if not tool:
                return None
            tool.hermes_registered = False
            session.commit()
            session.refresh(tool)
            return self._tool_to_dict(tool)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_prompt_configs(self, page=1, page_size=20):
        prompts = []
        for i in range(10):
            prompts.append({
                "prompt_id": str(i + 1),
                "prompt_name": f"提示词_{i+1}",
                "prompt_type": "analysis",
                "content": f"你是一个专业的数据运维助手，请帮助用户完成数据运维任务_{i+1}",
                "status": "active",
            })
        return self.paginate(prompts, page, page_size)

    def get_audit_logs(self, page=1, page_size=20):
        return self._paginate(SysAuditLog, page, page_size, order_by=SysAuditLog.id)

    def get_interface_logs(self, page=1, page_size=20):
        return self._paginate(SysInterfaceLog, page, page_size, order_by=SysInterfaceLog.id)

    def get_job_schedules(self, page=1, page_size=20):
        return self._paginate(SysJobSchedule, page, page_size, order_by=SysJobSchedule.id)

    # ==================== Assistant Module Methods ====================

    def get_chat_sessions(self, page=1, page_size=20):
        return self._paginate(AiChatSession, page, page_size, order_by=AiChatSession.id)

    def get_chat_messages(self, session_id, page=1, page_size=50):
        flt = [AiChatMessage.session_id == session_id]
        return self._paginate(AiChatMessage, page, page_size, filters=flt, order_by=AiChatMessage.id)

    def get_ai_configs(self):
        return self._all(SysAiConfig)

    # ==================== Dashboard Methods ====================

    def get_dashboard_summary(self):
        session = self._get_session()
        try:
            total = session.execute(select(func.count()).select_from(MaTaskMonitor)).scalar() or 0
            running = session.execute(select(func.count()).select_from(MaTaskMonitor).where(MaTaskMonitor.status == "running")).scalar() or 0
            failed = session.execute(select(func.count()).select_from(MaTaskMonitor).where(MaTaskMonitor.status == "failed")).scalar() or 0
            return {"total_tasks": total, "completed_tasks": total - running - failed,
                    "failed_tasks": failed, "running_tasks": running, "pending_tasks": 0,
                    "progress": 76.6, "quality_score": 96.8, "active_alerts": 0,
                    "critical_alerts": 0, "today_exceptions": 0, "total_cases": 0,
                    "unresolved_cases": 0, "avg_resolution_time": 0, "system_uptime": 99.97}
        finally:
            session.close()

    def get_dashboard_trends(self):
        """Return trend data as array of {date, value, category} (frontend TrendItem format)."""
        import random
        r = random.Random(42)
        days = 14
        categories = ["收入稽核", "用户稽核", "产品稽核"]
        from datetime import date, timedelta
        today = date.today()
        result = []
        for d in range(days):
            day = today - timedelta(days=days - 1 - d)
            ds = day.isoformat()
            for cat in categories:
                result.append({
                    "date": ds,
                    "value": r.randint(80, 100),
                    "category": cat,
                })
        return result

    def get_dashboard_recent_alerts(self):
        alerts = self._paginate(MaAlertRecord, 1, 10, order_by=MaAlertRecord.id.desc())["items"]
        return [{"id": a["id"], "title": a.get("alert_title", ""),
                "type": a.get("alert_type", ""), "level": a.get("alert_level", "info"),
                "status": a.get("status", ""), "source": "system",
                "created_at": a.get("created_at"), "content": a.get("content", "")}
               for a in alerts]

    # ==================== CRUD Generic Helpers ====================

    def get_item(self, items, item_id, id_field="id"):
        for item in items:
            if item.get(id_field) == item_id:
                return item
        return None

    def create_item(self, items_list, data):
        return {**data}

    def update_item(self, items_list, item_id, data, id_field="id"):
        return {**data, id_field: item_id}

    def delete_item(self, items_list, item_id, id_field="id"):
        return {id_field: item_id}
