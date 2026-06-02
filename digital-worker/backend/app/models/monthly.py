import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float, Boolean,
    ForeignKey, JSON, DECIMAL, Enum as SAEnum, Time, BigInteger
)
from sqlalchemy.orm import relationship
from app.database import Base


class MaMonthAccountConfig(Base):
    """月账配置"""
    __tablename__ = "ma_month_account_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_month = Column(String(7), nullable=False, comment="账期(YYYY-MM)")
    account_name = Column(String(200), comment="账期名称")
    account_type = Column(String(50), comment="账期类型: monthly/quarterly/yearly")
    start_date = Column(Date, comment="开始日期")
    end_date = Column(Date, comment="结束日期")
    status = Column(String(20), default="pending", comment="状态: pending/processing/completed/failed")
    progress = Column(Float, default=0, comment="进度(0-100)")
    total_tasks = Column(Integer, default=0, comment="总任务数")
    completed_tasks = Column(Integer, default=0, comment="已完成任务数")
    failed_tasks = Column(Integer, default=0, comment="失败任务数")
    quality_score = Column(Float, comment="质量评分")
    owner = Column(String(100), comment="负责人")
    description = Column(Text, comment="描述")
    remark = Column(Text, comment="备注")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaTaskMonitor(Base):
    """任务监控"""
    __tablename__ = "ma_task_monitor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_month = Column(String(7), comment="账期")
    task_code = Column(String(100), nullable=False, comment="任务编码")
    task_name = Column(String(200), comment="任务名称")
    task_type = Column(String(50), comment="任务类型")
    priority = Column(String(20), default="normal", comment="优先级: urgent/high/normal/low")
    status = Column(String(20), default="pending", comment="状态: pending/running/completed/failed/skipped")
    progress = Column(Float, default=0, comment="进度")
    plan_start_time = Column(DateTime, comment="计划开始时间")
    plan_end_time = Column(DateTime, comment="计划结束时间")
    actual_start_time = Column(DateTime, comment="实际开始时间")
    actual_end_time = Column(DateTime, comment="实际结束时间")
    duration_seconds = Column(Integer, comment="实际耗时(秒)")
    expected_duration = Column(Integer, comment="预期耗时(秒)")
    owner = Column(String(100), comment="负责人")
    dependency_ids = Column(JSON, comment="依赖任务ID列表")
    retry_count = Column(Integer, default=0, comment="重试次数")
    max_retries = Column(Integer, default=3, comment="最大重试次数")
    error_message = Column(Text, comment="错误信息")
    execution_log = Column(Text, comment="执行日志")
    result_summary = Column(JSON, comment="结果摘要")
    is_critical = Column(Boolean, default=False, comment="是否关键任务")
    notify_on_failure = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaAuditResult(Base):
    """月账审计结果"""
    __tablename__ = "ma_audit_result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_month = Column(String(7), comment="账期")
    audit_type = Column(String(50), comment="审计类型: data_integrity/data_accuracy/data_timeliness")
    result = Column(String(20), comment="结果: pass/warning/fail")
    total_checks = Column(Integer, default=0, comment="总检查项")
    passed_checks = Column(Integer, default=0, comment="通过数")
    failed_checks = Column(Integer, default=0, comment="失败数")
    pass_rate = Column(Float, comment="通过率")
    details = Column(JSON, comment="详细结果")
    checked_by = Column(String(100), comment="检查人")
    checked_at = Column(DateTime, comment="检查时间")
    created_at = Column(DateTime, default=datetime.datetime.now)


