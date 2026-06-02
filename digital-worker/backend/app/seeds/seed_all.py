#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive seed script for db_digital_worker.

Populates all 45 tables with realistic Chinese telecom/billing domain data.
Run with: python -m app.seeds.seed_all
"""
import random
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import (
    SysDepartment, SysUser, SysRole, SysUserRole, SysPermission,
    SysRolePermission, SysConfig, SysDataDict, SysNotificationRecord,
    SysAuditLog, SysInterfaceLog, SysJobSchedule, SysAiConfig,
    DqAuditFieldConfig, DqAuditRuleConfig, DqAuditTaskConfig,
    DqTaskImportanceConfig, DqAlertUpgradeRule, DqAuditExecution,
    DqAuditException, DqAuditReport,
    OpsRootCauseType, OpsTaskLineage, OpsAnalysisPath, OpsProblemCase,
    OpsRootCauseAnalysis, OpsAnalysisTraceLog, OpsCaseUsageStats,
    OpsUserFeedback,
    MaMonthAccountConfig, MaTaskMonitor, MaAuditResult,
    MaAdjustmentRecord, MaDailyReport, MaSummaryReport, MaKpiMetrics,
    MaMilestoneTrack, MaAlertRecord, MaMlModelConfig,
    MaConfigStage, MaConfigMilestone, MaConfigWorkPlan, MaConfigTask,
    AiChatSession, AiChatMessage,
)

random.seed(42)
NOW = datetime.now()
BASE = date(2026, 6, 1)

ALL_TABLES = [
    "ai_chat_message", "ai_chat_session",
    "ma_config_task", "ma_config_work_plan", "ma_config_milestone", "ma_config_stage",
    "ma_alert_record", "ma_milestone_track", "ma_kpi_metrics",
    "ma_summary_report", "ma_daily_report", "ma_adjustment_record",
    "ma_audit_result", "ma_task_monitor", "ma_month_account_config", "ma_ml_model_config",
    "ops_user_feedback", "ops_analysis_trace_log", "ops_root_cause_analysis",
    "ops_case_usage_stats", "ops_problem_case", "ops_analysis_path",
    "ops_task_lineage", "ops_root_cause_type",
    "dq_audit_exception", "dq_audit_execution", "dq_audit_task_config",
    "dq_alert_upgrade_rule", "dq_audit_rule_config", "dq_audit_field_config",
    "dq_task_importance_config", "dq_audit_report",
    "sys_notification_record", "sys_audit_log", "sys_interface_log",
    "sys_role_permission", "sys_user_role", "sys_permission",
    "sys_data_dict", "sys_config", "sys_user", "sys_role",
    "sys_department", "sys_job_schedule", "sys_ai_config",
]



def seed():
    engine = create_engine(settings.DATABASE_URL_SYNC, echo=False)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # ---- TRUNCATE ----
        print("Truncating all tables...")
        db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for tbl in ALL_TABLES:
            db.execute(text(f"TRUNCATE TABLE {tbl}"))
        db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        db.commit()
        print("All tables truncated.")

        # ================================================================
        # SYS_DEPARTMENT (8)
        # ================================================================
        print("sys_department ...")
        dept_data = [
            ["综合管理部", "DEPT_ADMIN", 0, "管理部门", "赵明", "010-88880001", 1],
            ["数据管理部", "DEPT_DM", 0, "数据管理", "钱华", "010-88880002", 2],
            ["技术研发部", "DEPT_RD", 0, "技术研发", "孙伟", "010-88880003", 3],
            ["业务运营部", "DEPT_OPS", 0, "业务运营", "李强", "010-88880004", 4],
            ["质量监控部", "DEPT_QA", 0, "质量监控", "周丽", "010-88880005", 5],
            ["财务结算部", "DEPT_FIN", 0, "财务结算", "吴芳", "010-88880006", 6],
            ["数据产品部", "DEPT_DP", 0, "数据产品", "郑杰", "010-88880007", 7],
            ["运维保障部", "DEPT_OPSVC", 0, "运维保障", "王磊", "010-88880008", 8],
        ]
        depts = []
        for nm, cd, lv, desc, mgr, ph, so in dept_data:
            d = SysDepartment(dept_name=nm, dept_code=cd, dept_level=lv, dept_type="部门",
                              manager=mgr, phone=ph, email=f"dept{so}@dw.cn",
                              sort_order=so, status=1, description=desc)
            db.add(d)
            depts.append(d)
        db.flush()
        for i in range(1, len(depts)):
            depts[i].parent_id = depts[0].id
        db.flush()
        print(f"  {len(depts)} rows.")

        # ================================================================
        # SYS_USER (20)
        # ================================================================
        print("sys_user ...")
        user_data = [
            ("admin","admin123","系统管理员","admin@dw.cn","13800000000",0,"管理员",True),
            ("zhangsan","pass123","张三","zhangsan@dw.cn","13800000001",1,"数据管理专员",False),
            ("lisi","pass123","李四","lisi@dw.cn","13800000002",1,"数据分析师",False),
            ("wangwu","pass123","王五","wangwu@dw.cn","13800000003",2,"高级开发工程师",False),
            ("zhaoliu","pass123","赵六","zhaoliu@dw.cn","13800000004",2,"前端开发工程师",False),
            ("sunqi","pass123","孙七","sunqi@dw.cn","13800000005",3,"业务运营主管",False),
            ("zhouba","pass123","周八","zhouba@dw.cn","13800000006",3,"运营专员",False),
            ("wujiu","pass123","吴九","wujiu@dw.cn","13800000007",4,"质量审核主管",False),
            ("zhengshi","pass123","郑十","zhengshi@dw.cn","13800000008",4,"质量审核员",False),
            ("chenyi","pass123","陈一","chenyi@dw.cn","13800000009",5,"财务专员",False),
            ("liner","pass123","林二","liner@dw.cn","13800000010",5,"结算主管",False),
            ("huangsan","pass123","黄三","huangsan@dw.cn","13800000011",6,"产品经理",False),
            ("liusi","pass123","刘四","liusi@dw.cn","13800000012",6,"数据分析师",False),
            ("yangwu","pass123","杨五","yangwu@dw.cn","13800000013",7,"运维工程师",False),
            ("tanliu","pass123","谭六","tanliu@dw.cn","13800000014",7,"DBA",False),
            ("xieqi","pass123","谢七","xieqi@dw.cn","13800000015",0,"行政专员",False),
            ("hanba","pass123","韩八","hanba@dw.cn","13800000016",2,"测试工程师",False),
            ("cengjiu","pass123","曾九","cengjiu@dw.cn","13800000017",4,"质量监控专员",False),
            ("heshi","pass123","何十","heshi@dw.cn","13800000018",3,"数据分析师",False),
            ("luoyi","pass123","罗一","luoyi@dw.cn","13800000019",1,"数据工程师",False),
        ]
        users = []
        for un, pw, rn, em, ph, didx, pos, adm in user_data:
            u = SysUser(username=un, password=pw, real_name=rn, email=em, phone=ph,
                        department_id=depts[didx].id, position=pos, status=1, is_admin=adm,
                        last_login_time=NOW, last_login_ip=f"192.168.1.{10 + len(users)}",
                        created_by="system")
            db.add(u)
            users.append(u)
        db.flush()
        print(f"  {len(users)} rows.")

        # ================================================================
        # SYS_ROLE (5)
        # ================================================================
        print("sys_role ...")
        role_data = [
            ("系统管理员","ROLE_ADMIN","系统最高权限管理员"),
            ("数据分析师","ROLE_ANALYST","数据查询与分析"),
            ("数据工程师","ROLE_ENGINEER","数据处理与ETL开发"),
            ("质量审核员","ROLE_AUDITOR","数据质量审核"),
            ("普通用户","ROLE_USER","普通查看权限"),
        ]
        roles = []
        for nm, cd, desc in role_data:
            r = SysRole(role_name=nm, role_code=cd, description=desc, status=1, created_by="system")
            db.add(r)
            roles.append(r)
        db.flush()
        print(f"  {len(roles)} rows.")

        # ================================================================
        # SYS_USER_ROLE (~26)
        # ================================================================
        print("sys_user_role ...")
        ur_list = [
            (0,0),(1,1),(1,4),(2,1),(2,4),(3,2),(4,2),(4,4),
            (5,1),(5,3),(6,3),(6,4),(7,4),(8,4),(9,4),
            (10,4),(11,1),(11,4),(12,1),(13,2),(14,2),
            (15,4),(16,2),(17,3),(18,1),(19,2),
        ]
        for uid, rid in ur_list:
            db.add(SysUserRole(user_id=users[uid].id, role_id=roles[rid].id))
        db.flush()
        print(f"  {len(ur_list)} rows.")

        # ================================================================
        # SYS_PERMISSION (18)
        # ================================================================
        print("sys_permission ...")
        perm_parents = [
            ("系统管理","sys_manage","/sys","menu","setting",1),
            ("数据质量审计","dq_audit","/dq","menu","audit",2),
            ("根因分析","ops_rca","/ops","menu","search",3),
            ("月账管理","ma_monthly","/ma","menu","file",4),
            ("AI助手","ai_assistant","/ai","menu","robot",5),
            ("系统监控","sys_monitor","/monitor","menu","monitor",6),
        ]
        perms = []
        for nm, cd, path, typ, icon, so in perm_parents:
            p = SysPermission(permission_name=nm, permission_code=cd, menu_path=path,
                              permission_type=typ, icon=icon, sort_order=so, status=1)
            db.add(p)
            perms.append(p)
        db.flush()

        perm_children = [
            (0,"用户管理","sys_user","/sys/user","menu","user",1),
            (0,"角色管理","sys_role","/sys/role","menu","team",2),
            (0,"配置管理","sys_config","/sys/config","menu","setting",3),
            (1,"审计配置","dq_config","/dq/config","menu","audit",1),
            (1,"审计执行","dq_exec","/dq/exec","menu","play-circle",2),
            (1,"审计报告","dq_report","/dq/report","menu","file-text",3),
            (2,"案例管理","ops_case","/ops/case","menu","book",1),
            (2,"分析管理","ops_analysis","/ops/analysis","menu","share-alt",2),
            (2,"路径配置","ops_path","/ops/path","menu","branches",3),
            (3,"账期管理","ma_month","/ma/month","menu","calendar",1),
            (3,"任务监控","ma_task","/ma/task","menu","dashboard",2),
            (3,"报表管理","ma_report","/ma/report","menu","bar-chart",3),
        ]
        for pidx, nm, cd, path, typ, icon, so in perm_children:
            p = SysPermission(permission_name=nm, permission_code=cd, menu_path=path,
                              permission_type=typ, parent_id=perms[pidx].id,
                              icon=icon, sort_order=so, status=1)
            db.add(p)
            perms.append(p)
        db.flush()
        print(f"  {len(perms)} rows.")

        # ================================================================
        # SYS_ROLE_PERMISSION (~25)
        # ================================================================
        print("sys_role_permission ...")
        rp_list = [
            (0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(0,9),
            (0,10),(0,11),(0,12),(0,13),(0,14),(0,15),(0,16),(0,17),
            (1,0),(1,3),(1,4),(1,5),(1,6),(1,7),(1,9),(1,10),(1,11),
            (2,0),(2,3),(2,4),(2,6),(2,7),(2,9),(2,10),
            (3,0),(3,3),(3,4),(3,5),(3,6),(3,7),
            (4,0),(4,3),(4,9),(4,10),
        ]
        for ridx, pidx in rp_list:
            db.add(SysRolePermission(role_id=roles[ridx].id, permission_id=perms[pidx].id))
        db.flush()
        print(f"  {len(rp_list)} rows.")

        # ================================================================
        # SYS_CONFIG (10)
        # ================================================================
        print("sys_config ...")
        cfg_data = [
            ("system.title","Digital Worker 智能数字员工平台","system","系统标题"),
            ("system.version","1.0.0","system","系统版本"),
            ("alert.data_delay_threshold","30","alert","数据延迟告警阈值(分钟)"),
            ("alert.quality_score_threshold","95.0","alert","质量评分告警阈值"),
            ("alert.task_failure_alert","true","alert","任务失败告警开关"),
            ("notification.email_enabled","true","notification","邮件通知启用"),
            ("notification.sms_enabled","false","notification","短信通知启用"),
            ("business.account_month_format","YYYY-MM","business","账期格式"),
            ("business.default_timezone","Asia/Shanghai","business","默认时区"),
            ("system.maintenance_mode","false","system","维护模式开关"),
        ]
        for ck, cv, ct, desc in cfg_data:
            db.add(SysConfig(config_key=ck, config_value=cv, config_type=ct,
                             description=desc, status=1, created_by="system"))
        db.flush()
        print(f"  {len(cfg_data)} rows.")

        # ================================================================
        # SYS_DATA_DICT (25)
        # ================================================================
        print("sys_data_dict ...")
        dict_types = [
            ("task_type","任务类型"),("alert_level","告警级别"),
            ("audit_status","审计状态"),("data_source","数据源类型"),
            ("priority","优先级"),
        ]
        dtypes = []
        for dk, dv in dict_types:
            dd = SysDataDict(dict_key=dk, dict_value=dv, dict_type="system_category", status=1)
            db.add(dd)
            dtypes.append(dd)
        db.flush()

        dict_vals = [
            (0,"TDP_TASK","TDP任务","task_type"),(0,"SQL_SCRIPT","SQL脚本","task_type"),
            (0,"PUBLISH_MSG","消息发布","task_type"),(0,"MANUAL_OP","人工操作","task_type"),
            (1,"info","提示","alert_level"),(1,"warning","警告","alert_level"),
            (1,"critical","严重","alert_level"),(1,"emergency","紧急","alert_level"),
            (2,"pending","待处理","audit_status"),(2,"running","运行中","audit_status"),
            (2,"completed","已完成","audit_status"),(2,"failed","失败","audit_status"),
            (3,"mysql","MySQL数据库","data_source"),(3,"oracle","Oracle数据库","data_source"),
            (3,"hive","Hive数据仓库","data_source"),(3,"api","API接口","data_source"),
            (4,"urgent","紧急","priority"),(4,"high","高","priority"),
            (4,"normal","普通","priority"),(4,"low","低","priority"),
        ]
        for tidx, dk, dv, dt in dict_vals:
            db.add(SysDataDict(dict_key=dk, dict_value=dv, dict_type=dt,
                               parent_id=dtypes[tidx].id, status=1))
        db.flush()
        print(f"  {len(dict_types) + len(dict_vals)} rows.")

        # ================================================================
        # SYS_AI_CONFIG (2)
        # ================================================================
        print("sys_ai_config ...")
        ai_cfgs = [
            ("默认GPT-4配置", "AI_CONFIG_DEFAULT", "openai", settings.AI_ENDPOINT,
             settings.AI_API_KEY, settings.AI_MODEL, 4096, 0.7, 10, True),
            ("备用GPT-3.5配置", "AI_CONFIG_BACKUP", "openai", settings.AI_ENDPOINT,
             settings.AI_API_KEY, "gpt-3.5-turbo", 2048, 0.8, 8, False),
        ]
        for nm, cd, prov, ep, key, mdl, mt, tmp, ctx, isdef in ai_cfgs:
            db.add(SysAiConfig(config_name=nm, config_code=cd, provider=prov, endpoint=ep,
                               api_key=key, model_name=mdl, max_tokens=mt,
                               temperature=tmp, context_limit=ctx, is_default=isdef,
                               status=1, created_by="system"))
        db.flush()
        print(f"  {len(ai_cfgs)} rows.")
        # ================================================================
        # SYS_NOTIFICATION_RECORD (15)
        # ================================================================
        print("sys_notification_record ...")
        notif_data = [
            ("alert", "数据延迟告警", "月账任务INFBSN一号批次处理延迟超过30分钟", 0, "张三", "system", False, "sent"),
            ("alert", "质量评分告警", "2025-01账期质量评分低于95%阈值", 1, "李四", "system", False, "sent"),
            ("reminder", "任务提醒", "前置作业-3号任务即将到达截止时间", 2, "王五", "system", True, "delivered"),
            ("system", "系统升级通知", "系统将于本周六凌晨2:00-4:00进行升级维护", 3, "赵六", "email", False, "sent"),
            ("business", "账期结算完成", "2025-01账期结算已完成请查看结算报告", 4, "孙七", "system", True, "delivered"),
            ("alert", "数据异常告警", "用户表T_USER数据量异常增长请及时检查", 5, "周八", "dingtalk", False, "sent"),
            ("reminder", "审核任务提醒", "您有3条审计异常记录待处理", 6, "吴九", "system", False, "sent"),
            ("system", "密码过期提醒", "您的登录密码将于3天后过期请及时修改", 7, "郑十", "email", False, "sent"),
            ("business", "月报生成通知", "2026年5月月度报告已生成待查看", 8, "陈一", "system", True, "delivered"),
            ("alert", "接口调用失败", "上游数据接口返回500错误", 9, "林二", "system", False, "sent"),
            ("reminder", "模型训练完成", "异常检测模型v2.1训练已完成准确率97.2%", 10, "黄三", "system", False, "delivered"),
            ("business", "案例库更新", "新增3条数据质量问题案例请查阅", 11, "刘四", "system", False, "sent"),
            ("alert", "磁盘空间告警", "数据服务器/data分区使用率已达85%", 12, "杨五", "system", False, "sent"),
            ("system", "审批通知", "您申请的调账记录已通过审批", 13, "谭六", "system", True, "delivered"),
            ("business", "KPI通报", "本月核心指标已完成80%请关注未完成项", 14, "谢七", "email", False, "sent"),
        ]
        for nt, title, content_t, ridx, rname, ch, is_read, st in notif_data:
            db.add(SysNotificationRecord(
                notification_type=nt, title=title, content=content_t,
                receiver_id=users[ridx].id, receiver_name=rname, channel=ch,
                is_read=is_read, status=st,
                send_time=NOW - timedelta(hours=random.randint(1, 72))))
        db.flush()
        print(f"  {len(notif_data)} rows.")

        # ================================================================
        # SYS_AUDIT_LOG (20)
        # ================================================================
        print("sys_audit_log ...")
        audit_log_data = [
            (0, "admin", "login", "系统管理", "用户登录系统", "/api/auth/login", "POST", 200, "127.0.0.1", "success", 120),
            (1, "zhangsan", "query", "数据管理", "查询数据字典列表", "/api/sys/dict/list", "GET", 200, "192.168.1.10", "success", 45),
            (2, "lisi", "create", "月账管理", "创建月账任务监控", "/api/ma/task", "POST", 201, "192.168.1.11", "success", 230),
            (3, "wangwu", "update", "系统管理", "修改系统配置参数", "/api/sys/config/1", "PUT", 200, "192.168.1.12", "success", 67),
            (4, "zhaoliu", "delete", "系统管理", "删除过期通知记录", "/api/sys/notification/5", "DELETE", 200, "192.168.1.13", "success", 34),
            (5, "sunqi", "query", "业务运营", "查询月账进度汇总", "/api/ma/summary", "GET", 200, "192.168.1.14", "success", 89),
            (6, "zhouba", "create", "业务运营", "创建调账申请记录", "/api/ma/adjustment", "POST", 201, "192.168.1.15", "success", 156),
            (7, "wujiu", "query", "质量监控", "查看审计异常列表", "/api/dq/exception", "GET", 200, "192.168.1.16", "success", 52),
            (8, "zhengshi", "update", "质量监控", "处理审计异常记录", "/api/dq/exception/1", "PUT", 200, "192.168.1.17", "success", 340),
            (0, "admin", "login", "系统管理", "用户登录系统", "/api/auth/login", "POST", 200, "10.0.0.1", "success", 98),
            (9, "chenyi", "query", "财务结算", "查询账期结算列表", "/api/ma/month", "GET", 200, "192.168.1.18", "success", 41),
            (10, "liner", "create", "财务结算", "创建月度结算报告", "/api/ma/report", "POST", 201, "192.168.1.19", "success", 512),
            (11, "huangsan", "update", "数据产品", "更新ML模型配置", "/api/ma/ml/1", "PUT", 200, "192.168.1.20", "success", 78),
            (12, "liusi", "query", "数据产品", "查询KPI指标趋势", "/api/ma/kpi", "GET", 200, "192.168.1.21", "success", 33),
            (13, "yangwu", "update", "运维保障", "执行系统维护任务", "/api/sys/job/run/1", "POST", 200, "192.168.1.22", "success", 1200),
            (14, "tanliu", "query", "运维保障", "查询接口调用日志", "/api/sys/interface-log", "GET", 200, "192.168.1.23", "success", 55),
            (15, "xieqi", "logout", "系统管理", "用户退出系统", "/api/auth/logout", "POST", 200, "192.168.1.24", "success", 12),
            (0, "admin", "delete", "系统管理", "批量删除审计日志", "/api/sys/audit-log/batch", "DELETE", 200, "127.0.0.1", "success", 890),
            (16, "hanba", "query", "技术研发", "查询系统运行状态", "/api/sys/config", "GET", 200, "192.168.1.25", "success", 28),
            (17, "cengjiu", "update", "质量监控", "更新审计规则配置", "/api/dq/rule/3", "PUT", 200, "192.168.1.26", "failure", 450),
        ]
        for uid, un, at, mod, detail, url, method, code, ip, st, dur in audit_log_data:
            db.add(SysAuditLog(
                user_id=users[uid].id, username=un, action_type=at, module=mod,
                action_detail=detail, request_url=url, request_method=method,
                response_code=code, ip_address=ip, status=st, duration_ms=dur,
                request_params={}))
        db.flush()
        print(f"  {len(audit_log_data)} rows.")

        # ================================================================
        # SYS_INTERFACE_LOG (15)
        # ================================================================
        print("sys_interface_log ...")
        iface_log_data = [
            ("上游计费数据同步", "external", "/api/v1/billing/sync", "POST", 200, 1230, "计费系统", "success"),
            ("用户信息查询接口", "external", "/api/v1/user/info", "GET", 200, 45, "CRM系统", "success"),
            ("月账任务状态推送", "internal", "/api/v1/task/status", "POST", 200, 67, "调度中心", "success"),
            ("数据质量审计结果", "internal", "/api/v1/audit/result", "POST", 201, 234, "审计引擎", "success"),
            ("结算文件生成请求", "external", "/api/v1/settlement/generate", "POST", 200, 3400, "结算系统", "success"),
            ("告警消息推送", "internal", "/api/v1/alert/push", "POST", 200, 89, "告警中心", "success"),
            ("AI对话请求", "internal", "/api/v1/ai/chat", "POST", 200, 2300, "AI服务", "success"),
            ("上游数据查询", "external", "/api/v1/billing/query", "GET", 500, 12000, "计费系统", "failure"),
            ("报表数据导出", "internal", "/api/v1/report/export", "GET", 200, 5600, "报表服务", "success"),
            ("ML模型预测", "internal", "/api/v1/ml/predict", "POST", 200, 450, "ML引擎", "success"),
            ("数据字典同步", "internal", "/api/v1/dict/sync", "POST", 200, 156, "数据中台", "success"),
            ("任务调度触发", "internal", "/api/v1/scheduler/trigger", "POST", 200, 34, "调度中心", "success"),
            ("审计报告生成", "internal", "/api/v1/audit/report", "POST", 201, 8900, "审计引擎", "success"),
            ("根因分析请求", "internal", "/api/v1/rca/analyze", "POST", 200, 3400, "RCA引擎", "success"),
            ("用户权限验证", "internal", "/api/v1/auth/verify", "POST", 200, 23, "认证中心", "success"),
        ]
        for nm, typ, url, method, code, dur, caller, st in iface_log_data:
            db.add(SysInterfaceLog(
                interface_name=nm, interface_type=typ, request_url=url,
                request_method=method, response_code=code, duration_ms=dur,
                caller=caller, status=st, error_message="" if st == "success" else "Connection timeout"))
        db.flush()
        print(f"  {len(iface_log_data)} rows.")

        # ================================================================
        # SYS_JOB_SCHEDULE (8)
        # ================================================================
        print("sys_job_schedule ...")
        job_data = [
            ("月账任务调度", "JOB_MONTHLY_TASK", "monthly", "cron", {"cron": "0 0 1 * *"}, "app.jobs.monthly.run_monthly_task", 1, 142, 3),
            ("数据质量审计", "JOB_DQ_AUDIT", "audit", "cron", {"cron": "0 2 * * *"}, "app.jobs.audit.run_audit", 1, 56, 1),
            ("日报生成", "JOB_DAILY_REPORT", "monthly", "cron", {"cron": "0 6 * * *"}, "app.jobs.report.generate_daily", 1, 89, 0),
            ("KPI指标计算", "JOB_KPI_CALC", "monthly", "cron", {"cron": "30 1 * * *"}, "app.jobs.kpi.calculate", 1, 34, 2),
            ("接口健康检查", "JOB_HEALTH_CHECK", "system", "interval", {"interval": 300}, "app.jobs.monitor.health_check", 1, 567, 0),
            ("数据备份", "JOB_DATA_BACKUP", "system", "cron", {"cron": "0 3 * * 0"}, "app.jobs.backup.run_backup", 1, 22, 0),
            ("月总结报告生成", "JOB_MONTHLY_SUMMARY", "monthly", "cron", {"cron": "0 8 1 * *"}, "app.jobs.report.generate_summary", 1, 12, 1),
            ("AI模型训练", "JOB_AI_TRAIN", "system", "cron", {"cron": "0 0 15 * *"}, "app.jobs.ai.train_model", 0, 8, 0),
        ]
        for nm, cd, jt, tt, tc, fn, st, rc, fc in job_data:
            db.add(SysJobSchedule(
                job_name=nm, job_code=cd, job_type=jt, trigger_type=tt,
                trigger_config=tc, target_function=fn, status=st,
                run_count=rc, fail_count=fc, created_by="system"))
        db.flush()
        print(f"  {len(job_data)} rows.")

        # ================================================================
        # DQ_AUDIT_FIELD_CONFIG (30)
        # ================================================================
        print("dq_audit_field_config ...")
        field_data = [
            ("user_id","用户ID","ds_billing","计费系统","billing","T_USER","BIGINT",20,False,"100001"),
            ("user_name","用户姓名","ds_billing","计费系统","billing","T_USER","VARCHAR",100,False,"张三"),
            ("phone_no","手机号码","ds_billing","计费系统","billing","T_USER","VARCHAR",20,False,"13800138000"),
            ("id_card","身份证号","ds_billing","计费系统","billing","T_USER","VARCHAR",18,True,"110101199001011234"),
            ("account_balance","账户余额","ds_billing","计费系统","billing","T_ACCOUNT","DECIMAL",12,False,"500.00"),
            ("bill_amount","账单金额","ds_billing","计费系统","billing","T_BILL","DECIMAL",12,True,"299.00"),
            ("bill_month","账单月份","ds_billing","计费系统","billing","T_BILL","VARCHAR",7,False,"2026-05"),
            ("charge_type","计费类型","ds_billing","计费系统","billing","T_CHARGE","VARCHAR",50,False,"月租费"),
            ("charge_amount","计费金额","ds_billing","计费系统","billing","T_CHARGE","DECIMAL",12,False,"199.00"),
            ("payment_status","支付状态","ds_billing","计费系统","billing","T_PAYMENT","VARCHAR",20,False,"已支付"),
            ("payment_time","支付时间","ds_billing","计费系统","billing","T_PAYMENT","DATETIME",0,True,"2026-05-15 10:30:00"),
            ("task_id","任务ID","ds_scheduler","调度系统","scheduler","T_TASK","BIGINT",20,False,"20001"),
            ("task_name","任务名称","ds_scheduler","调度系统","scheduler","T_TASK","VARCHAR",200,False,"月账数据导入"),
            ("task_status","任务状态","ds_scheduler","调度系统","scheduler","T_TASK","VARCHAR",20,False,"completed"),
            ("task_start_time","任务开始时间","ds_scheduler","调度系统","scheduler","T_TASK","DATETIME",0,True,"2026-06-01 01:00:00"),
            ("task_end_time","任务结束时间","ds_scheduler","调度系统","scheduler","T_TASK","DATETIME",0,True,"2026-06-01 02:30:00"),
            ("error_code","错误编码","ds_scheduler","调度系统","scheduler","T_TASK_LOG","VARCHAR",50,True,"E0001"),
            ("error_message","错误信息","ds_scheduler","调度系统","scheduler","T_TASK_LOG","TEXT",0,True,"数据源连接超时"),
            ("data_source","数据源名称","ds_quality","质量系统","quality","T_AUDIT_LOG","VARCHAR",100,False,"billing_mysql"),
            ("record_count","记录数","ds_quality","质量系统","quality","T_AUDIT_LOG","INT",10,False,"10000"),
            ("pass_count","通过数","ds_quality","质量系统","quality","T_AUDIT_LOG","INT",10,False,"9980"),
            ("fail_count","失败数","ds_quality","质量系统","quality","T_AUDIT_LOG","INT",10,False,"20"),
            ("pass_rate","通过率","ds_quality","质量系统","quality","T_AUDIT_LOG","FLOAT",6,False,"99.80"),
            ("kpi_code","KPI编码","ds_report","报表系统","report","T_KPI","VARCHAR",50,False,"KPI_001"),
            ("kpi_value","KPI值","ds_report","报表系统","report","T_KPI","FLOAT",10,False,"95.5"),
            ("report_date","报表日期","ds_report","报表系统","report","T_REPORT","DATE",0,False,"2026-06-01"),
            ("created_by","创建人","ds_system","系统","system","T_AUDIT","VARCHAR",100,True,"system"),
            ("created_at","创建时间","ds_system","系统","system","T_AUDIT","DATETIME",0,False,"2026-06-01 00:00:00"),
            ("updated_at","更新时间","ds_system","系统","system","T_AUDIT","DATETIME",0,True,"2026-06-01 12:00:00"),
            ("remark","备注","ds_system","系统","system","T_AUDIT","TEXT",0,True,"测试数据"),
        ]
        fields = []
        for fn, fd, dsid, dsn, sn, tn, ft, fl, isnull, sample in field_data:
            f = DqAuditFieldConfig(
                field_name=fn, field_desc=fd, datasource_id=dsid, datasource_name=dsn,
                schema_name=sn, table_name=tn, field_type=ft, field_length=fl,
                is_nullable=isnull, sample_data=sample, status=1, created_by="system")
            db.add(f)
            fields.append(f)
        db.flush()
        print(f"  {len(fields)} rows.")

        # ================================================================
        # DQ_AUDIT_RULE_CONFIG (12)
        # ================================================================
        print("dq_audit_rule_config ...")
        rule_data = [
            ("非空校验-用户姓名","RULE_NULL_USERNAME","null_check","error",{"field":"user_name","action":"reject"},0,"user_name","T_USER",0.0,"high",False),
            ("非空校验-手机号","RULE_NULL_PHONE","null_check","error",{"field":"phone_no","action":"reject"},0,"phone_no","T_USER",0.0,"high",False),
            ("重复校验-用户ID","RULE_DUP_USERID","duplicate","error",{"field":"user_id","dedup":True},0,"user_id","T_USER",0.0,"high",False),
            ("重复校验-账单","RULE_DUP_BILL","duplicate","warning",{"field":"bill_id","dedup":True},0,"bill_id","T_BILL",0.01,"medium",False),
            ("范围校验-金额","RULE_RANGE_AMOUNT","range","error",{"field":"bill_amount","min":0,"max":999999},5,"bill_amount","T_BILL",0.05,"high",True),
            ("范围校验-余额","RULE_RANGE_BALANCE","range","warning",{"field":"account_balance","min":-1000,"max":999999},5,"account_balance","T_ACCOUNT",0.05,"medium",False),
            ("格式校验-手机号","RULE_FORMAT_PHONE","format","error",{"field":"phone_no","pattern":"^1[3-9]\\d{9}$"},1,"phone_no","T_USER",0.02,"high",False),
            ("格式校验-身份证","RULE_FORMAT_IDCARD","format","warning",{"field":"id_card","pattern":"^\\d{17}[\\dX]$"},1,"id_card","T_USER",0.01,"medium",False),
            ("格式校验-日期","RULE_FORMAT_DATE","format","error",{"field":"payment_time","pattern":"datetime"},5,"payment_time","T_PAYMENT",0.03,"medium",False),
            ("自定义-账期一致性","RULE_CONSIST_MONTH","custom","error",{"rule":"bill_month == account_month"},0,"bill_month","T_BILL",0.0,"high",True),
            ("自定义-金额平衡","RULE_BALANCE_AMOUNT","custom","error",{"rule":"sum(charge_amount) == sum(bill_amount)"},0,"bill_amount","T_BILL",0.01,"high",True),
            ("自定义-数据时效性","RULE_TIMELINESS","custom","warning",{"field":"task_end_time","max_delay_minutes":30},4,"task_end_time","T_TASK",0.1,"medium",False),
        ]
        rules = []
        for rn, rc, rt, rl, rcon, fidx, fn, tn, thr, sev, ai in rule_data:
            r = DqAuditRuleConfig(
                rule_name=rn, rule_code=rc, rule_type=rt, rule_level=rl,
                rule_content=rcon, field_id=fields[fidx].id if fidx >= 0 else None,
                field_name=fn, table_name=tn, threshold=thr, severity=sev,
                status=1, ai_generated=ai, created_by="system")
            db.add(r)
            rules.append(r)
        db.flush()
        print(f"  {len(rules)} rows.")

        # ================================================================
        # DQ_TASK_IMPORTANCE_CONFIG (5)
        # ================================================================
        print("dq_task_importance_config ...")
        imp_data = [
            (1,"一般","green","0-60","常规任务无需特殊关注",["system"],1440),
            (2,"重要","blue","61-80","需要关注的任务",["system","email"],480),
            (3,"紧急","orange","81-90","需要优先处理的任务",["system","email","dingtalk"],120),
            (4,"严重","red","91-99","需要立即处理的任务",["system","email","dingtalk","sms"],30),
            (5,"灾难","darkred","100","灾难级任务需全员响应",["system","email","dingtalk","sms","phone"],5),
        ]
        for lv, lnm, color, score, desc, chs, resp in imp_data:
            db.add(DqTaskImportanceConfig(
                level=lv, level_name=lnm, color=color, score_range=score,
                description=desc, notify_channels=chs, response_time_minutes=resp))
        db.flush()
        print(f"  {len(imp_data)} rows.")

        # ================================================================
        # DQ_ALERT_UPGRADE_RULE (6)
        # ================================================================
        print("dq_alert_upgrade_rule ...")
        upgrade_data = [
            ("连续失败升级","task_failure",{"consecutive_failures":3},2,["dept_manager","tech_lead"],"【升级】任务连续失败3次",3,True),
            ("异常率升级","data_anomaly",{"anomaly_rate_gte":0.1},3,["dept_manager","director"],"【升级】数据异常率超过10%",2,True),
            ("处理超时升级","handle_timeout",{"timeout_minutes":120},2,["tech_lead","ops_manager"],"【升级】异常处理超时2小时",3,True),
            ("批量异常升级","batch_anomaly",{"count_gte":100},4,["director","vp"],"【严重升级】批量异常超过100条",2,True),
            ("关键任务失败升级","critical_failure",{"task_level":"critical"},4,["director","vp","cto"],"【严重升级】关键任务执行失败",1,True),
            ("SLA违规升级","sla_violation",{"sla_minutes":30},3,["ops_manager","dept_manager"],"【升级】SLA违规超过30分钟",3,True),
        ]
        for rn, at, tc, ul, nt, ntpl, muc, active in upgrade_data:
            db.add(DqAlertUpgradeRule(
                rule_name=rn, alert_type=at, trigger_condition=tc,
                upgrade_level=ul, notify_targets=nt, notify_template=ntpl,
                max_upgrade_count=muc, is_active=active))
        db.flush()
        print(f"  {len(upgrade_data)} rows.")

        # ================================================================
        # DQ_AUDIT_TASK_CONFIG (8)
        # ================================================================
        print("dq_audit_task_config ...")
        task_cfg_data = [
            ("用户数据完整性审计","field_audit",[1,2,3],[1,2,3,4],"daily",{"time":"02:00"},"full",100.0,1,3),
            ("账单数据准确性审计","rule_audit",[4,5,6],[5,6,7],"daily",{"time":"03:00"},"full",100.0,1,4),
            ("支付数据一致性审计","rule_audit",[7,8,9],[8,9,10],"daily",{"time":"04:00"},"full",100.0,1,3),
            ("全量数据质量审计","full_audit",[1,2,3,4,5,6,7,8,9,10,11,12],[1,2,3,4,5,6,7,8,9,10],"weekly",{"day":"Monday","time":"01:00"},"sample",20.0,1,5),
            ("月账数据专项审计","field_audit",[3,4,5],[5,6,7,8],"monthly",{"day":1,"time":"00:00"},"full",100.0,1,4),
            ("实时数据流质量监控","rule_audit",[7,10],[1,2,3],"manual",{},"sample",10.0,1,2),
            ("KPI指标数据审计","field_audit",[11,12],[24,25,26],"daily",{"time":"06:00"},"full",100.0,1,2),
            ("上游数据源接入审计","rule_audit",[1,6,10],[17,18,19],"weekly",{"day":"Friday","time":"03:00"},"sample",50.0,1,3),
        ]
        task_cfgs = []
        for tn, tt, rids, fids, st, sc, es, sr, im, last_imp in task_cfg_data:
            tc = DqAuditTaskConfig(
                task_name=tn, task_type=tt, rule_ids=rids, field_ids=fids,
                schedule_type=st, schedule_config=sc, execute_strategy=es,
                sample_rate=sr, status=1, importance=last_imp, created_by="system")
            db.add(tc)
            task_cfgs.append(tc)
        db.flush()
        print(f"  {len(task_cfgs)} rows.")

        # ================================================================
        # DQ_AUDIT_EXECUTION (15)
        # ================================================================
        print("dq_audit_execution ...")
        exec_data = [
            (0,"用户数据完整性审计",150,100000,50000,49800,200,99.6,"completed"),
            (1,"账单数据准确性审计",230,500000,250000,248500,1500,99.4,"completed"),
            (2,"支付数据一致性审计",180,300000,150000,149800,200,99.87,"completed"),
            (3,"全量数据质量审计",3600,2000000,400000,395000,5000,98.75,"completed"),
            (4,"月账数据专项审计",560,800000,800000,796000,4000,99.5,"completed"),
            (5,"实时数据流质量监控",30,10000,1000,995,5,99.5,"completed"),
            (6,"KPI指标数据审计",45,50000,25000,24980,20,99.92,"completed"),
            (7,"上游数据源接入审计",300,200000,100000,99800,200,99.8,"completed"),
            (0,"用户数据完整性审计",160,100000,50000,49750,250,99.5,"completed"),
            (1,"账单数据准确性审计",245,500000,250000,247800,2200,99.12,"completed"),
            (2,"支付数据一致性审计",175,300000,150000,149900,100,99.93,"completed"),
            (4,"月账数据专项审计",590,800000,800000,794000,6000,99.25,"completed"),
            (3,"全量数据质量审计",4200,2000000,400000,393000,7000,98.25,"completed"),
            (6,"KPI指标数据审计",50,50000,25000,24990,10,99.96,"completed"),
            (5,"实时数据流质量监控",35,10000,1000,992,8,99.2,"completed"),
        ]
        executions = []
        for tidx, tn, dur, total, sample, passed, failed, pr, st in exec_data:
            e = DqAuditExecution(
                task_id=task_cfgs[tidx].id, task_name=tn,
                execute_time=NOW - timedelta(hours=random.randint(1, 168)),
                execute_duration=dur, total_records=total, sample_records=sample,
                passed_records=passed, failed_records=failed, pass_rate=pr, status=st)
            db.add(e)
            executions.append(e)
        db.flush()
        print(f"  {len(executions)} rows.")

        # ================================================================
        # DQ_AUDIT_EXCEPTION (20)
        # ================================================================
        print("dq_audit_exception ...")
        exc_data = [
            (0,0,"非空校验-用户姓名","user_name","T_USER","null_violation","None",50,0.05,"medium","open",None),
            (0,1,"非空校验-手机号","phone_no","T_USER","null_violation","None",30,0.03,"high","handling","张三"),
            (1,2,"重复校验-用户ID","user_id","T_USER","duplicate","100001,100002",5,0.005,"high","resolved","李四"),
            (1,3,"重复校验-账单","bill_id","T_BILL","duplicate","B2026050001",2,0.002,"medium","closed","王五"),
            (2,4,"范围校验-金额","bill_amount","T_BILL","range_violation","-500.00",100,0.02,"high","open",None),
            (2,5,"范围校验-余额","account_balance","T_ACCOUNT","range_violation","9999999.00",15,0.015,"medium","handling","赵六"),
            (3,6,"格式校验-手机号","phone_no","T_USER","format_violation","12345678901",80,0.08,"high","open",None),
            (3,7,"格式校验-身份证","id_card","T_USER","format_violation","12345",20,0.02,"medium","resolved","孙七"),
            (4,8,"格式校验-日期","payment_time","T_PAYMENT","format_violation","2026-13-01",10,0.01,"medium","closed","周八"),
            (4,9,"自定义-账期一致性","bill_month","T_BILL","consistency_violation","2026-04",45,0.045,"high","open",None),
            (5,10,"自定义-金额平衡","bill_amount","T_BILL","balance_violation","-1500.00",200,0.04,"high","handling","吴九"),
            (5,11,"自定义-数据时效性","task_end_time","T_TASK","timeliness_violation","delay 60min",5,0.05,"medium","open",None),
            (6,0,"非空校验-用户姓名","user_name","T_USER","null_violation","None",25,0.025,"medium","resolved","郑十"),
            (6,1,"非空校验-手机号","phone_no","T_USER","null_violation","None",18,0.018,"high","closed","陈一"),
            (7,2,"重复校验-用户ID","user_id","T_USER","duplicate","100005,100006",3,0.003,"high","handling","林二"),
            (8,4,"范围校验-金额","bill_amount","T_BILL","range_violation","9999999.99",60,0.06,"high","open",None),
            (8,6,"格式校验-手机号","phone_no","T_USER","format_violation","123456",35,0.035,"high","handling","黄三"),
            (9,9,"自定义-账期一致性","bill_month","T_BILL","consistency_violation","2026-02",22,0.022,"high","open",None),
            (9,10,"自定义-金额平衡","bill_amount","T_BILL","balance_violation","+3000.00",150,0.03,"high","resolved","刘四"),
            (10,4,"范围校验-金额","bill_amount","T_BILL","range_violation","-999.00",12,0.012,"medium","closed","杨五"),
        ]
        for eidx, ridx, rn, fn, tn, et, ev, ec, er, sev, st, handler in exc_data:
            db.add(DqAuditException(
                execution_id=executions[eidx].id, rule_id=rules[ridx].id,
                rule_name=rn, field_name=fn, table_name=tn, exception_type=et,
                exception_value=ev, exception_count=ec, exception_rate=er,
                severity=sev, status=st, handler=handler))
        db.flush()
        print(f"  {len(exc_data)} rows.")

        # ================================================================
        # DQ_AUDIT_REPORT (10)
        # ================================================================
        print("dq_audit_report ...")
        report_data = [
            ("2026-05月数据质量日报","daily",[0,1,2],3,900000,1700,99.81,"数据质量整体良好","通过",["持续监控异常字段"]),
            ("2026-05月数据质量周报","weekly",[0,1,2,3],4,2900000,6900,99.76,"本周数据质量略有波动","需要关注",["加强手机号格式校验","优化金额范围检查"]),
            ("2026年5月数据质量月报","monthly",[0,1,2,3,4],5,3700000,10900,99.71,"本月数据质量总体稳定","通过",["建议新增身份证校验规则","优化重复检测算法"]),
            ("2026-06-01数据质量日报","daily",[0,5],2,110000,255,99.77,"单日数据质量正常","通过",["关注实时流质量"]),
            ("2026-06-02数据质量日报","daily",[6,7],2,250000,220,99.91,"KPI数据质量优秀","通过",[]),
            ("2026年5月专项审计报告","custom",[4],1,800000,4000,99.5,"月账数据专项审计完成","通过",["调整金额校验阈值"]),
            ("2026年5月第2周周报","weekly",[1,3,7],3,2700000,7200,99.73,"本月第二周质量平稳","需要关注",["重点监控上游数据"]),
            ("2026-06-03数据质量日报","daily",[8,9],2,850000,2210,99.74,"数据质量正常","通过",[]),
            ("2026年5月第3周周报","weekly",[3,4,7],3,3000000,13000,99.57,"全量审计通过率下降","需要关注",["排查自定义规则异常"]),
            ("2026年5月数据质量汇总","monthly",[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14],15,6000000,13000,99.78,"汇总所有审计执行数据","通过",["持续改进数据质量"]),
        ]
        for rn, rt, eids, te, tr, texc, opr, summ, conc, recs in report_data:
            db.add(DqAuditReport(
                report_name=rn, report_type=rt, execution_ids=eids,
                total_executions=te, total_records=tr, total_exceptions=texc,
                overall_pass_rate=opr, summary=summ, conclusion=conc,
                recommendations=recs, status="published", created_by="system"))
        db.flush()
        print(f"  {len(report_data)} rows.")

        print("Audit tables seeded successfully.")

        # ================================================================
        # OPS_ROOT_CAUSE_TYPE (8 - tree: 4 parents + 4 children)
        # ================================================================
        print("ops_root_cause_type ...")
        rct_data = [
            ("DATA_ISSUE", "数据问题", None, 1, "数据相关根因分类", 1),
            ("SYSTEM_ISSUE", "系统问题", None, 1, "系统相关根因分类", 2),
            ("PROCESS_ISSUE", "流程问题", None, 1, "流程相关根因分类", 3),
            ("EXTERNAL_ISSUE", "外部原因", None, 1, "外部因素根因分类", 4),
        ]
        rctypes = []
        for tc, tn, pid, lv, desc, so in rct_data:
            r = OpsRootCauseType(type_code=tc, type_name=tn, parent_id=pid, level=lv,
                                  description=desc, sort_order=so, status=1)
            db.add(r)
            rctypes.append(r)
        db.flush()

        rct_child_data = [
            (0, "DATA_MISSING", "数据缺失", 2, "数据缺失或为空", 1),
            (1, "SYSTEM_FAILURE", "系统故障", 2, "系统宕机或异常", 1),
            (2, "PROCESS_ERROR", "人工失误", 2, "操作人员失误", 1),
            (3, "UPSTREAM_ANOMALY", "上游数据异常", 2, "上游数据源问题", 1),
        ]
        for pidx, tc, tn, lv, desc, so in rct_child_data:
            r = OpsRootCauseType(type_code=tc, type_name=tn, parent_id=rctypes[pidx].id,
                                  level=lv, description=desc, sort_order=so, status=1)
            db.add(r)
            rctypes.append(r)
        db.flush()
        print(f"  {len(rctypes)} rows.")

        # ================================================================
        # OPS_TASK_LINEAGE (10)
        # ================================================================
        print("ops_task_lineage ...")
        lineage_data = [
            ("ETL_BILL_001","账单数据导入","etl",["SRC_BILL_RAW"],["DWD_BILL_CLEAN"],"billing_raw","billing_dwd","daily","张三","数据管理部"),
            ("ETL_USER_001","用户数据导入","etl",["SRC_USER_RAW"],["DWD_USER_CLEAN"],"crm_raw","crm_dwd","daily","李四","数据管理部"),
            ("ETL_CHARGE_001","计费数据导入","etl",["SRC_CHARGE_RAW"],["DWD_CHARGE_CLEAN"],"charging_raw","charging_dwd","daily","王五","数据管理部"),
            ("DQC_USER_001","用户数据质量检查","dqc",["DWD_USER_CLEAN"],["DWS_USER_QUALITY"],"crm_dwd","quality_check","daily","赵六","质量监控部"),
            ("DQC_BILL_001","账单数据质量检查","dqc",["DWD_BILL_CLEAN"],["DWS_BILL_QUALITY"],"billing_dwd","quality_check","daily","孙七","质量监控部"),
            ("RPT_MONTHLY_001","月账报表生成","report",["DWS_BILL_QUALITY","DWS_USER_QUALITY"],["RPT_MONTHLY_SUMMARY"],"quality_check","reporting","monthly","周八","数据产品部"),
            ("API_BILL_SYNC","账单数据对外同步","api",["DWD_BILL_CLEAN"],["EXT_BILL_API"],"billing_dwd","external_api","daily","吴九","技术研发部"),
            ("ETL_PAYMENT_001","支付数据导入","etl",["SRC_PAYMENT_RAW"],["DWD_PAYMENT_CLEAN"],"payment_raw","payment_dwd","daily","郑十","数据管理部"),
            ("DQC_PAYMENT_001","支付数据质量检查","dqc",["DWD_PAYMENT_CLEAN"],["DWS_PAYMENT_QUALITY"],"payment_dwd","quality_check","daily","陈一","质量监控部"),
            ("RPT_KPI_001","KPI指标计算","report",["DWS_BILL_QUALITY","DWS_USER_QUALITY","DWS_PAYMENT_QUALITY"],["RPT_KPI_DASHBOARD"],"quality_check","kpi_dashboard","daily","林二","数据产品部"),
        ]
        for tc, tn, tt, up, down, dsi, dso, sched, owner, dept in lineage_data:
            db.add(OpsTaskLineage(
                task_code=tc, task_name=tn, task_type=tt, upstream_tasks=up,
                downstream_tasks=down, datasource_input=dsi, datasource_output=dso,
                schedule_type=sched, owner=owner, department=dept, status=1))
        db.flush()
        print(f"  {len(lineage_data)} rows.")


        # ================================================================
        # OPS_ROOT_CAUSE_ANALYSIS (10)
        # ================================================================
        print("ops_root_cause_analysis ...")
        analysis_data = [
            (0,0,"账单数据延迟根因分析","2026年5月账单数据导入延迟2小时",
             [{"step":"确认延迟范围","result":"ETL任务延迟2小时"},{"step":"检查上游依赖","result":"上游接口超时"},{"step":"定位根因","result":"数据源端连接池耗尽"}],
             "数据源端连接池配置不足导致接口响应超时",4,"上游系统连接池配置不足",0.92,"completed",True,1800,True,"张三"),
            (1,1,"用户数据异常增长分析","T_USER表数据量异常增长300%",
             [{"step":"确认异常字段","result":"用户表记录数异常"},{"step":"分析异常模式","result":"存在大量重复导入"},{"step":"追溯数据来源","result":"采集任务配置错误"},{"step":"定位根因","result":"批量导入脚本循环调用"}],
             "数据采集任务配置错误",4,"批量导入脚本缺少去重逻辑",0.95,"completed",True,900,True,"李四"),
            (2,2,"账单金额校验异常分析","账单金额负数校验失败",
             [{"step":"确认异常字段","result":"bill_amount存在负数"},{"step":"分析异常模式","result":"退款场景未区分"},{"step":"追溯数据来源","result":"计费规则变更"},{"step":"定位根因","result":"校验规则未同步更新"}],
             "计费规则变更后未更新校验规则",4,"规则变更管理流程缺失",0.88,"completed",False,1200,True,"王五"),
            (3,3,"ETL任务OOM崩溃分析","月账ETL任务内存溢出崩溃",
             [{"step":"确认故障现象","result":"Java进程OOM退出"},{"step":"检查系统日志","result":"OutOfMemoryError"},{"step":"分析调用链","result":"数据量超预期"},{"step":"定位根因","result":"JVM参数未调整"}],
             "数据量增长但JVM堆内存未相应调整",3,"JVM参数未随数据量增长调整",0.90,"completed",True,600,True,"赵六"),
            (4,0,"上游接口超时分析","CRM接口响应超时",
             [{"step":"确认故障现象","result":"HTTP 504"},{"step":"检查系统日志","result":"数据库锁等待"},{"step":"分析调用链","result":"全表扫描导致锁等待"},{"step":"定位根因","result":"缺少索引"}],
             "上游系统SQL缺少索引导致全表扫描",4,"缺少关键查询索引",0.85,"completed",False,2400,True,"孙七"),
            (0,0,"账单数据延迟回溯分析","2026年5月第2次账单延迟",
             [{"step":"确认延迟范围","result":"延迟30分钟"},{"step":"检查资源使用","result":"CPU使用率100%"},{"step":"定位根因","result":"资源竞争"}],
             "资源隔离不充分",4,"资源隔离不充分",0.75,"completed",False,1200,False,"张三"),
            (5,4,"支付对账差异分析","支付数据对账差额35万",
             [{"step":"确认业务影响","result":"财务对账不平"},{"step":"分析数据差异","result":"部分支付记录缺失"},{"step":"追溯业务变更","result":"支付系统版本升级"},{"step":"定位根因","result":"升级后数据同步逻辑变更"}],
             "支付系统升级导致数据未同步",5,"系统升级未充分测试数据同步",0.70,"analyzing",False,3600,False,"吴九"),
            (6,2,"质量审计任务失败分析","全量审计任务执行中断",
             [{"step":"确认故障现象","result":"任务执行中断"},{"step":"检查系统日志","result":"内存不足"},{"step":"定位根因","result":"采样率过高"}],
             "全量审计配置采样率100%导致OOM",4,"审计策略未考虑数据量",0.82,"completed",False,900,True,"周八"),
            (7,1,"KPI指标异常分析","KPI完成率突降至60%",
             [{"step":"确认异常字段","result":"completion_rate=60%"},{"step":"分析异常模式","result":"多个任务未完成"},{"step":"追溯数据来源","result":"月账任务进度延迟"},{"step":"定位根因","result":"任务依赖阻塞"}],
             "关键依赖任务未完成导致KPI偏低",4,"任务依赖链路未设超时机制",0.78,"analyzing",False,1800,False,"林二"),
            (2,3,"金额校验规则优化分析","金额范围校验误报分析",
             [{"step":"确认异常数据","result":"退款金额被误报"},{"step":"分析规则逻辑","result":"规则未排除退款场景"},{"step":"优化方案","result":"增加退款类型判断"},{"step":"验证结果","result":"误报率降至0.1%"}],
             "规则未考虑退款场景导致误报",6,"规则设计未涵盖所有业务场景",0.93,"completed",True,3600,True,"王五"),
        ]
        analyses = []
        for cidx, pidx, atitle, pdesc, aproc, conc, rctidx, rcdesc, conf, st, issaved, dur, ai, creator in analysis_data:
            a = OpsRootCauseAnalysis(
                case_id=cases[cidx].id, path_id=paths[pidx].id, analysis_title=atitle,
                problem_description=pdesc, analysis_process=aproc, conclusion=conc,
                root_cause_type_id=rctypes[rctidx].id, root_cause_desc=rcdesc,
                confidence=conf, status=st, is_saved_as_case=issaved,
                analysis_duration=dur, ai_assisted=ai, created_by=creator)
            db.add(a)
            analyses.append(a)
        db.flush()
        print(f"  {len(analyses)} rows.")


        # ================================================================
        # OPS_ANALYSIS_TRACE_LOG (20)
        # ================================================================
        print("ops_analysis_trace_log ...")
        trace_data = [
            (0,"确认延迟范围",1,"query_task_log",{"task_code":"ETL_BILL_001"},{"delay_minutes":120},"查询任务日志确认延迟时间","completed",1500),
            (0,"检查上游依赖",2,"check_upstream",{"task_code":"ETL_BILL_001"},{"upstream_status":"timeout"},"检查上游任务完成状态","completed",2300),
            (0,"分析资源瓶颈",3,"analyze_resources",{"server":"etl-server-01"},{"cpu":"95%","mem":"80%"},"分析服务器资源使用情况","completed",1800),
            (0,"定位根因",4,"identify_root_cause",{},{"root_cause":"conn_pool_exhausted"},"综合以上分析定位根因","completed",500),
            (1,"确认异常字段",1,"query_audit_result",{"audit_id":"AUDIT_001"},{"anomaly_field":"user_name"},"查询审计结果定位异常字段","completed",800),
            (1,"分析异常模式",2,"analyze_pattern",{"field":"user_name"},{"pattern":"duplicate_import"},"分析异常数据分布模式","completed",1200),
            (1,"追溯数据来源",3,"trace_lineage",{"table":"T_USER"},{"source":"ETL_USER_001"},"追踪数据血缘关系","completed",2000),
            (1,"定位根因",4,"identify_root_cause",{},{"root_cause":"loop_import_bug"},"定位根本原因","completed",300),
            (2,"确认异常字段",1,"query_audit_result",{"audit_id":"AUDIT_002"},{"anomaly_field":"bill_amount"},"查询审计结果","completed",600),
            (2,"分析异常模式",2,"analyze_pattern",{"field":"bill_amount"},{"pattern":"negative_value"},"分析异常模式","completed",1500),
            (3,"确认故障现象",1,"check_system_status",{"server":"etl-server-01"},{"status":"crashed"},"检查系统运行状态","completed",300),
            (3,"检查系统日志",2,"analyze_logs",{"service":"etl-service"},{"error":"OutOfMemoryError"},"分析系统日志定位错误","completed",2500),
            (4,"确认故障现象",1,"check_system_status",{"server":"crm-server"},{"status":"slow"},"检查上游系统状态","completed",400),
            (4,"检查系统日志",2,"analyze_logs",{"service":"crm-api"},{"error":"Lock wait timeout"},"分析系统日志","completed",1800),
            (6,"确认业务影响",1,"assess_business_impact",{"case_id":6},{"impact_amount":350000},"评估业务影响范围","completed",2000),
            (6,"分析数据差异",2,"compare_data",{"source":"payment","target":"settlement"},{"diff_count":5000},"对比数据差异","completed",3000),
            (8,"确认异常字段",1,"query_audit_result",{"audit_id":"AUDIT_003"},{"anomaly_field":"completion_rate"},"查询KPI数据","completed",500),
            (8,"分析异常模式",2,"analyze_pattern",{"field":"completion_rate"},{"pattern":"downward_trend"},"分析下降趋势","completed",1000),
            (9,"确认异常数据",1,"query_audit_result",{"rule_id":"RULE_RANGE_AMOUNT"},{"false_positive_rate":0.3},"检查规则误报情况","completed",1800),
            (9,"分析规则逻辑",2,"analyze_pattern",{"rule":"RULE_RANGE_AMOUNT"},{"issue":"refund_unhandled"},"分析规则逻辑缺陷","completed",2200),
        ]
        for aidx, sn, so, action, inp, out, reason, st, dur in trace_data:
            db.add(OpsAnalysisTraceLog(
                analysis_id=analyses[aidx].id, step_name=sn, step_order=so,
                action=action, input_data=inp, output_data=out, reasoning=reason,
                status=st, duration=dur))
        db.flush()
        print(f"  {len(trace_data)} rows.")

        # ================================================================
        # OPS_USER_FEEDBACK (12)
        # ================================================================
        print("ops_user_feedback ...")
        fb_data = [
            (0,0,"helpful",5,"分析结果非常准确帮助我们快速定位了问题原因","张三","数据管理部",True),
            (1,1,"useful",4,"案例很有参考价值减少了排查时间","李四","数据管理部",True),
            (2,2,"accurate",5,"根因分析定位准确解决方案有效","王五","质量监控部",True),
            (3,3,"timely",4,"分析速度快在问题升级前完成了定位","赵六","运维保障部",True),
            (0,0,"useful",4,"数据延迟分析很全面建议补充网络层检查","孙七","技术研发部",True),
            (4,4,"helpful",3,"分析结果有帮助但缺少具体优化建议","周八","技术研发部",True),
            (5,5,"other",2,"正在处理中暂时无法评价完整效果","吴九","财务结算部",False),
            (6,6,"useful",4,"审计任务失败的根因分析很到位","郑十","质量监控部",True),
            (7,7,"accurate",5,"KPI异常分析建议已被采纳优化了计算逻辑","陈一","数据产品部",True),
            (2,2,"useful",4,"规则优化分析帮助我们减少了误报率","林二","质量监控部",True),
            (1,1,"timely",5,"数据异常增长案例第一时间匹配成功","黄三","数据管理部",True),
            (3,3,"helpful",4,"OOM分析建议已落实JVM参数已调整","刘四","运维保障部",True),
        ]
        for aidx, cidx, ft, rating, fbc, un, ud, resolved in fb_data:
            db.add(OpsUserFeedback(
                analysis_id=analyses[aidx].id, case_id=cases[cidx].id,
                feedback_type=ft, rating=rating, content=fbc,
                user_name=un, user_department=ud, is_resolved=resolved))
        db.flush()
        print(f"  {len(fb_data)} rows.")

        print("Root cause tables seeded successfully.")

        # ================================================================
        # MA_MONTH_ACCOUNT_CONFIG (6)
        # ================================================================
        print("ma_month_account_config ...")
        month_data = [
            ("2025-01","2025年1月账期","monthly",date(2025,1,1),date(2025,1,31),"completed",100.0,50,50,0,98.5,"张三"),
            ("2025-02","2025年2月账期","monthly",date(2025,2,1),date(2025,2,28),"completed",100.0,50,50,0,97.8,"张三"),
            ("2025-03","2025年3月账期","monthly",date(2025,3,1),date(2025,3,31),"completed",100.0,50,49,1,96.2,"李四"),
            ("2025-04","2025年4月账期","monthly",date(2025,4,1),date(2025,4,30),"completed",100.0,50,50,0,99.1,"李四"),
            ("2025-05","2025年5月账期","monthly",date(2025,5,1),date(2025,5,31),"completed",100.0,50,48,2,95.5,"王五"),
            ("2025-06","2025年6月账期","monthly",date(2025,6,1),date(2025,6,30),"processing",65.0,50,33,1,0,"王五"),
        ]
        months = []
        for am, an, at, sd, ed, st, prog, tt, ct, ft, qs, owner in month_data:
            m = MaMonthAccountConfig(
                account_month=am, account_name=an, account_type=at, start_date=sd, end_date=ed,
                status=st, progress=prog, total_tasks=tt, completed_tasks=ct, failed_tasks=ft,
                quality_score=qs, owner=owner, created_by="system")
            db.add(m)
            months.append(m)
        db.flush()
        print(f"  {len(months)} rows.")

        # ================================================================
        # MA_TASK_MONITOR (20)
        # ================================================================
        print("ma_task_monitor ...")
        task_mon_data = [
            ("2025-01","TASK_IMP_DATA_001","用户数据导入","etl","high","completed",100.0,2,4,2,4,120,180,"张三",True),
            ("2025-01","TASK_IMP_BILL_001","账单数据导入","etl","urgent","completed",100.0,2,6,2,6,300,240,"张三",True),
            ("2025-01","TASK_DQC_USER_001","用户数据质量检查","dqc","high","completed",100.0,3,5,3,5,150,120,"李四",True),
            ("2025-01","TASK_DQC_BILL_001","账单数据质量检查","dqc","high","completed",100.0,3,5,3,5,180,150,"李四",True),
            ("2025-02","TASK_IMP_DATA_001","用户数据导入","etl","high","completed",100.0,2,4,2,4,130,180,"张三",True),
            ("2025-02","TASK_IMP_BILL_001","账单数据导入","etl","urgent","completed",100.0,2,6,2,6,280,240,"张三",True),
            ("2025-03","TASK_IMP_BILL_001","账单数据导入","etl","urgent","completed",100.0,2,6,2,6,350,240,"张三",True),
            ("2025-03","TASK_DQC_BILL_001","账单数据质量检查","dqc","high","failed",80.0,3,5,3,5,200,150,"李四",True),
            ("2025-04","TASK_IMP_DATA_001","用户数据导入","etl","high","completed",100.0,2,4,2,4,110,180,"张三",True),
            ("2025-04","TASK_RPT_001","月账报表生成","report","urgent","completed",100.0,5,8,5,8,600,480,"王五",True),
            ("2025-05","TASK_IMP_DATA_001","用户数据导入","etl","high","completed",100.0,2,4,2,4,140,180,"张三",True),
            ("2025-05","TASK_IMP_BILL_001","账单数据导入","etl","urgent","completed",100.0,2,6,2,6,320,240,"张三",True),
            ("2025-05","TASK_DQC_USER_001","用户数据质量检查","dqc","high","completed",100.0,3,5,3,5,160,120,"李四",True),
            ("2025-05","TASK_DQC_BILL_001","账单数据质量检查","dqc","high","failed",75.0,3,5,3,5,210,150,"李四",True),
            ("2025-05","TASK_RPT_001","月账报表生成","report","urgent","completed",100.0,5,8,5,8,550,480,"王五",True),
            ("2025-06","TASK_IMP_DATA_001","用户数据导入","etl","high","running",60.0,2,4,1,0,0,180,"张三",True),
            ("2025-06","TASK_IMP_BILL_001","账单数据导入","etl","urgent","running",80.0,2,6,1,0,0,240,"张三",True),
            ("2025-06","TASK_DQC_USER_001","用户数据质量检查","dqc","high","pending",0,3,5,0,0,0,120,"李四",True),
            ("2025-06","TASK_DQC_BILL_001","账单数据质量检查","dqc","high","pending",0,3,5,0,0,0,150,"李四",True),
            ("2025-06","TASK_RPT_001","月账报表生成","report","urgent","pending",0,5,8,0,0,0,480,"王五",True),
        ]
        for am, tc, tn, tt, pri, st, prog, pst, pet, ast, aet, dur, edur, owner, crit in task_mon_data:
            pst_dt = NOW - timedelta(hours=pst * 24) if pst > 0 else None
            pet_dt = NOW - timedelta(hours=pet * 24) if pet > 0 else None
            ast_dt = NOW - timedelta(hours=ast * 24) if ast > 0 else None
            aet_dt = NOW - timedelta(hours=aet * 24) if aet > 0 else None
            db.add(MaTaskMonitor(
                account_month=am, task_code=tc, task_name=tn, task_type=tt, priority=pri,
                status=st, progress=prog, plan_start_time=pst_dt, plan_end_time=pet_dt,
                actual_start_time=ast_dt, actual_end_time=aet_dt, duration_seconds=dur,
                expected_duration=edur, owner=owner, is_critical=crit))
        db.flush()
        print(f"  {len(task_mon_data)} rows.")


        # ================================================================
        # MA_KPI_METRICS (15)
        # ================================================================
        print("ma_kpi_metrics ...")
        kpi_data = [
            ("2025-01","KPI_TASK_COMP","任务完成率","efficiency",100.0,100.0,"%","stable","good"),
            ("2025-01","KPI_DATA_QUALITY","数据质量评分","quality",95.0,98.5,"分","up","good"),
            ("2025-01","KPI_ON_TIME","准时完成率","efficiency",100.0,100.0,"%","stable","good"),
            ("2025-02","KPI_TASK_COMP","任务完成率","efficiency",100.0,100.0,"%","stable","good"),
            ("2025-02","KPI_DATA_QUALITY","数据质量评分","quality",95.0,97.8,"分","down","good"),
            ("2025-03","KPI_TASK_COMP","任务完成率","efficiency",100.0,98.0,"%","down","warning"),
            ("2025-03","KPI_DATA_QUALITY","数据质量评分","quality",95.0,96.2,"分","down","warning"),
            ("2025-04","KPI_TASK_COMP","任务完成率","efficiency",100.0,100.0,"%","up","good"),
            ("2025-04","KPI_DATA_QUALITY","数据质量评分","quality",95.0,99.1,"分","up","good"),
            ("2025-05","KPI_TASK_COMP","任务完成率","efficiency",100.0,96.0,"%","down","warning"),
            ("2025-05","KPI_DATA_QUALITY","数据质量评分","quality",95.0,95.5,"分","down","warning"),
            ("2025-01","KPI_PROCESS_TIME","平均处理时长","efficiency",240,210,"分钟","down","good"),
            ("2025-03","KPI_PROCESS_TIME","平均处理时长","efficiency",240,280,"分钟","up","warning"),
            ("2025-05","KPI_PROCESS_TIME","平均处理时长","efficiency",240,260,"分钟","up","warning"),
            ("2025-06","KPI_TASK_COMP","任务完成率","efficiency",100.0,66.0,"%","stable","good"),
        ]
        for am, mc, mn, mcat, tv, av, unit, trend, st in kpi_data:
            db.add(MaKpiMetrics(
                account_month=am, metric_code=mc, metric_name=mn, metric_category=mcat,
                target_value=tv, actual_value=av, unit=unit, trend=trend, status=st,
                formula="count(task)/total*100", data_source="月账任务系统"))
        db.flush()
        print(f"  {len(kpi_data)} rows.")

        # ================================================================
        # MA_MILESTONE_TRACK (8)
        # ================================================================
        print("ma_milestone_track ...")
        ms_track_data = [
            ("2025-05","用户作业完成","stage",date(2025,5,1),date(2025,5,1),"completed",0,100.0,"张三","用户作业阶段完成"),
            ("2025-05","前置作业完成","stage",date(2025,5,2),date(2025,5,2),"completed",0,100.0,"李四","前置作业阶段完成"),
            ("2025-05","实收作业完成","stage",date(2025,5,5),date(2025,5,6),"delayed",1,100.0,"王五","实收作业阶段完成延迟1天"),
            ("2025-05","应收作业完成","stage",date(2025,5,8),date(2025,5,10),"delayed",2,100.0,"赵六","应收作业延迟2天"),
            ("2025-05","集团作业完成","stage",date(2025,5,10),date(2025,5,12),"delayed",2,100.0,"孙七","集团作业延迟2天"),
            ("2025-06","用户作业完成","stage",date(2025,6,1),date(2025,6,1),"completed",0,100.0,"张三","用户作业按时完成"),
            ("2025-06","前置作业完成","stage",date(2025,6,2),None,"running",0,60.0,"李四","前置作业进行中"),
            ("2025-06","实收作业处理","stage",date(2025,6,5),None,"pending",0,0,"王五","等待前置作业完成"),
        ]
        for am, mn, mt, pd, ad, st, dd, cp, rp, desc in ms_track_data:
            db.add(MaMilestoneTrack(
                account_month=am, milestone_name=mn, milestone_type=mt,
                plan_date=pd, actual_date=ad, status=st, delay_days=dd,
                completion_percentage=cp, responsible_person=rp, description=desc))
        db.flush()
        print(f"  {len(ms_track_data)} rows.")

        # ================================================================
        # MA_ALERT_RECORD (15)
        # ================================================================
        print("ma_alert_record ...")
        alert_data = [
            ("2025-03","账单数据质量检查失败","task_failure","critical","质量监控系统",7,"账单数据质量检查","unread",None),
            ("2025-03","数据导入延迟告警","schedule_delay","warning","调度系统",6,"账单数据导入","read","张三"),
            ("2025-05","ETL任务OOM崩溃","task_failure","critical","监控系统",3,"ETL任务","handled","赵六"),
            ("2025-05","数据导入延迟告警","schedule_delay","warning","调度系统",1,"用户数据导入","read","张三"),
            ("2025-05","金额校验异常","data_anomaly","warning","审计引擎",2,"金额范围检查","handled","李四"),
            ("2025-05","上游接口超时","task_failure","warning","API网关",4,"账单数据导入","handled","孙七"),
            ("2025-05","质量评分下降","quality_issue","info","质量监控系统",5,"全量审计","unread",None),
            ("2025-06","用户数据导入延迟","schedule_delay","info","调度系统",0,"用户数据导入","unread",None),
            ("2025-06","磁盘空间不足","task_failure","warning","监控系统",0,"ETL任务","unread",None),
            ("2025-04","数据质量评分优秀","quality_issue","info","质量监控系统",8,"全量审计","read","王五"),
            ("2025-03","任务重试超过阈值","task_failure","warning","调度系统",7,"账单数据质量检查","handled","李四"),
            ("2025-04","月账结算完成通知","quality_issue","info","结算系统",9,"月账报表生成","read","赵明"),
            ("2025-05","实时流质量抖动","data_anomaly","info","实时监控",5,"实时数据流质量监控","read","周八"),
            ("2025-05","KPI异常告警","data_anomaly","warning","KPI系统",8,"KPI指标计算","handled","林二"),
            ("2025-06","定时任务未触发","task_failure","critical","调度系统",0,"KPI指标计算","unread",None),
        ]
        for am, title, at, al, src, tid, tn, st, handler in alert_data:
            db.add(MaAlertRecord(
                account_month=am, alert_title=title, alert_type=at, alert_level=al,
                source=src, related_task_id=tid, related_task_name=tn, status=st,
                handler=handler, content=f"告警内容: {title}",
                handle_time=handler and NOW - timedelta(hours=random.randint(1, 48)) or None,
                handle_result=handler and "已处理" or None))
        db.flush()
        print(f"  {len(alert_data)} rows.")

        # ================================================================
        # MA_ML_MODEL_CONFIG (4)
        # ================================================================
        print("ma_ml_model_config ...")
        ml_data = [
            ("异常检测模型v2.1","ML_ANOMALY_V2_1","anomaly_detection","2.1","Isolation Forest",
             {"n_estimators":100,"contamination":0.1},["bill_amount","charge_amount","record_count"],
             "异常率","monthly",NOW - timedelta(days=15),97.2,"active","系统"),
            ("数据预测模型v1.0","ML_FORECAST_V1_0","forecast","1.0","Prophet",
             {"seasonality_mode":"multiplicative","yearly_seasonality":True},["bill_amount","user_count"],
             "账单金额预测","monthly",NOW - timedelta(days=30),93.5,"active","系统"),
            ("数据分类模型v3.0","ML_CLASSIFY_V3_0","classification","3.0","XGBoost",
             {"max_depth":6,"learning_rate":0.3,"n_estimators":200},["payment_status","charge_type"],
             "用户分类准确率","weekly",NOW - timedelta(days=7),96.8,"active","系统"),
            ("回归预测模型v1.2","ML_REGRESSION_V1_2","regression","1.2","LinearRegression",
             {"fit_intercept":True,"normalize":False},["kpi_value","completion_rate"],
             "KPI趋势预测","monthly",NOW - timedelta(days=60),89.2,"inactive","系统"),
        ]
        for mn, mc, mt, mv, algo, params, features, target, tf, lta, acc, st, cb in ml_data:
            db.add(MaMlModelConfig(
                model_name=mn, model_code=mc, model_type=mt, model_version=mv,
                algorithm=algo, parameters=params, features=features,
                target_metric=target, training_frequency=tf, last_trained_at=lta,
                accuracy=acc, status=st, created_by=cb))
        db.flush()
        print(f"  {len(ml_data)} rows.")

        print("Monthly base tables seeded successfully.")

        # ================================================================
        # MA_CONFIG_STAGE (5)
        # ================================================================
        print("ma_config_stage ...")
        stage_names = ["用户作业","前置作业","实收作业","应收作业","集团作业"]
        stage_statuses = ["completed","completed","running","pending","pending"]
        stages_config = []
        for si, (sname, sst) in enumerate(zip(stage_names, stage_statuses)):
            stg = MaConfigStage(stage_code=f"ST_{si}", name=sname, sort_order=si+1, status=sst)
            db.add(stg)
            stages_config.append(stg)
        db.flush()

        wp_end_times = {}
        ms_end_times = {}
        st_end_times = {}

        # ================================================================
        # MA_CONFIG_MILESTONE (~22)
        # ================================================================
        print("ma_config_milestone ...")
        ms_names_by_stage = {
            0: ["用户作业-1号任务","用户作业-2号任务","用户作业-3号任务"],
            1: ["前置作业-1号任务","前置作业-2号任务","前置作业-3号任务","前置作业-4号任务"],
            2: ["实收作业-1号任务","实收作业-2号任务","实收作业-3号任务",
                "实收作业-4号任务","实收作业-5号任务","实收作业-6号任务",
                "实收作业-7号任务","实收作业-8号任务","实收作业-9号任务"],
            3: ["应收作业-1号任务","应收作业-2号任务","应收作业-3号任务"],
            4: ["集团作业-1号任务","集团作业-2号任务","集团作业-3号任务"],
        }

        def get_ms_status(si, mi):
            if si < 2: return "completed"
            if si == 2:
                if mi < 3: return "completed"
                if mi == 3: return "running"
                return "pending"
            return "pending"

        milestones_config = []
        for si, stage in enumerate(stages_config):
            for mi, ms_name in enumerate(ms_names_by_stage[si]):
                mst = get_ms_status(si, mi)
                ms = MaConfigMilestone(
                    stage_id=stage.id, milestone_code=f"MS_{si}_{mi}", name=ms_name,
                    sort_order=mi+1, status=mst,
                    progress_pct=100.0 if mst == "completed" else (50.0 if mst == "running" else 0.0))
                db.add(ms)
                milestones_config.append((si, mi, ms))
        db.flush()

        # ================================================================
        # MA_CONFIG_WORK_PLAN (~65)
        # ================================================================
        print("ma_config_work_plan ...")
        plan_templates = [
            ("截图计费1号批次接口层采集任务启动情况","1日10:00","人工",False),
            ("检查用户数据完整性并发送通知","1日12:00","数字员工",True),
            ("实收数据核对与稽核","2日09:00","数字员工",False),
            ("应收账单生成与校验","3日08:00","数字员工",False),
            ("集团数据汇总上报","5日14:00","数字员工",False),
        ]

        def get_plan_status(ms_st, pi):
            if ms_st == "completed": return "completed"
            if ms_st == "running":
                if pi < 2: return "completed"
                if pi == 2: return "running"
                return "pending"
            return "pending"

        work_plans = []
        for si, mi, ms in milestones_config:
            plan_count = random.randint(2, 5)
            for pi in range(plan_count):
                template = plan_templates[(si + mi + pi) % len(plan_templates)]
                pst = get_plan_status(ms.status, pi)
                wp = MaConfigWorkPlan(
                    milestone_id=ms.id, plan_code=f"PL_{si}_{mi}_{pi}",
                    seq_no=pi+1, name=template[0], time_point=template[1],
                    task_mode=template[2], is_system_task=template[3], status=pst)
                db.add(wp)
                work_plans.append((si, mi, pi, wp))
        db.flush()

        # ================================================================
        # MA_CONFIG_TASK (~157)
        # ================================================================
        print("ma_config_task ...")
        task_templates = [
            ("MANUAL_OP","截图计费1号批次接口层采集任务启动情况"),
            ("TDP_TASK","[TDP][统一处理][序号2251][月]INFBSN一号批次_1"),
            ("PUBLISH_MSG","前置作业3：计费1号批次接口层采集任务已启动"),
            ("SQL_SCRIPT","select count(*) from T_USER where status = 'ACTIVE'"),
            ("MANUAL_OP","核对实收数据与银行对账单一致性"),
            ("TDP_TASK","[TDP][统一处理][序号2252][月]INFBSN二号批次_1"),
            ("SQL_SCRIPT","update T_BILL set status = 'PROCESSED' where bill_date = '2026-06-01'"),
            ("PUBLISH_MSG","实收作业完成通知：本月实收数据已核对完毕"),
        ]

        def get_task_status(wp_st, ti):
            if wp_st == "completed": return "completed"
            if wp_st == "running":
                if ti < 2: return "completed"
                return "pending"
            return "pending"

        BASE_DT = datetime(2026, 6, 1, 9, 0, 0)

        for si, mi, pi, wp in work_plans:
            task_count = random.randint(1, 4)
            for ti in range(task_count):
                template = task_templates[(si + mi + pi + ti) % len(task_templates)]
                tst = get_task_status(wp.status, ti)
                start_time = None
                end_time = None
                if tst == "completed":
                    start_time = BASE_DT + timedelta(hours=random.randint(0, 48))
                    end_time = start_time + timedelta(minutes=random.randint(10, 120))
                elif tst == "running":
                    start_time = BASE_DT + timedelta(hours=random.randint(0, 48))

                task = MaConfigTask(
                    plan_id=wp.id, task_code=f"TK_{si}_{mi}_{pi}_{ti}",
                    task_type=template[0], content=template[1],
                    sort_order=ti+1, status=tst, start_time=start_time, end_time=end_time)
                db.add(task)
                if end_time:
                    wp_end_times.setdefault(wp.id, []).append((ti + 1, end_time))
        db.flush()

        # Compute completed_at for work_plans
        for wp_id, times in wp_end_times.items():
            latest = max(times, key=lambda x: x[0])
            result = db.execute(select(MaConfigWorkPlan).where(MaConfigWorkPlan.id == wp_id))
            wp_obj = result.scalar_one()
            wp_obj.completed_at = latest[1]
            ms_end_times.setdefault(wp_obj.milestone_id, []).append((wp_obj.seq_no, latest[1]))
        db.flush()

        # Compute completed_at for milestones
        for ms_id, times in ms_end_times.items():
            latest = max(times, key=lambda x: x[0])
            result = db.execute(select(MaConfigMilestone).where(MaConfigMilestone.id == ms_id))
            ms_obj = result.scalar_one()
            ms_obj.completed_at = latest[1]
            st_end_times.setdefault(ms_obj.stage_id, []).append((ms_obj.sort_order, latest[1]))
        db.flush()

        # Compute completed_at for stages
        for st_id, times in st_end_times.items():
            latest = max(times, key=lambda x: x[0])
            result = db.execute(select(MaConfigStage).where(MaConfigStage.id == st_id))
            stg_obj = result.scalar_one()
            stg_obj.completed_at = latest[1]
        db.flush()
        print(f"  stages: {len(stages_config)}, milestones: {len(milestones_config)}, plans: {len(work_plans)}")

        # ================================================================
        # AI_CHAT_SESSION (10)
        # ================================================================
        print("ai_chat_session ...")
        session_data = [
            ("月账数据分析咨询","analysis",5,"孙七","关于月账进度和异常分析的问题",5,"active",True),
            ("数据质量审计辅助","audit",7,"吴九","审计规则配置和异常分析对话",8,"active",False),
            ("根因分析咨询","analysis",3,"王五","关于ETL任务OOM根因分析",3,"active",False),
            ("月报生成辅助","report",12,"刘四","月度报告生成和数据汇总对话",6,"active",True),
            ("系统操作指南","general",1,"张三","系统功能使用咨询",4,"active",False),
            ("KPI分析对话","analysis",18,"何十","KPI指标趋势分析和优化建议",7,"archived",False),
            ("AI模型配置咨询","general",0,"admin","ML模型参数配置咨询",10,"active",True),
            ("调账审核辅助","audit",9,"陈一","调账记录审核相关对话",3,"active",False),
            ("任务调度咨询","general",4,"赵六","任务调度配置和优化咨询",2,"active",False),
            ("案例库检索","general",12,"刘四","历史案例检索和相似度匹配",5,"archived",False),
        ]
        sessions = []
        for title, stype, uid, uname, summary, mcount, status, pinned in session_data:
            s = AiChatSession(
                session_title=title, session_type=stype, user_id=users[uid].id,
                user_name=uname, context_summary=summary, message_count=mcount,
                status=status, is_pinned=pinned)
            db.add(s)
            sessions.append(s)
        db.flush()
        print(f"  {len(sessions)} rows.")

        # ================================================================
        # AI_CHAT_MESSAGE (~30)
        # ================================================================
        print("ai_chat_message ...")
        msg_data = [
            (0,"user","请帮我分析2025年5月的月账数据情况","text",15,"gpt-4",None,5),
            (0,"assistant","好的，我来分析2025年5月的月账数据。从系统数据来看，5月账期整体完成率为96%，其中ETL任务出现了OOM异常导致部分任务延迟。主要问题包括：\n1. ETL任务OOM崩溃（已修复）\n2. 账单数据质量检查失败\n3. 部分任务延迟2天\n建议关注资源使用情况并及时调整JVM参数。","markdown",156,"gpt-4",None,None),
            (0,"user","那6月的进展情况如何？","text",10,"gpt-4",None,None),
            (0,"assistant","6月账期目前处理中，进度约65%。当前用户作业和前置作业已完成，实收作业正在运行中。整体进度正常，预计可按期完成。","markdown",82,"gpt-4",None,None),
            (1,"user","帮我配置一条数据质量审计规则，检查手机号格式","text",18,"gpt-4",None,None),
            (1,"assistant","已为您创建手机号格式校验规则：\n- 规则名称：格式校验-手机号\n- 规则编码：RULE_FORMAT_PHONE\n- 校验模式：^1[3-9]\\d{9}$\n- 严重级别：high\n该规则将检查T_USER表中的phone_no字段是否符合手机号格式规范。","markdown",134,"gpt-4",None,5),
            (1,"user","能否生成一条SQL来查询异常数据？","text",14,"gpt-4",None,None),
            (1,"assistant","以下是查询手机号格式异常数据的SQL：\n```sql\nSELECT * FROM T_USER \nWHERE phone_no IS NOT NULL \nAND phone_no NOT REGEXP '^1[3-9]\\\\d{9}$';\n```\n这条SQL会返回所有手机号格式不符合规范的用户记录。","markdown",145,"gpt-4",None,None),
            (2,"user","ETL任务OOM的原因是什么？","text",12,"gpt-4",None,4),
            (2,"assistant","根据根因分析，ETL任务OOM的主要原因是：\n1. 数据量较上月增长了300%\n2. JVM堆内存仍为2G未调整\n3. 未设置数据量监控预警\n\n建议方案：\n- 将JVM堆内存调整为8G\n- 建立数据量增长趋势监控\n- 设置内存使用率告警阈值","markdown",195,"gpt-4",None,None),
            (3,"user","请生成2025年5月的月报摘要","text",14,"gpt-4",None,None),
            (3,"assistant","2025年5月账期总结报告摘要：\n\n本月整体完成率96%，质量评分95.5分。\n\n完成情况：\n- 用户作业：完成\n- 前置作业：完成\n- 实收作业：完成（延迟1天）\n- 应收作业：完成（延迟2天）\n- 集团作业：完成（延迟2天）\n\n主要异常：\n- ETL任务OOM崩溃（已修复）\n- 账单数据质量检查失败\n- KPI指标异常告警\n\n建议：关注资源使用，优化ETL性能。","markdown",280,"gpt-4",None,5),
            (3,"user","下月的改进计划有什么建议？","text",12,"gpt-4",None,None),
            (3,"assistant","基于本月情况，建议以下改进措施：\n1. 技术层面：调整JVM参数，增加数据量监控\n2. 流程层面：优化任务依赖关系，增加超时机制\n3. 质量层面：补充金额校验规则的退款场景\n4. 管理层面：建立月账处理SLA标准","markdown",168,"gpt-4",None,None),
            (4,"user","系统的用户管理功能在哪里？","text",13,"gpt-4",None,None),
            (4,"assistant","系统管理功能在左侧导航菜单中：\n1. 系统管理 > 用户管理：查看和操作用户列表\n2. 系统管理 > 角色管理：配置角色和权限\n3. 系统管理 > 配置管理：系统参数设置\n\n您可以通过点击左侧菜单的「系统管理」展开子菜单。","markdown",156,"gpt-4",None,None),
            (5,"user","KPI指标的趋势如何？","text",10,"gpt-4",None,None),
            (5,"assistant","2025年KPI趋势分析：\n\n任务完成率：\n- 1月：100% - 2月：100% - 3月：98% - 4月：100% - 5月：96%\n\n数据质量评分：\n- 1月：98.5 - 2月：97.8 - 3月：96.2 - 4月：99.1 - 5月：95.5\n\n平均处理时长(分钟)：\n- 1月：210 - 3月：280 - 5月：260\n\n建议关注5月指标下滑趋势，分析根因并制定改进措施。","markdown",245,"gpt-4",None,4),
            (6,"user","帮我配置一个异常检测模型","text",14,"gpt-4",None,None),
            (6,"assistant","已为您推荐异常检测模型配置：\n\n模型名称：异常检测模型v2.1\n算法：Isolation Forest\n参数：\n- n_estimators: 100\n- contamination: 0.1\n\n适用特征：\n- bill_amount（账单金额）\n- charge_amount（计费金额）\n- record_count（记录数）\n\n该模型已训练完成，准确率97.2%。","markdown",189,"gpt-4",None,5),
            (7,"user","审核一条调账申请记录","text",12,"gpt-4",None,None),
            (7,"assistant","请提供调账记录ID或相关信息，我将为您查询并给出审核建议。根据系统记录，目前有待审批的调账申请包括：\n- 2025-03-015：支付状态更新（待审批）","markdown",123,"gpt-4",None,None),
            (8,"user","如何配置定时任务调度？","text",13,"gpt-4",None,None),
            (8,"assistant","任务调度配置步骤如下：\n1. 进入系统监控 > 调度管理\n2. 点击新增任务调度\n3. 填写任务信息：\n   - 任务名称：如「月账数据导入」\n   - 触发类型：cron/interval/manual\n   - 配置表达式：如「0 2 * * *」表示每天2点执行\n4. 保存并启用\n\n当前系统已配置8个调度任务。","markdown",210,"gpt-4",None,None),
            (9,"user","帮我查找类似的数据延迟案例","text",14,"gpt-4",None,None),
            (9,"assistant","已找到相关案例：\n\n1. 账单数据延迟（2026-05-01）\n   - 根因：上游接口超时\n   - 解决时长：150分钟\n   - 评分：4.5\n\n2. 上游接口响应超时（2026-05-20）\n   - 根因：数据库锁等待\n   - 解决时长：120分钟\n   - 评分：4.0\n\n3. 数据采集延迟（2026-05-15）\n   - 根因：任务配置错误\n   - 解决时长：150分钟\n   - 评分：4.8\n\n建议参考案例1和案例2的解决方案。","markdown",256,"gpt-4",None,None),
            (0,"user","谢谢你的分析","text",4,"gpt-4",None,5),
            (0,"assistant","不客气，如果后续有任何问题，随时可以向我咨询。祝您工作顺利！","markdown",32,"gpt-4",None,None),
            (0,"user","数据质量审计的一般流程是什么？","text",15,"gpt-4",None,None),
            (0,"assistant","数据质量审计的标准流程：\n\n1. 配置阶段\n   - 配置审计字段\n   - 配置审计规则\n   - 配置审计任务\n\n2. 执行阶段\n   - 按调度执行审计\n   - 记录审计结果\n   - 发现异常数据\n\n3. 处理阶段\n   - 异常分类和处理\n   - 根因分析\n   - 修复验证\n\n4. 报告阶段\n   - 生成审计报告\n   - 提出改进建议\n   - 跟踪改进落实","markdown",231,"gpt-4",None,None),
            (1,"user","帮我查看当前的审计任务状态","text",14,"gpt-4",None,None),
            (1,"assistant","当前审计任务状态：\n\n1. 用户数据完整性审计 - 已完成\n2. 账单数据准确性审计 - 已完成\n3. 支付数据一致性审计 - 已完成\n4. 全量数据质量审计 - 已完成\n5. 月账数据专项审计 - 已完成\n6. 实时数据流质量监控 - 已完成\n7. KPI指标数据审计 - 已完成\n8. 上游数据源接入审计 - 待执行\n\n最近一次全量审计通过率：98.25%","markdown",189,"gpt-4",None,None),
        ]
        for sidx, role, msg_content, ct, tokens, model, meta, feedback in msg_data:
            db.add(AiChatMessage(
                session_id=sessions[sidx].id, role=role, content=msg_content,
                content_type=ct, tokens_used=tokens, ai_model=model,
                message_metadata=meta, feedback_score=feedback))
        db.flush()
        print(f"  {len(msg_data)} rows.")

        # ================================================================
        # FINAL COMMIT
        # ================================================================
        print("=" * 60)
        print("All 45 tables seeded successfully!")
        print("=" * 60)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"ERROR: Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
