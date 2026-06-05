"""Monthly module API endpoints - 12+ endpoints."""
from fastapi import APIRouter, Query, Path, HTTPException, Depends
from typing import Optional, Any, Dict
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.response import success_response, paginated_response
from app.services.monthly_service import MonthlyService
from app.services.ledger_service import LedgerService
from app.schemas.monthly import (
    OrchestrationTaskCreate, OrchestrationTaskUpdate,
    DailyReportGenerateRequest, DailyReportUpdateRequest,
    BillingTaskCreate, BillingTaskUpdate, BillingTaskStatusUpdate,
    BriefGenerateRequest, ImportBillingTasksRequest,
    ConfigStageCreate, ConfigStageUpdate,
    ConfigMilestoneCreate, ConfigMilestoneUpdate,
    ConfigWorkPlanCreate, ConfigWorkPlanUpdate,
    ConfigTaskCreate, ConfigTaskUpdate,
)

router = APIRouter()
service = MonthlyService()
ledger_service = LedgerService()

# ==================== Field Mapping ====================

_STATUS_MAP = {
    "pending": "未开始", "running": "进行中", "completed": "已完成",
    "failed": "异常", "skipped": "已跳过", "paused": "已暂停", "manual_skipped": "手动跳过",
}

_CYCLE_STATUS_MAP = {
    "pending": "pending", "processing": "processing",
    "completed": "completed", "active": "active",
}