class MaAdjustmentRecord(Base):
    """调账记录"""
    __tablename__ = "ma_adjustment_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_month = Column(String(7), comment="账期")
    adjustment_type = Column(String(50), comment="调账类型: data_correction/amount_adjustment/other")
    target_table = Column(String(200), comment="目标表")
    target_record_id = Column(String(100), comment="目标记录ID")
    original_value = Column(JSON, comment="原值")
    new_value = Column(JSON, comment="新值")
    reason = Column(Text, comment="调账原因")
    operator = Column(String(100), comment="操作人")
    approver = Column(String(100), comment="审批人")
    status = Column(String(20), default="pending", comment="状态: pending/approved/rejected")
    apply_time = Column(DateTime, comment="申请时间")
    approve_time = Column(DateTime, comment="审批时间")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaDailyReport(Base):
    """日报"""
    __tablename__ = "ma_daily_report"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(Date, nullable=False, comment="报告日期")
    account_month = Column(String(7), comment="所属账期")
    title = Column(String(300), comment="标题")
    content = Column(JSON, comment="报告内容(JSON结构化)")
    summary = Column(Text, comment="摘要")
    task_completed = Column(Integer, default=0, comment="完成任务数")
    task_total = Column(Integer, default=0, comment="任务总数")
    exception_count = Column(Integer, default=0, comment="异常数")
    quality_score = Column(Float, comment="质量评分")
    progress = Column(Float, comment="整体进度")
    ai_generated = Column(Boolean, default=False, comment="是否AI生成")
    status = Column(String(20), default="draft", comment="状态: draft/published")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaSummaryReport(Base):
    """月总结报告"""
    __tablename__ = "ma_summary_report"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_month = Column(String(7), nullable=False, comment="账期")
    title = Column(String(300), comment="标题")
    report_type = Column(String(20), default="monthly", comment="报告类型: monthly/quarterly/yearly")
    overview = Column(Text, comment="概述")
    key_metrics = Column(JSON, comment="关键指标")
    progress_summary = Column(JSON, comment="进度总结")
    problem_analysis = Column(Text, comment="问题分析")
    achievements = Column(Text, comment="成果")
    improvement_plan = Column(Text, comment="改进计划")
    attachments = Column(JSON, comment="附件")
    status = Column(String(20), default="draft", comment="状态: draft/published/archived")
    exception_flag = Column(Boolean, default=False, comment="异常标记")
    exception_detail = Column(Text, comment="异常详情")
    publisher = Column(String(100), comment="发布人")
    publish_time = Column(DateTime, comment="发布时间")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaKpiMetrics(Base):
    """KPI指标"""
    __tablename__ = "ma_kpi_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_month = Column(String(7), comment="账期")
    metric_code = Column(String(100), nullable=False, comment="指标编码")
    metric_name = Column(String(200), comment="指标名称")
    metric_category = Column(String(50), comment="指标分类: efficiency/quality/progress/cost")
    target_value = Column(Float, comment="目标值")
    actual_value = Column(Float, comment="实际值")
    unit = Column(String(20), comment="单位")
    trend = Column(String(20), comment="趋势: up/down/stable")
    status = Column(String(20), comment="状态: good/warning/bad")
    formula = Column(String(500), comment="计算公式")
    data_source = Column(String(200), comment="数据来源")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaMilestoneTrack(Base):
    """里程碑追踪"""
    __tablename__ = "ma_milestone_track"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_month = Column(String(7), comment="账期")
    milestone_name = Column(String(200), nullable=False, comment="里程碑名称")
    milestone_type = Column(String(50), comment="里程碑类型")
    plan_date = Column(Date, comment="计划日期")
    actual_date = Column(Date, comment="实际日期")
    status = Column(String(20), default="pending", comment="状态: pending/completed/delayed")
    delay_days = Column(Integer, default=0, comment="延迟天数")
    completion_percentage = Column(Float, comment="完成百分比")
    responsible_person = Column(String(100), comment="责任人")
    description = Column(Text, comment="描述")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaAlertRecord(Base):
    """告警记录"""
    __tablename__ = "ma_alert_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_month = Column(String(7), comment="账期")
    alert_title = Column(String(300), comment="告警标题")
    alert_type = Column(String(50), comment="告警类型: task_failure/data_anomaly/schedule_delay/quality_issue")
    alert_level = Column(String(20), default="info", comment="告警级别: critical/warning/info")
    source = Column(String(100), comment="告警来源")
    content = Column(Text, comment="告警内容")
    related_task_id = Column(Integer, comment="关联任务ID")
    related_task_name = Column(String(200), comment="关联任务名称")
    status = Column(String(20), default="unread", comment="状态: unread/read/handled/ignored")
    handler = Column(String(100), comment="处理人")
    handle_time = Column(DateTime, comment="处理时间")
    handle_result = Column(Text, comment="处理结果")
    is_upgraded = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)


