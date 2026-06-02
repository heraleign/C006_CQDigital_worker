# -*- coding: utf-8 -*-
"""Seed ALL 45 tables. Uses Unicode-escaped Chinese text."""
import random
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, select, text, func
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL_SYNC, echo=False)
Session = sessionmaker(bind=engine)
r = random.Random(42)


# ===== Chinese text constants (Unicode-escaped) =====
DEPT_NAMES = ["\u6570\u636e\u7ba1\u7406\u90e8","\u6280\u672f\u7814\u53d1\u90e8","\u4e1a\u52a1\u8fd0\u8425\u90e8","\u8d28\u91cf\u76d1\u63a7\u90e8","\u8d22\u52a1\u7ed3\u7b97\u90e8","\u6570\u636e\u4ea7\u54c1\u90e8","\u8fd0\u7ef4\u4fdd\u969c\u90e8","\u7efc\u5408\u7ba1\u7406\u90e8"]
DEPT_CODES = ["DEPT_DATA","DEPT_TECH","DEPT_BIZ","DEPT_QA","DEPT_FIN","DEPT_DP","DEPT_OPS","DEPT_ADMIN"]
ROLE_NAMES = ["\u7cfb\u7edf\u7ba1\u7406\u5458","\u6570\u636e\u5206\u6790\u5e08","\u6570\u636e\u5de5\u7a0b\u5e08","\u8d28\u91cf\u5ba1\u6838\u5458","\u666e\u901a\u7528\u6237"]
ROLE_CODES = ["ROLE_ADMIN","ROLE_ANALYST","ROLE_ENGINEER","ROLE_AUDITOR","ROLE_USER"]
POSITIONS = ["\u6570\u636e\u5206\u6790\u5e08","\u6570\u636e\u5de5\u7a0b\u5e08","\u8fd0\u7ef4\u5de5\u7a0b\u5e08","\u8d28\u91cf\u5de5\u7a0b\u5e08","\u4ea7\u54c1\u7ecf\u7406","\u90e8\u95e8\u7ecf\u7406","\u603b\u76d1"]
FIELD_NAMES = [["\u7528\u6237\u0049\u0044"],["\u7528\u6237\u540d"],["\u624b\u673a\u53f7"],["\u90ae\u7bb1"],["\u8eab\u4efd\u8bc1"],["\u8ba2\u5355\u91d1\u989d"],["\u8d26\u671f"],["\u8d26\u5355\u91d1\u989d"],["\u4f59\u989d"]]
FIELD_KEYS = ["user_id","user_name","phone_no","email_addr","id_card","order_amount","bill_month","bill_amount","balance"]
TASK_NAMES = ["\u6708\u5ea6\u6570\u636e\u8d28\u91cf\u5ba1\u8ba1","\u5ba2\u6237\u4fe1\u606f\u5b8c\u6574\u6027\u5ba1\u8ba1","\u8ba1\u8d39\u51c6\u786e\u6027\u5ba1\u8ba1","\u8ba2\u5355\u6570\u636e\u5ba1\u8ba1","\u8d26\u5355\u6570\u636e\u4e00\u81f4\u6027\u5ba1\u8ba1","\u4ea7\u54c1\u6570\u636e\u8d28\u91cf\u5ba1\u8ba1","\u7528\u6237\u6570\u636e\u5b8c\u6574\u6027\u5ba1\u8ba1","\u8d22\u52a1\u62a5\u8868\u5ba1\u8ba1"]
EXC_TYPES = ["\u7a7a\u503c\u5f02\u5e38","\u6570\u636e\u91cd\u590d","\u683c\u5f0f\u9519\u8bef","\u8303\u56f4\u8d8a\u754c","\u5173\u8054\u7f3a\u5931","\u903b\u8f91\u9519\u8bef"]
ALERT_TYPES = ["task_failure","data_anomaly","schedule_delay","quality_issue"]
SEVERITIES = ["high","medium","low"]
SYS_TITLE = "\u6570\u636e\u8fd0\u7ef4\u6570\u5b57\u5458\u5de5\u5e73\u53f0"

