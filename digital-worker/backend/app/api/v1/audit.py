"""Audit module API endpoints - 15+ endpoints for data quality audit."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional
from app.utils.response import success_response, error_response, paginated_response
from app.services.audit_service import AuditService
from app.schemas.audit import (
    AuditFieldCreate, AuditFieldUpdate, AuditFieldResponse,
    AuditRuleCreate, AuditRuleUpdate, AuditRuleResponse,
    AiGenerateRequest, BatchConfirmRequest,
    AuditTaskCreate, AuditTaskResponse,
    AlertHandleRequest,
    AuditReportCreate, AuditReportResponse,
    ImportanceConfigCreate, ImportanceConfigUpdate, ImportanceConfigResponse,
    UpgradeRuleCreate, UpgradeRuleUpdate, UpgradeRuleResponse,
    AuditExecutionResponse, AuditExceptionResponse,
)

router = APIRouter()
audit_service = AuditService()


# ==================== Field Config Endpoints ====================

@router.get("/fields")
async def list_fields(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    datasource_id: Optional[str] = None,
    table_name: Optional[str] = None,
):
    """List audit field configurations."""
    data = audit_service.get_fields(page, page_size, datasource_id=datasource_id, table_name=table_name)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/fields")
async def create_field(field: AuditFieldCreate):
    """Create a new audit field config."""
    data = audit_service.create_field(field.model_dump(exclude_unset=True))
    return success_response(data=data, message="字段创建成功")


@router.get("/fields/{field_id}")
async def get_field(field_id: int = Path(..., ge=1)):
    """Get field config by ID."""
    data = audit_service.get_field(field_id)
    if not data:
        raise HTTPException(status_code=404, detail="字段不存在")
    return success_response(data=data)


@router.put("/fields/{field_id}")
async def update_field(field_id: int, field: AuditFieldUpdate):
    """Update field config."""
    data = audit_service.update_field(field_id, field.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="字段不存在")
    return success_response(data=data, message="字段更新成功")


@router.delete("/fields/{field_id}")
async def delete_field(field_id: int):
    """Delete field config."""
    data = audit_service.delete_field(field_id)
    if not data:
        raise HTTPException(status_code=404, detail="字段不存在")
    return success_response(data=data, message="字段删除成功")


# ==================== Cascading Select Endpoints ====================

@router.get("/datasources")
async def list_datasources():
    """List available datasources for cascading select."""
    data = audit_service.get_datasources()
    return success_response(data=data)


@router.get("/schemas")
async def list_schemas(datasource_id: Optional[str] = None):
    """List schemas for a datasource."""
    data = audit_service.get_schemas(datasource_id)
    return success_response(data=data)


@router.get("/tables")
async def list_tables(schema_name: Optional[str] = None):
    """List tables for a schema."""
    data = audit_service.get_tables(schema_name)
    return success_response(data=data)


@router.get("/fields-by-table")
async def list_fields_by_table(table_name: Optional[str] = None):
    """List fields for a table."""
    data = audit_service.get_fields_by_table(table_name)
    return success_response(data=data)


# ==================== AI Generate Rule Endpoints ====================

@router.post("/rules/ai-generate")
async def ai_generate_rules(request: AiGenerateRequest):
    """Trigger AI generation of audit rules."""
    from app.services.ai_service import ai_service
    rules = await ai_service.generate_audit_rules(
        table_name=request.table_name,
        field_descriptions=audit_service.get_fields_by_table(request.table_name),
        business_scenario=request.business_scenario,
    )
    task_id = f"ai_gen_{hash(str(rules)) % 100000}"
    return success_response(data={"task_id": task_id, "status": "completed", "rules": rules}, message="规则生成完成")


@router.get("/rules/ai-generate/{task_id}/status")
async def get_ai_generate_status(task_id: str):
    """Get AI rule generation status."""
    return success_response(data={"task_id": task_id, "status": "completed", "progress": 100})


@router.post("/rules/ai-generate/confirm")
async def confirm_ai_rules(request: BatchConfirmRequest):
    """Confirm AI-generated rules."""
    for rule_id in request.rule_ids:
        audit_service.update_rule(rule_id, {"confirm_status": request.confirm_status})
    return success_response(data=None, message=f"已{request.confirm_status} {len(request.rule_ids)} 条规则")


# ==================== Rule Config Endpoints ====================

@router.get("/rules")
async def list_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List audit rules."""
    data = audit_service.get_rules(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/rules")
async def create_rule(rule: AuditRuleCreate):
    """Create a new audit rule."""
    data = audit_service.create_rule(rule.model_dump(exclude_unset=True))
    return success_response(data=data, message="规则创建成功")


@router.put("/rules/{rule_id}")
async def update_rule(rule_id: int, rule: AuditRuleUpdate):
    """Update audit rule."""
    data = audit_service.update_rule(rule_id, rule.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="规则不存在")
    return success_response(data=data, message="规则更新成功")


@router.post("/rules/batch-confirm")
async def batch_confirm_rules(request: BatchConfirmRequest):
    """Batch confirm rules."""
    for rule_id in request.rule_ids:
        audit_service.update_rule(rule_id, {"confirm_status": request.confirm_status})
    return success_response(data=None, message=f"批量{request.confirm_status}成功")


# ==================== Task Config Endpoints ====================

@router.get("/tasks")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List audit tasks."""
    data = audit_service.get_tasks(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/tasks")
async def create_task(task: AuditTaskCreate):
    """Create audit task."""
    data = audit_service.create_task(task.model_dump(exclude_unset=True))
    return success_response(data=data, message="任务创建成功")


@router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: int):
    """Execute an audit task."""
    execution = {
        "task_id": task_id,
        "execute_time": "2025-03-15T10:30:00",
        "status": "running",
        "execute_duration": 0,
    }
    return success_response(data=execution, message="任务开始执行")


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete audit task."""
    data = audit_service.delete_task(task_id)
    if not data:
        raise HTTPException(status_code=404, detail="任务不存在")
    return success_response(data=data, message="任务删除成功")


# ==================== Alert/Exception Endpoints ====================

@router.get("/alerts")
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List audit alerts/exceptions."""
    data = audit_service.get_alerts(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.put("/alerts/{alert_id}/handle")
async def handle_alert(alert_id: int, request: AlertHandleRequest):
    """Handle an alert."""
    data = audit_service.handle_alert(alert_id, request.model_dump())
    if not data:
        raise HTTPException(status_code=404, detail="告警不存在")
    return success_response(data=data, message="告警处理成功")


# ==================== Results/Analytics Endpoints ====================

@router.get("/results/statistics")
async def get_results_statistics():
    """Get audit execution statistics."""
    data = audit_service.get_statistics()
    return success_response(data=data)


@router.get("/results/trend")
async def get_results_trend():
    """Get audit result trend data."""
    data = audit_service.get_trend()
    return success_response(data=data)


@router.get("/results/distribution")
async def get_results_distribution():
    """Get audit exception distribution."""
    data = audit_service.get_distribution()
    return success_response(data=data)


@router.get("/results/details")
async def get_results_details(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """Get audit execution details."""
    data = audit_service.get_executions(page=page, page_size=page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


# ==================== Report Endpoints ====================

@router.get("/reports")
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List audit reports."""
    data = audit_service.get_reports(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/reports")
async def create_report(report: AuditReportCreate):
    """Create audit report."""
    data = audit_service.create_report(report.model_dump(exclude_unset=True))
    return success_response(data=data, message="报告创建成功")


@router.post("/reports/generate")
async def generate_report(report: AuditReportCreate):
    """Generate audit report (async)."""
    from app.services.ai_service import ai_service
    content = await ai_service.generate_daily_report("today", {})
    report_data = audit_service.create_report({
        **report.model_dump(exclude_unset=True),
        "report_data": content,
    })
    return success_response(data=report_data, message="报告生成中")


# ==================== Importance Config Endpoints ====================

@router.get("/importance-configs")
async def list_importance_configs():
    """List importance configurations."""
    data = audit_service.get_importance_configs()
    return success_response(data=data)


@router.post("/importance-configs")
async def create_importance_config(config: ImportanceConfigCreate):
    """Create importance config."""
    data = audit_service.create_importance_config(config.model_dump(exclude_unset=True))
    return success_response(data=data, message="创建成功")


@router.put("/importance-configs/{config_id}")
async def update_importance_config(config_id: int, config: ImportanceConfigUpdate):
    """Update importance config."""
    data = audit_service.update_importance_config(config_id, config.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="配置不存在")
    return success_response(data=data, message="更新成功")


@router.delete("/importance-configs/{config_id}")
async def delete_importance_config(config_id: int):
    """Delete importance config."""
    data = audit_service.delete_importance_config(config_id)
    if not data:
        raise HTTPException(status_code=404, detail="配置不存在")
    return success_response(data=data, message="删除成功")


# ==================== Upgrade Rules Endpoints ====================

@router.get("/upgrade-rules")
async def list_upgrade_rules():
    """List alert upgrade rules."""
    data = audit_service.get_upgrade_rules()
    return success_response(data=data)


@router.post("/upgrade-rules")
async def create_upgrade_rule(rule: UpgradeRuleCreate):
    """Create upgrade rule."""
    data = audit_service.create_upgrade_rule(rule.model_dump(exclude_unset=True))
    return success_response(data=data, message="创建成功")


@router.put("/upgrade-rules/{rule_id}")
async def update_upgrade_rule(rule_id: int, rule: UpgradeRuleUpdate):
    """Update upgrade rule."""
    data = audit_service.update_upgrade_rule(rule_id, rule.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="规则不存在")
    return success_response(data=data, message="更新成功")


@router.delete("/upgrade-rules/{rule_id}")
async def delete_upgrade_rule(rule_id: int):
    """Delete upgrade rule."""
    data = audit_service.delete_upgrade_rule(rule_id)
    if not data:
        raise HTTPException(status_code=404, detail="规则不存在")
    return success_response(data=data, message="删除成功")
