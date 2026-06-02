import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float, Boolean,
    ForeignKey, JSON, BigInteger
)
from sqlalchemy.orm import relationship
from app.database import Base


class OpsTaskLineage(Base):
    """任务血缘关系"""
    __tablename__ = "ops_task_lineage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_code = Column(String(100), nullable=False, comment="任务编码")
    task_name = Column(String(200), comment="任务名称")
    task_type = Column(String(50), comment="任务类型: etl/dqc/report/api")
    upstream_tasks = Column(JSON, comment="上游任务列表")
    downstream_tasks = Column(JSON, comment="下游任务列表")
    datasource_input = Column(String(200), comment="输入数据源")
    datasource_output = Column(String(200), comment="输出数据源")
    schedule_type = Column(String(20), comment="调度类型")
    owner = Column(String(100), comment="负责人")
    department = Column(String(100), comment="所属部门")
    description = Column(Text, comment="描述")
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class OpsProblemCase(Base):
    """问题案例库"""
    __tablename__ = "ops_problem_case"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_title = Column(String(300), nullable=False, comment="案例标题")
    case_type = Column(String(50), comment="案例类型: data_quality/data_delay/system_fault/business")
    case_source = Column(String(50), comment="案例来源: manual/auto/imported")
    status = Column(String(20), default="open", comment="状态")
    severity = Column(String(20), comment="严重程度: critical/high/medium/low")
    description = Column(Text, comment="问题描述")
    impact_range = Column(Text, comment="影响范围")
    root_cause = Column(Text, comment="根因分析")
    solution = Column(Text, comment="解决方案")
    lessons_learned = Column(Text, comment="经验教训")
    tags = Column(JSON, comment="标签")
    related_task_code = Column(String(100), comment="关联任务编码")
    related_tables = Column(JSON, comment="关联表")
    handler = Column(String(100), comment="处理人")
    handler_department = Column(String(100), comment="处理部门")
    occurrence_time = Column(DateTime, comment="发生时间")
    resolve_time = Column(DateTime, comment="解决时间")
    resolution_duration = Column(Integer, comment="解决时长(分钟)")
    is_template = Column(Boolean, default=False, comment="是否模板")
    usage_count = Column(Integer, default=0, comment="使用次数")
    rating = Column(Float, comment="评分")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class OpsAnalysisPath(Base):
    """分析路径模板"""
    __tablename__ = "ops_analysis_path"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path_name = Column(String(200), nullable=False, comment="路径名称")
    path_type = Column(String(50), comment="路径类型: data_delay/data_quality/system/business")
    steps = Column(JSON, comment="分析步骤列表")
    applicable_scenarios = Column(Text, comment="适用场景")
    expected_duration = Column(Integer, comment="预计时长(分钟)")
    success_rate = Column(Float, comment="成功率")
    usage_count = Column(Integer, default=0)
    status = Column(Integer, default=1)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class OpsRootCauseType(Base):
    """根因类型字典"""
    __tablename__ = "ops_root_cause_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_code = Column(String(100), unique=True, comment="类型编码")
    type_name = Column(String(200), nullable=False, comment="类型名称")
    parent_id = Column(Integer, ForeignKey("ops_root_cause_type.id"), comment="父类型ID")
    level = Column(Integer, default=1, comment="层级")
    description = Column(Text, comment="描述")
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)

    children = relationship("OpsRootCauseType", backref="parent", remote_side=[id])


class OpsRootCauseAnalysis(Base):
    """根因分析记录"""
    __tablename__ = "ops_root_cause_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("ops_problem_case.id"), comment="关联案例ID")
    path_id = Column(Integer, ForeignKey("ops_analysis_path.id"), comment="关联路径ID")
    analysis_title = Column(String(300), comment="分析标题")
    problem_description = Column(Text, comment="问题描述")
    analysis_process = Column(JSON, comment="分析过程")
    conclusion = Column(Text, comment="分析结论")
    root_cause_type_id = Column(Integer, ForeignKey("ops_root_cause_type.id"), comment="根因类型")
    root_cause_desc = Column(Text, comment="根因描述")
    confidence = Column(Float, comment="置信度")
    status = Column(String(20), default="analyzing", comment="状态: analyzing/completed/failed")
    is_saved_as_case = Column(Boolean, default=False, comment="是否已保存为案例")
    analysis_duration = Column(Integer, comment="分析时长(秒)")
    ai_assisted = Column(Boolean, default=False, comment="是否AI辅助")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    case = relationship("OpsProblemCase", backref="analyses")
    path = relationship("OpsAnalysisPath", backref="analyses")
    root_cause_type = relationship("OpsRootCauseType", backref="analyses")


class OpsAnalysisTraceLog(Base):
    """分析追踪日志"""
    __tablename__ = "ops_analysis_trace_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("ops_root_cause_analysis.id"), comment="分析ID")
    step_name = Column(String(200), comment="步骤名称")
    step_order = Column(Integer, comment="步骤顺序")
    action = Column(String(100), comment="操作")
    input_data = Column(JSON, comment="输入数据")
    output_data = Column(JSON, comment="输出数据")
    reasoning = Column(Text, comment="推理过程")
    status = Column(String(20), default="completed", comment="状态")
    duration = Column(Integer, comment="耗时(毫秒)")
    created_at = Column(DateTime, default=datetime.datetime.now)

    analysis = relationship("OpsRootCauseAnalysis", backref="trace_logs")


class OpsCaseUsageStats(Base):
    """案例使用统计"""
    __tablename__ = "ops_case_usage_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("ops_problem_case.id"), comment="案例ID")
    usage_date = Column(Date, comment="使用日期")
    usage_count = Column(Integer, default=0, comment="使用次数")
    match_count = Column(Integer, default=0, comment="匹配次数")
    adopt_count = Column(Integer, default=0, comment="采纳次数")
    feedback_count = Column(Integer, default=0, comment="反馈次数")
    avg_rating = Column(Float, comment="平均评分")
    created_at = Column(DateTime, default=datetime.datetime.now)

    case = relationship("OpsProblemCase", backref="usage_stats")


class OpsUserFeedback(Base):
    """用户反馈"""
    __tablename__ = "ops_user_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("ops_root_cause_analysis.id"), comment="分析ID")
    case_id = Column(Integer, ForeignKey("ops_problem_case.id"), comment="案例ID")
    feedback_type = Column(String(50), comment="反馈类型: helpful/useful/accurate/timely/other")
    rating = Column(Integer, comment="评分(1-5)")
    content = Column(Text, comment="反馈内容")
    user_name = Column(String(100), comment="用户名称")
    user_department = Column(String(100), comment="用户部门")
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
