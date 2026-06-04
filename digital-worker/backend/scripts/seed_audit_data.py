"""
数据质量稽核模块 - 种子数据脚本
为所有 dq_* 表插入测试数据，供前端读取展示
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.audit import (
    DqAuditFieldConfig, DqAuditRuleConfig, DqAuditTaskConfig,
    DqTaskImportanceConfig, DqAlertUpgradeRule, DqAuditExecution,
    DqAuditException, DqAuditReport,
)

engine = create_engine(settings.DATABASE_URL_SYNC, echo=False)
Session = sessionmaker(bind=engine)
session = Session()


def clean():
    """清空所有 dq_ 表"""
    for table in ['dq_audit_exception', 'dq_audit_execution', 'dq_audit_report',
                   'dq_alert_upgrade_rule', 'dq_audit_rule_config',
                   'dq_audit_task_config', 'dq_task_importance_config',
                   'dq_audit_field_config']:
        session.execute(text(f"DELETE FROM {table}"))
        session.execute(text(f"ALTER TABLE {table} AUTO_INCREMENT = 1"))
    session.commit()
    print("已清空所有 dq_ 表")

def seed():
    now = datetime.now()

    # ========== 1. dq_audit_field_config ==========
    fields_data = [
        ("bill_id", "账单ID", "DS_BILL", "计费系统", "billing", "t_bill_detail", "VARCHAR", 32, False, "BILL202605010001"),
        ("user_id", "用户ID", "DS_BILL", "计费系统", "billing", "t_bill_detail", "VARCHAR", 32, False, "U100001"),
        ("amount", "账单金额", "DS_BILL", "计费系统", "billing", "t_bill_detail", "DECIMAL", 18, False, "158.50"),
        ("bill_month", "账单月份", "DS_BILL", "计费系统", "billing", "t_bill_detail", "VARCHAR", 6, False, "202605"),
        ("status_cd", "账单状态", "DS_BILL", "计费系统", "billing", "t_bill_detail", "VARCHAR", 2, False, "00"),
        ("charge_type", "计费类型", "DS_BILL", "计费系统", "billing", "t_charge_record", "VARCHAR", 10, False, "语音"),
        ("call_duration", "通话时长(秒)", "DS_BILL", "计费系统", "billing", "t_charge_record", "INT", 10, True, "3600"),
        ("data_usage", "流量使用(MB)", "DS_BILL", "计费系统", "billing", "t_charge_record", "DECIMAL", 12, True, "2048.50"),
        ("pay_amount", "缴费金额", "DS_BILL", "计费系统", "billing", "t_payment_trans", "DECIMAL", 18, False, "200.00"),
        ("pay_time", "缴费时间", "DS_BILL", "计费系统", "billing", "t_payment_trans", "DATETIME", None, False, "2026-05-15 10:30:00"),
        ("cust_name", "客户姓名", "DS_CRM", "客户关系系统", "customer", "t_customer_info", "VARCHAR", 100, False, "张三"),
        ("id_card", "身份证号", "DS_CRM", "客户关系系统", "customer", "t_customer_info", "VARCHAR", 18, False, "110101199001011234"),
        ("phone", "手机号", "DS_CRM", "客户关系系统", "customer", "t_customer_info", "VARCHAR", 11, False, "13800138000"),
        ("email", "电子邮箱", "DS_CRM", "客户关系系统", "customer", "t_customer_info", "VARCHAR", 100, True, "zhangsan@example.com"),
        ("address", "联系地址", "DS_CRM", "客户关系系统", "customer", "t_customer_info", "VARCHAR", 200, True, "北京市朝阳区建国路88号"),
        ("order_amount", "订单金额", "DS_CRM", "客户关系系统", "customer", "t_user_order", "DECIMAL", 18, False, "299.00"),
        ("order_status", "订单状态", "DS_CRM", "客户关系系统", "customer", "t_user_order", "VARCHAR", 10, False, "已完成"),
        ("product_code", "产品编码", "DS_BOSS", "业务运营支撑系统", "product", "t_product_def", "VARCHAR", 20, False, "PKG_VOICE_2026"),
        ("product_price", "产品价格", "DS_BOSS", "业务运营支撑系统", "product", "t_product_def", "DECIMAL", 18, False, "99.00"),
        ("create_time", "创建时间", "DS_BOSS", "业务运营支撑系统", "product", "t_product_def", "DATETIME", None, False, "2026-01-01 00:00:00"),
    ]

    field_objs = []
    for fd in fields_data:
        f = DqAuditFieldConfig(
            field_name=fd[0], field_desc=fd[1],
            datasource_id=fd[2], datasource_name=fd[3],
            schema_name=fd[4], table_name=fd[5],
            field_type=fd[6], field_length=fd[7],
            is_nullable=fd[8], sample_data=fd[9],
            status=1, created_by="admin",
            created_at=now, updated_at=now,
        )
        session.add(f)
        field_objs.append(f)
    session.flush()
    print(f"已插入 {len(field_objs)} 条字段配置")
    # ========== 2. dq_audit_rule_config ==========
    rules_data = [
        ("非空检查-账单ID", "DQ_NULL_BILL_ID", "null_check", "error",
         {"check_empty": True}, 1, "bill_id"),
        ("非空检查-客户姓名", "DQ_NULL_CUST_NAME", "null_check", "error",
         {"check_empty": True}, 11, "cust_name"),
        ("非空检查-手机号", "DQ_NULL_PHONE", "null_check", "error",
         {"check_empty": True}, 12, "phone"),
        ("非空检查-身份证号", "DQ_NULL_ID_CARD", "null_check", "error",
         {"check_empty": True}, 11, "id_card"),
        ("金额范围检查", "DQ_RANGE_AMOUNT", "range", "error",
         {"min_value": 0, "max_value": 999999.99}, 2, "amount"),
        ("订单金额范围检查", "DQ_RANGE_ORDER", "range", "warning",
         {"min_value": 0, "max_value": 99999.99}, 15, "order_amount"),
        ("手机号格式校验", "DQ_FORMAT_PHONE", "format", "error",
         {"regex": "^1[3-9]\d{9}$", "description": "11位手机号"}, 12, "phone"),
        ("身份证号格式校验", "DQ_FORMAT_IDCARD", "format", "error",
         {"regex": "^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$", "description": "18位身份证号"}, 11, "id_card"),
        ("邮箱格式校验", "DQ_FORMAT_EMAIL", "format", "warning",
         {"regex": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}, 13, "email"),
        ("重复检查-账单ID", "DQ_DUPLICATE_BILL", "duplicate", "error",
         {"check_duplicate": True, "key_fields": ["bill_id"]}, 0, "bill_id"),
        ("重复检查-身份证号", "DQ_DUPLICATE_IDCARD", "duplicate", "warning",
         {"check_duplicate": True, "key_fields": ["id_card"]}, 11, "id_card"),
        ("账单状态有效性", "DQ_CUSTOM_STATUS", "custom", "info",
         {"valid_values": ["00", "01", "02", "03", "99"]}, 4, "status_cd"),
        ("缴费金额非负检查", "DQ_RANGE_PAY", "range", "error",
         {"min_value": 0}, 8, "pay_amount"),
        ("通话时长合理性", "DQ_RANGE_DURATION", "range", "info",
         {"min_value": 0, "max_value": 86400}, 6, "call_duration"),
        ("订单状态枚举检查", "DQ_CUSTOM_ORDER_STATUS", "custom", "warning",
         {"valid_values": ["待支付", "已支付", "已完成", "已取消", "已退款"]}, 16, "order_status"),
    ]

    rule_objs = []
    for i, rd in enumerate(rules_data):
        fid = rd[5]
        tbl = ""
        for f in field_objs:
            if f.id == fid + 1:
                tbl = f.table_name
                break
        r = DqAuditRuleConfig(
            rule_name=rd[0], rule_code=rd[1], rule_type=rd[2],
            rule_level=rd[3], rule_content=rd[4],
            field_id=fid + 1, field_name=rd[5], table_name=tbl,
            threshold=95.0,
            severity="high" if rd[3]=="error" else "medium",
            status=1, ai_generated=False, confirm_status="confirmed",
            created_by="admin", created_at=now, updated_at=now,
        )
        session.add(r)
        rule_objs.append(r)
    session.flush()
    print(f"已插入 {len(rule_objs)} 条规则配置")
    # ========== 3. dq_audit_task_config ==========
    tasks_data = [
        ("月度数据质量审计-计费", "full_audit", "monthly",
         {"day": 1, "hour": 2, "minute": 0}, "full", 100.0, 5),
        ("客户信息完整性审计", "field_audit", "weekly",
         {"day_of_week": 1, "hour": 3}, "sample", 20.0, 4),
        ("每日账单流水审计", "rule_audit", "daily",
         {"hour": 1, "minute": 30}, "full", 100.0, 3),
        ("订单数据准确性审计", "rule_audit", "daily",
         {"hour": 2, "minute": 0}, "sample", 30.0, 4),
        ("产品信息完整性检查", "field_audit", "weekly",
         {"day_of_week": 5, "hour": 4}, "full", 100.0, 2),
        ("身份证号合规专项审计", "full_audit", "monthly",
         {"day": 15, "hour": 3}, "full", 100.0, 5),
        ("实时流水异常监控", "rule_audit", "manual",
         {}, "full", 100.0, 5),
        ("周度数据质量巡检", "full_audit", "weekly",
         {"day_of_week": 3, "hour": 2}, "sample", 15.0, 2),
    ]

    task_objs = []
    for td in tasks_data:
        t = DqAuditTaskConfig(
            task_name=td[0], task_type=td[1],
            rule_ids=[r.id for r in rule_objs[:8]],
            field_ids=[f.id for f in field_objs],
            schedule_type=td[2], schedule_config=td[3],
            execute_strategy=td[4], sample_rate=td[5],
            status=1, importance=td[6],
            created_by="admin", created_at=now, updated_at=now,
        )
        session.add(t)
        task_objs.append(t)
    session.flush()
    print(f"已插入 {len(task_objs)} 条任务配置")

    # ========== 4. dq_task_importance_config ==========
    importance_data = [
        (1, "一般", "#909399", "[0,60)", "低优先级任务", ["系统内"], 1440),
        (2, "重要", "#E6A23C", "[60,80)", "中等优先级", ["系统内", "邮件"], 480),
        (3, "高", "#F56C6C", "[80,90)", "高优先级", ["邮件", "企业微信"], 120),
        (4, "严重", "#F56C6C", "[90,95)", "严重级别", ["邮件", "企业微信", "短信"], 60),
        (5, "灾难", "#C03639", "[95,100]", "灾难级别", ["邮件", "短信", "电话"], 15),
    ]
    for ic in importance_data:
        obj = DqTaskImportanceConfig(
            level=ic[0], level_name=ic[1], color=ic[2],
            score_range=ic[3], description=ic[4],
            notify_channels=ic[5], response_time_minutes=ic[6],
            created_at=now, updated_at=now,
        )
        session.add(obj)
    print("已插入 5 条重要性配置")

    # ========== 5. dq_alert_upgrade_rule ==========
    upgrade_data = [
        ("连续3次失败升级", "execution_failure", {"consecutive_failures": 3}, 3,
         ["ops_leader@company.com"], "【严重告警】任务 {task_name} 已连续3次执行失败", 3, True),
        ("异常率超50%升级", "exception_rate", {"threshold": 50.0}, 4,
         ["ops_leader@company.com", "13800138000"], "异常率已达{exception_rate}%", 3, True),
        ("1小时内重复告警升级", "repeat_alert", {"within_hours": 1, "count": 5}, 2,
         ["ops_team@company.com"], "1小时内已触发5次告警", 5, True),
        ("24小时未处理升级", "handle_timeout", {"timeout_hours": 24}, 3,
         ["ops_leader@company.com", "duty_phone"], "告警已超24小时未处理", 3, True),
        ("关键字段异常升级", "critical_field", {"field_names": ["id_card", "phone", "amount"]}, 5,
         ["cto@company.com", "vp_ops@company.com"], "关键字段发生数据异常", 2, False),
    ]
    for ud in upgrade_data:
        obj = DqAlertUpgradeRule(
            rule_name=ud[0], alert_type=ud[1], trigger_condition=ud[2],
            upgrade_level=ud[3], notify_targets=ud[4],
            notify_template=ud[5], max_upgrade_count=ud[6],
            is_active=ud[7], created_at=now, updated_at=now,
        )
        session.add(obj)
    print("已插入 5 条告警升级规则")
    session.commit()

    # ========== 6. dq_audit_execution ==========
    statuses = ["completed", "completed", "completed", "completed", "failed"]
    execution_objs = []
    for i in range(25):
        days_ago = 30 - i
        exec_time = now - timedelta(days=days_ago)
        task = task_objs[i % len(task_objs)]
        total = 50000 + (i * 1000)
        failed = int(total * (5 + (i % 15)) / 100)
        passed = total - failed
        rate = round(passed / total * 100, 2)
        status = statuses[i % len(statuses)]
        e = DqAuditExecution(
            task_id=task.id,
            task_name=task.task_name,
            execute_time=exec_time,
            execute_duration=round(30 + i * 2.5, 1),
            total_records=total,
            sample_records=total,
            passed_records=passed,
            failed_records=failed,
            pass_rate=rate,
            status=status,
            result_summary={
                "checked_rules": 8,
                "passed_rules": 7 if failed < 5000 else 5,
                "failed_rules": 1 if failed < 5000 else 3,
            },
            created_at=exec_time,
        )
        session.add(e)
        execution_objs.append(e)
    session.flush()
    print(f"已插入 {len(execution_objs)} 条执行记录")

    # ========== 7. dq_audit_exception ==========
    exc_types = ["空值异常", "数据重复", "格式错误", "范围越界", "枚举值非法"]
    sevs = ["high", "medium", "low"]
    alerts = ["critical", "major", "minor", "warning"]
    exc_statuses = ["open", "open", "open", "handling", "resolved", "closed"]
    for i in range(40):
        ex = execution_objs[i % len(execution_objs)]
        rule = rule_objs[i % len(rule_objs)]
        etype = exc_types[i % len(exc_types)]
        ecount = max(1, int(ex.failed_records * (0.5 + (i % 5) * 0.1) / 3))
        erate = round(ecount / ex.total_records * 100, 2) if ex.total_records > 0 else 0
        obj = DqAuditException(
            execution_id=ex.id,
            rule_id=rule.id,
            rule_name=rule.rule_name,
            field_name=rule.field_name,
            table_name=ex.task_name,
            exception_type=etype,
            exception_value=f"发现{ecount}条异常记录",
            exception_count=ecount,
            exception_rate=erate,
            severity=sevs[i % len(sevs)],
            status=exc_statuses[i % len(exc_statuses)],
            alert_level=alerts[i % len(alerts)],
            is_upgraded=(erate > 10),
            created_at=ex.execute_time,
        )
        session.add(obj)
    session.flush()
    print("已插入 40 条异常记录")
    # ========== 8. dq_audit_report ==========
    reports_data = [
        ("2026年5月数据质量月报", "monthly", [e.id for e in execution_objs[:20]],
         20, sum(e.total_records for e in execution_objs[:20]),
         sum(e.failed_records for e in execution_objs[:20]),
         round(sum(e.pass_rate for e in execution_objs[:20])/20, 2),
         "本月共执行20次审计任务，整体通过率良好。身份证号格式异常较突出。",
         "计费系统数据质量稳定，客户信息完整性需重点关注。",
         ["加强身份证号录入前端校验", "定期扫描客户信息完整性", "建立异常自动修复机制"],
         "published", "admin"),
        ("5月第4周数据质量周报", "weekly", [e.id for e in execution_objs[16:24]],
         8, sum(e.total_records for e in execution_objs[16:24]),
         sum(e.failed_records for e in execution_objs[16:24]),
         round(sum(e.pass_rate for e in execution_objs[16:24])/8, 2),
         "本周数据质量良好，实时流水监控发现少量异常已处理。",
         "系统运行稳定，数据质量可控。",
         ["持续关注实时流水异常监控", "优化采样率提高检测效率"],
         "published", "admin"),
        ("5月30日数据质量日报", "daily", [execution_objs[-1].id],
         1, execution_objs[-1].total_records,
         execution_objs[-1].failed_records,
         execution_objs[-1].pass_rate,
         "今日审计完成，通过率正常。",
         "无异常",
         [],
         "published", "admin"),
        ("客户信息专项审计报告", "custom", [e.id for e in execution_objs[5:15]],
         10, sum(e.total_records for e in execution_objs[5:15]),
         sum(e.failed_records for e in execution_objs[5:15]),
         round(sum(e.pass_rate for e in execution_objs[5:15])/10, 2),
         "客户信息专项审计发现身份证号和手机号存在少量格式异常。",
         "客户信息整体质量良好，建议持续关注身份证号合规性。",
         ["推进存量身份证号清洗", "优化CRM录入校验", "建立客户信息质量看板"],
         "published", "admin"),
        ("计费数据月度质量分析", "monthly", [e.id for e in execution_objs],
         25, sum(e.total_records for e in execution_objs),
         sum(e.failed_records for e in execution_objs),
         round(sum(e.pass_rate for e in execution_objs)/25, 2),
         "计费数据质量整体良好，5月通过率维持在98%以上。",
         "计费系统数据质量可靠，建议加强异常根因分析。",
         ["建立质量趋势分析机制", "优化异常告警阈值", "开展季度应急演练"],
         "draft", "admin"),
    ]
    for rd in reports_data:
        obj = DqAuditReport(
            report_name=rd[0], report_type=rd[1],
            execution_ids=rd[2], total_executions=rd[3],
            total_records=rd[4], total_exceptions=rd[5],
            overall_pass_rate=rd[6], summary=rd[7],
            conclusion=rd[8], recommendations=rd[9],
            report_data={
                "generated_at": now.isoformat(),
                "period": rd[1],
                "execution_count": rd[3],
                "pass_rate": rd[6],
                "exception_count": rd[5],
            },
            status=rd[10], created_by=rd[11],
            created_at=now, updated_at=now,
        )
        session.add(obj)
    session.commit()
    print()
    print("===== 种子数据全部插入完成 =====")
    print("字段配置: 20条")
    print("规则配置: 15条")
    print("任务配置: 8条")
    print("重要性配置: 5条")
    print("告警升级规则: 5条")
    print("执行记录: 25条")
    print("异常记录: 40条")
    print("审计报告: 5条")


if __name__ == "__main__":
    try:
        clean()
        seed()
    except Exception as e:
        session.rollback()
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
