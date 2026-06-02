-- ============================================================
-- 数据运维数字员工平台 - 数据库建表语句
-- Database: db_digital_worker
-- Charset: utf8mb4
-- ============================================================

CREATE DATABASE IF NOT EXISTS db_digital_worker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_digital_worker;

-- ============================================================
-- 告警升级规则表
-- ============================================================
CREATE TABLE dq_alert_upgrade_rule (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    rule_name VARCHAR(200) NOT NULL COMMENT '规则名称',
    alert_type VARCHAR(50) COMMENT '告警类型',
    trigger_condition JSON COMMENT '触发条件',
    upgrade_level INT COMMENT '升级级别',
    notify_targets JSON COMMENT '通知目标',
    notify_template TEXT COMMENT '通知模板',
    max_upgrade_count INT DEFAULT 3 COMMENT '最大升级次数',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '告警升级规则表';

-- ============================================================
-- 审计字段配置表
-- ============================================================
CREATE TABLE dq_audit_field_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    field_name VARCHAR(200) NOT NULL COMMENT '字段名称',
    field_desc VARCHAR(500) COMMENT '字段描述',
    datasource_id VARCHAR(100) COMMENT '数据源ID',
    datasource_name VARCHAR(200) COMMENT '数据源名称',
    schema_name VARCHAR(200) COMMENT '模式名',
    table_name VARCHAR(200) COMMENT '表名',
    field_type VARCHAR(100) COMMENT '字段类型',
    field_length INT COMMENT '字段长度',
    is_nullable TINYINT(1) DEFAULT 1 COMMENT '是否可空',
    default_value VARCHAR(500) COMMENT '默认值',
    sample_data TEXT COMMENT '样例数据',
    status INT DEFAULT 1 COMMENT '状态: 0禁用 1启用',
    remark VARCHAR(500) COMMENT '备注',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '审计字段配置表';

-- ============================================================
-- 审计报告表
-- ============================================================
CREATE TABLE dq_audit_report (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    report_name VARCHAR(200) NOT NULL COMMENT '报告名称',
    report_type VARCHAR(50) COMMENT '报告类型: daily/weekly/monthly/custom',
    execution_ids JSON COMMENT '关联执行ID列表',
    total_executions INT COMMENT '总执行次数',
    total_records INT COMMENT '总记录数',
    total_exceptions INT COMMENT '总异常数',
    overall_pass_rate FLOAT COMMENT '整体通过率',
    summary TEXT COMMENT '报告摘要',
    conclusion TEXT COMMENT '结论',
    recommendations JSON COMMENT '改进建议',
    report_data JSON COMMENT '报告详细数据',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/published',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '审计报告表';

-- ============================================================
-- 审计任务配置表
-- ============================================================
CREATE TABLE dq_audit_task_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    task_name VARCHAR(200) NOT NULL COMMENT '任务名称',
    task_type VARCHAR(50) COMMENT '任务类型: field_audit/rule_audit/full_audit',
    rule_ids JSON COMMENT '关联规则ID列表',
    field_ids JSON COMMENT '关联字段ID列表',
    schedule_type VARCHAR(20) DEFAULT 'manual' COMMENT '调度类型: manual/daily/weekly/monthly',
    schedule_config JSON COMMENT '调度配置',
    execute_strategy VARCHAR(50) COMMENT '执行策略: full/sample',
    sample_rate FLOAT DEFAULT 100.0 COMMENT '采样率(%)',
    status INT DEFAULT 1 COMMENT '状态',
    importance INT DEFAULT 1 COMMENT '重要性',
    last_execute_time DATETIME COMMENT '最后执行时间',
    last_execute_result VARCHAR(20) COMMENT '最后执行结果',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '审计任务配置表';

-- ============================================================
-- 任务重要性配置表
-- ============================================================
CREATE TABLE dq_task_importance_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    level INT NOT NULL COMMENT '重要性级别',
    level_name VARCHAR(100) COMMENT '级别名称',
    color VARCHAR(20) COMMENT '颜色标识',
    score_range VARCHAR(100) COMMENT '评分范围',
    description VARCHAR(500) COMMENT '描述',
    notify_channels JSON COMMENT '通知渠道',
    response_time_minutes INT COMMENT '响应时间(分钟)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '任务重要性配置表';

-- ============================================================
-- 审计规则配置表
-- ============================================================
CREATE TABLE dq_audit_rule_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    rule_name VARCHAR(200) NOT NULL COMMENT '规则名称',
    rule_code VARCHAR(100) UNIQUE COMMENT '规则编码',
    rule_type VARCHAR(50) COMMENT '规则类型: null_check/duplicate/range/format/custom',
    rule_level VARCHAR(20) COMMENT '规则级别: error/warning/info',
    rule_content JSON COMMENT '规则内容(JSON)',
    field_id INT COMMENT '关联字段ID',
    field_name VARCHAR(200) COMMENT '字段名称',
    table_name VARCHAR(200) COMMENT '所属表名',
    threshold FLOAT COMMENT '告警阈值',
    severity VARCHAR(20) DEFAULT 'medium' COMMENT '严重程度: high/medium/low',
    status INT DEFAULT 1 COMMENT '状态',
    ai_generated TINYINT(1) DEFAULT 0 COMMENT '是否AI生成',
    generate_task_id VARCHAR(100) COMMENT 'AI生成任务ID',
    confirm_status VARCHAR(20) DEFAULT 'pending' COMMENT '确认状态: pending/confirmed/rejected',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '审计规则配置表';

-- ============================================================
-- 审计执行记录表
-- ============================================================
CREATE TABLE dq_audit_execution (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    task_id INT COMMENT '任务ID',
    task_name VARCHAR(200) COMMENT '任务名称',
    execute_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '执行时间',
    execute_duration FLOAT COMMENT '执行时长(秒)',
    total_records INT COMMENT '总记录数',
    sample_records INT COMMENT '采样记录数',
    passed_records INT COMMENT '通过记录数',
    failed_records INT COMMENT '失败记录数',
    pass_rate FLOAT COMMENT '通过率',
    error_message TEXT COMMENT '错误信息',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '执行状态: pending/running/completed/failed',
    result_summary JSON COMMENT '结果摘要',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '审计执行记录表';

-- ============================================================
-- 审计异常记录表
-- ============================================================
CREATE TABLE dq_audit_exception (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    execution_id INT COMMENT '执行ID',
    rule_id INT COMMENT '规则ID',
    rule_name VARCHAR(200) COMMENT '规则名称',
    field_name VARCHAR(200) COMMENT '字段名称',
    table_name VARCHAR(200) COMMENT '表名',
    exception_type VARCHAR(50) COMMENT '异常类型',
    exception_value TEXT COMMENT '异常值',
    exception_count INT COMMENT '异常数量',
    exception_rate FLOAT COMMENT '异常率',
    severity VARCHAR(20) DEFAULT 'medium' COMMENT '严重程度',
    status VARCHAR(20) DEFAULT 'open' COMMENT '状态: open/handling/resolved/closed',
    handler VARCHAR(100) COMMENT '处理人',
    handle_time DATETIME COMMENT '处理时间',
    handle_result TEXT COMMENT '处理结果',
    alert_level VARCHAR(20) COMMENT '告警级别',
    is_upgraded TINYINT(1) DEFAULT 0 COMMENT '是否已升级',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '审计异常记录表';

-- ============================================================
-- 月账期配置表
-- ============================================================
CREATE TABLE ma_month_account_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    account_month VARCHAR(7) NOT NULL COMMENT '账期(YYYY-MM)',
    account_name VARCHAR(200) COMMENT '账期名称',
    account_type VARCHAR(50) COMMENT '账期类型: monthly/quarterly/yearly',
    start_date DATE COMMENT '开始日期',
    end_date DATE COMMENT '结束日期',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/processing/completed/failed',
    progress FLOAT DEFAULT 0 COMMENT '进度(0-100)',
    total_tasks INT DEFAULT 0 COMMENT '总任务数',
    completed_tasks INT DEFAULT 0 COMMENT '已完成任务数',
    failed_tasks INT DEFAULT 0 COMMENT '失败任务数',
    quality_score FLOAT COMMENT '质量评分',
    owner VARCHAR(100) COMMENT '负责人',
    description TEXT COMMENT '描述',
    remark TEXT COMMENT '备注',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '月账期配置表';

-- ============================================================
-- 任务监控表
-- ============================================================
CREATE TABLE ma_task_monitor (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    account_month VARCHAR(7) COMMENT '账期',
    task_code VARCHAR(100) NOT NULL COMMENT '任务编码',
    task_name VARCHAR(200) COMMENT '任务名称',
    task_type VARCHAR(50) COMMENT '任务类型',
    priority VARCHAR(20) DEFAULT 'normal' COMMENT '优先级: urgent/high/normal/low',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/running/completed/failed/skipped',
    progress FLOAT DEFAULT 0 COMMENT '进度',
    plan_start_time DATETIME COMMENT '计划开始时间',
    plan_end_time DATETIME COMMENT '计划结束时间',
    actual_start_time DATETIME COMMENT '实际开始时间',
    actual_end_time DATETIME COMMENT '实际结束时间',
    duration_seconds INT COMMENT '实际耗时(秒)',
    expected_duration INT COMMENT '预期耗时(秒)',
    owner VARCHAR(100) COMMENT '负责人',
    dependency_ids JSON COMMENT '依赖任务ID列表',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    max_retries INT DEFAULT 3 COMMENT '最大重试次数',
    error_message TEXT COMMENT '错误信息',
    execution_log TEXT COMMENT '执行日志',
    result_summary JSON COMMENT '结果摘要',
    is_critical TINYINT(1) DEFAULT 0 COMMENT '是否关键任务',
    notify_on_failure TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '任务监控表';

-- ============================================================
-- 审计结果表
-- ============================================================
CREATE TABLE ma_audit_result (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    account_month VARCHAR(7) COMMENT '账期',
    audit_type VARCHAR(50) COMMENT '审计类型: data_integrity/data_accuracy/data_timeliness',
    result VARCHAR(20) COMMENT '结果: pass/warning/fail',
    total_checks INT DEFAULT 0 COMMENT '总检查项',
    passed_checks INT DEFAULT 0 COMMENT '通过数',
    failed_checks INT DEFAULT 0 COMMENT '失败数',
    pass_rate FLOAT COMMENT '通过率',
    details JSON COMMENT '详细结果',
    checked_by VARCHAR(100) COMMENT '检查人',
    checked_at DATETIME COMMENT '检查时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '审计结果表';

-- ============================================================
-- 调账记录表
-- ============================================================
CREATE TABLE ma_adjustment_record (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    account_month VARCHAR(7) COMMENT '账期',
    adjustment_type VARCHAR(50) COMMENT '调账类型: data_correction/amount_adjustment/other',
    target_table VARCHAR(200) COMMENT '目标表',
    target_record_id VARCHAR(100) COMMENT '目标记录ID',
    original_value JSON COMMENT '原值',
    new_value JSON COMMENT '新值',
    reason TEXT COMMENT '调账原因',
    operator VARCHAR(100) COMMENT '操作人',
    approver VARCHAR(100) COMMENT '审批人',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/approved/rejected',
    apply_time DATETIME COMMENT '申请时间',
    approve_time DATETIME COMMENT '审批时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '调账记录表';

-- ============================================================
-- 月账日报表
-- ============================================================
CREATE TABLE ma_daily_report (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    report_date DATE NOT NULL COMMENT '报告日期',
    account_month VARCHAR(7) COMMENT '所属账期',
    title VARCHAR(300) COMMENT '标题',
    content JSON COMMENT '报告内容(JSON结构化)',
    summary TEXT COMMENT '摘要',
    task_completed INT DEFAULT 0 COMMENT '完成任务数',
    task_total INT DEFAULT 0 COMMENT '任务总数',
    exception_count INT DEFAULT 0 COMMENT '异常数',
    quality_score FLOAT COMMENT '质量评分',
    progress FLOAT COMMENT '整体进度',
    ai_generated TINYINT(1) DEFAULT 0 COMMENT '是否AI生成',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/published',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '月账日报表';

-- ============================================================
-- 月账汇总报告表
-- ============================================================
CREATE TABLE ma_summary_report (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    account_month VARCHAR(7) NOT NULL COMMENT '账期',
    title VARCHAR(300) COMMENT '标题',
    report_type VARCHAR(20) DEFAULT 'monthly' COMMENT '报告类型: monthly/quarterly/yearly',
    overview TEXT COMMENT '概述',
    key_metrics JSON COMMENT '关键指标',
    progress_summary JSON COMMENT '进度总结',
    problem_analysis TEXT COMMENT '问题分析',
    achievements TEXT COMMENT '成果',
    improvement_plan TEXT COMMENT '改进计划',
    attachments JSON COMMENT '附件',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/published/archived',
    exception_flag TINYINT(1) DEFAULT 0 COMMENT '异常标记',
    exception_detail TEXT COMMENT '异常详情',
    publisher VARCHAR(100) COMMENT '发布人',
    publish_time DATETIME COMMENT '发布时间',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '月账汇总报告表';

-- ============================================================
-- KPI指标表
-- ============================================================
CREATE TABLE ma_kpi_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    account_month VARCHAR(7) COMMENT '账期',
    metric_code VARCHAR(100) NOT NULL COMMENT '指标编码',
    metric_name VARCHAR(200) COMMENT '指标名称',
    metric_category VARCHAR(50) COMMENT '指标分类: efficiency/quality/progress/cost',
    target_value FLOAT COMMENT '目标值',
    actual_value FLOAT COMMENT '实际值',
    unit VARCHAR(20) COMMENT '单位',
    trend VARCHAR(20) COMMENT '趋势: up/down/stable',
    status VARCHAR(20) COMMENT '状态: good/warning/bad',
    formula VARCHAR(500) COMMENT '计算公式',
    data_source VARCHAR(200) COMMENT '数据来源',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = 'KPI指标表';

-- ============================================================
-- 里程碑跟踪表
-- ============================================================
CREATE TABLE ma_milestone_track (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    account_month VARCHAR(7) COMMENT '账期',
    milestone_name VARCHAR(200) NOT NULL COMMENT '里程碑名称',
    milestone_type VARCHAR(50) COMMENT '里程碑类型',
    plan_date DATE COMMENT '计划日期',
    actual_date DATE COMMENT '实际日期',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/completed/delayed',
    delay_days INT DEFAULT 0 COMMENT '延迟天数',
    completion_percentage FLOAT COMMENT '完成百分比',
    responsible_person VARCHAR(100) COMMENT '责任人',
    description TEXT COMMENT '描述',
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '里程碑跟踪表';

-- ============================================================
-- 告警记录表
-- ============================================================
CREATE TABLE ma_alert_record (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    account_month VARCHAR(7) COMMENT '账期',
    alert_title VARCHAR(300) COMMENT '告警标题',
    alert_type VARCHAR(50) COMMENT '告警类型: task_failure/data_anomaly/schedule_delay/quality_issue',
    alert_level VARCHAR(20) DEFAULT 'info' COMMENT '告警级别: critical/warning/info',
    source VARCHAR(100) COMMENT '告警来源',
    content TEXT COMMENT '告警内容',
    related_task_id INT COMMENT '关联任务ID',
    related_task_name VARCHAR(200) COMMENT '关联任务名称',
    status VARCHAR(20) DEFAULT 'unread' COMMENT '状态: unread/read/handled/ignored',
    handler VARCHAR(100) COMMENT '处理人',
    handle_time DATETIME COMMENT '处理时间',
    handle_result TEXT COMMENT '处理结果',
    is_upgraded TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '告警记录表';

-- ============================================================
-- 机器学习模型配置表
-- ============================================================
CREATE TABLE ma_ml_model_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    model_name VARCHAR(200) NOT NULL COMMENT '模型名称',
    model_code VARCHAR(100) UNIQUE COMMENT '模型编码',
    model_type VARCHAR(50) COMMENT '模型类型: forecast/anomaly_detection/classification/regression',
    model_version VARCHAR(50) COMMENT '模型版本',
    algorithm VARCHAR(100) COMMENT '算法',
    parameters JSON COMMENT '参数配置',
    features JSON COMMENT '特征列表',
    target_metric VARCHAR(200) COMMENT '目标指标',
    training_frequency VARCHAR(20) COMMENT '训练频率',
    last_trained_at DATETIME COMMENT '最后训练时间',
    accuracy FLOAT COMMENT '准确率',
    status VARCHAR(20) DEFAULT 'inactive' COMMENT '状态: active/inactive/deprecated',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '机器学习模型配置表';

-- ============================================================
-- 月账作业阶段配置表
-- ============================================================
CREATE TABLE ma_config_stage (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    stage_code VARCHAR(50) NOT NULL UNIQUE COMMENT '阶段编码',
    name VARCHAR(200) NOT NULL COMMENT '阶段名称',
    sort_order INT DEFAULT 0 COMMENT '排序',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: completed/pending/running',
    completed_at DATETIME COMMENT '完成时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '月账作业阶段配置表';

-- ============================================================
-- 月账里程碑配置表
-- ============================================================
CREATE TABLE ma_config_milestone (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    stage_id INT NOT NULL COMMENT '所属阶段ID',
    milestone_code VARCHAR(50) NOT NULL UNIQUE COMMENT '里程碑编码',
    name VARCHAR(200) NOT NULL COMMENT '里程碑名称',
    sort_order INT DEFAULT 0 COMMENT '排序',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: completed/pending/running',
    progress_pct FLOAT DEFAULT 0 COMMENT '完成百分比',
    completed_at DATETIME COMMENT '完成时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '月账里程碑配置表';

-- ============================================================
-- 月账作业计划配置表
-- ============================================================
CREATE TABLE ma_config_work_plan (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    milestone_id INT NOT NULL COMMENT '所属里程碑ID',
    plan_code VARCHAR(50) NOT NULL UNIQUE COMMENT '计划编码',
    seq_no INT DEFAULT 0 COMMENT '序号',
    name VARCHAR(200) NOT NULL COMMENT '计划名称',
    time_point VARCHAR(50) COMMENT '时间点',
    task_mode VARCHAR(50) DEFAULT '人工' COMMENT '执行方式: 人工/数字员工',
    is_system_task TINYINT(1) DEFAULT 0 COMMENT '是否系统任务',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: completed/pending/running',
    completed_at DATETIME COMMENT '完成时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '月账作业计划配置表';

-- ============================================================
-- 月账任务配置表
-- ============================================================
CREATE TABLE ma_config_task (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    plan_id INT NOT NULL COMMENT '所属计划ID',
    task_code VARCHAR(50) NOT NULL UNIQUE COMMENT '任务编码',
    task_type VARCHAR(50) DEFAULT 'MANUAL_OP' COMMENT '任务类型: TDP_TASK/PUBLISH_MSG/MANUAL_OP/SQL_SCRIPT',
    content TEXT NOT NULL COMMENT '任务内容',
    sort_order INT DEFAULT 0 COMMENT '排序',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: completed/pending/running/paused/manual_skipped',
    start_time DATETIME COMMENT '开始时间',
    end_time DATETIME COMMENT '结束时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '月账任务配置表';

-- ============================================================
-- 任务血缘关系表
-- ============================================================
CREATE TABLE ops_task_lineage (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    task_code VARCHAR(100) NOT NULL COMMENT '任务编码',
    task_name VARCHAR(200) COMMENT '任务名称',
    task_type VARCHAR(50) COMMENT '任务类型: etl/dqc/report/api',
    upstream_tasks JSON COMMENT '上游任务列表',
    downstream_tasks JSON COMMENT '下游任务列表',
    datasource_input VARCHAR(200) COMMENT '输入数据源',
    datasource_output VARCHAR(200) COMMENT '输出数据源',
    schedule_type VARCHAR(20) COMMENT '调度类型',
    owner VARCHAR(100) COMMENT '负责人',
    department VARCHAR(100) COMMENT '所属部门',
    description TEXT COMMENT '描述',
    status INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '任务血缘关系表';

-- ============================================================
-- 问题案例表
-- ============================================================
CREATE TABLE ops_problem_case (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    case_title VARCHAR(300) NOT NULL COMMENT '案例标题',
    case_type VARCHAR(50) COMMENT '案例类型: data_quality/data_delay/system_fault/business',
    case_source VARCHAR(50) COMMENT '案例来源: manual/auto/imported',
    status VARCHAR(20) DEFAULT 'open' COMMENT '状态',
    severity VARCHAR(20) COMMENT '严重程度: critical/high/medium/low',
    description TEXT COMMENT '问题描述',
    impact_range TEXT COMMENT '影响范围',
    root_cause TEXT COMMENT '根因分析',
    solution TEXT COMMENT '解决方案',
    lessons_learned TEXT COMMENT '经验教训',
    tags JSON COMMENT '标签',
    related_task_code VARCHAR(100) COMMENT '关联任务编码',
    related_tables JSON COMMENT '关联表',
    handler VARCHAR(100) COMMENT '处理人',
    handler_department VARCHAR(100) COMMENT '处理部门',
    occurrence_time DATETIME COMMENT '发生时间',
    resolve_time DATETIME COMMENT '解决时间',
    resolution_duration INT COMMENT '解决时长(分钟)',
    is_template TINYINT(1) DEFAULT 0 COMMENT '是否模板',
    usage_count INT DEFAULT 0 COMMENT '使用次数',
    rating FLOAT COMMENT '评分',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '问题案例表';

-- ============================================================
-- 分析路径表
-- ============================================================
CREATE TABLE ops_analysis_path (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    path_name VARCHAR(200) NOT NULL COMMENT '路径名称',
    path_type VARCHAR(50) COMMENT '路径类型: data_delay/data_quality/system/business',
    steps JSON COMMENT '分析步骤列表',
    applicable_scenarios TEXT COMMENT '适用场景',
    expected_duration INT COMMENT '预计时长(分钟)',
    success_rate FLOAT COMMENT '成功率',
    usage_count INT DEFAULT 0,
    status INT DEFAULT 1,
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '分析路径表';

-- ============================================================
-- 根因类型表
-- ============================================================
CREATE TABLE ops_root_cause_type (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    type_code VARCHAR(100) UNIQUE COMMENT '类型编码',
    type_name VARCHAR(200) NOT NULL COMMENT '类型名称',
    parent_id INT COMMENT '父类型ID',
    level INT DEFAULT 1 COMMENT '层级',
    description TEXT COMMENT '描述',
    sort_order INT DEFAULT 0,
    status INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '根因类型表';

-- ============================================================
-- 根因分析表
-- ============================================================
CREATE TABLE ops_root_cause_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    case_id INT COMMENT '关联案例ID',
    path_id INT COMMENT '关联路径ID',
    analysis_title VARCHAR(300) COMMENT '分析标题',
    problem_description TEXT COMMENT '问题描述',
    analysis_process JSON COMMENT '分析过程',
    conclusion TEXT COMMENT '分析结论',
    root_cause_type_id INT COMMENT '根因类型',
    root_cause_desc TEXT COMMENT '根因描述',
    confidence FLOAT COMMENT '置信度',
    status VARCHAR(20) DEFAULT 'analyzing' COMMENT '状态: analyzing/completed/failed',
    is_saved_as_case TINYINT(1) DEFAULT 0 COMMENT '是否已保存为案例',
    analysis_duration INT COMMENT '分析时长(秒)',
    ai_assisted TINYINT(1) DEFAULT 0 COMMENT '是否AI辅助',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '根因分析表';

-- ============================================================
-- 分析追溯日志表
-- ============================================================
CREATE TABLE ops_analysis_trace_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    analysis_id INT COMMENT '分析ID',
    step_name VARCHAR(200) COMMENT '步骤名称',
    step_order INT COMMENT '步骤顺序',
    action VARCHAR(100) COMMENT '操作',
    input_data JSON COMMENT '输入数据',
    output_data JSON COMMENT '输出数据',
    reasoning TEXT COMMENT '推理过程',
    status VARCHAR(20) DEFAULT 'completed' COMMENT '状态',
    duration INT COMMENT '耗时(毫秒)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '分析追溯日志表';

-- ============================================================
-- 案例使用统计表
-- ============================================================
CREATE TABLE ops_case_usage_stats (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    case_id INT COMMENT '案例ID',
    usage_date DATE COMMENT '使用日期',
    usage_count INT DEFAULT 0 COMMENT '使用次数',
    match_count INT DEFAULT 0 COMMENT '匹配次数',
    adopt_count INT DEFAULT 0 COMMENT '采纳次数',
    feedback_count INT DEFAULT 0 COMMENT '反馈次数',
    avg_rating FLOAT COMMENT '平均评分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '案例使用统计表';

-- ============================================================
-- 用户反馈表
-- ============================================================
CREATE TABLE ops_user_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    analysis_id INT COMMENT '分析ID',
    case_id INT COMMENT '案例ID',
    feedback_type VARCHAR(50) COMMENT '反馈类型: helpful/useful/accurate/timely/other',
    rating INT COMMENT '评分(1-5)',
    content TEXT COMMENT '反馈内容',
    user_name VARCHAR(100) COMMENT '用户名称',
    user_department VARCHAR(100) COMMENT '用户部门',
    is_resolved TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '用户反馈表';

-- ============================================================
-- 部门表
-- ============================================================
CREATE TABLE sys_department (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    dept_name VARCHAR(200) NOT NULL COMMENT '部门名称',
    dept_code VARCHAR(100) UNIQUE COMMENT '部门编码',
    parent_id INT COMMENT '上级部门ID',
    dept_level INT DEFAULT 1 COMMENT '部门层级',
    dept_type VARCHAR(50) COMMENT '部门类型',
    manager VARCHAR(100) COMMENT '部门负责人',
    phone VARCHAR(20) COMMENT '联系电话',
    email VARCHAR(200) COMMENT '邮箱',
    sort_order INT DEFAULT 0,
    status INT DEFAULT 1,
    description TEXT COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '部门表';

-- ============================================================
-- 用户表
-- ============================================================
CREATE TABLE sys_user (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(100) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(200) NOT NULL COMMENT '密码',
    real_name VARCHAR(100) COMMENT '真实姓名',
    email VARCHAR(200) COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    avatar VARCHAR(500) COMMENT '头像',
    department_id INT COMMENT '部门ID',
    position VARCHAR(100) COMMENT '职位',
    status INT DEFAULT 1 COMMENT '状态: 0禁用 1启用',
    is_admin TINYINT(1) DEFAULT 0 COMMENT '是否管理员',
    last_login_time DATETIME COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) COMMENT '最后登录IP',
    remark TEXT COMMENT '备注',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '用户表';

-- ============================================================
-- 角色表
-- ============================================================
CREATE TABLE sys_role (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    role_name VARCHAR(100) NOT NULL UNIQUE COMMENT '角色名称',
    role_code VARCHAR(100) UNIQUE COMMENT '角色编码',
    description TEXT COMMENT '描述',
    status INT DEFAULT 1,
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '角色表';

-- ============================================================
-- 用户角色关联表
-- ============================================================
CREATE TABLE sys_user_role (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    user_id INT NOT NULL COMMENT '用户ID',
    role_id INT NOT NULL COMMENT '角色ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '用户角色关联表';

-- ============================================================
-- 权限表
-- ============================================================
CREATE TABLE sys_permission (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    permission_name VARCHAR(100) NOT NULL COMMENT '权限名称',
    permission_code VARCHAR(100) UNIQUE COMMENT '权限编码',
    menu_path VARCHAR(200) COMMENT '菜单路径',
    parent_id INT COMMENT '父权限ID',
    permission_type VARCHAR(20) DEFAULT 'menu' COMMENT '类型: menu/button/api',
    icon VARCHAR(100) COMMENT '图标',
    sort_order INT DEFAULT 0,
    description TEXT COMMENT '描述',
    status INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '权限表';

-- ============================================================
-- 角色权限关联表
-- ============================================================
CREATE TABLE sys_role_permission (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    role_id INT NOT NULL COMMENT '角色ID',
    permission_id INT NOT NULL COMMENT '权限ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '角色权限关联表';

-- ============================================================
-- 系统审计日志表
-- ============================================================
CREATE TABLE sys_audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    user_id INT COMMENT '用户ID',
    username VARCHAR(100) COMMENT '用户名',
    action_type VARCHAR(50) COMMENT '操作类型: create/update/delete/query/login/logout',
    module VARCHAR(50) COMMENT '功能模块',
    action_detail TEXT COMMENT '操作详情',
    request_url VARCHAR(500) COMMENT '请求URL',
    request_method VARCHAR(10) COMMENT '请求方法',
    request_params JSON COMMENT '请求参数',
    response_code INT COMMENT '响应码',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent VARCHAR(500) COMMENT 'User-Agent',
    duration_ms INT COMMENT '耗时(毫秒)',
    status VARCHAR(10) DEFAULT 'success' COMMENT '状态: success/failure',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '系统审计日志表';

-- ============================================================
-- 系统参数配置表
-- ============================================================
CREATE TABLE sys_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    config_key VARCHAR(200) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_type VARCHAR(50) COMMENT '配置类型: system/business/alert/notification',
    description TEXT COMMENT '描述',
    is_encrypted TINYINT(1) DEFAULT 0 COMMENT '是否加密',
    status INT DEFAULT 1,
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '系统参数配置表';

-- ============================================================
-- 数据字典表
-- ============================================================
CREATE TABLE sys_data_dict (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    dict_key VARCHAR(100) COMMENT '字典键',
    dict_value VARCHAR(200) NOT NULL COMMENT '字典值',
    dict_type VARCHAR(100) NOT NULL COMMENT '字典类型',
    parent_id INT COMMENT '父字典ID',
    sort_order INT DEFAULT 0,
    status INT DEFAULT 1,
    remark TEXT COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '数据字典表';

-- ============================================================
-- 通知记录表
-- ============================================================
CREATE TABLE sys_notification_record (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    notification_type VARCHAR(50) COMMENT '通知类型: alert/reminder/system/business',
    title VARCHAR(300) COMMENT '标题',
    content TEXT COMMENT '内容',
    receiver_id INT COMMENT '接收人ID',
    receiver_name VARCHAR(100) COMMENT '接收人名称',
    channel VARCHAR(50) COMMENT '渠道: system/email/sms/dingtalk/wechat',
    is_read TINYINT(1) DEFAULT 0 COMMENT '是否已读',
    read_time DATETIME COMMENT '阅读时间',
    status VARCHAR(20) DEFAULT 'sent' COMMENT '状态: sent/delivered/failed',
    send_time DATETIME COMMENT '发送时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '通知记录表';

-- ============================================================
-- AI聊天会话表
-- ============================================================
CREATE TABLE ai_chat_session (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    session_title VARCHAR(200) COMMENT '会话标题',
    session_type VARCHAR(50) DEFAULT 'general' COMMENT '会话类型: general/analysis/audit/report',
    user_id INT COMMENT '用户ID',
    user_name VARCHAR(100) COMMENT '用户名',
    context_summary TEXT COMMENT '上下文摘要',
    message_count INT DEFAULT 0 COMMENT '消息数量',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/archived/deleted',
    is_pinned TINYINT(1) DEFAULT 0 COMMENT '是否置顶',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = 'AI聊天会话表';

-- ============================================================
-- AI聊天消息表
-- ============================================================
CREATE TABLE ai_chat_message (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    session_id INT NOT NULL COMMENT '会话ID',
    role VARCHAR(20) NOT NULL COMMENT '角色: user/assistant/system',
    content TEXT NOT NULL COMMENT '消息内容',
    content_type VARCHAR(50) DEFAULT 'text' COMMENT '内容类型: text/markdown/code/image',
    tokens_used INT COMMENT 'Token数量',
    ai_model VARCHAR(100) COMMENT 'AI模型',
    message_metadata JSON COMMENT '元数据',
    feedback_score INT COMMENT '反馈评分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = 'AI聊天消息表';

-- ============================================================
-- AI模型配置表
-- ============================================================
CREATE TABLE sys_ai_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    config_name VARCHAR(200) NOT NULL COMMENT '配置名称',
    config_code VARCHAR(100) UNIQUE COMMENT '配置编码',
    provider VARCHAR(50) DEFAULT 'openai' COMMENT '提供商: openai/azure/ollama',
    endpoint VARCHAR(500) COMMENT 'API端点',
    api_key VARCHAR(500) COMMENT 'API密钥(加密)',
    model_name VARCHAR(100) COMMENT '模型名称',
    parameters JSON COMMENT '参数配置',
    max_tokens INT DEFAULT 4096 COMMENT '最大Token数',
    temperature FLOAT DEFAULT 0.7 COMMENT '温度参数',
    context_limit INT DEFAULT 10 COMMENT '上下文限制(消息数)',
    is_default TINYINT(1) DEFAULT 0 COMMENT '是否默认配置',
    status INT DEFAULT 1,
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = 'AI模型配置表';

-- ============================================================
-- 接口调用日志表
-- ============================================================
CREATE TABLE sys_interface_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    interface_name VARCHAR(200) COMMENT '接口名称',
    interface_type VARCHAR(50) COMMENT '接口类型: internal/external',
    request_url VARCHAR(500) COMMENT '请求URL',
    request_method VARCHAR(10) COMMENT '请求方法',
    request_headers JSON COMMENT '请求头',
    request_body JSON COMMENT '请求体',
    response_code INT COMMENT '响应码',
    response_body JSON COMMENT '响应体',
    duration_ms INT COMMENT '耗时(毫秒)',
    caller VARCHAR(100) COMMENT '调用方',
    status VARCHAR(10) DEFAULT 'success',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT = '接口调用日志表';

-- ============================================================
-- 定时任务调度表
-- ============================================================
CREATE TABLE sys_job_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    job_name VARCHAR(200) NOT NULL COMMENT '任务名称',
    job_code VARCHAR(100) UNIQUE COMMENT '任务编码',
    job_type VARCHAR(50) COMMENT '任务类型: audit/monthly/system',
    trigger_type VARCHAR(20) COMMENT '触发类型: cron/interval/manual',
    trigger_config JSON COMMENT '触发配置',
    target_function VARCHAR(200) COMMENT '目标函数',
    parameters JSON COMMENT '参数',
    status INT DEFAULT 1 COMMENT '状态: 0禁用 1启用',
    last_run_time DATETIME COMMENT '最后运行时间',
    last_run_result VARCHAR(20) COMMENT '最后运行结果',
    next_run_time DATETIME COMMENT '下次运行时间',
    run_count INT DEFAULT 0 COMMENT '运行次数',
    fail_count INT DEFAULT 0 COMMENT '失败次数',
    description TEXT COMMENT '描述',
    created_by VARCHAR(100) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT = '定时任务调度表';