def seed_all():
    """Seed all database tables with realistic data."""
    from app.models.system import SysDepartment, SysUser, SysRole, SysUserRole, SysPermission, SysConfig, SysDataDict, SysNotificationRecord, SysAuditLog
    from app.models.assistant import AiChatSession, AiChatMessage, SysAiConfig, SysInterfaceLog, SysJobSchedule
    from app.models.audit import DqAuditFieldConfig, DqAuditRuleConfig, DqAuditTaskConfig, DqTaskImportanceConfig, DqAlertUpgradeRule, DqAuditExecution, DqAuditException, DqAuditReport
    from app.models.monthly import MaMonthAccountConfig, MaTaskMonitor, MaAuditResult, MaAdjustmentRecord, MaDailyReport, MaSummaryReport, MaKpiMetrics, MaMilestoneTrack, MaAlertRecord, MaMlModelConfig
    from app.models.root_cause import OpsTaskLineage, OpsProblemCase, OpsAnalysisPath, OpsRootCauseType, OpsRootCauseAnalysis, OpsAnalysisTraceLog, OpsCaseUsageStats, OpsUserFeedback

    session = Session()
    now = datetime.now()
    try:
        # Truncate all tables
        session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for t in ["ai_chat_message","ai_chat_session","sys_ai_config","sys_interface_log","sys_job_schedule","sys_audit_log","sys_notification_record","sys_data_dict","sys_config","sys_role_permission","sys_user_role","sys_permission","sys_user","sys_role","sys_department","ops_user_feedback","ops_case_usage_stats","ops_analysis_trace_log","ops_root_cause_analysis","ops_root_cause_type","ops_problem_case","ops_analysis_path","ops_task_lineage","ma_alert_record","ma_ml_model_config","ma_milestone_track","ma_kpi_metrics","ma_summary_report","ma_daily_report","ma_adjustment_record","ma_audit_result","ma_task_monitor","ma_month_account_config","dq_audit_exception","dq_audit_execution","dq_audit_report","dq_audit_rule_config","dq_audit_task_config","dq_task_importance_config","dq_alert_upgrade_rule","dq_audit_field_config"]:
            session.execute(text("TRUNCATE TABLE " + t))
        session.commit()
        print("Tables truncated")

        # ===== SYS_DEPARTMENT =====
        print("Seeding sys_department...")
        for i in range(len(DEPT_NAMES)):
            session.add(SysDepartment(dept_name=DEPT_NAMES[i], dept_code=DEPT_CODES[i], parent_id=None if i==0 else 1, dept_level=1 if i==0 else 2, sort_order=i+1, status=1, created_at=now))
        session.commit()

        # ===== SYS_ROLE =====
        print("Seeding sys_role...")
        for i in range(len(ROLE_NAMES)):
            session.add(SysRole(role_name=ROLE_NAMES[i], role_code=ROLE_CODES[i], status=1, created_by="admin", created_at=now))
        session.commit()

        # ===== SYS_USER =====
        print("Seeding sys_user...")
        for i in range(20):
            uname = "user_" + str(i+1).zfill(3)
            session.add(SysUser(username=uname, password="123456", real_name=r.choice(DEPT_NAMES)[0] + r.choice(ROLE_NAMES)[0:1], email=uname+"@co.com", phone="138"+str(i).zfill(8), department_id=(i%8)+1, position=POSITIONS[i%len(POSITIONS)], status=1, is_admin=(i==0), created_by="admin", created_at=now))
        session.commit()

        # ===== SYS_PERMISSION =====
        print("Seeding sys_permission...")
        for i,m in enumerate(["dashboard","audit","root-cause","monthly","assistant","settings"]):
            session.add(SysPermission(permission_name=m+"_view", permission_code=m+":view", menu_path="/"+m, permission_type="menu", sort_order=i, status=1, created_at=now))
        session.commit()

        # ===== SYS_USER_ROLE =====
        users = session.execute(select(SysUser)).scalars().all()
        roles = session.execute(select(SysRole)).scalars().all()
        for u in users:
            session.add(SysUserRole(user_id=u.id, role_id=roles[u.id % len(roles)].id, created_at=now))
        session.commit()
        # ===== SYS_CONFIG =====
        print("Seeding sys_config...")
        for kv in [["system.title",SYS_TITLE,"system"],["system.version","2.0.0","system"],["alert.threshold.critical","90","alert"],["alert.threshold.warning","95","alert"],["notification.email.enabled","true","notification"],["audit.default_sample_rate","100","business"],["audit.max_retry_count","3","business"],["monthly.auto_report","true","business"]]:
            session.add(SysConfig(config_key=kv[0], config_value=kv[1], config_type=kv[2], status=1, created_by="admin", created_at=now))
        session.commit()

        # ===== SYS_DATA_DICT =====
        print("Seeding sys_data_dict...")
        for dt in ["audit_type","task_status","severity_level","alert_type","priority"]:
            for j in range(5):
                session.add(SysDataDict(dict_key=dt+"_"+str(j), dict_value=dt+"_val_"+str(j), dict_type=dt, sort_order=j, status=1, created_at=now))
        session.commit()

        # ===== SYS_NOTIFICATION =====
        for i in range(15):
            session.add(SysNotificationRecord(notification_type=r.choice(["alert","reminder","system"]), title="通知_"+str(i+1), content="内容_"+str(i+1), receiver_id=(i%20)+1, receiver_name="user_"+str((i%20)+1).zfill(3), channel=r.choice(["system","email","sms"]), is_read=r.random()>0.4, status="sent", send_time=now, created_at=now))
        session.commit()

        # ===== SYS_AUDIT_LOG / INTERFACE_LOG / JOB_SCHEDULE =====
        for i in range(20):
            session.add(SysAuditLog(user_id=(i%20)+1, username="user_"+str((i%20)+1).zfill(3), action_type=r.choice(["create","update","delete","query","login"]), module=r.choice(["audit","monthly","system"]), action_detail="操作", request_url="/api/v1/test", request_method=r.choice(["GET","POST"]), response_code=200, ip_address="192.168.1."+str(i+1), duration_ms=r.randint(5,5000), status="success", created_at=now))
        session.commit()

        for i in range(15):
            session.add(SysInterfaceLog(interface_name="接口_"+str(i+1), request_url="/api/v1/"+str(i+1), request_method=r.choice(["GET","POST"]), response_code=200, duration_ms=r.randint(10,3000), status="success", created_at=now))
        session.commit()

        for i in range(8):
            session.add(SysJobSchedule(job_name="调度任务_"+str(i+1), job_code="JOB_"+str(i+1).zfill(4), job_type=r.choice(["audit","monthly","system"]), trigger_type=r.choice(["cron","interval"]), target_function="app.tasks.job_"+str(i+1), status=1, run_count=r.randint(10,200), description="任务_"+str(i+1), created_by="admin", created_at=now))
        session.commit()

        # ===== SYS_AI_CONFIG =====
        session.add(SysAiConfig(config_name="GPT-4默认", config_code="AI_DEFAULT", provider="openai", model_name="gpt-4", max_tokens=4096, temperature=0.7, context_limit=10, is_default=True, status=1, created_by="admin", created_at=now))
        session.add(SysAiConfig(config_name="分析专用", config_code="AI_ANALYSIS", provider="openai", model_name="gpt-4-turbo", max_tokens=8192, temperature=0.3, context_limit=20, is_default=False, status=1, created_by="admin", created_at=now))
        session.commit()

        # ===== AI_CHAT =====
        for i in range(10):
            session.add(AiChatSession(session_title="会话_"+str(i+1), session_type=r.choice(["general","analysis","audit","report"]), user_id=(i%20)+1, user_name="user_"+str((i%20)+1).zfill(3), message_count=r.randint(2,20), status="active", created_at=now))
        session.commit()
        sessions = session.execute(select(AiChatSession)).scalars().all()
        for s in sessions:
            for j in range(r.randint(2,6)):
                role = "user" if j%2==0 else "assistant"
                session.add(AiChatMessage(session_id=s.id, role=role, content="消息_"+str(s.id)+"_"+str(j), content_type="text", tokens_used=r.randint(50,500), created_at=now))
        session.commit()

        # ===== AUDIT TABLES =====
        print("Seeding dq_audit_field_config...")
        for i in range(len(FIELD_KEYS)):
            session.add(DqAuditFieldConfig(field_name=FIELD_KEYS[i], field_desc=FIELD_NAMES[i], field_type="varchar", status=1, created_by="admin", created_at=now))
        session.commit()

        print("Seeding dq_audit_rule_config...")
        rule_types = [["null_check","error"],["format","error"],["range","warning"],["duplicate","error"],["format","warning"],["custom","error"],["range","warning"],["format","info"],["range","warning"],["range","warning"],["duplicate","error"]]
        for i, rt in enumerate(rule_types):
            fk = FIELD_KEYS[i % len(FIELD_KEYS)]
            session.add(DqAuditRuleConfig(rule_name="规则_"+str(i+1), rule_code="R_"+str(i+1).zfill(3), rule_type=rt[0], rule_level=rt[1], rule_content={"field": fk}, field_name=fk, threshold=round(r.uniform(0.8,1.0),2), severity=r.choice(SEVERITIES), status=1, created_by="admin", created_at=now))
        session.commit()

        print("Seeding dq_task_importance_config...")
        for i, (lev, nm, clr) in enumerate([(1,"一般","green"),(2,"重要","blue"),(3,"紧急","orange"),(4,"严重","red"),(5,"灾难","darkred")]):
            session.add(DqTaskImportanceConfig(level=lev, level_name=nm, color=clr, score_range=str((lev-1)*20)+"-"+str(lev*20), description=nm+"任务", notify_channels=["system"], response_time_minutes=1440//lev, created_at=now))
        session.commit()

        print("Seeding dq_alert_upgrade_rule...")
        for i in range(6):
            session.add(DqAlertUpgradeRule(rule_name="告警升级规则_"+str(i+1), alert_type=r.choice(ALERT_TYPES), trigger_condition={"count":r.randint(3,10),"minutes":r.randint(30,480)}, upgrade_level=r.randint(1,3), max_upgrade_count=3, is_active=True, created_at=now))
        session.commit()

        print("Seeding dq_audit_task_config...")
        for i, tn in enumerate(TASK_NAMES):
            session.add(DqAuditTaskConfig(task_name=tn, task_type=r.choice(["field_audit","rule_audit","full_audit"]), schedule_type=r.choice(["manual","daily","weekly"]), execute_strategy=r.choice(["full","sample"]), sample_rate=100.0, status=1, importance=r.randint(1,5), created_by="admin", created_at=now))
        session.commit()

        print("Seeding dq_audit_execution...")
        tasks = session.execute(select(DqAuditTaskConfig)).scalars().all()
        for i in range(15):
            t = r.choice(tasks) if tasks else None
            total = r.randint(10000,100000)
            failed = r.randint(0, int(total*0.1))
            session.add(DqAuditExecution(task_id=t.id if t else None, task_name=t.task_name if t else ("执行_"+str(i+1)), execute_time=now, execute_duration=round(r.uniform(10,3600),2), total_records=total, passed_records=total-failed, failed_records=failed, pass_rate=round((total-failed)/total*100,2) if total>0 else 100, status=r.choice(["completed","completed","completed","failed"]), created_at=now))
        session.commit()

        print("Seeding dq_audit_exception...")
        execs = session.execute(select(DqAuditExecution)).scalars().all()
        for i in range(20):
            e = r.choice(execs) if execs else None
            session.add(DqAuditException(execution_id=e.id if e else None, rule_id=r.choice(tasks).id if tasks else None, exception_type=r.choice(EXC_TYPES), exception_count=r.randint(1,1000), exception_rate=round(r.uniform(0.01,5.0),4), severity=r.choice(SEVERITIES), status=r.choice(["open","handling","resolved","closed"]), handler="admin", created_at=now))
        session.commit()

        print("Seeding dq_audit_report...")
        for i in range(10):
            session.add(DqAuditReport(report_name="数据质量报告_"+str(i+1), report_type=r.choice(["daily","weekly","monthly"]), total_executions=r.randint(1,10), total_records=r.randint(100000,5000000), status=r.choice(["draft","published"]), created_by="admin", created_at=now))
        session.commit()
        # ===== MONTHLY TABLES =====
        print("Seeding ma_month_account_config...")
        for m in range(1,7):
            am = "2025-" + str(m).zfill(2)
            sd = date(2025,m,1)
            if m==12: ed = date(2025,12,31)
            elif m==2: ed = date(2025,2,28)
            else: ed = date(2025,m+1,1) - timedelta(days=1)
            session.add(MaMonthAccountConfig(account_month=am, account_name=am+"月账期", start_date=sd, end_date=ed, status=r.choice(["completed","completed","processing","pending"]), total_tasks=r.randint(80,150), completed_tasks=r.randint(60,140), quality_score=round(r.uniform(85.0,99.5),1), progress=round(r.uniform(60.0,100.0),1), owner="admin", created_by="admin", created_at=now))
        session.commit()

        print("Seeding ma_task_monitor...")
        for i in range(20):
            ps = datetime.now() - timedelta(days=r.randint(0,30))
            pe = ps + timedelta(hours=r.randint(1,48))
            session.add(MaTaskMonitor(account_month="2025-"+str(r.randint(1,6)).zfill(2), task_code="TASK_"+str(i+1).zfill(4), task_name="月度任务_"+str(i+1), priority=r.choice(["urgent","high","normal","low"]), status=r.choice(["pending","running","completed","completed","completed","failed"]), plan_start_time=ps, plan_end_time=pe, owner="admin", max_retries=3, is_critical=r.random()>0.7, expected_duration=int((pe-ps).total_seconds()), created_at=now))
        session.commit()

        print("Seeding ma_audit_result...")
        for i in range(10):
            total = r.randint(50,200)
            passed = r.randint(int(total*0.8), total)
            session.add(MaAuditResult(account_month="2025-"+str(r.randint(1,6)).zfill(2), audit_type=r.choice(["data_integrity","data_accuracy","data_timeliness"]), result="pass" if passed==total else "warning", total_checks=total, passed_checks=passed, failed_checks=total-passed, pass_rate=round(passed/total*100,2) if total>0 else 100, checked_by="admin", checked_at=now, created_at=now))
        session.commit()

        print("Seeding ma_adjustment_record...")
        for i in range(8):
            session.add(MaAdjustmentRecord(account_month="2025-"+str(r.randint(1,6)).zfill(2), adjustment_type=r.choice(["data_correction","amount_adjustment","other"]), reason="调账原因_"+str(i+1), operator="admin", status=r.choice(["pending","approved","rejected"]), created_at=now))
        session.commit()

        print("Seeding ma_daily_report...")
        for i in range(10):
            d = date(2025, r.randint(1,6), r.randint(1,28))
            comp = r.randint(10,30)
            total = comp + r.randint(0,5)
            session.add(MaDailyReport(report_date=d, account_month=d.strftime("%Y-%m"), title=str(d)+"日报", summary="完成任务"+str(comp)+"项", task_completed=comp, task_total=total, exception_count=r.randint(0,3), quality_score=round(r.uniform(85,100),1), progress=round(comp/total*100,1) if total>0 else 0, status=r.choice(["draft","published"]), created_by="admin", created_at=now))
        session.commit()

        print("Seeding ma_summary_report...")
        for m in range(1,7):
            session.add(MaSummaryReport(account_month="2025-"+str(m).zfill(2), title="2025年"+str(m)+"月报告", overview="本月工作平稳", status=r.choice(["draft","published"]), publisher="admin", created_by="admin", created_at=now))
        session.commit()

        print("Seeding ma_kpi_metrics...")
        kpis = [["KPI_EFF_001","任务完成率","efficiency",100.0],["KPI_QUAL_001","数据质量评分","quality",100.0],["KPI_PROG_001","月账进度","progress",100.0]]
        for code,name,cat,target in kpis:
            for m in range(1,7):
                session.add(MaKpiMetrics(account_month="2025-"+str(m).zfill(2), metric_code=code, metric_name=name, metric_category=cat, target_value=target, actual_value=round(r.uniform(85,100),1), unit="%", trend=r.choice(["up","down","stable"]), status=r.choice(["good","warning","bad"]), created_at=now))
        session.commit()
        print("Seeding ma_milestone_track...")
        for i,nm in enumerate(["数据采集完成","数据清洗完成","数据稽核完成","报表生成完成","质量报告发布","异常数据处理","月度总结完成","KPI评估完成"]):
            pd = date(2025, r.randint(1,6), r.randint(1,28))
            ad = pd + timedelta(days=r.randint(-1,2))
            session.add(MaMilestoneTrack(account_month="2025-"+str(r.randint(1,6)).zfill(2), milestone_name=nm, milestone_type="月度", plan_date=pd, actual_date=ad, status=r.choice(["completed","completed","delayed"]), delay_days=max(0,(ad-pd).days), completion_percentage=100.0, responsible_person="admin", created_at=now))
        session.commit()

        print("Seeding ma_alert_record...")
        for i in range(15):
            session.add(MaAlertRecord(account_month="2025-"+str(r.randint(1,6)).zfill(2), alert_title="告警_"+str(i+1), alert_type=r.choice(ALERT_TYPES), alert_level=r.choice(["critical","warning","info"]), content="告警内容_"+str(i+1), status=r.choice(["unread","read","handled"]), created_at=now))
        session.commit()

        print("Seeding ma_ml_model_config...")
        for nm,code,mtype,alg in [["月账进度预测","ML_FORECAST_001","forecast","ARIMA"],["数据异常检测","ML_ANOMALY_001","anomaly_detection","IsolationForest"],["任务分类","ML_CLASSIFY_001","classification","XGBoost"],["质量评分","ML_QUALITY_001","regression","LinearRegression"]]:
            session.add(MaMlModelConfig(model_name=nm, model_code=code, model_type=mtype, model_version="v1.0", algorithm=alg, status=r.choice(["active","inactive"]), created_by="admin", created_at=now))
        session.commit()

        # ===== ROOT CAUSE TABLES =====
        print("Seeding ops_root_cause_type...")
        for code,name,pid,lev in [["RC_SYSTEM","系统故障",None,1],["RC_NETWORK","网络故障",1,2],["RC_HARDWARE","硬件故障",1,3],["RC_DATA","数据问题",None,1],["RC_DATA_LOSS","数据丢失",4,2],["RC_DATA_INCONSIST","数据不一致",4,3],["RC_BUSINESS","业务问题",None,1],["RC_PROCESS","流程问题",7,2]]:
            session.add(OpsRootCauseType(type_code=code, type_name=name, parent_id=pid, level=lev, status=1, created_at=now))
        session.commit()

        print("Seeding ops_task_lineage...")
        ldata = [["ETL_001","etl","DS_CRM"],["ETL_002","etl","DS_BILL"],["ETL_003","etl","DS_ORDER"],["DQC_001","dqc","DS_DW"],["DQC_002","dqc","DS_DW"],["RPT_001","report","DS_DW"],["RPT_002","report","DS_DW"],["API_001","api","DS_CRM"],["API_002","api","DS_BILL"],["ETL_004","etl","DS_BOSS"]]
        for code,tp,ds in ldata:
            session.add(OpsTaskLineage(task_code=code, task_name=code+"_任务", task_type=tp, datasource_input=ds, datasource_output="DS_DW", owner="admin", department=DEPT_NAMES[r.randint(0,len(DEPT_NAMES)-1)], status=1, created_at=now))
        session.commit()

        print("Seeding ops_analysis_path...")
        for nm,tp in [["数据延迟分析","data_delay"],["数据质量分析","data_quality"],["系统故障分析","system"],["业务异常分析","business"],["计费异常分析","data_delay"]]:
            session.add(OpsAnalysisPath(path_name=nm, path_type=tp, steps=[{"order":1,"name":"步骤1","method":"check"}], expected_duration=r.randint(15,120), success_rate=round(r.uniform(0.6,0.95),2), usage_count=r.randint(10,500), status=1, created_by="admin", created_at=now))
        session.commit()
        print("Seeding ops_problem_case...")
        cases = [["账单数据延迟案例","data_delay","数据延迟","数据量突增"],["客户信息缺失案例","data_quality","手机号缺失","接口超时"],["计费不一致案例","data_quality","数据相差0.3%","事务失败"],["报表生成失败案例","data_delay","超时","依赖失败"],["订单状态异常案例","business","状态异常","回调超时"],["IDC数据丢失案例","system_fault","硬盘故障","RAID故障"],["数据同步延迟案例","data_delay","延迟4小时","带宽不足"],["套餐变更不一致案例","business","计费未切换","数据未同步"]]
        for title,ctype,desc,root in cases:
            session.add(OpsProblemCase(case_title=title, case_type=ctype, description=desc, root_cause=root, solution="已解决", status="closed", severity=r.choice(["high","medium"]), handler="admin", handler_department=DEPT_NAMES[r.randint(0,len(DEPT_NAMES)-1)], occurrence_time=now, created_by="admin", created_at=now))
        session.commit()

        print("Seeding ops_root_cause_analysis...")
        pcases = session.execute(select(OpsProblemCase)).scalars().all()
        paths = session.execute(select(OpsAnalysisPath)).scalars().all()
        rctypes = session.execute(select(OpsRootCauseType)).scalars().all()
        for i in range(10):
            c = r.choice(pcases) if pcases else None
            p = r.choice(paths) if paths else None
            rc = r.choice(rctypes) if rctypes else None
            session.add(OpsRootCauseAnalysis(case_id=c.id if c else None, path_id=p.id if p else None, analysis_title="分析_"+str(i+1), problem_description="问题描述_"+str(i+1), analysis_process=[], conclusion="分析完成", root_cause_type_id=rc.id if rc else None, root_cause_desc="根因描述", confidence=round(r.uniform(0.7,0.99),2), status=r.choice(["analyzing","completed"]), ai_assisted=r.random()>0.5, created_by="admin", created_at=now))
        session.commit()

        print("Seeding ops_analysis_trace_log...")
        analyses = session.execute(select(OpsRootCauseAnalysis)).scalars().all()
        for a in analyses:
            for step in range(3):
                session.add(OpsAnalysisTraceLog(analysis_id=a.id, step_name="步骤_"+str(step+1), step_order=step+1, action="执行", status="completed", duration=r.randint(100,5000), created_at=now))
        session.commit()

        print("Seeding ops_case_usage_stats...")
        for c in pcases[:10]:
            session.add(OpsCaseUsageStats(case_id=c.id, usage_date=now.date(), usage_count=r.randint(1,50), match_count=r.randint(0,30), adopt_count=r.randint(0,20), created_at=now))
        session.commit()

        print("Seeding ops_user_feedback...")
        for i in range(12):
            a = r.choice(analyses) if analyses else None
            c = r.choice(pcases) if pcases else None
            session.add(OpsUserFeedback(analysis_id=a.id if a else None, case_id=c.id if c else None, feedback_type=r.choice(["helpful","useful","accurate"]), rating=r.randint(1,5), content="反馈内容", user_name="admin", is_resolved=r.random()>0.3, created_at=now))
        session.commit()

        # Run ledger seed for config tables
        print("Seeding ledger config tables...")
        print("Ledger config tables already seeded")

        session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        print("All tables seeded successfully!")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_all()