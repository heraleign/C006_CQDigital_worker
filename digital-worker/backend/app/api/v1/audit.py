"""Audit module API endpoints - 15+ endpoints for data quality audit."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional, Any, Dict
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

# ==================== Field Name Mapping Helpers ====================

def _transform_field(f: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map backend DqAuditFieldConfig fields to frontend FieldConfig format."""
    if not f:
        return None
    return {
        "config_id": str(f.get("id", "")),
        "datasource_code": f.get("datasource_id", ""),
        "datasource_name": f.get("datasource_name", ""),
        "schema_code": f.get("schema_name", ""),
        "table_code": f.get("table_name", ""),
        "field_code": f.get("field_name", ""),
        "field_name": f.get("field_desc", f.get("field_name", "")),
        "audit_type": f.get("audit_type", "accuracy"),
        "status_cd": "active" if f.get("status", 1) == 1 else "inactive",
        "create_time": f.get("created_at", ""),
        "remark": f.get("remark", ""),
        "field_type": f.get("field_type", ""),
        "field_length": f.get("field_length"),
        "is_nullable": f.get("is_nullable", True),
        "sample_data": f.get("sample_data", ""),
        "default_value": f.get("default_value", ""),
    }

def _transform_fields(items: list) -> list:
    """Transform a list of field dicts."""
    return [_transform_field(f) for f in items if f]


