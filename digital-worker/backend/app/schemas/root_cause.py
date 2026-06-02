from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# --- Task Lineage ---
class TaskLineageResponse(BaseModel):
    id: int
    task_code: str
    task_name: str
    task_type: Optional[str] = None
    upstream_tasks: Optional[list] = None
    downstream_tasks: Optional[list] = None
    datasource_input: Optional[str] = None
    datasource_output: Optional[str] = None
    schedule_type: Optional[str] = None
    owner: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    status: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BatchImportLineageRequest(BaseModel):
    tasks: list[dict]


# --- Analysis Path ---
class AnalysisPathCreate(BaseModel):
    path_name: str
    path_type: Optional[str] = None
    steps: Optional[list] = None
    applicable_scenarios: Optional[str] = None
    expected_duration: Optional[int] = None
    success_rate: Optional[float] = None


class AnalysisPathUpdate(AnalysisPathCreate):
    path_name: Optional[str] = None


class AnalysisPathResponse(BaseModel):
    id: int
    path_name: str
    path_type: Optional[str] = None
    steps: Optional[Any] = None
    applicable_scenarios: Optional[str] = None
    expected_duration: Optional[int] = None
    success_rate: Optional[float] = None
    usage_count: int = 0
    status: int = 1
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Root Cause Analysis ---
class AnalysisCreate(BaseModel):
    case_id: Optional[int] = None
    path_id: Optional[int] = None
    analysis_title: str
    problem_description: str
    ai_assisted: bool = True


class AnalysisResponse(BaseModel):
    id: int
    case_id: Optional[int] = None
    path_id: Optional[int] = None
    analysis_title: Optional[str] = None
    problem_description: Optional[str] = None
    analysis_process: Optional[Any] = None
    conclusion: Optional[str] = None
    root_cause_type_id: Optional[int] = None
    root_cause_desc: Optional[str] = None
    confidence: Optional[float] = None
    status: str = "analyzing"
    is_saved_as_case: bool = False
    analysis_duration: Optional[int] = None
    ai_assisted: bool = False
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AnalysisStepResponse(BaseModel):
    id: int
    analysis_id: int
    step_name: Optional[str] = None
    step_order: Optional[int] = None
    action: Optional[str] = None
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    reasoning: Optional[str] = None
    status: str = "completed"
    duration: Optional[int] = None
    created_at: Optional[datetime] = None


# --- Feedback ---
class FeedbackCreate(BaseModel):
    analysis_id: Optional[int] = None
    case_id: Optional[int] = None
    feedback_type: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    content: Optional[str] = None
    user_name: Optional[str] = None
    user_department: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    analysis_id: Optional[int] = None
    case_id: Optional[int] = None
    feedback_type: Optional[str] = None
    rating: Optional[int] = None
    content: Optional[str] = None
    user_name: Optional[str] = None
    user_department: Optional[str] = None
    is_resolved: bool = False
    created_at: Optional[datetime] = None


# --- Cases ---
class CaseCreate(BaseModel):
    case_title: str
    case_type: Optional[str] = None
    case_source: str = "manual"
    severity: Optional[str] = "medium"
    description: Optional[str] = None
    impact_range: Optional[str] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    lessons_learned: Optional[str] = None
    tags: Optional[list] = None
    related_task_code: Optional[str] = None
    related_tables: Optional[list] = None
    handler: Optional[str] = None
    handler_department: Optional[str] = None
    occurrence_time: Optional[datetime] = None
    resolve_time: Optional[datetime] = None


class CaseUpdate(CaseCreate):
    case_title: Optional[str] = None


class CaseResponse(BaseModel):
    id: int
    case_title: str
    case_type: Optional[str] = None
    case_source: Optional[str] = None
    status: str = "open"
    severity: Optional[str] = None
    description: Optional[str] = None
    impact_range: Optional[str] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    lessons_learned: Optional[str] = None
    tags: Optional[Any] = None
    related_task_code: Optional[str] = None
    related_tables: Optional[Any] = None
    handler: Optional[str] = None
    handler_department: Optional[str] = None
    occurrence_time: Optional[datetime] = None
    resolve_time: Optional[datetime] = None
    resolution_duration: Optional[int] = None
    is_template: bool = False
    usage_count: int = 0
    rating: Optional[float] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CaseStatisticsResponse(BaseModel):
    total_cases: int
    by_type: dict = {}
    by_severity: dict = {}
    by_status: dict = {}
    avg_resolution_time: float
    top_tags: list[dict] = []
    recent_cases: int = 0


class CaseMatchRequest(BaseModel):
    problem_description: str
    top_k: int = 5


class CaseMatchResponse(BaseModel):
    case_id: int
    case_title: str
    similarity: float
    match_reason: str
    case: CaseResponse


# --- Suggestions ---
class SuggestionResponse(BaseModel):
    id: int
    case_id: Optional[int] = None
    analysis_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    suggestion_type: Optional[str] = None
    status: str = "pending"
    created_at: Optional[datetime] = None


class SuggestionStatisticsResponse(BaseModel):
    total: int
    adopted: int
    ignored: int
    pending: int
    adopt_rate: float