class MaMlModelConfig(Base):
    """ML模型配置"""
    __tablename__ = "ma_ml_model_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(200), nullable=False, comment="模型名称")
    model_code = Column(String(100), unique=True, comment="模型编码")
    model_type = Column(String(50), comment="模型类型: forecast/anomaly_detection/classification/regression")
    model_version = Column(String(50), comment="模型版本")
    algorithm = Column(String(100), comment="算法")
    parameters = Column(JSON, comment="参数配置")
    features = Column(JSON, comment="特征列表")
    target_metric = Column(String(200), comment="目标指标")
    training_frequency = Column(String(20), comment="训练频率")
    last_trained_at = Column(DateTime, comment="最后训练时间")
    accuracy = Column(Float, comment="准确率")
    status = Column(String(20), default="inactive", comment="状态: active/inactive/deprecated")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaConfigStage(Base):
    """月账作业阶段配置"""
    __tablename__ = "ma_config_stage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stage_code = Column(String(50), unique=True, nullable=False, comment="阶段编码")
    name = Column(String(200), nullable=False, comment="阶段名称")
    sort_order = Column(Integer, default=0, comment="排序")
    status = Column(String(20), default="pending", comment="状态: completed/pending/running")
    completed_at = Column(DateTime, comment="完成时间")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaConfigMilestone(Base):
    """月账里程碑配置"""
    __tablename__ = "ma_config_milestone"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stage_id = Column(Integer, ForeignKey("ma_config_stage.id"), nullable=False, comment="所属阶段ID")
    milestone_code = Column(String(50), unique=True, nullable=False, comment="里程碑编码")
    name = Column(String(200), nullable=False, comment="里程碑名称")
    sort_order = Column(Integer, default=0, comment="排序")
    status = Column(String(20), default="pending", comment="状态: completed/pending/running")
    progress_pct = Column(Float, default=0, comment="完成百分比")
    completed_at = Column(DateTime, comment="完成时间")
    stage = relationship("MaConfigStage", backref="milestones")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaConfigWorkPlan(Base):
    """月账作业计划配置"""
    __tablename__ = "ma_config_work_plan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    milestone_id = Column(Integer, ForeignKey("ma_config_milestone.id"), nullable=False, comment="所属里程碑ID")
    plan_code = Column(String(50), unique=True, nullable=False, comment="计划编码")
    seq_no = Column(Integer, default=0, comment="序号")
    name = Column(String(200), nullable=False, comment="计划名称")
    time_point = Column(String(50), comment="时间点")
    task_mode = Column(String(50), default="人工", comment="执行方式: 人工/数字员工")
    is_system_task = Column(Boolean, default=False, comment="是否系统任务")
    status = Column(String(20), default="pending", comment="状态: completed/pending/running")
    completed_at = Column(DateTime, comment="完成时间")
    milestone = relationship("MaConfigMilestone", backref="work_plans")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class MaConfigTask(Base):
    """月账任务配置"""
    __tablename__ = "ma_config_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("ma_config_work_plan.id"), nullable=False, comment="所属计划ID")
    task_code = Column(String(50), unique=True, nullable=False, comment="任务编码")
    task_type = Column(String(50), default="MANUAL_OP", comment="任务类型: TDP_TASK/PUBLISH_MSG/MANUAL_OP/SQL_SCRIPT")
    content = Column(Text, nullable=False, comment="任务内容")
    sort_order = Column(Integer, default=0, comment="排序")
    status = Column(String(20), default="pending", comment="状态: completed/pending/running/paused/manual_skipped")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    work_plan = relationship("MaConfigWorkPlan", backref="tasks")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
