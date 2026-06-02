-- ============================================================
-- 数据运维数字员工平台 - 数据库建表语句
-- Database: db_digital_worker
-- Charset: utf8mb4
-- ============================================================

CREATE DATABASE IF NOT EXISTS db_digital_worker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_digital_worker;


CREATE TABLE dq_alert_upgrade_rule (
) COMMENT = '告警升级规则表'




CREATE TABLE dq_audit_field_config (
) COMMENT = '审计字段配置表'




CREATE TABLE dq_audit_report (
) COMMENT = '审计报告表'




CREATE TABLE dq_audit_task_config (
) COMMENT = '审计任务配置表'




CREATE TABLE dq_task_importance_config (
) COMMENT = '任务重要性配置表'




CREATE TABLE ma_adjustment_record (
) COMMENT = '调账记录表'




CREATE TABLE ma_alert_record (
) COMMENT = '告警记录表'




CREATE TABLE ma_audit_result (
) COMMENT = '审计结果表'




CREATE TABLE ma_daily_report (
) COMMENT = '月账日报表'




CREATE TABLE ma_kpi_metrics (
) COMMENT = 'KPI指标表'




CREATE TABLE ma_milestone_track (
) COMMENT = '里程碑跟踪表'




CREATE TABLE ma_ml_model_config (
) COMMENT = '机器学习模型配置表'




CREATE TABLE ma_month_account_config (
) COMMENT = '月账期配置表'




CREATE TABLE ma_summary_report (
) COMMENT = '月账汇总报告表'




CREATE TABLE ma_task_monitor (
) COMMENT = '任务监控表'




CREATE TABLE ops_analysis_path (
) COMMENT = '分析路径表'




CREATE TABLE ops_problem_case (
) COMMENT = '问题案例表'




CREATE TABLE ops_root_cause_type (
) COMMENT = '根因类型表'




CREATE TABLE ops_task_lineage (
) COMMENT = '任务血缘关系表'




CREATE TABLE sys_ai_config (
) COMMENT = 'AI模型配置表'




CREATE TABLE sys_config (
) COMMENT = '系统参数配置表'




CREATE TABLE sys_data_dict (
) COMMENT = '数据字典表'




CREATE TABLE sys_department (
) COMMENT = '部门表'




CREATE TABLE sys_interface_log (
) COMMENT = '接口调用日志表'




CREATE TABLE sys_job_schedule (
) COMMENT = '定时任务调度表'




CREATE TABLE sys_permission (
) COMMENT = '权限表'




CREATE TABLE sys_role (
) COMMENT = '角色表'




CREATE TABLE dq_audit_execution (
) COMMENT = '审计执行记录表'




CREATE TABLE dq_audit_rule_config (
) COMMENT = '审计规则配置表'




CREATE TABLE ops_case_usage_stats (
) COMMENT = '案例使用统计表'




CREATE TABLE ops_root_cause_analysis (
) COMMENT = '根因分析表'




CREATE TABLE sys_role_permission (
) COMMENT = '角色权限关联表'




CREATE TABLE sys_user (
) COMMENT = '用户表'




CREATE TABLE ai_chat_session (
) COMMENT = 'AI聊天会话表'




CREATE TABLE dq_audit_exception (
) COMMENT = '审计异常记录表'




CREATE TABLE ops_analysis_trace_log (
) COMMENT = '分析追溯日志表'




CREATE TABLE ops_user_feedback (
) COMMENT = '用户反馈表'




CREATE TABLE sys_audit_log (
) COMMENT = '系统审计日志表'




CREATE TABLE sys_notification_record (
) COMMENT = '通知记录表'




CREATE TABLE sys_user_role (
) COMMENT = '用户角色关联表'




CREATE TABLE ai_chat_message (
) COMMENT = 'AI聊天消息表'


