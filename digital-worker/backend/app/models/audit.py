import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float, Boolean,
    ForeignKey, JSON, DECIMAL, Enum as SAEnum, Time, BigInteger
)
from sqlalchemy.orm import relationship
from app.database import Base


class DqAuditFieldConfig(Base):
    """数据质量审计字段配置"""
    __tablename__ = "dq_audit_field_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_name = Column(String(200), nullable=False, comment="字段名称")
    field_desc = Column(String(500), comment="字段描述")
    datasource_id = Column(String(100), comment="数据源ID")
    datasource_name = Column(String(200), comment="数据源名称")
    schema_name = Column(String(200), comment="模式名")
    table_name = Column(String(200), comment="表名")
    field_type = Column(String(100), comment="字段类型")
    field_length = Column(Integer, comment="字段长度")
    is_nullable = Column(Boolean, default=True, comment="是否可空")
    default_value = Column(String(500), comment="默认值")
    sample_data = Column(Text, comment="样例数据")
    status = Column(Integer, default=1, comment="状态: 0禁用 1启用")
    remark = Column(String(500), comment="备注")
    created_by = Column(String(100), comment="创建人")
    created_at = Column(DateTime, default=datetime.datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now, comment="更新时间")


class DqAuditRuleConfig(Base):
    """数据质量审计规则配置"""
    __tablename__ = "dq_audit_rule_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(200), nullable=False, comment="规则名称")
    rule_code = Column(String(100), unique=True, comment="规则编码")
    rule_type = Column(String(50), comment="规则类型: null_check/duplicate/range/format/custom")
    rule_level = Column(String(20), comment="规则级别: error/warning/info")
    rule_content = Column(JSON, comment="规则内容(JSON)")
    field_id = Column(Integer, ForeignKey("dq_audit_field_config.id"), comment="关联字段ID")
    field_name = Column(String(200), comment="字段名称")
    table_name = Column(String(200), comment="所属表名")
    threshold = Column(Float, comment="告警阈值")
    severity = Column(String(20), default="medium", comment="严重程度: high/medium/low")
    status = Column(Integer, default=1, comment="状态")
    ai_generated = Column(Boolean, default=False, comment="是否AI生成")
    generate_task_id = Column(String(100), comment="AI生成任务ID")
    confirm_status = Column(String(20), default="pending", comment="确认状态: pending/confirmed/rejected")
    created_by = Column(String(100), comment="创建人")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    field = relationship("DqAuditFieldConfig", backref="rules")


class DqAuditTaskConfig(Base):
    """数据质量审计任务配置"""
    __tablename__ = "dq_audit_task_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(200), nullable=False, comment="任务名称")
    task_type = Column(String(50), comment="任务类型: field_audit/rule_audit/full_audit")
    rule_ids = Column(JSON, comment="关联规则ID列表")
    field_ids = Column(JSON, comment="关联字段ID列表")
    schedule_type = Column(String(20), default="manual", comment="调度类型: manual/daily/weekly/monthly")
    schedule_config = Column(JSON, comment="调度配置")
    execute_strategy = Column(String(50), comment="执行策略: full/sample")
    sample_rate = Column(Float, default=100.0, comment="采样率(%)")
    status = Column(Integer, default=1, comment="状态")
    importance = Column(Integer, default=1, comment="重要性")
    last_execute_time = Column(DateTime, comment="最后执行时间")
    last_execute_result = Column(String(20), comment="最后执行结果")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class DqTaskImportanceConfig(Base):
    """任务重要性配置"""
    __tablename__ = "dq_task_importance_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer, nullable=False, comment="重要性级别")
    level_name = Column(String(100), comment="级别名称")
    color = Column(String(20), comment="颜色标识")
    score_range = Column(String(100), comment="评分范围")
    description = Column(String(500), comment="描述")
    notify_channels = Column(JSON, comment="通知渠道")
    response_time_minutes = Column(Integer, comment="响应时间(分钟)")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class DqAlertUpgradeRule(Base):
    """告警升级规则"""
    __tablename__ = "dq_alert_upgrade_rule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(200), nullable=False, comment="规则名称")
    alert_type = Column(String(50), comment="告警类型")
    trigger_condition = Column(JSON, comment="触发条件")
    upgrade_level = Column(Integer, comment="升级级别")
    notify_targets = Column(JSON, comment="通知目标")
    notify_template = Column(Text, comment="通知模板")
    max_upgrade_count = Column(Integer, default=3, comment="最大升级次数")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)


class DqAuditExecution(Base):
    """审计执行记录"""
    __tablename__ = "dq_audit_execution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("dq_audit_task_config.id"), comment="任务ID")
    task_name = Column(String(200), comment="任务名称")
    execute_time = Column(DateTime, default=datetime.datetime.now, comment="执行时间")
    execute_duration = Column(Float, comment="执行时长(秒)")
    total_records = Column(Integer, comment="总记录数")
    sample_records = Column(Integer, comment="采样记录数")
    passed_records = Column(Integer, comment="通过记录数")
    failed_records = Column(Integer, comment="失败记录数")
    pass_rate = Column(Float, comment="通过率")
    error_message = Column(Text, comment="错误信息")
    status = Column(String(20), default="pending", comment="执行状态: pending/running/completed/failed")
    result_summary = Column(JSON, comment="结果摘要")
    created_at = Column(DateTime, default=datetime.datetime.now)

    task = relationship("DqAuditTaskConfig", backref="executions")


class DqAuditException(Base):
    """审计异常记录"""
    __tablename__ = "dq_audit_exception"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey("dq_audit_execution.id"), comment="执行ID")
    rule_id = Column(Integer, ForeignKey("dq_audit_rule_config.id"), comment="规则ID")
    rule_name = Column(String(200), comment="规则名称")
    field_name = Column(String(200), comment="字段名称")
    table_name = Column(String(200), comment="表名")
    exception_type = Column(String(50), comment="异常类型")
    exception_value = Column(Text, comment="异常值")
    exception_count = Column(Integer, comment="异常数量")
    exception_rate = Column(Float, comment="异常率")
    severity = Column(String(20), default="medium", comment="严重程度")
    status = Column(String(20), default="open", comment="状态: open/handling/resolved/closed")
    handler = Column(String(100), comment="处理人")
    handle_time = Column(DateTime, comment="处理时间")
    handle_result = Column(Text, comment="处理结果")
    alert_level = Column(String(20), comment="告警级别")
    is_upgraded = Column(Boolean, default=False, comment="是否已升级")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    execution = relationship("DqAuditExecution", backref="exceptions")
    rule = relationship("DqAuditRuleConfig", backref="exceptions")


class DqAuditReport(Base):
    """审计报告"""
    __tablename__ = "dq_audit_report"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_name = Column(String(200), nullable=False, comment="报告名称")
    report_type = Column(String(50), comment="报告类型: daily/weekly/monthly/custom")
    execution_ids = Column(JSON, comment="关联执行ID列表")
    total_executions = Column(Integer, comment="总执行次数")
    total_records = Column(Integer, comment="总记录数")
    total_exceptions = Column(Integer, comment="总异常数")
    overall_pass_rate = Column(Float, comment="整体通过率")
    summary = Column(Text, comment="报告摘要")
    conclusion = Column(Text, comment="结论")
    recommendations = Column(JSON, comment="改进建议")
    report_data = Column(JSON, comment="报告详细数据")
    status = Column(String(20), default="draft", comment="状态: draft/published")
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
