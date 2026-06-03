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
    """List knowledge base / cases in KnowledgeDoc format."""
    data = service.get_knowledge(page, page_size, keyword=keyword)
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
    """Get task lineage as graph {nodes, edges}."""
    data = service.get_lineage_graph(page, page_size)
    return success_response(data=data)


@router.post("/lineage/batch-import")
async def batch_import_lineage(tasks: list[dict]):
    """Batch import lineage tasks."""
    data = service.batch_import_lineage(tasks)
    return success_response(data=data, message="导入成功")


# ==================== Analysis Paths Endpoints ====================

@router.get("/analysis-paths")
async def list_analysis_paths(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """List analysis paths as flat rows (one row per step)."""
    data = service.get_paths_flat(page, page_size)
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
    """Create a new root cause analysis. Supports preset demo data."""
    # If preset_type is provided, return rich preset demo data
    preset_type = data.get("preset_type")
    if preset_type:
        preset = _get_preset_analysis(preset_type)
        if preset:
            return success_response(data=preset, message="分析完成")

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


# Preset analysis data matching the frontend CASE_STUDIES format
_PRESETS = {
    "task_delay": {
        "record_id": "AR_PRESET_task_delay",
        "preset_type": "task_delay",
        "is_preset": True,
        "analysis_status": "completed",
        "analysis_logs": [
            {"step": 1, "action": "获取任务状态", "detail": '调用 get_task_status("JT_PROD_INST_UPLOAD")', "result": "任务状态：waiting（等待中），未失败 → 进入上游依赖追溯", "duration": "1秒", "status": "completed"},
            {"step": 2, "action": "获取上游依赖", "detail": '调用 get_upstream_dependencies("JT_PROD_INST_UPLOAD")', "result": "上游任务：TASK_A(✓已完成)、TASK_B(✓已完成)、TASK_C(✗等待中)", "duration": "2秒", "status": "completed"},
            {"step": 3, "action": "递归追溯上游", "detail": '调用 get_upstream_dependencies("TASK_C")', "result": "上游任务：TASK_C1(✓已完成)、TASK_C2(✗失败) ← 根源任务", "duration": "2秒", "status": "completed"},
            {"step": 4, "action": "获取错误信息", "detail": '调用 get_task_error_info("TASK_C2")', "result": "错误类型：FILE_NOT_ARRIVED\n源文件不存在 /data/interface/prod_inst_20260420.dat", "duration": "1秒", "status": "completed"},
            {"step": 5, "action": "文件状态检查", "detail": "检查文件 /data/interface/prod_inst_20260420.dat", "result": "文件不存在 | 预计到达05:30 | 已延迟180分钟 | 近7天送达率100%", "duration": "3秒", "status": "completed"},
            {"step": 6, "action": "核实根因详情", "detail": "综合所有信息进行根因定位", "result": "根因类型：FILE_NOT_ARRIVED（源文件未送达）\n溯源深度：2级\n影响链路：TASK_C2 → TASK_C → JT_PROD_INST_UPLOAD", "duration": "2秒", "status": "completed"},
            {"step": 7, "action": "生成分析报告", "detail": "生成结构化分析报告", "result": "报告已生成，即将推送通知", "duration": "2秒", "status": "completed"},
        ],
        "root_cause_result": "源文件未送达（FILE_NOT_ARRIVED）",
        "root_cause_detail": "上游任务TASK_C2（源系统接口采集）因源文件 /data/interface/prod_inst_20260420.dat 未按时送达而失败，导致依赖链路上的TASK_C和JT_PROD_INST_UPLOAD任务阻塞等待。历史数据显示该文件近7天均准时到达（平均05:15），本次属偶发性延迟。",
        "root_cause": "源文件未送达（FILE_NOT_ARRIVED）",
        "trace_path": "JT_PROD_INST_UPLOAD(waiting) → TASK_C(waiting) → TASK_C2(failed) ← 根因",
        "evidence": [
            "任务状态确认：JT_PROD_INST_UPLOAD 处于 waiting 状态，非失败",
            "上游追溯：TASK_C 因上游 TASK_C2 失败而阻塞",
            "根因定位：TASK_C2 源文件采集任务失败，错误类型 FILE_NOT_ARRIVED",
            "文件检查：/data/interface/prod_inst_20260420.dat 不存在于服务器",
            "历史对比：近7天文件均准时送达（平均05:15），属偶发性延迟",
        ],
        "source_system": "集团CRM系统",
        "source_contact": "集团数据组-张三（13912345678）",
        "impact_assessment": "影响下游2个任务阻塞，涉及产品实例表数据更新，预计影响5个业务报表的时效性",
        "severity": "中",
        "risk_level": "MEDIUM",
        "solution": [
            "联系集团数据组张三（13912345678）确认文件状态和预计送达时间",
            "文件送达后，手动触发 TASK_C2 任务重跑",
            "TASK_C 和 JT_PROD_INST_UPLOAD 将自动恢复执行",
            "验证下游数据完整性和准确性",
        ],
        "prevention": [
            "增加文件送达预警监控，设置超时自动告警",
            "建立文件送达确认机制，数据提供方送达后自动通知",
            "考虑设置文件等待超时上限，超时后自动通知人工介入",
        ],
        "manual_time": "75分钟",
        "auto_time": "15秒",
        "improvement_pct": "99.7%",
    },
    "metric_anomaly": {
        "record_id": "AR_PRESET_metric_anomaly",
        "preset_type": "metric_anomaly",
        "is_preset": True,
        "analysis_status": "completed",
        "analysis_logs": [
            {"step": 1, "action": "意图识别", "detail": "识别问题类型", "result": "指标异常波动类 | 分析路径：多维度下钻 | 置信度96%", "duration": "5秒", "status": "completed"},
            {"step": 2, "action": "数据质量校验", "detail": "检查数据完整性、重复性、逻辑性", "result": "✓ 数据完整 | ✗ 2,600条同一经办人 | ✗ 1,800条14-15时集中入网 | ✗ 实名率8%", "duration": "30秒", "status": "completed"},
            {"step": 3, "action": "多维度下钻分析", "detail": "按时间→地域→渠道→产品→用户画像逐级下钻", "result": "14:00-15:00(+213%) → 渝北区(+220%,占增量73%) → XX代理商(+1300%) → 0元体验卡(+5100%) → 单人张三1800户/小时", "duration": "90秒", "status": "completed"},
            {"step": 4, "action": "业务规则验证", "detail": "执行5项业务规则检查", "result": "单人效能(×180倍)✗ | 号码连号率68%✗ | 实名率8%✗ | 激活率3%✗ | 产品集中度96%✗", "duration": "30秒", "status": "completed"},
            {"step": 5, "action": "根因定位", "detail": "综合多维度交叉分析结果", "result": "根因类型：CHANNEL_FRAUD（渠道虚假发展）\n置信度：98%\n证据：5维度交叉确认", "duration": "10秒", "status": "completed"},
            {"step": 6, "action": "生成报告并推送", "detail": "生成结构化报告并推送通知", "result": "报告已生成，推送至量子密信+启明APP", "duration": "10秒", "status": "completed"},
        ],
        "root_cause_result": "渠道虚假发展（CHANNEL_FRAUD）",
        "root_cause_detail": "渝北XX代理商为冲刺KPI考核，利用0元体验卡政策漏洞，由经办人张三个人在14:00-15:00一小时内批量录入1,800户虚假用户信息。用户均未实名认证、未激活使用，号码连号率高达68%，属于典型的虚假发展行为。",
        "root_cause": "渠道虚假发展（CHANNEL_FRAUD）",
        "trace_path": "指标异常(+30%) → 时间下钻(14时+213%) → 地域下钻(渝北+220%) → 渠道下钻(XX代理+1300%) → 产品下钻(0元卡+5100%) → 交叉定位 → 规则验证 → 根因确认",
        "evidence": [
            "时间集中：14:00-15:00暴增1,800户（+213%）",
            "地域集中：渝北区增长2,200户，占增量73%",
            "渠道集中：XX代理商增长2,600户（+1300%）",
            "产品集中：0元体验卡2,600户（+5100%）",
            "经办集中：单人张三办理1,800户/小时，超标180倍",
            "号码异常：连号率68%（正常<5%）",
            "实名缺失：实名率8%（正常>95%）",
            "未激活：激活率3%（正常>80%）",
        ],
        "fake_users": 2600,
        "severity": "严重",
        "risk_level": "CRITICAL",
        "impact_assessment": "2,600户虚假用户数据将严重影响经营分析准确性，涉及违反实名制监管规定",
        "solution": [
            "【紧急】冻结渝北XX代理商发展权限，立即执行",
            "【紧急】锁定经办人张三操作账号，暂停业务办理",
            "【紧急】冻结2,600个疑似虚假用户，防止入网",
            "【调查】追溯该代理商近30天发展明细，排查历史数据",
            "【调查】外呼核实200个样本号码，确认虚假比例",
            "【长效】设置单人单小时发展量上限（≤20户）",
            "【长效】启用号码连号检测拦截规则（>5个连号触发）",
            "【长效】强制0元卡实时实名认证，未实名拒绝办理",
        ],
        "prevention": [
            "单人单小时发展量上限 ≤20户，超限自动拦截",
            "号码连号检测：连号>5个时自动阻断发展",
            "实名认证强制：0元体验卡必须100%实时实名",
            "72小时未激活预警：激活率<30%时触发渠道预警",
        ],
        "manual_time": "120分钟",
        "auto_time": "79秒",
        "improvement_pct": "99%",
    },
}


def _get_preset_analysis(preset_type: str) -> dict | None:
    """Return preset analysis data matching the frontend CASE_STUDIES format."""
    return _PRESETS.get(preset_type)


@router.get("/analysis/records")
async def get_analysis_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
):
    """Get analysis records."""
    data = service.get_analyses_records(page, page_size)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get root cause analysis by ID. Supports preset string IDs."""
    # Preset IDs like "AR_PRESET_task_delay" → return rich preset data
    if analysis_id.startswith("AR_PRESET_"):
        preset_key = analysis_id.replace("AR_PRESET_", "")
        preset = _get_preset_analysis(preset_key)
        if preset:
            return success_response(data=preset)
        raise HTTPException(status_code=404, detail="预设场景不存在")

    try:
        aid = int(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的分析ID")
    data = service.get_analysis(aid)
    if not data:
        raise HTTPException(status_code=404, detail="分析记录不存在")
    return success_response(data=data)


@router.get("/analysis/{analysis_id}/steps")
async def get_analysis_steps(analysis_id: str):
    """Get analysis trace steps."""
    try:
        aid = int(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的分析ID")
    data = service.get_analysis_steps(aid)
    return success_response(data=data)


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


# ── Task List ────────────────────────────────────────────────────

@router.get("/task-list")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    status: Optional[str] = None,
):
    """List RCA tasks for the task-list page."""
    data = service.get_task_list(page, page_size, status=status)
    return paginated_response(data["items"], data["total"], data["page"], data["page_size"])