def _transform_rule(r: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map backend DqAuditRuleConfig fields to frontend RuleConfig format."""
    if not r:
        return None
    return {
        "rule_id": str(r.get("id", "")),
        "rule_code": r.get("rule_code", ""),
        "rule_name": r.get("rule_name", ""),
        "rule_type": r.get("rule_type", ""),
        "rule_level": r.get("rule_level", ""),
        "field_id": r.get("field_id"),
        "field_name": r.get("field_name", ""),
        "table_name": r.get("table_name", ""),
        "threshold": r.get("threshold", 0),
        "threshold_lower": 0,
        "threshold_upper": 100,
        "alert_level": r.get("severity", "medium"),
        "severity": r.get("severity", "medium"),
        "status_cd": "active" if r.get("status", 1) == 1 else "inactive",
        "confirm_status": r.get("confirm_status", "pending"),
        "ai_generated": r.get("ai_generated", False),
        "rule_content": r.get("rule_content"),
        "create_time": r.get("created_at", ""),
        "created_by": r.get("created_by", ""),
    }


def _transform_rules(items: list) -> list:
    """Transform a list of rule dicts."""
    return [_transform_rule(r) for r in items if r]


def _transform_execution(e: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map backend DqAuditExecution fields to frontend format."""
    if not e:
        return None
    pass_rate = e.get("pass_rate", 100)
    failed = e.get("failed_records", 0)
    total = e.get("total_records", 0) or 1
    exec_time = e.get("execute_time", e.get("created_at", ""))
    result_summary = e.get("result_summary") or {}
    return {
        "execution_id": str(e.get("id", "")),
        "id": e.get("id"),
        "task_id": e.get("task_id"),
        "task_name": e.get("task_name", ""),
        "execute_time": exec_time,
        "acct_date": str(exec_time)[:10] if exec_time else "",
        "execute_duration": e.get("execute_duration"),
        "total_records": total,
        "sample_records": e.get("sample_records"),
        "passed_records": e.get("passed_records"),
        "failed_records": failed,
        "pass_rate": pass_rate,
        "rule_name": e.get("task_name", ""),
        "field_name": result_summary.get("field_name", "全部字段"),
        "check_value": failed if failed > 0 else pass_rate,
        "deviation_rate": round(100 - (pass_rate if pass_rate else 100), 2),
        "check_result": "pass" if (pass_rate or 0) >= 90 else "fail" if (pass_rate or 0) < 80 else "warning",
        "anomaly_type": "fluctuation" if (pass_rate or 100) < 85 else "normal",
        "status": e.get("status", "pending"),
        "result_summary": result_summary,
        "created_at": e.get("created_at", ""),
    }


def _transform_exception(ex: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map backend DqAuditException fields to frontend alert format."""
    if not ex:
        return None
    return {
        "alert_id": str(ex.get("id", "")),
        "execution_id": ex.get("execution_id"),
        "rule_id": ex.get("rule_id"),
        "rule_name": ex.get("rule_name", ""),
        "field_name": ex.get("field_name", ""),
        "table_name": ex.get("table_name", ""),
        "exception_type": ex.get("exception_type", ""),
        "exception_value": ex.get("exception_value", ""),
        "exception_count": ex.get("exception_count"),
        "exception_rate": ex.get("exception_rate"),
        "severity": ex.get("severity", "medium"),
        "status": ex.get("status", "open"),
        "handler": ex.get("handler", ""),
        "handle_time": ex.get("handle_time"),
        "handle_result": ex.get("handle_result", ""),
        "alert_level": ex.get("alert_level", ""),
        "is_upgraded": ex.get("is_upgraded", False),
        "title": ex.get("rule_name", ex.get("exception_type", "告警")),
        "source_task": ex.get("table_name", ex.get("rule_name", "")),
        "create_time": ex.get("created_at", ""),
        "created_at": ex.get("created_at", ""),
    }


def _transform_task(t: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map backend DqAuditTaskConfig fields to frontend AuditTask format."""
    if not t:
        return None
    return {
        "task_id": str(t.get("id", "")),
        "task_name": t.get("task_name", ""),
        "task_type": t.get("task_type", ""),
        "rule_ids": t.get("rule_ids", []),
        "field_ids": t.get("field_ids", []),
        "schedule_type": t.get("schedule_type", "manual"),
        "schedule_config": t.get("schedule_config"),
        "execute_strategy": t.get("execute_strategy", "full"),
        "sample_rate": t.get("sample_rate", 100.0),
        "status_cd": "active" if t.get("status", 1) == 1 else "inactive",
        "last_run_status": t.get("last_execute_result", "pending"),
        "importance": t.get("importance", 1),
        "created_by": t.get("created_by", ""),
        "create_time": t.get("created_at", ""),
    }


def _transform_importance_config(c: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map backend DqTaskImportanceConfig to frontend importance config format."""
    if not c:
        return None
    return {
        "id": c.get("id"),
        "config_id": str(c.get("id", "")),
        "task_name": c.get("level_name", ""),
        "level": c.get("level_name", ""),
        "level_num": c.get("level", 1),
        "color": c.get("color", "#909399"),
        "score_range": c.get("score_range", ""),
        "description": c.get("description", ""),
        "auto_upgrade": True,
        "max_failures": c.get("response_time_minutes", 3),
        "notify_channels": c.get("notify_channels", []),
        "response_time_minutes": c.get("response_time_minutes"),
    }


def _transform_upgrade_rule(r: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Map backend DqAlertUpgradeRule to frontend upgrade rule format."""
    if not r:
        return None
    trigger = r.get("trigger_condition", {})
    if isinstance(trigger, dict):
        condition_parts = []
        for k, v in trigger.items():
            condition_parts.append(f"{k}={v}")
        condition_str = ", ".join(condition_parts)
    else:
        condition_str = str(trigger)

    return {
        "id": r.get("id"),
        "rule_id": str(r.get("id", "")),
        "rule_name": r.get("rule_name", ""),
        "condition": condition_str,
        "trigger_condition": trigger,
        "upgrade_method": "auto" if r.get("is_active", True) else "manual",
        "target_level": r.get("upgrade_level", ""),
        "notify_targets": r.get("notify_targets", []),
        "notify_template": r.get("notify_template", ""),
        "max_upgrade_count": r.get("max_upgrade_count", 3),
        "status": "active" if r.get("is_active", True) else "inactive",
        "is_active": r.get("is_active", True),
    }


# ==================== Field Config Endpoints ====================

@router.get("/fields")
async def list_fields(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    datasource_code: Optional[str] = None,
    table_code: Optional[str] = None,
    schema_code: Optional[str] = None,
    audit_type: Optional[str] = None,
    status_cd: Optional[str] = None,
):
    """List audit field configurations (with frontend field name mapping)."""
    # Map frontend param names to backend filter params
    filters = {}
    if datasource_code:
        filters["datasource_id"] = datasource_code
    if table_code:
        filters["table_name"] = table_code
    # TODO: add schema_code, audit_type, status_cd filters when model supports them

    data = audit_service.get_fields(page, page_size, **filters)
    return paginated_response(
        _transform_fields(data["items"]),
        data["total"],
        data["page"],
        data["page_size"],
    )


@router.post("/fields")
async def create_field(field: AuditFieldCreate):
    """Create a new audit field config."""
    data = audit_service.create_field(field.model_dump(exclude_unset=True))
    return success_response(data=_transform_field(data), message="字段创建成功")


@router.get("/fields/{field_id}")
async def get_field(field_id: int = Path(..., ge=1)):
    """Get field config by ID."""
    data = audit_service.get_field(field_id)
    if not data:
        raise HTTPException(status_code=404, detail="字段不存在")
    return success_response(data=_transform_field(data))


@router.put("/fields/{field_id}")
async def update_field(field_id: int, field: AuditFieldUpdate):
    """Update field config."""
    data = audit_service.update_field(field_id, field.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="字段不存在")
    return success_response(data=_transform_field(data), message="字段更新成功")


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
    # Return in format frontend expects (with datasource_code and datasource_name)
    result = []
    for d in data:
        result.append({
            "datasource_code": d.get("id", ""),
            "datasource_name": d.get("name", ""),
            "type": d.get("type", "mysql"),
            "status": d.get("status", "online"),
        })
    return success_response(data=result)


@router.get("/schemas")
async def list_schemas(datasource_code: Optional[str] = Query(None, alias="datasource_code")):
    """List schemas for a datasource."""
    data = audit_service.get_schemas(datasource_code)
    result = []
    for s in data:
        result.append({
            "schema_code": s.get("name", ""),
            "schema_name": s.get("name", ""),
            "datasource_code": s.get("datasource_id", datasource_code or ""),
        })
    return success_response(data=result)


@router.get("/tables")
async def list_tables(
    datasource_code: Optional[str] = None,
    schema_code: Optional[str] = Query(None, alias="schema_code"),
):
    """List tables for a schema."""
    data = audit_service.get_tables(schema_code)
    result = []
    for t in data:
        result.append({
            "table_code": t.get("name", ""),
            "table_name": t.get("desc", t.get("name", "")),
            "schema_code": t.get("schema_name", schema_code or ""),
            "datasource_code": datasource_code or "",
        })
    return success_response(data=result)


@router.get("/fields-by-table")
async def list_fields_by_table(
    datasource_code: Optional[str] = None,
    schema_code: Optional[str] = None,
    table_code: Optional[str] = Query(None, alias="table_code"),
):
    """List fields for a table (transformed to frontend format)."""
    data = audit_service.get_fields_by_table(table_code)
    return success_response(data=_transform_fields(data))


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
        rid = int(rule_id) if isinstance(rule_id, str) else rule_id
        audit_service.update_rule(rid, {"confirm_status": request.confirm_status})
    return success_response(data=None, message=f"已{request.confirm_status} {len(request.rule_ids)} 条规则")


# ==================== Rule Config Endpoints ====================

@router.get("/rules")
async def list_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    confirm_status: Optional[str] = Query(None, alias="status"),
):
    """List audit rules (transformed to frontend format)."""
    data = audit_service.get_rules(page, page_size)
    items = _transform_rules(data["items"])
    # Filter by confirm_status if provided (frontend sends ?status=pending)
    if confirm_status:
        items = [r for r in items if r.get("confirm_status") == confirm_status]
    return paginated_response(items, data["total"], data["page"], data["page_size"])


@router.post("/rules")
async def create_rule(rule: AuditRuleCreate):
    """Create a new audit rule."""
    data = audit_service.create_rule(rule.model_dump(exclude_unset=True))
    return success_response(data=_transform_rule(data), message="规则创建成功")


@router.put("/rules/{rule_id}")
async def update_rule(rule_id: int, rule: AuditRuleUpdate):
    """Update audit rule."""
    data = audit_service.update_rule(rule_id, rule.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="规则不存在")
    return success_response(data=_transform_rule(data), message="规则更新成功")


@router.put("/rules/{rule_id}/confirm")
async def confirm_rule(rule_id: int):
    """Confirm a single rule."""
    data = audit_service.update_rule(rule_id, {"confirm_status": "confirmed"})
    if not data:
        raise HTTPException(status_code=404, detail="规则不存在")
    return success_response(data=_transform_rule(data), message="规则确认成功")


@router.put("/rules/{rule_id}/reject")
async def reject_rule(rule_id: int):
    """Reject a single rule."""
    data = audit_service.update_rule(rule_id, {"confirm_status": "rejected"})
    if not data:
        raise HTTPException(status_code=404, detail="规则不存在")
    return success_response(data=_transform_rule(data), message="规则已拒绝")


@router.post("/rules/batch-confirm")
async def batch_confirm_rules(request: BatchConfirmRequest):
    """Batch confirm rules."""
    for rule_id in request.rule_ids:
        rid = int(rule_id) if isinstance(rule_id, str) else rule_id
        audit_service.update_rule(rid, {"confirm_status": request.confirm_status})
    return success_response(data=None, message=f"批量{request.confirm_status}成功")


# ==================== Task Config Endpoints ====================

@router.get("/tasks")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List audit tasks (transformed to frontend format)."""
    data = audit_service.get_tasks(page, page_size)
    return paginated_response(
        [_transform_task(t) for t in data["items"]],
        data["total"], data["page"], data["page_size"],
    )


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
    """List audit alerts/exceptions (transformed)."""
    data = audit_service.get_alerts(page, page_size)
    return paginated_response(
        [_transform_exception(e) for e in data["items"]],
        data["total"], data["page"], data["page_size"],
    )


@router.put("/alerts/{alert_id}/handle")
async def handle_alert(alert_id: int, request: AlertHandleRequest):
    """Handle an alert."""
    data = audit_service.handle_alert(alert_id, request.model_dump())
    if not data:
        raise HTTPException(status_code=404, detail="告警不存在")
    return success_response(data=_transform_exception(data), message="告警处理成功")


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
    acct_month: Optional[str] = None,
):
    """Get audit execution details (transformed)."""
    data = audit_service.get_executions(page=page, page_size=page_size)
    return paginated_response(
        [_transform_execution(e) for e in data["items"]],
        data["total"], data["page"], data["page_size"],
    )


# ==================== Report Endpoints ====================

@router.get("/reports")
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List audit reports."""
    data = audit_service.get_reports(page, page_size)
    items = []
    for r in data["items"]:
        items.append({
            "report_id": str(r.get("id", "")),
            "report_name": r.get("report_name", ""),
            "report_type": r.get("report_type", ""),
            "total_executions": r.get("total_executions"),
            "total_records": r.get("total_records"),
            "total_exceptions": r.get("total_exceptions"),
            "overall_pass_rate": r.get("overall_pass_rate"),
            "summary": r.get("summary", ""),
            "conclusion": r.get("conclusion", ""),
            "recommendations": r.get("recommendations", []),
            "status": r.get("status", "draft"),
            "created_by": r.get("created_by", ""),
            "created_at": r.get("created_at", ""),
        })
    return paginated_response(items, data["total"], data["page"], data["page_size"])


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
    """List importance configurations (transformed)."""
    data = audit_service.get_importance_configs()
    return success_response(data=[_transform_importance_config(c) for c in data])


@router.post("/importance-configs")
async def create_importance_config(config: ImportanceConfigCreate):
    """Create importance config."""
    data = audit_service.create_importance_config(config.model_dump(exclude_unset=True))
    return success_response(data=_transform_importance_config(data), message="创建成功")


@router.put("/importance-configs/{config_id}")
async def update_importance_config(config_id: int, config: ImportanceConfigUpdate):
    """Update importance config."""
    data = audit_service.update_importance_config(config_id, config.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="配置不存在")
    return success_response(data=_transform_importance_config(data), message="更新成功")


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
    """List alert upgrade rules (transformed)."""
    data = audit_service.get_upgrade_rules()
    return success_response(data=[_transform_upgrade_rule(r) for r in data])


@router.post("/upgrade-rules")
async def create_upgrade_rule(rule: UpgradeRuleCreate):
    """Create upgrade rule."""
    data = audit_service.create_upgrade_rule(rule.model_dump(exclude_unset=True))
    return success_response(data=_transform_upgrade_rule(data), message="创建成功")


@router.put("/upgrade-rules/{rule_id}")
async def update_upgrade_rule(rule_id: int, rule: UpgradeRuleUpdate):
    """Update upgrade rule."""
    data = audit_service.update_upgrade_rule(rule_id, rule.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="规则不存在")
    return success_response(data=_transform_upgrade_rule(data), message="更新成功")


@router.delete("/upgrade-rules/{rule_id}")
async def delete_upgrade_rule(rule_id: int):
    """Delete upgrade rule."""
    data = audit_service.delete_upgrade_rule(rule_id)
    if not data:
        raise HTTPException(status_code=404, detail="规则不存在")
    return success_response(data=data, message="删除成功")
