from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date


# --- Progress ---
class MonthlyProgressResponse(BaseModel):
    account_month: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    running_tasks: int
    pending_tasks: int
    progress: float
    quality_score: Optional[float] = None
    days_elapsed: int = 0
    days_total: int = 30
    status: str


class MilestoneResponse(BaseModel):
    id: int
    account_month: Optional[str] = None
    milestone_name: str
    milestone_type: Optional[str] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: str = "pending"
    delay_days: int = 0
    completion_percentage: Optional[float] = None
    responsible_person: Optional[str] = None
    description: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None


class RunningTaskResponse(BaseModel):
    id: int
    task_name: str
    task_type: Optional[str] = None
    priority: str = "normal"
    status: str
    progress: float = 0
    plan_start_time: Optional[datetime] = None
    plan_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    owner: Optional[str] = None
    is_critical: bool = False
    expected_duration: Optional[int] = None
    elapsed_seconds: Optional[int] = None


# --- Tasks ---
class MonthlyTaskResponse(BaseModel):
    id: int
    account_month: Optional[str] = None
    task_code: str
    task_name: str
    task_type: Optional[str] = None
    priority: str = "normal"
    status: str = "pending"
    progress: float = 0
    plan_start_time: Optional[datetime] = None
    plan_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    expected_duration: Optional[int] = None
    owner: Optional[str] = None
    dependency_ids: Optional[list] = None
    retry_count: int = 0
    is_critical: bool = False
    error_message: Optional[str] = None
    result_summary: Optional[Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TaskLogResponse(BaseModel):
    id: int
    task_id: int
    log_content: str
    log_level: str = "info"
    created_at: Optional[datetime] = None


# --- Orchestration ---
class OrchestrationTaskCreate(BaseModel):
    task_name: str
    task_code: Optional[str] = None
    task_type: Optional[str] = None
    priority: str = "normal"
    plan_start_time: Optional[datetime] = None
    plan_end_time: Optional[datetime] = None
    expected_duration: Optional[int] = None
    owner: Optional[str] = None
    dependency_ids: Optional[list[int]] = None
    is_critical: bool = False
    description: Optional[str] = None


class OrchestrationTaskUpdate(OrchestrationTaskCreate):
    task_name: Optional[str] = None
    status: Optional[str] = None


class OrchestrationTaskResponse(BaseModel):
    id: int
    task_name: str
    task_code: Optional[str] = None
    task_type: Optional[str] = None
    priority: str = "normal"
    status: str = "pending"
    plan_start_time: Optional[datetime] = None
    plan_end_time: Optional[datetime] = None
    expected_duration: Optional[int] = None
    owner: Optional[str] = None
    dependency_ids: Optional[list] = None
    is_critical: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GanttTask(BaseModel):
    id: int
    task_name: str
    start: str
    end: str
    progress: float
    dependency: Optional[str] = None
    priority: str
    status: str
    owner: str


class DagNode(BaseModel):
    id: str
    label: str
    status: str
    type: str


class DagEdge(BaseModel):
    source: str
    target: str
    type: str = "default"


class GanttResponse(BaseModel):
    tasks: list[GanttTask]


class DagResponse(BaseModel):
    nodes: list[DagNode]
    edges: list[DagEdge]


class ValidateResponse(BaseModel):
    is_valid: bool
    issues: list[dict] = []
    warnings: list[dict] = []


class GeneratePlanRequest(BaseModel):
    account_month: str
    tasks: Optional[list[dict]] = None


# --- Daily Report ---
class DailyReportGenerateRequest(BaseModel):
    report_date: date
    account_month: Optional[str] = None
    ai_generate: bool = False


class DailyReportUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[Any] = None
    summary: Optional[str] = None
    status: Optional[str] = None


class DailyReportResponse(BaseModel):
    id: int
    report_date: Optional[date] = None
    account_month: Optional[str] = None
    title: Optional[str] = None
    content: Optional[Any] = None
    summary: Optional[str] = None
    task_completed: int = 0
    task_total: int = 0
    exception_count: int = 0
    quality_score: Optional[float] = None
    progress: Optional[float] = None
    ai_generated: bool = False
    status: str = "draft"
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Summary Report ---
class SummaryReportResponse(BaseModel):
    id: int
    account_month: str
    title: Optional[str] = None
    report_type: str = "monthly"
    overview: Optional[str] = None
    key_metrics: Optional[Any] = None
    progress_summary: Optional[Any] = None
    problem_analysis: Optional[str] = None
    achievements: Optional[str] = None
    improvement_plan: Optional[str] = None
    attachments: Optional[Any] = None
    status: str = "draft"
    exception_flag: bool = False
    exception_detail: Optional[str] = None
    publisher: Optional[str] = None
    publish_time: Optional[datetime] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReportStatisticsResponse(BaseModel):
    total_reports: int
    published: int
    draft: int
    with_exception: int
    by_month: dict = {}


# --- Billing Progress ---
class BillingTaskCreate(BaseModel):
    task_code: str
    task_name: str
    work_type: str = Field(..., pattern="^(前置作业|用户作业|实收作业|应收作业)$")
    planned_start: str
    planned_end: str
    duration_minutes: int = 0
    dependency_codes: Optional[str] = None
    assignee: Optional[str] = None


class BillingTaskStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(未开始|进行中|已完成|异常)$")
    actual_end: Optional[str] = None


class BriefGenerateRequest(BaseModel):
    cycle_id: str = "202601"


class BillingTaskUpdate(BaseModel):
    task_code: Optional[str] = None
    task_name: Optional[str] = None
    work_type: Optional[str] = Field(None, pattern="^(前置作业|用户作业|实收作业|应收作业)$")
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    duration_minutes: Optional[int] = None
    dependency_codes: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(未开始|进行中|已完成|异常)$")


class ImportBillingTasksRequest(BaseModel):
    cycle_id: str = "202605"
    tasks: list[BillingTaskCreate] = []
