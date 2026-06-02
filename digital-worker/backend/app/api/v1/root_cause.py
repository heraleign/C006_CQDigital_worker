"""Root Cause module API endpoints - 18 endpoints."""
from fastapi import APIRouter, Query, Path, HTTPException
from typing import Optional
from app.utils.response import success_response, paginated_response
from app.services.root_cause_service import RootCauseService
from app.schemas.root_cause import (
    AnalysisPathCreate, AnalysisPathUpdate,
    CaseCreate, CaseUpdate, CaseMatchRequest,
    FeedbackCreate,
)

router = APIRouter()
service = RootCauseService()


# ==================== Knowledge Base (Cases) Endpoints ====================

@router.get("/knowledge")
async def list_knowledge(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    keyword: Optional[str] = None,
):
    """List knowledge base / cases."""
    if keyword:
        from app.services.knowledge_service import KnowledgeService
        ks = KnowledgeService()
        data = ks.search_cases(keyword, page, page_size)
        return paginated_response(data["items"], data["total"], data["page"], data["page_size"])
    data = service.get_cases(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.get("/knowledge/search")
async def search_knowledge(
    keyword: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """Search knowledge base."""
    from app.services.knowledge_service import KnowledgeService
    ks = KnowledgeService()
    data = ks.search_cases(keyword, page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.get("/knowledge/{case_id}")
async def get_knowledge(case_id: int):
    """Get knowledge case by ID."""
    data = service.get_case(case_id)
    if not data:
        raise HTTPException(status_code=404, detail="案例不存在")
    return success_response(data=data)


# ==================== Lineage Endpoints ====================

@router.get("/lineage")
async def list_lineage(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """Get task lineage."""
    data = service.get_lineage(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/lineage/batch-import")
async def batch_import_lineage(tasks: list[dict]):
    """Batch import lineage tasks."""
    data = service.batch_import_lineage(tasks)
    return success_response(data=data, message="导入成功")


# ==================== Analysis Paths Endpoints ====================

@router.get("/analysis-paths")
async def list_analysis_paths(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List analysis path templates."""
    data = service.get_paths(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/analysis-paths")
async def create_analysis_path(path: AnalysisPathCreate):
    """Create analysis path."""
    data = service.create_path(path.model_dump(exclude_unset=True))
    return success_response(data=data, message="创建成功")


@router.put("/analysis-paths/{path_id}")
async def update_analysis_path(path_id: int, path: AnalysisPathUpdate):
    """Update analysis path."""
    data = service.update_path(path_id, path.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="路径不存在")
    return success_response(data=data, message="更新成功")


@router.delete("/analysis-paths/{path_id}")
async def delete_analysis_path(path_id: int):
    """Delete analysis path."""
    data = service.delete_path(path_id)
    if not data:
        raise HTTPException(status_code=404, detail="路径不存在")
    return success_response(data=data, message="删除成功")


# ==================== Root Cause Analysis Endpoints ====================

@router.post("/analysis")
async def create_analysis(data: dict):
    """Create a new root cause analysis."""
    from app.services.ai_service import ai_service
    ai_result = await ai_service.root_cause_analysis(
        data.get("problem_description", ""),
        data,
    )
    analysis = service.create_analysis({
        **data,
        "conclusion": ai_result.get("root_cause", ""),
        "confidence": ai_result.get("confidence", 0),
        "analysis_process": ai_result.get("analysis_process", []),
        "status": "completed",
        "ai_assisted": True,
    })
    return success_response(data=analysis, message="分析完成")


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: int):
    """Get root cause analysis by ID."""
    data = service.get_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="分析记录不存在")
    return success_response(data=data)


@router.get("/analysis/{analysis_id}/steps")
async def get_analysis_steps(analysis_id: int):
    """Get analysis trace steps."""
    data = service.get_analysis_steps(analysis_id)
    return success_response(data=data)


@router.get("/analysis/records")
async def get_analysis_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """Get analysis records."""
    data = service.get_analyses_records(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/analysis/{analysis_id}/feedback")
async def add_analysis_feedback(analysis_id: int, feedback: FeedbackCreate):
    """Add feedback to an analysis."""
    data = service.add_feedback({**feedback.model_dump(), "analysis_id": analysis_id})
    return success_response(data=data, message="反馈提交成功")


@router.post("/analysis/{analysis_id}/save-as-case")
async def save_analysis_as_case(analysis_id: int):
    """Save analysis result as case."""
    result = service.save_as_case(analysis_id)
    return success_response(data=result, message="已保存为案例")


# ==================== Problem Cases Endpoints ====================

@router.get("/cases")
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List problem cases."""
    data = service.get_cases(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.post("/cases")
async def create_case(case: CaseCreate):
    """Create problem case."""
    data = service.create_case(case.model_dump(exclude_unset=True))
    return success_response(data=data, message="案例创建成功")


@router.get("/cases/statistics")
async def get_case_statistics():
    """Get case statistics."""
    data = service.get_case_statistics()
    return success_response(data=data)


@router.put("/cases/{case_id}")
async def update_case(case_id: int, case: CaseUpdate):
    """Update problem case."""
    data = service.update_case(case_id, case.model_dump(exclude_unset=True))
    if not data:
        raise HTTPException(status_code=404, detail="案例不存在")
    return success_response(data=data, message="更新成功")


@router.delete("/cases/{case_id}")
async def delete_case(case_id: int):
    """Delete problem case."""
    data = service.delete_case(case_id)
    if not data:
        raise HTTPException(status_code=404, detail="案例不存在")
    return success_response(data=data, message="删除成功")


@router.post("/cases/match")
async def match_cases(request: CaseMatchRequest):
    """Match similar cases."""
    data = service.match_cases(request.problem_description, request.top_k)
    return success_response(data=data)


# ==================== Suggestions Endpoints ====================

@router.get("/suggestions")
async def list_suggestions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """List suggestions."""
    data = service.get_suggestions(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.get("/suggestions/statistics")
async def get_suggestion_statistics():
    """Get suggestion statistics."""
    data = service.get_suggestion_statistics()
    return success_response(data=data)


@router.post("/suggestions/generate")
async def generate_suggestions(data: dict):
    """Generate suggestions automatically."""
    result = service.generate_suggestions(data)
    return success_response(data=result, message="建议生成中")


@router.put("/suggestions/{suggestion_id}/adopt")
async def adopt_suggestion(suggestion_id: int):
    """Adopt a suggestion."""
    data = service.update_suggestion(suggestion_id, {"status": "adopted"})
    if not data:
        raise HTTPException(status_code=404, detail="建议不存在")
    return success_response(data=data, message="已采纳")


@router.put("/suggestions/{suggestion_id}/ignore")
async def ignore_suggestion(suggestion_id: int):
    """Ignore a suggestion."""
    data = service.update_suggestion(suggestion_id, {"status": "ignored"})
    if not data:
        raise HTTPException(status_code=404, detail="建议不存在")
    return success_response(data=data, message="已忽略")
