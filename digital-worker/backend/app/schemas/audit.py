from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# --- Field Config ---
class AuditFieldCreate(BaseModel):
    field_name: str = Field(..., description="字段名称")
    field_desc: Optional[str] = None
    datasource_id: Optional[str] = None
    datasource_name: Optional[str] = None
    schema_name: Optional[str] = None
    table_name: Optional[str] = None
    field_type: Optional[str] = None
    field_length: Optional[int] = None
    is_nullable: bool = True
    default_value: Optional[str] = None
    sample_data: Optional[str] = None
    remark: Optional[str] = None


class AuditFieldUpdate(AuditFieldCreate):
    field_name: Optional[str] = None


class AuditFieldResponse(BaseModel):
    id: int
    field_name: str
    field_desc: Optional[str] = None
    datasource_id: Optional[str] = None
    datasource_name: Optional[str] = None
    schema_name: Optional[str] = None
    table_name: Optional[str] = None
    field_type: Optional[str] = None
    field_length: Optional[int] = None
    is_nullable: bool = True
    default_value: Optional[str] = None
    sample_data: Optional[str] = None
    status: int = 1
    remark: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Rule Config ---
class AuditRuleCreate(BaseModel):
    rule_name: str
    rule_code: Optional[str] = None
    rule_type: Optional[str] = None
    rule_level: Optional[str] = None
    rule_content: Optional[Any] = None
    field_id: Optional[int] = None
    field_name: Optional[str] = None
    table_name: Optional[str] = None
    threshold: Optional[float] = None
    severity: str = "medium"


class AuditRuleUpdate(AuditRuleCreate):
    rule_name: Optional[str] = None


class AuditRuleResponse(BaseModel):
    id: int
    rule_name: str
    rule_code: Optional[str] = None
    rule_type: Optional[str] = None
    rule_level: Optional[str] = None
    rule_content: Optional[Any] = None
    field_id: Optional[int] = None
    field_name: Optional[str] = None
    table_name: Optional[str] = None
    threshold: Optional[float] = None
    severity: str = "medium"
    status: int = 1
    ai_generated: bool = False
    generate_task_id: Optional[str] = None
    confirm_status: str = "pending"
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- AI Generate ---
class AiGenerateRequest(BaseModel):
    table_name: str
    field_ids: list[int] = []
    business_scenario: Optional[str] = None


class AiGenerateStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int = 0
    result: Optional[list[AuditRuleResponse]] = None


class BatchConfirmRequest(BaseModel):
    rule_ids: list[int]
    confirm_status: str = "confirmed"


# --- Task Config ---
class AuditTaskCreate(BaseModel):
    task_name: str
    task_type: Optional[str] = None
    rule_ids: Optional[list[int]] = None
    field_ids: Optional[list[int]] = None
    schedule_type: str = "manual"
    schedule_config: Optional[Any] = None
    execute_strategy: str = "full"
    sample_rate: float = 100.0
    importance: int = 1


class AuditTaskResponse(BaseModel):
    id: int
    task_name: str
    task_type: Optional[str] = None
    rule_ids: Optional[list] = None
    field_ids: Optional[list] = None
    schedule_type: str = "manual"
    schedule_config: Optional[Any] = None
    execute_strategy: str = "full"
    sample_rate: float = 100.0
    status: int = 1
    importance: int = 1
    last_execute_time: Optional[datetime] = None
    last_execute_result: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Execution ---
class AuditExecutionResponse(BaseModel):
    id: int
    task_id: Optional[int] = None
    task_name: Optional[str] = None
    execute_time: Optional[datetime] = None
    execute_duration: Optional[float] = None
    total_records: Optional[int] = None
    sample_records: Optional[int] = None
    passed_records: Optional[int] = None
    failed_records: Optional[int] = None
    pass_rate: Optional[float] = None
    error_message: Optional[str] = None
    status: str = "pending"
    result_summary: Optional[Any] = None
    created_at: Optional[datetime] = None


# --- Exception ---
class AlertHandleRequest(BaseModel):
    handler: str
    handle_result: str


class AuditExceptionResponse(BaseModel):
    id: int
    execution_id: Optional[int] = None
    rule_id: Optional[int] = None
    rule_name: Optional[str] = None
    field_name: Optional[str] = None
    table_name: Optional[str] = None
    exception_type: Optional[str] = None
    exception_value: Optional[str] = None
    exception_count: Optional[int] = None
    exception_rate: Optional[float] = None
    severity: str = "medium"
    status: str = "open"
    handler: Optional[str] = None
    handle_time: Optional[datetime] = None
    handle_result: Optional[str] = None
    alert_level: Optional[str] = None
    is_upgraded: bool = False
    created_at: Optional[datetime] = None


# --- Report ---
class AuditReportCreate(BaseModel):
    report_name: str
    report_type: Optional[str] = "daily"
    execution_ids: Optional[list[int]] = None
    summary: Optional[str] = None


class AuditReportResponse(BaseModel):
    id: int
    report_name: str
    report_type: Optional[str] = None
    execution_ids: Optional[list] = None
    total_executions: Optional[int] = None
    total_records: Optional[int] = None
    total_exceptions: Optional[int] = None
    overall_pass_rate: Optional[float] = None
    summary: Optional[str] = None
    conclusion: Optional[str] = None
    recommendations: Optional[Any] = None
    report_data: Optional[Any] = None
    status: str = "draft"
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None


# --- Importance Config ---
class ImportanceConfigCreate(BaseModel):
    level: int
    level_name: str
    color: Optional[str] = None
    score_range: Optional[str] = None
    description: Optional[str] = None
    notify_channels: Optional[list] = None
    response_time_minutes: Optional[int] = None


class ImportanceConfigUpdate(ImportanceConfigCreate):
    level: Optional[int] = None
    level_name: Optional[str] = None


class ImportanceConfigResponse(BaseModel):
    id: int
    level: int
    level_name: str
    color: Optional[str] = None
    score_range: Optional[str] = None
    description: Optional[str] = None
    notify_channels: Optional[Any] = None
    response_time_minutes: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Upgrade Rule ---
class UpgradeRuleCreate(BaseModel):
    rule_name: str
    alert_type: Optional[str] = None
    trigger_condition: Optional[Any] = None
    upgrade_level: Optional[int] = None
    notify_targets: Optional[Any] = None
    notify_template: Optional[str] = None
    max_upgrade_count: int = 3
    is_active: bool = True


class UpgradeRuleUpdate(UpgradeRuleCreate):
    rule_name: Optional[str] = None


class UpgradeRuleResponse(BaseModel):
    id: int
    rule_name: str
    alert_type: Optional[str] = None
    trigger_condition: Optional[Any] = None
    upgrade_level: Optional[int] = None
    notify_targets: Optional[Any] = None
    notify_template: Optional[str] = None
    max_upgrade_count: int = 3
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Statistics ---
class AuditStatisticsResponse(BaseModel):
    total_executions: int
    total_exceptions: int
    avg_pass_rate: float
    total_tasks: int
    active_alerts: int
    by_severity: dict = {}
    by_type: dict = {}


class AuditTrendResponse(BaseModel):
    dates: list[str]
    pass_rates: list[float]
    exception_counts: list[int]


class AuditDistributionResponse(BaseModel):
    by_type: dict = {}
    by_severity: dict = {}
    by_table: dict = {}
    by_status: dict = {}
