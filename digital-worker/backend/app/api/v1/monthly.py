"""Monthly module API endpoints - 12+ endpoints."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional
from datetime import date
from app.utils.response import success_response, paginated_response
from app.services.monthly_service import MonthlyService
from app.schemas.monthly import (
    OrchestrationTaskCreate, OrchestrationTaskUpdate,
    DailyReportGenerateRequest, DailyReportUpdateRequest,
    BillingTaskCreate, BillingTaskUpdate, BillingTaskStatusUpdate,
    BriefGenerateRequest, ImportBillingTasksRequest,
)

router = APIRouter()
service = MonthlyService()


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


@router.get("/daily-report/list")
async def list_daily_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List daily reports."""
    data = service.get_daily_reports(page, page_size)
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
    return success_response(data=data)


@router.get("/billing-progress/tasks")
async def list_billing_progress_tasks(
    cycle_id: str = Query("202601"),
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=500),
):
    """List billing progress tasks."""
    data = service.get_billing_progress_tasks(cycle_id, page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


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