def _transform_billing_task(t: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map backend MaTaskMonitor fields to frontend BillingTask format."""
    if not t:
        return None
    acct_month = (t.get("account_month") or "")
    dep_ids = t.get("dependency_ids")
    if isinstance(dep_ids, list):
        dep_str = ",".join(str(x) for x in dep_ids)
    else:
        dep_str = str(dep_ids) if dep_ids else None

    dur_sec = t.get("expected_duration") or t.get("duration_seconds") or 0
    dur_min = round(dur_sec / 60) if dur_sec else 0

    status_en = t.get("status", "pending")
    status_cn = _STATUS_MAP.get(status_en, status_en)

    return {
        "task_id": t.get("id"),
        "cycle_id": acct_month.replace("-", ""),
        "task_code": t.get("task_code", ""),
        "task_name": t.get("task_name", ""),
        "work_type": t.get("stage_name") or t.get("task_type") or t.get("plan_name") or "",
        "planned_start": (t.get("plan_start_time") or ""),
        "planned_end": (t.get("plan_end_time") or ""),
        "duration_minutes": dur_min,
        "dependency_codes": dep_str,
        "assignee": t.get("owner", ""),
        "status": status_cn,
        "actual_start": (t.get("actual_start_time") or ""),
        "actual_end": (t.get("actual_end_time") or ""),
        "remark": t.get("error_message", ""),
        "priority": t.get("priority", "normal"),
        "progress": t.get("progress", 0),
        "is_critical": t.get("is_critical", False),
    }


# ==================== Progress & Dashboard Endpoints ====================

@router.get("/progress")
async def get_progress(account_month: Optional[str] = None):
    """Get monthly progress."""
    data = service.get_progress(account_month)
    return success_response(data=data)


@router.get("/milestones")
async def get_milestones(account_month: Optional[str] = None):
    """Get monthly milestones."""
    data = service.get_milestones(account_month)
    return success_response(data=data)


@router.get("/running-tasks")
async def get_running_tasks():
    """Get currently running tasks."""
    data = service.get_running_tasks()
    return success_response(data=data)


# ==================== Task Endpoints ====================

@router.get("/tasks")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List monthly tasks."""
    data = service.get_tasks(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.get("/tasks/{task_id}/logs")
async def get_task_logs(task_id: int):
    """Get task execution logs."""
    data = service.get_task_logs(task_id)
    return success_response(data=data)


# ==================== Orchestration Endpoints ====================

@router.get("/orchestration")
async def list_orchestration_redirect():
    """Redirect /orchestration to /orchestration/tasks (frontend compatibility)."""
    from app.utils.response import paginated_response
    data = service.get_orchestration_tasks(page=1, page_size=200)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.get("/orchestration/tasks")
async def list_orchestration_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List orchestration tasks."""
    data = service.get_orchestration_tasks(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/orchestration/tasks")
async def create_orchestration_task(task: OrchestrationTaskCreate):
    """Create orchestration task."""
    data = service.create_orchestration_task(task.model_dump(exclude_unset=True))
    return success_response(data=data, message="任务创建成功")


@router.put("/orchestration/tasks/{task_id}")
async def update_orchestration_task(task_id: int, task: OrchestrationTaskUpdate):
    """Update orchestration task."""
    data = service.update_orchestration_task(task_id, task.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(data=data, message="更新成功")


@router.delete("/orchestration/tasks/{task_id}")
async def delete_orchestration_task(task_id: int):
    """Delete orchestration task."""
    data = service.delete_orchestration_task(task_id)
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(data=data, message="删除成功")


@router.get("/orchestration/gantt")
async def get_gantt():
    """Get Gantt chart data."""
    data = service.get_gantt()
    return success_response(data=data)


@router.get("/orchestration/dag")
async def get_dag():
    """Get DAG visualization data."""
    data = service.get_dag()
    return success_response(data=data)


@router.post("/orchestration/validate")
async def validate_orchestration():
    """Validate orchestration plan."""
    data = service.validate_orchestration()
    return success_response(data=data)


@router.post("/orchestration/generate-plan")
async def generate_plan(request: dict):
    """Generate orchestration plan."""
    data = service.generate_plan(request)
    return success_response(data=data, message="计划生成中")


# ==================== Daily Report Endpoints ====================

@router.post("/daily-report/generate")
async def generate_daily_report(request: DailyReportGenerateRequest):
    """Generate daily report."""
    from app.services.ai_service import ai_service
    ai_content = await ai_service.generate_daily_report(
        str(request.report_date),
        {"tasks": []},
    )
    report = service.create_daily_report({
        "report_date": str(request.report_date),
        "account_month": request.account_month or str(request.report_date)[:7],
        "title": f"{request.report_date} 日报",
        "content": ai_content,
        "summary": ai_content.get("summary", ""),
        "task_completed": ai_content.get("task_completion", {}).get("completed", 0),
        "task_total": ai_content.get("task_completion", {}).get("total", 0),
        "ai_generated": request.ai_generate,
        "status": "draft",
    })
    return success_response(data=report, message="日报生成成功")


@router.get("/daily-report")
@router.get("/daily-report/list")
async def list_daily_reports(
    acct_month: Optional[str] = Query(None, description="账期(YYYY-MM)"),
    report_date: Optional[str] = Query(None, description="报告日期(YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List daily reports with optional filters."""
    data = service.get_daily_reports(page, page_size, acct_month=acct_month, report_date=report_date)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.get("/daily-report/{report_id}")
async def get_daily_report(report_id: int):
    """Get daily report by ID."""
    data = service.get_daily_report(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="日报不存在")
    return success_response(data=data)


@router.put("/daily-report/{report_id}")
async def update_daily_report(report_id: int, request: DailyReportUpdateRequest):
    """Update daily report."""
    data = service.update_daily_report(report_id, request.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="日报不存在")
    return success_response(data=data, message="更新成功")


@router.get("/daily-report/{report_id}/export")
async def export_daily_report(report_id: int, fmt: str = Query("pdf", pattern="^(pdf|docx|html)$")):
    """Export daily report."""
    data = service.export_daily_report(report_id, fmt)
    return success_response(data=data)


# ==================== Summary Report Endpoints ====================

@router.get("/reports/statistics")
async def get_report_statistics():
    """Get report statistics."""
    data = service.get_report_statistics()
    return success_response(data=data)


@router.get("/reports")
async def list_summary_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List summary reports."""
    data = service.get_summary_reports(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.get("/reports/{report_id}")
async def get_summary_report(report_id: int):
    """Get summary report by ID."""
    data = service.get_summary_report(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="报告不存在")
    return success_response(data=data)


@router.post("/reports/{report_id}/publish")
async def publish_report(report_id: int):
    """Publish summary report."""
    data = service.publish_report(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="报告不存在")
    return success_response(data=data, message="发布成功")


@router.post("/reports/{report_id}/republish")
async def republish_report(report_id: int):
    """Republish summary report."""
    data = service.republish_report(report_id)
    if not data:
        raise HTTPException(status_code=404, detail="报告不存在")
    return success_response(data=data, message="重新发布成功")


@router.post("/reports/{report_id}/handle-exception")
async def handle_report_exception(report_id: int, data: dict):
    """Handle exception in report."""
    result = service.handle_exception(report_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="报告不存在")
    return success_response(data=result, message="异常处理成功")


# ==================== Billing Progress Endpoints ====================

@router.get("/billing-progress/cycles")
async def list_billing_cycles():
    """List billing cycles."""
    data = service.get_billing_cycles()
    return success_response(data=data)


@router.get("/billing-progress/gantt")
async def get_billing_progress_gantt(cycle_id: str = Query("202601")):
    """Get billing progress Gantt chart data."""
    data = service.get_billing_progress_gantt(cycle_id)
    tasks = [_transform_billing_task(t) for t in data.get("tasks", []) if t]
    data["tasks"] = tasks
    return success_response(data=data)


@router.get("/billing-progress/tasks")
async def list_billing_progress_tasks(
    cycle_id: str = Query("202601"),
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=500),
):
    """List billing progress tasks (transformed)."""
    data = service.get_billing_progress_tasks(cycle_id, page, page_size)
    return paginated_response(
        [_transform_billing_task(t) for t in data["items"]],
        data["total"], data["page"], data["page_size"],
    )


@router.post("/billing-progress/tasks")
async def create_billing_progress_task(task: BillingTaskCreate):
    """Create billing progress task."""
    data = service.create_billing_progress_task("202605", task.model_dump(exclude_unset=True))
    return success_response(data=data, message="任务创建成功")


@router.put("/billing-progress/tasks/{task_id}/status")
async def update_billing_progress_task_status(task_id: int, update: BillingTaskStatusUpdate):
    """Update billing progress task status."""
    data = service.update_billing_progress_task_status(
        task_id, update.status, actual_end=update.actual_end
    )
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(data=data, message="状态更新成功")


@router.post("/billing-progress/brief")
async def generate_billing_brief(request: BriefGenerateRequest):
    """Generate billing progress brief."""
    data = service.generate_billing_brief(request.cycle_id)
    return success_response(data=data)


@router.put("/billing-progress/tasks/{task_id}")
async def update_billing_progress_task(task_id: int, task: BillingTaskUpdate):
    """Update billing progress task details."""
    data = service.update_billing_progress_task_detail(task_id, task.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(data=data, message="更新成功")


@router.delete("/billing-progress/tasks/{task_id}")
async def delete_billing_progress_task(task_id: int):
    """Delete billing progress task."""
    data = service.delete_billing_progress_task(task_id)
    return success_response(data=data, message="删除成功")


@router.post("/billing-progress/import")
async def import_billing_progress_tasks(request: ImportBillingTasksRequest):
    """Import billing progress tasks from Excel."""
    data = service.import_billing_progress_tasks(
        request.cycle_id, [t.model_dump() for t in request.tasks]
    )
    return success_response(data=data, message=f"成功导入 {data['imported_count']} 条任务")


# ==================== Ledger Overview Endpoints ====================

@router.get("/ledger/overview")
async def get_ledger_overview(
    acct_month: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get full 4-level ledger hierarchy."""
    data = await ledger_service.get_ledger_overview(db, acct_month)
    return success_response(data=data)


# ==================== Config - Stage Endpoints ====================

@router.get("/config/stages")
async def list_config_stages(
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List config stages."""
    data = await ledger_service.list_stages(db, page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/config/stages")
async def create_config_stage(stage: ConfigStageCreate, db: AsyncSession = Depends(get_db)):
    """Create config stage."""
    data = await ledger_service.create_stage(db, stage.model_dump(exclude_unset=True))
    return success_response(data=data, message="阶段创建成功")


@router.get("/config/stages/{stage_id}")
async def get_config_stage(stage_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_db)):
    """Get config stage by ID."""
    data = await ledger_service.get_stage(db, stage_id)
    if not data:
        raise HTTPException(status_code=404, detail="阶段不存在")
    return success_response(data=data)


@router.put("/config/stages/{stage_id}")
async def update_config_stage(
    stage_id: int,
    stage: ConfigStageUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update config stage."""
    data = await ledger_service.update_stage(db, stage_id, stage.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="阶段不存在")
    return success_response(data=data, message="阶段更新成功")


@router.delete("/config/stages/{stage_id}")
async def delete_config_stage(stage_id: int, db: AsyncSession = Depends(get_db)):
    """Delete config stage."""
    data = await ledger_service.delete_stage(db, stage_id)
    if not data:
        raise HTTPException(status_code=404, detail="阶段不存在")
    return success_response(data=data, message="阶段删除成功")


# ==================== Config - Milestone Endpoints ====================

@router.get("/config/milestones")
async def list_config_milestones(
    stage_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List config milestones."""
    data = await ledger_service.list_milestones(db, stage_id, page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/config/milestones")
async def create_config_milestone(
    milestone: ConfigMilestoneCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create config milestone."""
    data = await ledger_service.create_milestone(db, milestone.model_dump(exclude_unset=True))
    return success_response(data=data, message="里程碑创建成功")


@router.get("/config/milestones/{milestone_id}")
async def get_config_milestone(
    milestone_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
):
    """Get config milestone by ID."""
    data = await ledger_service.get_milestone(db, milestone_id)
    if not data:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    return success_response(data=data)


@router.put("/config/milestones/{milestone_id}")
async def update_config_milestone(
    milestone_id: int,
    milestone: ConfigMilestoneUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update config milestone."""
    data = await ledger_service.update_milestone(
        db, milestone_id, milestone.model_dump(exclude_unset=True)
    )
    if not data:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    return success_response(data=data, message="里程碑更新成功")


@router.delete("/config/milestones/{milestone_id}")
async def delete_config_milestone(
    milestone_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete config milestone."""
    data = await ledger_service.delete_milestone(db, milestone_id)
    if not data:
        raise HTTPException(status_code=404, detail="里程碑不存在")
    return success_response(data=data, message="里程碑删除成功")


# ==================== Config - Work Plan Endpoints ====================

@router.get("/config/work-plans")
async def list_config_work_plans(
    milestone_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List config work plans."""
    data = await ledger_service.list_work_plans(db, milestone_id, page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/config/work-plans")
async def create_config_work_plan(
    plan: ConfigWorkPlanCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create config work plan."""
    data = await ledger_service.create_work_plan(db, plan.model_dump(exclude_unset=True))
    return success_response(data=data, message="作业计划创建成功")


@router.get("/config/work-plans/{plan_id}")
async def get_config_work_plan(
    plan_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
):
    """Get config work plan by ID."""
    data = await ledger_service.get_work_plan(db, plan_id)
    if not data:
        raise HTTPException(status_code=404, detail="作业计划不存在")
    return success_response(data=data)


@router.put("/config/work-plans/{plan_id}")
async def update_config_work_plan(
    plan_id: int,
    plan: ConfigWorkPlanUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update config work plan."""
    data = await ledger_service.update_work_plan(
        db, plan_id, plan.model_dump(exclude_unset=True)
    )
    if not data:
        raise HTTPException(status_code=404, detail="作业计划不存在")
    return success_response(data=data, message="作业计划更新成功")


@router.delete("/config/work-plans/{plan_id}")
async def delete_config_work_plan(plan_id: int, db: AsyncSession = Depends(get_db)):
    """Delete config work plan."""
    data = await ledger_service.delete_work_plan(db, plan_id)
    if not data:
        raise HTTPException(status_code=404, detail="作业计划不存在")
    return success_response(data=data, message="作业计划删除成功")


# ==================== Config - Task Endpoints ====================

@router.get("/config/tasks")
async def list_config_tasks(
    plan_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List config tasks."""
    data = await ledger_service.list_tasks(db, plan_id, page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/config/tasks")
async def create_config_task(task: ConfigTaskCreate, db: AsyncSession = Depends(get_db)):
    """Create config task."""
    data = await ledger_service.create_task(db, task.model_dump(exclude_unset=True))
    return success_response(data=data, message="任务创建成功")


@router.get("/config/tasks/{task_id}")
async def get_config_task(
    task_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
):
    """Get config task by ID."""
    data = await ledger_service.get_task(db, task_id)
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(data=data)


@router.put("/config/tasks/{task_code}")
async def update_config_task(
    task_code: str,
    task: ConfigTaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update config task by task_code (string, e.g. TK_0_0_1_3)."""
    data = await ledger_service.update_task_by_code(db, task_code, task.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(data=data, message="任务更新成功")


@router.delete("/config/tasks/{task_id}")
async def delete_config_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Delete config task."""
    data = await ledger_service.delete_task(db, task_id)
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(data=data, message="任务删除成功")


# ==================== Config - Template Parse ====================

@router.post("/config/parse-template")
async def parse_template(data: dict):
    """Parse template string into task list."""
    template = data.get("template", "")
    tasks = []
    if template:
        lines = [line.strip() for line in template.split("\n") if line.strip()]
        for idx, line in enumerate(lines):
            task_type = "MANUAL_OP"
            if line.startswith("[TDP]"):
                task_type = "TDP_TASK"
            elif line.startswith("SQL:") or line.startswith("SELECT") or line.startswith("select"):
                task_type = "SQL_SCRIPT"
            elif "通知" in line or "发布" in line or "消息" in line:
                task_type = "PUBLISH_MSG"
            tasks.append({
                "task_code": f"TK_AUTO_{idx + 1}",
                "task_type": task_type,
                "content": line,
                "sort_order": idx + 1,
                "status": "pending",
            })
    return success_response(data=tasks, message="模板解析成功")
