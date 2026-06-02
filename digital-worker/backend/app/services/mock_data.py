"""Mock data service for all 36 tables - provides realistic Chinese telecom/billing domain data"""
import random
import math
from datetime import datetime, timedelta, date
from typing import Any, Optional


class MockDataService:
    """Generates rich mock data for all modules."""

    CHINESE_SURNAMES = [
        "王", "李", "张", "刘", "陈", "杨", "黄", "赵", "周", "吴",
        "徐", "孙", "马", "朱", "胡", "郭", "何", "高", "林", "罗",
        "郑", "梁", "谢", "宋", "唐", "韩", "曹", "许", "邓", "萧",
    ]
    CHINESE_GIVEN_NAMES = [
        "伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "洋",
        "勇", "艳", "杰", "娟", "军", "超", "明", "华", "婷", "刚",
        "平", "辉", "玲", "桂英", "涛", "慧", "霞", "鑫", "浩", "雪",
    ]

    DEPARTMENTS = [
        {"id": 1, "name": "数据管理部", "code": "DEPT_DATA"},
        {"id": 2, "name": "技术研发部", "code": "DEPT_TECH"},
        {"id": 3, "name": "业务运营部", "code": "DEPT_BIZ"},
        {"id": 4, "name": "质量监控部", "code": "DEPT_QA"},
        {"id": 5, "name": "财务结算部", "code": "DEPT_FIN"},
        {"id": 6, "name": "数据产品部", "code": "DEPT_DP"},
        {"id": 7, "name": "运维保障部", "code": "DEPT_OPS"},
        {"id": 8, "name": "综合管理部", "code": "DEPT_ADMIN"},
    ]

    DATASOURCES = [
        {"id": "DS_BILL", "name": "计费系统"},
        {"id": "DS_CRM", "name": "客户关系系统"},
        {"id": "DS_OSS", "name": "运维支撑系统"},
        {"id": "DS_BOSS", "name": "业务运营支撑系统"},
        {"id": "DS_DW", "name": "数据仓库"},
        {"id": "DS_ORDER", "name": "订单中心"},
        {"id": "DS_INVENTORY", "name": "库存管理系统"},
    ]

    SCHEMAS = ["billing", "customer", "product", "order", "inventory", "log"]

    TABLES = [
        {"schema": "billing", "name": "t_bill_detail", "desc": "账单明细表"},
        {"schema": "billing", "name": "t_charge_record", "desc": "计费记录表"},
        {"schema": "billing", "name": "t_payment_trans", "desc": "缴费交易表"},
        {"schema": "billing", "name": "t_account_balance", "desc": "账户余额表"},
        {"schema": "customer", "name": "t_customer_info", "desc": "客户信息表"},
        {"schema": "customer", "name": "t_user_order", "desc": "用户订单表"},
        {"schema": "customer", "name": "t_user_basic", "desc": "用户基本信息表"},
        {"schema": "product", "name": "t_product_def", "desc": "产品定义表"},
        {"schema": "product", "name": "t_package_def", "desc": "套餐定义表"},
        {"schema": "order", "name": "t_order_main", "desc": "订单主表"},
        {"schema": "order", "name": "t_order_item", "desc": "订单明细表"},
        {"schema": "log", "name": "t_operation_log", "desc": "操作日志表"},
        {"schema": "log", "name": "t_error_log", "desc": "错误日志表"},
    ]

    FIELDS_DATA = [
        {"field": "user_id", "type": "bigint", "desc": "用户ID"},
        {"field": "user_name", "type": "varchar(100)", "desc": "用户名"},
        {"field": "phone_no", "type": "varchar(20)", "desc": "手机号"},
        {"field": "id_card", "type": "varchar(20)", "desc": "身份证号"},
        {"field": "email_addr", "type": "varchar(200)", "desc": "邮箱地址"},
        {"field": "real_name", "type": "varchar(100)", "desc": "真实姓名"},
        {"field": "gender", "type": "tinyint", "desc": "性别"},
        {"field": "birth_date", "type": "date", "desc": "出生日期"},
        {"field": "address", "type": "varchar(500)", "desc": "地址"},
        {"field": "product_id", "type": "bigint", "desc": "产品ID"},
        {"field": "product_name", "type": "varchar(200)", "desc": "产品名称"},
        {"field": "package_id", "type": "bigint", "desc": "套餐ID"},
        {"field": "order_id", "type": "bigint", "desc": "订单ID"},
        {"field": "order_amount", "type": "decimal(18,2)", "desc": "订单金额"},
        {"field": "bill_month", "type": "varchar(7)", "desc": "账期"},
        {"field": "bill_amount", "type": "decimal(18,2)", "desc": "账单金额"},
        {"field": "charge_amount", "type": "decimal(18,2)", "desc": "计费金额"},
        {"field": "payment_status", "type": "tinyint", "desc": "支付状态"},
        {"field": "create_time", "type": "datetime", "desc": "创建时间"},
        {"field": "update_time", "type": "datetime", "desc": "更新时间"},
        {"field": "status", "type": "tinyint", "desc": "状态"},
        {"field": "remark", "type": "varchar(500)", "desc": "备注"},
    ]

    RULE_TYPES = [
        {"code": "null_check", "name": "空值检测"},
        {"code": "duplicate", "name": "重复检测"},
        {"code": "range", "name": "范围检测"},
        {"code": "format", "name": "格式检测"},
        {"code": "custom", "name": "自定义检测"},
    ]

    RULE_LEVELS = ["error", "warning", "info"]
    SEVERITIES = ["high", "medium", "low"]

    @staticmethod
    def random_name():
        return random.choice(MockDataService.CHINESE_SURNAMES) + random.choice(MockDataService.CHINESE_GIVEN_NAMES)

    @staticmethod
    def random_phone():
        prefixes = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139",
                     "150", "151", "152", "153", "155", "156", "157", "158", "159",
                     "180", "181", "182", "183", "184", "185", "186", "187", "188", "189"]
        return random.choice(prefixes) + "".join([str(random.randint(0, 9)) for _ in range(8)])

    @staticmethod
    def random_date(start_year=2024, end_year=2025):
        start = date(start_year, 1, 1)
        end = date(end_year, 12, 31)
        delta = (end - start).days
        return start + timedelta(days=random.randint(0, delta))

    @staticmethod
    def random_datetime(start_year=2024, end_year=2025):
        d = MockDataService.random_date(start_year, end_year)
        t = datetime.min.time().replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )
        return datetime.combine(d, t)

    @staticmethod
    def paginate(items, page, page_size):
        total = len(items)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "items": items[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }


    # ==================== Audit Module Methods ====================

    def get_audit_fields(self, page=1, page_size=20, **filters):
        fields = []
        for i, tbl in enumerate(self.TABLES):
            for j, fld in enumerate(self.FIELDS_DATA[:random.randint(5, 12)]):
                fields.append({
                    "id": i * 20 + j + 1,
                    "field_name": fld["field"],
                    "field_desc": fld["desc"],
                    "datasource_id": random.choice(self.DATASOURCES)["id"],
                    "datasource_name": random.choice(self.DATASOURCES)["name"],
                    "schema_name": tbl["schema"],
                    "table_name": tbl["name"],
                    "field_type": fld["type"],
                    "field_length": 20 if "varchar" in fld["type"] else None,
                    "is_nullable": random.random() > 0.3,
                    "default_value": None if random.random() > 0.3 else "0",
                    "sample_data": "13800138000" if "phone" in fld["field"] else "测试数据",
                    "status": 1,
                    "remark": fld["desc"],
                    "created_by": self.random_name(),
                    "created_at": self.random_datetime(2024, 2025).isoformat(),
                    "updated_at": self.random_datetime(2024, 2025).isoformat(),
                })
        return self.paginate(fields, page, page_size)

    def get_audit_rules(self, page=1, page_size=20, **filters):
        rule_defs = [
            {"name": "用户ID非空校验", "code": "R_NULL_USER_ID", "type": "null_check", "content": {"field": "user_id", "action": "reject"}},
            {"name": "手机号格式校验", "code": "R_FORMAT_PHONE", "type": "format", "content": {"field": "phone_no", "pattern": "^1[3-9]\\\\d{9}$"}},
            {"name": "身份证号格式校验", "code": "R_FORMAT_IDCARD", "type": "format", "content": {"field": "id_card", "pattern": "^\\\\d{17}[0-9X]$"}},
            {"name": "订单金额范围校验", "code": "R_RANGE_AMOUNT", "type": "range", "content": {"field": "order_amount", "min": 0, "max": 999999}},
            {"name": "邮箱格式校验", "code": "R_FORMAT_EMAIL", "type": "format", "content": {"field": "email_addr", "pattern": "^\\S+@\\S+\\.\\S+$"}},
            {"name": "用户手机号唯一性校验", "code": "R_DUP_PHONE", "type": "duplicate", "content": {"field": "phone_no", "scope": "global"}},
            {"name": "账单金额准确性校验", "code": "R_ACC_BILL", "type": "custom", "content": {"field": "bill_amount", "formula": "sum(charge_amount) = bill_amount"}},
            {"name": "账户余额下限校验", "code": "R_RANGE_BALANCE", "type": "range", "content": {"field": "balance", "min": 0}},
            {"name": "订单状态枚举校验", "code": "R_FORMAT_STATUS", "type": "format", "content": {"field": "status", "enum": [0, 1, 2, 3, 4]}},
            {"name": "用户年龄范围校验", "code": "R_RANGE_AGE", "type": "range", "content": {"field": "birth_date", "min_age": 0, "max_age": 120}},
            {"name": "充值金额范围校验", "code": "R_RANGE_CHARGE", "type": "range", "content": {"field": "charge_amount", "min": 0.01, "max": 99999}},
            {"name": "重复订单检测", "code": "R_DUP_ORDER", "type": "duplicate", "content": {"field": "order_id", "scope": "latest_month"}},
            {"name": "手机号归属地校验", "code": "R_FORMAT_HOME", "type": "format", "content": {"field": "phone_no", "rule": "segment_based"}},
            {"name": "出生日期非未来校验", "code": "R_RANGE_BIRTH", "type": "range", "content": {"field": "birth_date", "max": "today"}},
            {"name": "数据完整性校验", "code": "R_COMPLETE", "type": "custom", "content": {"fields": ["user_id", "phone_no", "real_name"], "threshold": 0.95}},
        ]
        rules = []
        for i, rd in enumerate(rule_defs):
            tbl = random.choice(self.TABLES)
            fld = random.choice(self.FIELDS_DATA)
            rules.append({
                "id": i + 1,
                "rule_name": rd["name"],
                "rule_code": rd["code"],
                "rule_type": rd["type"],
                "rule_level": random.choice(self.RULE_LEVELS),
                "rule_content": rd["content"],
                "field_id": i + 1,
                "field_name": fld["field"],
                "table_name": tbl["name"],
                "threshold": round(random.uniform(0.8, 1.0), 2),
                "severity": random.choice(self.SEVERITIES),
                "status": random.choice([0, 1, 1, 1]),
                "ai_generated": random.random() > 0.7,
                "generate_task_id": f"gen_{random.randint(10000, 99999)}" if random.random() > 0.7 else None,
                "confirm_status": random.choice(["pending", "confirmed", "confirmed", "rejected"]),
                "created_by": self.random_name(),
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(rules, page, page_size)

    def get_datasources(self):
        return [{"id": ds["id"], "name": ds["name"], "type": "mysql", "status": random.choice(["online", "online", "offline"])} for ds in self.DATASOURCES]

    def get_schemas(self, datasource_id=None):
        return [{"id": i + 1, "name": s, "datasource_id": random.choice(self.DATASOURCES)["id"]} for i, s in enumerate(self.SCHEMAS)]

    def get_tables(self, schema_name=None):
        result = []
        for i, t in enumerate(self.TABLES):
            if schema_name and t["schema"] != schema_name:
                continue
            result.append({"id": i + 1, "name": t["name"], "schema_name": t["schema"], "desc": t["desc"],
                           "row_count": random.randint(100000, 50000000), "storage_size": f"{random.randint(1, 100)}GB"})
        return result

    def get_fields_by_table(self, table_name=None):
        result = []
        for i, f in enumerate(self.FIELDS_DATA):
            tbl = random.choice(self.TABLES)
            if table_name:
                tbl = next((t for t in self.TABLES if t["name"] == table_name), tbl)
            result.append({"id": i + 1, "field_name": f["field"], "field_desc": f["desc"],
                           "field_type": f["type"], "is_nullable": random.random() > 0.3,
                           "table_name": tbl["name"], "schema_name": tbl["schema"]})
        return result

    def get_audit_tasks(self, page=1, page_size=20, **filters):
        task_names = ["月度数据质量审计", "客户信息完整性审计", "计费准确性审计", "订单数据审计",
                      "账单数据一致性审计", "产品数据质量审计", "用户数据完整性审计", "财务报表审计",
                      "库存数据审计", "操作日志审计", "实时数据质量监控", "定时数据稽核任务"]
        tasks = []
        for i, name in enumerate(task_names):
            tasks.append({
                "id": i + 1, "task_name": name,
                "task_type": random.choice(["field_audit", "rule_audit", "full_audit"]),
                "rule_ids": [random.randint(1, 15) for _ in range(random.randint(1, 5))],
                "field_ids": [random.randint(1, 22) for _ in range(random.randint(3, 10))],
                "schedule_type": random.choice(["manual", "daily", "weekly", "monthly"]),
                "schedule_config": {"cron": "0 2 * * *"} if random.random() > 0.5 else None,
                "execute_strategy": random.choice(["full", "sample"]),
                "sample_rate": random.choice([100.0, 100.0, 50.0, 30.0, 10.0]),
                "status": 1, "importance": random.randint(1, 5),
                "last_execute_time": self.random_datetime(2024, 2025).isoformat(),
                "last_execute_result": random.choice(["success", "success", "success", "failed"]),
                "created_by": self.random_name(),
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(tasks, page, page_size)

    def get_audit_executions(self, task_id=None, page=1, page_size=20):
        execs = []
        for i in range(20):
            total = random.randint(10000, 1000000)
            failed = random.randint(0, int(total * 0.1))
            passed = total - failed
            rate = round(passed / total * 100, 2) if total > 0 else 100
            execs.append({
                "id": i + 1, "task_id": task_id or random.randint(1, 12),
                "task_name": f"审计执行_{i+1}",
                "execute_time": self.random_datetime(2024, 2025).isoformat(),
                "execute_duration": round(random.uniform(10, 3600), 2),
                "total_records": total, "sample_records": random.randint(1000, total),
                "passed_records": passed, "failed_records": failed, "pass_rate": rate,
                "error_message": None if rate > 95 else "数据异常超出阈值",
                "status": random.choice(["completed", "completed", "completed", "failed"]),
                "result_summary": {"total_checks": random.randint(5, 20), "passed": random.randint(3, 20)},
                "created_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(execs, page, page_size)

    def get_audit_exceptions(self, execution_id=None, page=1, page_size=20):
        exception_types = ["空值异常", "数据重复", "格式错误", "范围越界", "关联缺失", "逻辑错误"]
        alerts = []
        for i in range(30):
            total = random.randint(1000, 50000)
            exc_count = random.randint(1, int(total * 0.05))
            alerts.append({
                "id": i + 1, "execution_id": execution_id or random.randint(1, 20),
                "rule_id": random.randint(1, 15), "rule_name": f"规则_{random.randint(1, 15)}",
                "field_name": random.choice(self.FIELDS_DATA)["field"],
                "table_name": random.choice(self.TABLES)["name"],
                "exception_type": random.choice(exception_types),
                "exception_value": f"发现{exc_count}条异常数据",
                "exception_count": exc_count,
                "exception_rate": round(exc_count / total * 100, 4),
                "severity": random.choice(self.SEVERITIES),
                "status": random.choice(["open", "open", "handling", "resolved", "closed"]),
                "handler": self.random_name() if random.random() > 0.3 else None,
                "handle_time": self.random_datetime(2024, 2025).isoformat() if random.random() > 0.3 else None,
                "handle_result": "已修复数据" if random.random() > 0.5 else "确认误报",
                "alert_level": random.choice(["critical", "warning", "info"]),
                "is_upgraded": random.random() > 0.8,
                "created_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(alerts, page, page_size)

    def get_audit_reports(self, page=1, page_size=20):
        reports = []
        for i in range(15):
            total_recs = random.randint(100000, 5000000)
            total_excs = random.randint(10, 5000)
            dt = self.random_datetime(2024, 2025)
            reports.append({
                "id": i + 1,
                "report_name": f"{random.choice(['日', '周', '月', '季度'])}度数据质量报告_{dt.strftime('%Y%m%d')}",
                "report_type": random.choice(["daily", "weekly", "monthly", "custom"]),
                "execution_ids": [random.randint(1, 20) for _ in range(random.randint(1, 5))],
                "total_executions": random.randint(1, 10),
                "total_records": total_recs, "total_exceptions": total_excs,
                "overall_pass_rate": round((total_recs - total_excs) / total_recs * 100, 2) if total_recs > 0 else 100,
                "summary": f"本期共检查{total_recs}条数据记录，发现{total_excs}条异常数据，整体通过率为{round((total_recs - total_excs) / total_recs * 100, 2)}%",
                "conclusion": "数据质量整体良好" if total_excs < 100 else "数据质量需关注",
                "recommendations": ["加强上游数据校验", "定期清理重复数据", "完善数据质量标准"],
                "report_data": {"charts": {}, "details": []},
                "status": random.choice(["draft", "draft", "published"]),
                "created_by": self.random_name(),
                "created_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(reports, page, page_size)

    def get_importance_configs(self):
        levels = [
            {"level": 1, "name": "一般", "color": "green", "range": "0-20", "desc": "常规任务，无需特殊关注", "notify": ["system"], "response": 1440},
            {"level": 2, "name": "重要", "color": "blue", "range": "21-40", "desc": "重要任务，需关注执行结果", "notify": ["system", "email"], "response": 480},
            {"level": 3, "name": "紧急", "color": "orange", "range": "41-60", "desc": "紧急任务，需及时处理", "notify": ["system", "email", "sms"], "response": 120},
            {"level": 4, "name": "严重", "color": "red", "range": "61-80", "desc": "严重任务，需立即处理", "notify": ["system", "email", "sms", "phone"], "response": 30},
            {"level": 5, "name": "灾难", "color": "darkred", "range": "81-100", "desc": "灾难性任务，全员响应", "notify": ["system", "email", "sms", "phone", "dingtalk"], "response": 5},
        ]
        result = []
        for i, l in enumerate(levels):
            result.append({"id": i + 1, "level": l["level"], "level_name": l["name"], "color": l["color"],
                           "score_range": l["range"], "description": l["desc"], "notify_channels": l["notify"],
                           "response_time_minutes": l["response"],
                           "created_at": "2024-01-01T00:00:00", "updated_at": "2024-06-01T00:00:00"})
        return result

    def get_upgrade_rules(self):
        rules = []
        for i in range(8):
            rules.append({
                "id": i + 1, "rule_name": f"告警升级规则_{i+1}",
                "alert_type": random.choice(["task_failure", "data_anomaly", "schedule_delay", "quality_issue"]),
                "trigger_condition": {"count": random.randint(3, 10), "within_minutes": random.randint(30, 480)},
                "upgrade_level": random.randint(1, 3),
                "notify_targets": {"users": [self.random_name() for _ in range(random.randint(1, 3))], "groups": ["oncall"]},
                "notify_template": "【严重告警】{{alert_title}}，请立即处理！",
                "max_upgrade_count": random.randint(3, 5), "is_active": random.random() > 0.2,
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return rules

    # ==================== Root Cause Module Methods ====================

    def get_task_lineage(self, page=1, page_size=20):
        tasks = []
        lineage_data = [
            ("ETL_001", "客户数据抽取", "etl", ["DS_CRM"], ["DS_DW"]),
            ("ETL_002", "账单数据抽取", "etl", ["DS_BILL"], ["DS_DW"]),
            ("ETL_003", "订单数据抽取", "etl", ["DS_ORDER"], ["DS_DW"]),
            ("DQC_001", "数据质量检查-客户", "dqc", ["DS_DW"], ["DS_DW"]),
            ("DQC_002", "数据质量检查-账单", "dqc", ["DS_DW"], ["DS_DW"]),
            ("RPT_001", "月度报表生成", "report", ["DS_DW"], ["DS_BOSS"]),
            ("RPT_002", "日经营报表", "report", ["DS_DW"], ["DS_BOSS"]),
            ("API_001", "用户查询接口", "api", ["DS_CRM"], ["DS_CRM"]),
            ("API_002", "账单查询接口", "api", ["DS_BILL"], ["DS_BILL"]),
            ("ETL_004", "产品数据抽取", "etl", ["DS_BOSS"], ["DS_DW"]),
            ("DQC_003", "数据质量检查-产品", "dqc", ["DS_DW"], ["DS_DW"]),
            ("RPT_003", "季度分析报告", "report", ["DS_DW"], ["DS_BOSS"]),
        ]
        for i, (code, name, typ, inp, out) in enumerate(lineage_data):
            tasks.append({
                "id": i + 1, "task_code": code, "task_name": name, "task_type": typ,
                "upstream_tasks": [{"code": f"ETL_{random.randint(1,4):03d}", "name": f"上游任务_{random.randint(1,10)}"} for _ in range(random.randint(0, 3))],
                "downstream_tasks": [{"code": f"DQC_{random.randint(1,3):03d}", "name": f"下游任务_{random.randint(1,10)}"} for _ in range(random.randint(0, 3))],
                "datasource_input": inp[0], "datasource_output": out[0],
                "schedule_type": random.choice(["daily", "hourly", "weekly"]),
                "owner": self.random_name(),
                "department": random.choice(self.DEPARTMENTS)["name"],
                "description": f"{name}-数据任务",
                "status": 1,
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(tasks, page, page_size)

    def get_analysis_paths(self, page=1, page_size=20):
        paths = []
        path_templates = [
            ("数据延迟分析流程", "data_delay", [
                {"order": 1, "name": "检查任务调度状态", "method": "check_schedule"},
                {"order": 2, "name": "检查上游数据就绪状态", "method": "check_upstream"},
                {"order": 3, "name": "检查数据量异常", "method": "check_volume"},
                {"order": 4, "name": "检查系统资源", "method": "check_resource"},
            ]),
            ("数据质量分析流程", "data_quality", [
                {"order": 1, "name": "数据完整性检查", "method": "check_completeness"},
                {"order": 2, "name": "数据准确性检查", "method": "check_accuracy"},
                {"order": 3, "name": "数据一致性检查", "method": "check_consistency"},
                {"order": 4, "name": "数据时效性检查", "method": "check_timeliness"},
            ]),
            ("系统故障分析流程", "system", [
                {"order": 1, "name": "系统资源使用率检查", "method": "check_sys_resource"},
                {"order": 2, "name": "应用日志分析", "method": "check_app_log"},
                {"order": 3, "name": "数据库连接检查", "method": "check_db_conn"},
                {"order": 4, "name": "网络连通性检查", "method": "check_network"},
            ]),
            ("业务异常分析流程", "business", [
                {"order": 1, "name": "业务指标波动检查", "method": "check_metric_change"},
                {"order": 2, "name": "数据源对比分析", "method": "compare_source"},
                {"order": 3, "name": "历史趋势分析", "method": "trend_analysis"},
                {"order": 4, "name": "关联业务分析", "method": "related_biz_analysis"},
            ]),
            ("计费异常分析流程", "data_delay", [
                {"order": 1, "name": "计费数据量检查", "method": "check_bill_volume"},
                {"order": 2, "name": "批价结果校验", "method": "check_pricing"},
                {"order": 3, "name": "账期切换检查", "method": "check_account_period"},
                {"order": 4, "name": "出账文件检查", "method": "check_output_file"},
            ]),
        ]
        for i, (name, ptype, steps) in enumerate(path_templates):
            paths.append({
                "id": i + 1, "path_name": name, "path_type": ptype, "steps": steps,
                "applicable_scenarios": f"适用于{name}相关的问题排查",
                "expected_duration": random.randint(15, 120),
                "success_rate": round(random.uniform(0.6, 0.95), 2),
                "usage_count": random.randint(10, 500),
                "status": 1,
                "created_by": self.random_name(),
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(paths, page, page_size)

    def get_problem_cases(self, page=1, page_size=20, **filters):
        cases = []
        case_templates = [
            ("某省账单数据延迟处理案例", "data_delay", "数据延迟导致出账推迟2小时", "数据量突增50%，原有调度资源不足", "增加调度节点，优化数据分片策略"),
            ("客户信息缺失导致营销失败案例", "data_quality", "客户信息表中20%记录缺少手机号", "接口调用超时未重试，数据写入失败", "添加接口重试机制，完善数据补偿流程"),
            ("计费系统数据不一致排查案例", "data_quality", "账务系统与计费系统数据相差0.3%", "分布式事务部分失败未回滚", "引入分布式事务中间件，完善对账机制"),
            ("月度报表生成失败案例", "data_delay", "报表生成超时导致管理层无法查看", "上游依赖任务执行失败未通知", "完善依赖监控，添加自动重试和告警机制"),
            ("用户订单状态异常案例", "business", "5%的订单状态长时间停留在待支付", "支付回调接口响应慢导致超时", "优化回调接口性能，添加补偿机制"),
            ("某省IDC数据丢失恢复案例", "system_fault", "硬盘故障导致部分数据丢失", "RAID卡故障且备份未及时更新", "修复RAID卡，从异地备份恢复数据"),
            ("跨域数据同步延迟案例", "data_delay", "集团与省公司数据同步延迟4小时", "网络带宽不足，数据压缩策略不合理", "升级网络带宽，优化数据压缩算法"),
            ("套餐变更数据不一致案例", "business", "用户套餐变更后计费未切换", "变更数据未同步到计费系统", "完善数据同步机制，添加变更审核流程"),
        ]
        for i, (title, ctype, desc, root, sol) in enumerate(case_templates):
            occur_time = self.random_datetime(2024, 2025)
            resolve_time = occur_time + timedelta(hours=random.randint(1, 72))
            cases.append({
                "id": i + 1, "case_title": title, "case_type": ctype,
                "case_source": random.choice(["manual", "auto", "imported"]),
                "status": random.choice(["open", "resolved", "closed"]),
                "severity": random.choice(["critical", "high", "medium"]),
                "description": desc, "impact_range": f"影响用户{random.randint(1000, 500000)}人",
                "root_cause": root, "solution": sol,
                "lessons_learned": "加强监控告警，完善应急预案",
                "tags": [ctype, "urgent" if random.random() > 0.5 else "common"],
                "related_task_code": f"ETL_{random.randint(1,10):03d}",
                "related_tables": [random.choice(self.TABLES)["name"] for _ in range(random.randint(1, 3))],
                "handler": self.random_name(), "handler_department": random.choice(self.DEPARTMENTS)["name"],
                "occurrence_time": occur_time.isoformat(),
                "resolve_time": resolve_time.isoformat(),
                "resolution_duration": int((resolve_time - occur_time).total_seconds() / 60),
                "is_template": random.random() > 0.8,
                "usage_count": random.randint(1, 200), "rating": round(random.uniform(1, 5), 1),
                "created_by": self.random_name(),
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(cases, page, page_size)

    def get_root_cause_analyses(self, page=1, page_size=20, **filters):
        analyses = []
        for i in range(15):
            analyses.append({
                "id": i + 1, "case_id": random.randint(1, 8) if random.random() > 0.3 else None,
                "path_id": random.randint(1, 5),
                "analysis_title": f"根因分析_{i+1}_{self.random_datetime(2024, 2025).strftime('%Y%m%d')}",
                "problem_description": f"系统检测到{random.choice(['数据延迟', '数据异常', '质量下降', '任务失败'])}，需进行根因分析",
                "analysis_process": [
                    {"step": 1, "action": "数据采集", "result": "已采集相关日志和数据"},
                    {"step": 2, "action": "特征提取", "result": "提取关键特征维度"},
                    {"step": 3, "action": "模型分析", "result": "完成相关性分析"},
                ],
                "conclusion": f"根因分析完成，主要原因为{random.choice(['数据源异常', '网络延迟', '资源不足', '代码缺陷', '配置错误'])}",
                "root_cause_type_id": random.randint(1, 8),
                "root_cause_desc": f"系统资源不足导致处理延迟" if random.random() > 0.5 else f"数据源端数据质量问题",
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "status": random.choice(["analyzing", "completed", "completed", "failed"]),
                "is_saved_as_case": random.random() > 0.7,
                "analysis_duration": random.randint(30, 600),
                "ai_assisted": random.random() > 0.3,
                "created_by": self.random_name(),
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(analyses, page, page_size)

    def get_analysis_steps(self, analysis_id):
        steps = []
        step_names = ["问题接收", "数据采集", "特征分析", "根因定位", "方案推荐", "结果验证"]
        for i, name in enumerate(step_names):
            steps.append({
                "id": i + 1, "analysis_id": analysis_id,
                "step_name": name, "step_order": i + 1,
                "action": f"执行{name}操作",
                "input_data": {"source": "system", "params": {}},
                "output_data": {"result": f"{name}完成", "details": {}},
                "reasoning": f"通过{name}步骤，逐步缩小问题范围",
                "status": random.choice(["completed", "running", "pending"]),
                "duration": random.randint(100, 30000),
                "created_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return steps

    def get_user_feedback(self, page=1, page_size=20):
        feedbacks = []
        for i in range(20):
            feedbacks.append({
                "id": i + 1, "analysis_id": random.randint(1, 15),
                "case_id": random.randint(1, 8),
                "feedback_type": random.choice(["helpful", "useful", "accurate", "timely", "other"]),
                "rating": random.randint(1, 5),
                "content": random.choice([
                    "分析结果准确，帮助快速定位问题",
                    "建议增加更多分析维度",
                    "根因定位非常精准，节省了大量排查时间",
                    "分析过程清晰，推荐方案可行",
                    "结果基本准确，但分析速度有待提升",
                ]),
                "user_name": self.random_name(),
                "user_department": random.choice(self.DEPARTMENTS)["name"],
                "is_resolved": random.random() > 0.3,
                "created_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(feedbacks, page, page_size)

    def get_case_statistics(self):
        types = ["data_delay", "data_quality", "system_fault", "business"]
        severities = ["critical", "high", "medium", "low"]
        statuses = ["open", "resolved", "closed"]
        return {
            "total_cases": 128,
            "by_type": {t: random.randint(10, 50) for t in types},
            "by_severity": {s: random.randint(10, 50) for s in severities},
            "by_status": {s: random.randint(10, 60) for s in statuses},
            "avg_resolution_time": 180,
            "top_tags": [{"tag": "数据延迟", "count": 45}, {"tag": "数据质量", "count": 38}, {"tag": "系统故障", "count": 22}, {"tag": "业务异常", "count": 18}, {"tag": "计费问题", "count": 12}],
            "recent_cases": 15,
        }

    def get_suggestions(self, page=1, page_size=20):
        suggestions = []
        for i in range(15):
            suggestions.append({
                "id": i + 1, "case_id": random.randint(1, 8),
                "analysis_id": random.randint(1, 15),
                "title": f"优化建议_{i+1}",
                "content": random.choice([
                    "建议增加数据质量预校验机制",
                    "建议优化调度策略，增加资源弹性伸缩",
                    "建议完善监控告警覆盖范围",
                    "建议建立数据补偿机制",
                    "建议优化SQL查询性能",
                ]),
                "suggestion_type": random.choice(["optimization", "monitor", "process", "technology"]),
                "status": random.choice(["pending", "adopted", "ignored"]),
                "created_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(suggestions, page, page_size)

    def get_suggestion_statistics(self):
        return {
            "total": 128,
            "adopted": 56,
            "ignored": 22,
            "pending": 50,
            "adopt_rate": 0.4375,
        }

    # ==================== Monthly Module Methods ====================

    def get_monthly_progress(self, account_month=None):
        months = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"]
        am = account_month or random.choice(months)
        total = random.randint(80, 200)
        completed = random.randint(int(total * 0.3), total)
        failed = random.randint(0, int(total * 0.05))
        running = random.randint(0, int(total * 0.2))
        pending = total - completed - failed - running
        return {
            "account_month": am, "total_tasks": total, "completed_tasks": completed,
            "failed_tasks": failed, "running_tasks": running, "pending_tasks": max(0, pending),
            "progress": round(completed / total * 100, 1) if total > 0 else 0,
            "quality_score": round(random.uniform(85, 99.5), 1),
            "days_elapsed": random.randint(5, 28), "days_total": 30,
            "status": random.choice(["pending", "processing", "processing", "completed"]),
        }

    def get_milestones(self, account_month=None):
        milestones = []
        milestone_data = [
            ("数据采集完成", "采集", 5, 3),
            ("数据清洗完成", "清洗", 10, 8),
            ("数据稽核完成", "稽核", 15, 14),
            ("报表生成完成", "报表", 20, 19),
            ("质量报告发布", "发布", 25, 24),
            ("异常数据处理", "处理", 12, 13),
            ("月度总结完成", "总结", 28, 28),
            ("KPI评估完成", "评估", 30, 30),
        ]
        for i, (name, mtype, plan, actual) in enumerate(milestone_data):
            plan_date = date(2025, 3, plan)
            actual_date = date(2025, 3, actual)
            is_delayed = actual > plan
            milestones.append({
                "id": i + 1, "account_month": account_month or "2025-03",
                "milestone_name": name, "milestone_type": mtype,
                "plan_date": plan_date.isoformat(),
                "actual_date": actual_date.isoformat() if random.random() > 0.2 else None,
                "status": random.choice(["completed", "completed", "delayed", "pending"]),
                "delay_days": (actual_date - plan_date).days if is_delayed else 0,
                "completion_percentage": random.choice([100, 100, 80, 50]),
                "responsible_person": self.random_name(),
                "description": f"{name}里程碑",
                "remark": "正常完成" if not is_delayed else f"延迟{(actual_date - plan_date).days}天",
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return milestones

    def get_running_tasks(self):
        tasks = []
        for i in range(10):
            plan_start = self.random_datetime(2025, 2025)
            plan_end = plan_start + timedelta(hours=random.randint(1, 48))
            actual_start = plan_start + timedelta(minutes=random.randint(-30, 30))
            tasks.append({
                "id": i + 1, "task_name": f"运行任务_{i+1}",
                "task_type": random.choice(["etl", "dqc", "report", "sync"]),
                "priority": random.choice(["urgent", "high", "normal", "low"]),
                "status": random.choice(["running", "running", "pending"]),
                "progress": round(random.uniform(10, 95), 1),
                "plan_start_time": plan_start.isoformat(),
                "plan_end_time": plan_end.isoformat(),
                "actual_start_time": actual_start.isoformat() if random.random() > 0.2 else None,
                "owner": self.random_name(),
                "is_critical": random.random() > 0.7,
                "expected_duration": int((plan_end - plan_start).total_seconds()),
                "elapsed_seconds": random.randint(100, 36000),
            })
        return tasks

    def get_monthly_tasks(self, page=1, page_size=20):
        tasks = []
        for i in range(25):
            plan_start = self.random_datetime(2025, 2025)
            plan_end = plan_start + timedelta(hours=random.randint(1, 72))
            actual_start = plan_start + timedelta(minutes=random.randint(-60, 60))
            actual_end = actual_start + timedelta(hours=random.randint(1, 72)) if random.random() > 0.3 else None
            tasks.append({
                "id": i + 1, "account_month": "2025-03",
                "task_code": f"TASK_{i+1:04d}",
                "task_name": f"月度任务_{i+1}_{self.random_name()}",
                "task_type": random.choice(["数据采集", "数据清洗", "数据稽核", "报表生成", "数据同步", "质量检查"]),
                "priority": random.choice(["urgent", "high", "normal", "low"]),
                "status": random.choice(["pending", "running", "completed", "failed", "skipped"]),
                "progress": round(random.uniform(0, 100), 1),
                "plan_start_time": plan_start.isoformat(),
                "plan_end_time": plan_end.isoformat(),
                "actual_start_time": actual_start.isoformat(),
                "actual_end_time": actual_end.isoformat() if actual_end else None,
                "duration_seconds": int((actual_end - actual_start).total_seconds()) if actual_end else None,
                "expected_duration": int((plan_end - plan_start).total_seconds()),
                "owner": self.random_name(),
                "dependency_ids": [random.randint(1, 25) for _ in range(random.randint(0, 3))],
                "retry_count": random.randint(0, 2),
                "is_critical": random.random() > 0.7,
                "error_message": "处理超时" if random.random() > 0.9 else None,
                "result_summary": {"processed": random.randint(1000, 100000), "success": True},
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(tasks, page, page_size)

    def get_task_logs(self, task_id):
        logs = []
        levels = ["info", "debug", "warning", "error"]
        for i in range(random.randint(5, 20)):
            logs.append({
                "id": i + 1, "task_id": task_id,
                "log_content": f"[{random.choice(levels)}] 任务执行第{i+1}步：{random.choice(['开始执行', '处理中', '处理完成', '遇到错误', '重试中'])}",
                "log_level": random.choice(levels),
                "created_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return logs

    def get_orchestration_tasks(self, page=1, page_size=20):
        tasks = []
        for i in range(20):
            plan_start = self.random_datetime(2025, 2025)
            plan_end = plan_start + timedelta(hours=random.randint(1, 48))
            tasks.append({
                "id": i + 1, "task_name": f"编排任务_{i+1}",
                "task_code": f"ORCH_{i+1:04d}",
                "task_type": random.choice(["etl", "dqc", "report", "sync", "audit"]),
                "priority": random.choice(["urgent", "high", "normal", "low"]),
                "status": random.choice(["pending", "running", "completed", "failed"]),
                "plan_start_time": plan_start.isoformat(),
                "plan_end_time": plan_end.isoformat(),
                "expected_duration": int((plan_end - plan_start).total_seconds()),
                "owner": self.random_name(),
                "dependency_ids": [random.randint(1, 20) for _ in range(random.randint(0, 3))],
                "is_critical": random.random() > 0.7,
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(tasks, page, page_size)

    def get_gantt_data(self):
        tasks = []
        start_base = datetime(2025, 3, 1, 8, 0, 0)
        for i in range(12):
            start = start_base + timedelta(hours=i * 4)
            end = start + timedelta(hours=random.randint(2, 8))
            tasks.append({
                "id": i + 1, "task_name": f"任务_{i+1}",
                "start": start.isoformat(), "end": end.isoformat(),
                "progress": round(random.uniform(0, 100), 1),
                "dependency": f"{i}" if i > 0 and random.random() > 0.5 else None,
                "priority": random.choice(["urgent", "high", "normal"]),
                "status": random.choice(["pending", "running", "completed"]),
                "owner": self.random_name(),
            })
        return {"tasks": tasks}

    def get_dag_data(self):
        nodes = []
        edges = []
        for i in range(10):
            nodes.append({
                "id": f"NODE_{i+1}", "label": f"任务_{i+1}",
                "status": random.choice(["pending", "running", "completed", "failed"]),
                "type": random.choice(["etl", "dqc", "report"]),
            })
        for i in range(9):
            edges.append({"source": f"NODE_{i+1}", "target": f"NODE_{i+2}", "type": "default"})
        return {"nodes": nodes, "edges": edges}

    def get_daily_reports(self, page=1, page_size=20):
        reports = []
        for i in range(15):
            report_date = self.random_date(2025, 2025)
            completed = random.randint(5, 30)
            total = completed + random.randint(0, 5)
            reports.append({
                "id": i + 1, "report_date": report_date.isoformat(),
                "account_month": "2025-03",
                "title": f"{report_date.isoformat()}日报",
                "content": {"sections": [{"title": "任务完成情况", "data": {}}, {"title": "异常统计", "data": {}}]},
                "summary": f"今日完成任务{completed}项，异常{random.randint(0, 3)}项",
                "task_completed": completed, "task_total": total,
                "exception_count": random.randint(0, 3),
                "quality_score": round(random.uniform(85, 100), 1),
                "progress": round(completed / total * 100, 1) if total > 0 else 0,
                "ai_generated": random.random() > 0.5,
                "status": random.choice(["draft", "published"]),
                "created_by": self.random_name(),
                "created_at": self.random_datetime(2025, 2025).isoformat(),
                "updated_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return self.paginate(reports, page, page_size)

    def get_summary_reports(self, page=1, page_size=20):
        reports = []
        for i in range(10):
            reports.append({
                "id": i + 1, "account_month": f"2025-{random.randint(1, 4):02d}",
                "title": f"2025年{random.randint(1, 4)}月数据运维月度报告",
                "report_type": "monthly",
                "overview": "本月数据运维工作整体平稳，各项指标达标",
                "key_metrics": {"data_quality": random.uniform(90, 99), "task_completion": random.uniform(85, 100), "system_uptime": 99.99},
                "progress_summary": {"total": 120, "completed": random.randint(100, 120), "failed": random.randint(0, 3)},
                "problem_analysis": "本月主要问题是数据同步延迟，影响范围有限",
                "achievements": "完成了数据质量监控体系升级，异常发现率提升30%",
                "improvement_plan": "下月计划：优化调度策略，完善监控覆盖",
                "attachments": [],
                "status": random.choice(["draft", "published", "archived"]),
                "exception_flag": random.random() > 0.8,
                "exception_detail": "存在异常" if random.random() > 0.8 else None,
                "publisher": self.random_name(),
                "publish_time": self.random_datetime(2025, 2025).isoformat() if random.random() > 0.3 else None,
                "created_by": self.random_name(),
                "created_at": self.random_datetime(2024, 2025).isoformat(),
                "updated_at": self.random_datetime(2024, 2025).isoformat(),
            })
        return self.paginate(reports, page, page_size)

    def get_alerts_records(self, page=1, page_size=20):
        alerts = []
        for i in range(25):
            alerts.append({
                "id": i + 1, "account_month": "2025-03",
                "alert_title": f"告警_{i+1}_{random.choice(['任务失败', '数据异常', '调度延迟', '质量下降'])}",
                "alert_type": random.choice(["task_failure", "data_anomaly", "schedule_delay", "quality_issue"]),
                "alert_level": random.choice(["critical", "warning", "info"]),
                "source": random.choice(["system", "manual", "auto"]),
                "content": f"检测到{random.choice(['任务执行失败', '数据异常波动', '调度延迟超过阈值', '质量评分下降'])}",
                "related_task_id": random.randint(1, 30),
                "related_task_name": f"关联任务_{random.randint(1, 30)}",
                "status": random.choice(["unread", "read", "handled", "ignored"]),
                "handler": self.random_name() if random.random() > 0.3 else None,
                "handle_time": self.random_datetime(2025, 2025).isoformat() if random.random() > 0.3 else None,
                "handle_result": "已处理完毕" if random.random() > 0.5 else None,
                "is_upgraded": random.random() > 0.9,
                "created_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return self.paginate(alerts, page, page_size)

    # ==================== System Module Methods ====================

    def get_users(self, page=1, page_size=20):
        users = []
        for i in range(25):
            dept = random.choice(self.DEPARTMENTS)
            users.append({
                "id": i + 1,
                "username": f"user_{i+1:03d}",
                "real_name": self.random_name(),
                "email": f"user{i+1:03d}@company.com",
                "phone": self.random_phone(),
                "avatar": None,
                "department_id": dept["id"],
                "department_name": dept["name"],
                "position": random.choice(["数据分析师", "数据工程师", "运维工程师", "质量工程师", "产品经理", "部门经理", "总监"]),
                "status": random.choice([1, 1, 1, 0]),
                "is_admin": i == 0,
                "roles": [{"id": random.randint(1, 5), "name": random.choice(["管理员", "分析师", "工程师", "查看者"])}],
                "last_login_time": self.random_datetime(2025, 2025).isoformat(),
                "remark": None,
                "created_by": "admin",
                "created_at": self.random_datetime(2024, 2024).isoformat(),
                "updated_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return self.paginate(users, page, page_size)

    def get_roles(self):
        roles_data = [
            (1, "系统管理员", "ROLE_ADMIN", "系统最高权限角色"),
            (2, "数据分析师", "ROLE_ANALYST", "数据查询和分析权限"),
            (3, "数据工程师", "ROLE_ENGINEER", "数据开发和维护权限"),
            (4, "质量审核员", "ROLE_AUDITOR", "数据质量审核权限"),
            (5, "普通用户", "ROLE_USER", "基础查看权限"),
        ]
        return [{"id": r[0], "role_name": r[1], "role_code": r[2], "description": r[3],
                  "status": 1, "permissions": [{"id": random.randint(1, 20), "name": f"权限_{random.randint(1, 20)}"}],
                  "created_at": "2024-01-01T00:00:00", "updated_at": "2024-06-01T00:00:00"}
                for r in roles_data]

    def get_permissions(self):
        perms = []
        modules = ["dashboard", "audit", "root_cause", "monthly", "assistant", "settings"]
        for i, mod in enumerate(modules):
            perms.append({"id": i * 3 + 1, "permission_name": f"{mod}_view", "permission_code": f"{mod}:view",
                          "menu_path": f"/{mod}", "parent_id": None, "permission_type": "menu",
                          "icon": "icon-view", "sort_order": i, "description": f"{mod}查看权限", "status": 1,
                          "children": [
                              {"id": i * 3 + 2, "permission_name": f"{mod}_edit", "permission_code": f"{mod}:edit",
                               "menu_path": f"/{mod}/edit", "parent_id": i * 3 + 1, "permission_type": "button",
                               "icon": None, "sort_order": 0, "description": f"{mod}编辑权限", "status": 1, "children": None},
                              {"id": i * 3 + 3, "permission_name": f"{mod}_delete", "permission_code": f"{mod}:delete",
                               "menu_path": f"/{mod}/delete", "parent_id": i * 3 + 1, "permission_type": "button",
                               "icon": None, "sort_order": 1, "description": f"{mod}删除权限", "status": 1, "children": None},
                          ], "created_at": "2024-01-01T00:00:00"})
        return perms

    def get_departments(self):
        return [{"id": d["id"], "dept_name": d["name"], "dept_code": d["code"],
                  "parent_id": None if d["id"] == 1 else 1, "dept_level": 1 if d["id"] == 1 else 2,
                  "dept_type": "management" if d["id"] <= 4 else "support",
                  "manager": self.random_name(), "phone": self.random_phone(),
                  "email": f"{d['code'].lower()}@company.com", "sort_order": d["id"],
                  "status": 1, "children": None,
                  "created_at": "2024-01-01T00:00:00"} for d in self.DEPARTMENTS]

    def get_system_configs(self, page=1, page_size=20):
        configs = []
        config_data = [
            ("system.title", "数据运维数字员工平台", "system"),
            ("system.version", "2.0.0", "system"),
            ("alert.threshold.critical", "90", "alert"),
            ("alert.threshold.warning", "95", "alert"),
            ("notification.email.enabled", "true", "notification"),
            ("notification.sms.enabled", "false", "notification"),
            ("audit.default_sample_rate", "100", "business"),
            ("audit.max_retry_count", "3", "business"),
            ("monthly.auto_report", "true", "business"),
            ("root_cause.max_analysis_minutes", "30", "business"),
        ]
        for i, (key, val, ctype) in enumerate(config_data):
            configs.append({
                "id": i + 1, "config_key": key, "config_value": val,
                "config_type": ctype,
                "description": f"{key}配置项",
                "is_encrypted": "key" in key and "secret" in key,
                "status": 1,
                "created_by": "admin",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-06-01T00:00:00",
            })
        return self.paginate(configs, page, page_size)

    def get_data_dicts(self, dict_type=None):
        dicts = []
        types = ["audit_type", "task_status", "severity_level", "alert_type", "priority"]
        for t in types:
            if dict_type and t != dict_type:
                continue
            for j in range(5):
                dicts.append({
                    "id": len(dicts) + 1,
                    "dict_key": f"{t}_{j}",
                    "dict_value": f"{t}_value_{j}",
                    "dict_type": t,
                    "parent_id": None,
                    "sort_order": j,
                    "status": 1,
                    "remark": f"{t}字典项{j}",
                    "created_at": "2024-01-01T00:00:00",
                })
        return dicts

    def get_notifications(self, page=1, page_size=20):
        notifications = []
        for i in range(20):
            notifications.append({
                "id": i + 1,
                "notification_type": random.choice(["alert", "reminder", "system", "business"]),
                "title": f"通知_{i+1}_{random.choice(['任务完成', '异常告警', '系统更新', '审批提醒'])}",
                "content": f"这是第{i+1}条通知内容",
                "receiver_id": random.randint(1, 25),
                "receiver_name": self.random_name(),
                "channel": random.choice(["system", "email", "sms", "dingtalk"]),
                "is_read": random.random() > 0.4,
                "read_time": self.random_datetime(2025, 2025).isoformat() if random.random() > 0.6 else None,
                "status": random.choice(["sent", "delivered", "failed"]),
                "send_time": self.random_datetime(2025, 2025).isoformat(),
                "created_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return self.paginate(notifications, page, page_size)

    def get_audit_logs(self, page=1, page_size=20):
        logs = []
        actions = ["create", "update", "delete", "query", "login", "logout"]
        modules = ["audit", "root_cause", "monthly", "system", "assistant", "dashboard"]
        for i in range(30):
            logs.append({
                "id": i + 1, "user_id": random.randint(1, 25),
                "username": self.random_name(),
                "action_type": random.choice(actions),
                "module": random.choice(modules),
                "action_detail": f"执行了{random.choice(actions)}操作",
                "request_url": f"/api/v1/{random.choice(modules)}/{random.randint(1, 100)}",
                "request_method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                "request_params": {"key": "value"},
                "response_code": random.choice([200, 200, 200, 400, 500]),
                "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "user_agent": "Mozilla/5.0",
                "duration_ms": random.randint(5, 5000),
                "status": random.choice(["success", "success", "success", "failure"]),
                "created_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return self.paginate(logs, page, page_size)

    def get_interface_logs(self, page=1, page_size=20):
        logs = []
        for i in range(20):
            logs.append({
                "id": i + 1, "interface_name": f"接口_{i+1}",
                "interface_type": random.choice(["internal", "external"]),
                "request_url": f"/api/v1/{random.choice(['audit', 'monthly', 'root-cause'])}/{random.randint(1, 100)}",
                "request_method": random.choice(["GET", "POST"]),
                "request_headers": {"Content-Type": "application/json"},
                "request_body": {"params": {}},
                "response_code": random.choice([200, 200, 200, 500]),
                "response_body": {"code": 200, "data": {}},
                "duration_ms": random.randint(10, 3000),
                "caller": self.random_name(),
                "status": random.choice(["success", "success", "failure"]),
                "error_message": None if random.random() > 0.2 else "Internal error",
                "created_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return self.paginate(logs, page, page_size)

    def get_job_schedules(self, page=1, page_size=20):
        jobs = []
        for i in range(10):
            jobs.append({
                "id": i + 1, "job_name": f"调度任务_{i+1}",
                "job_code": f"JOB_{i+1:04d}",
                "job_type": random.choice(["audit", "monthly", "system"]),
                "trigger_type": random.choice(["cron", "interval", "manual"]),
                "trigger_config": {"cron": "0 2 * * *"} if random.random() > 0.5 else {"interval": 3600},
                "target_function": f"app.tasks.{random.choice(['audit_tasks', 'monthly_tasks'])}.task_{i+1}",
                "parameters": {},
                "status": random.choice([1, 1, 0]),
                "last_run_time": self.random_datetime(2025, 2025).isoformat(),
                "last_run_result": random.choice(["success", "success", "failed"]),
                "next_run_time": self.random_datetime(2025, 2025).isoformat(),
                "run_count": random.randint(10, 1000),
                "fail_count": random.randint(0, 20),
                "description": f"调度任务_{i+1}描述",
                "created_by": "admin",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return self.paginate(jobs, page, page_size)

    def get_tool_configs(self, page=1, page_size=20):
        tools = []
        for i in range(10):
            tools.append({
                "id": i + 1, "config_name": f"工具_{i+1}",
                "config_code": f"TOOL_{i+1:04d}",
                "config_type": "tool",
                "config_value": f"工具配置值_{i+1}",
                "description": f"工具_{i+1}的配置描述",
                "parameters": {"param1": "value1", "param2": i * 10},
                "status": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-06-01T00:00:00",
            })
        return self.paginate(tools, page, page_size)

    def get_prompt_configs(self, page=1, page_size=20):
        prompts = []
        for i in range(10):
            prompts.append({
                "id": i + 1, "config_name": f"提示词_{i+1}",
                "config_code": f"PROMPT_{i+1:04d}",
                "config_type": "prompt",
                "config_value": f"你是一个专业的数据运维助手，请帮助用户完成数据运维任务_{i+1}",
                "description": f"提示词_{i+1}的描述",
                "parameters": {"temperature": 0.7, "max_tokens": 2000},
                "status": 1,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-06-01T00:00:00",
            })
        return self.paginate(prompts, page, page_size)

    # ==================== Assistant Module Methods ====================

    def get_chat_sessions(self, page=1, page_size=20):
        sessions = []
        for i in range(15):
            sessions.append({
                "id": i + 1, "session_title": f"会话_{i+1}_{random.choice(['数据质量分析', '根因排查', '报表咨询', '日常问答'])}",
                "session_type": random.choice(["general", "analysis", "audit", "report"]),
                "user_id": 1, "user_name": self.random_name(),
                "context_summary": f"关于{random.choice(['数据质量', '任务调度', '异常处理'])}的对话",
                "message_count": random.randint(2, 30),
                "status": random.choice(["active", "archived"]),
                "is_pinned": random.random() > 0.8,
                "created_at": self.random_datetime(2025, 2025).isoformat(),
                "updated_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return self.paginate(sessions, page, page_size)

    def get_chat_messages(self, session_id, page=1, page_size=50):
        messages = []
        roles = ["user", "assistant", "user", "assistant"]
        contents = [
            "帮我分析一下最近的数据质量情况",
            "根据最新数据，本月数据质量整体良好，通过率达到97.3%，比上月提升1.2个百分点。主要问题集中在客户信息完整性方面，建议重点关注。",
            "哪些表的数据质量需要关注？",
            "目前t_customer_info表的手机号缺失率达到3.5%，t_order_main表的订单状态异常率为1.2%，建议优先处理这两个表的数据质量问题。",
            "根因分析结果如何？",
            "经过系统分析，发现主要根因是上游CRM系统的接口超时导致数据写入失败，建议：1)增加接口超时时间 2)引入消息队列异步处理 3)建立数据补偿机制。",
            "好的，我了解了，谢谢！",
            "不客气！如有其他问题，随时可以向我咨询。建议您可以查看数据质量报告获取更详细的信息。",
        ]
        for i in range(random.randint(4, 20)):
            idx = i % len(contents)
            messages.append({
                "id": i + 1, "session_id": session_id,
                "role": roles[idx % len(roles)],
                "content": contents[idx],
                "content_type": "text",
                "tokens_used": random.randint(50, 500),
                "ai_model": "gpt-4",
                "metadata": None,
                "feedback_score": random.randint(1, 5) if i % 2 == 1 else None,
                "created_at": self.random_datetime(2025, 2025).isoformat(),
            })
        return self.paginate(messages, page, page_size)

    def get_ai_configs(self):
        configs = [
            {"id": 1, "config_name": "默认GPT-4配置", "config_code": "AI_DEFAULT", "provider": "openai",
             "endpoint": "https://api.openai.com/v1", "api_key": "sk-xxx", "model_name": "gpt-4",
             "parameters": {"temperature": 0.7, "top_p": 0.9}, "max_tokens": 4096, "temperature": 0.7,
             "context_limit": 10, "is_default": True, "status": 1,
             "created_by": "admin", "created_at": "2024-01-01T00:00:00", "updated_at": "2024-06-01T00:00:00"},
            {"id": 2, "config_name": "分析专用配置", "config_code": "AI_ANALYSIS", "provider": "openai",
             "endpoint": "https://api.openai.com/v1", "api_key": "sk-xxx", "model_name": "gpt-4-turbo",
             "parameters": {"temperature": 0.3, "top_p": 0.95}, "max_tokens": 8192, "temperature": 0.3,
             "context_limit": 20, "is_default": False, "status": 1,
             "created_by": "admin", "created_at": "2024-01-01T00:00:00", "updated_at": "2024-06-01T00:00:00"},
        ]
        return configs

    # ==================== Dashboard Methods ====================

    def get_dashboard_summary(self):
        return {
            "total_tasks": 128,
            "completed_tasks": 98,
            "failed_tasks": 3,
            "running_tasks": 12,
            "pending_tasks": 15,
            "progress": 76.6,
            "quality_score": 96.8,
            "active_alerts": 8,
            "critical_alerts": 2,
            "today_exceptions": 15,
            "total_cases": 128,
            "unresolved_cases": 23,
            "avg_resolution_time": 180,
            "system_uptime": 99.97,
        }

    def get_dashboard_trends(self):
        return {
            "quality_trend": {
                "dates": ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"],
                "values": [95.2, 96.1, 96.8, 97.3, 97.8],
            },
            "task_trend": {
                "dates": ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"],
                "total": [110, 115, 120, 125, 128],
                "completed": [90, 95, 100, 105, 98],
            },
            "alert_trend": {
                "dates": ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05"],
                "critical": [5, 3, 4, 2, 2],
                "warning": [12, 10, 8, 6, 5],
                "info": [20, 18, 15, 12, 10],
            },
            "exception_distribution": {
                "空值异常": 35,
                "数据重复": 25,
                "格式错误": 20,
                "范围越界": 12,
                "关联缺失": 8,
            },
        }

    def get_dashboard_recent_alerts(self):
        alerts = []
        for i in range(10):
            alerts.append({
                "id": i + 1,
                "title": f"告警_{i+1}_{random.choice(['任务执行失败', '数据同步延迟', '质量评分下降', '系统资源告警'])}",
                "type": random.choice(["task_failure", "data_anomaly", "schedule_delay", "quality_issue"]),
                "level": random.choice(["critical", "warning", "info"]),
                "status": random.choice(["unread", "read", "handled"]),
                "source": random.choice(["system", "manual"]),
                "created_at": self.random_datetime(2025, 2025).isoformat(),
                "content": f"检测到系统{random.choice(['异常', '告警', '问题'])}，请及时处理",
            })
        return alerts

        # ==================== Billing Progress Methods ====================

    def get_billing_cycles(self):
        """Get billing cycles."""
        return [
            {"cycle_id": "202601", "cycle_name": "2026年1月账期", "start_date": "2026-01-31", "end_date": "2026-02-03", "status": "closed"},
            {"cycle_id": "202602", "cycle_name": "2026年2月账期", "start_date": "2026-02-25", "end_date": "2026-02-28", "status": "closed"},
            {"cycle_id": "202603", "cycle_name": "2026年3月账期", "start_date": "2026-03-28", "end_date": "2026-03-31", "status": "closed"},
            {"cycle_id": "202604", "cycle_name": "2026年4月账期", "start_date": "2026-04-26", "end_date": "2026-04-30", "status": "closed"},
            {"cycle_id": "202605", "cycle_name": "2026年5月账期", "start_date": "2026-05-27", "end_date": "2026-05-30", "status": "active"},
        ]

    def _build_billing_tasks(self, cycle_id):
        """Build the 134 billing progress tasks for a given cycle."""
        cycle_start = {
            "202601": {"start": datetime(2026, 1, 31, 23, 0), "end": datetime(2026, 2, 3, 21, 30)},
            "202602": {"start": datetime(2026, 2, 25, 23, 0), "end": datetime(2026, 2, 28, 21, 30)},
            "202603": {"start": datetime(2026, 3, 28, 23, 0), "end": datetime(2026, 3, 31, 21, 30)},
            "202604": {"start": datetime(2026, 4, 26, 23, 0), "end": datetime(2026, 4, 30, 21, 30)},
            "202605": {"start": datetime(2026, 5, 27, 23, 0), "end": datetime(2026, 5, 30, 21, 30)},
        }
        base = cycle_start.get(cycle_id, cycle_start["202601"])
        s = base["start"]

        # Generate 134 tasks across 4 work types
        # Task code patterns: {WORK_TYPE}_{STAGE}_{SEQUENCE}
        # Work type prefixes: PRE(前置), USER(用户), INCOME(实收), REC(应收)

        task_defs = []

        # ========== 前置作业 (PRE) - ~34 tasks ==========
        pre_tasks = [
            ("PRE_END_001", "截图 otter 同步情况", 0, 5),
            ("PRE_END_002", "发布'账期准备开始'消息", 25, 1),
            ("PRE_D1_001", "启动计费1号批次接口层采集", 50, 5),
            ("PRE_D1_002", "启动计费1号批次服务层采集", 55, 5),
            ("PRE_D1_003", "启动计费1号批次数据同步", 65, 10),
            ("PRE_D1_004", "核查计费1号批次接口层数据", 80, 5),
            ("PRE_D1_005", "核查计费1号批次服务层数据", 85, 5),
            ("PRE_D1_006", "通知各系统计费1号批次完成", 100, 1),
            ("PRE_D1_007", "启动收入1号批次接口层采集", 110, 5),
            ("PRE_D1_008", "启动收入1号批次服务层采集", 115, 5),
            ("PRE_D1_009", "启动收入1号批次数据同步", 125, 10),
            ("PRE_D1_010", "核查收入1号批次接口层数据", 140, 5),
            ("PRE_D1_011", "核查收入1号批次服务层数据", 145, 5),
            ("PRE_D1_012", "通知各系统收入1号批次完成", 160, 1),
            ("PRE_D1_013", "启动融合1号批次接口层采集", 170, 5),
            ("PRE_D1_014", "启动融合1号批次服务层采集", 175, 5),
            ("PRE_D1_015", "启动融合1号批次数据同步", 185, 10),
            ("PRE_D1_016", "核查融合1号批次接口层数据", 200, 5),
            ("PRE_D1_017", "核查融合1号批次服务层数据", 205, 5),
            ("PRE_D1_018", "通知各系统融合1号批次完成", 220, 1),
            ("PRE_D1_019", "启动余额账本整合层数据采集", 230, 10),
            ("PRE_D1_020", "启动余额账本汇总层数据采集", 250, 10),
            ("PRE_D1_021", "启动余额账本基础层数据采集", 270, 10),
            ("PRE_D1_022", "启动余额账本整合层数据", 295, 10),
            ("PRE_D1_023", "通知余额账本采集完成", 315, 1),
            ("PRE_D2_001", "启动2号批次接口层采集", 330, 5),
            ("PRE_D2_002", "启动2号批次服务层采集", 335, 5),
            ("PRE_D2_003", "启动2号批次数据同步", 345, 10),
            ("PRE_D2_004", "核查2号批次接口层数据", 360, 5),
            ("PRE_D2_005", "核查2号批次服务层数据", 365, 5),
            ("PRE_D2_006", "通知各系统2号批次完成", 380, 1),
            ("PRE_D3_001", "启动3号批次数据采集", 400, 10),
            ("PRE_D3_002", "启动3号批次数据同步", 420, 10),
            ("PRE_D3_003", "通知各系统3号批次完成", 440, 1),
        ]
        for i, (code, name, offset, dur) in enumerate(pre_tasks):
            deps = []
            if i > 0:
                deps.append(pre_tasks[i-1][0])
            task_defs.append((code, name, "前置作业", offset, offset + dur, deps))

        # ========== 用户作业 (USER) - ~34 tasks ==========
        user_tasks = [
            ("USER_D1_001", "月认领基础表波动量审核", 660, 30),
            ("USER_D1_002", "月认领收入波动量审核", 700, 30),
            ("USER_D1_003", "月认领产品波动量审核", 740, 30),
            ("USER_D1_004", "月认领用户波动量审核", 780, 30),
            ("USER_D1_005", "受理数据完整性稽核", 820, 20),
            ("USER_D1_006", "计费数据完整性稽核", 850, 20),
            ("USER_D1_007", "结算数据完整性稽核", 880, 20),
            ("USER_D1_008", "收入数据完整性稽核", 910, 20),
            ("USER_D1_009", "用户数据一致性比对", 940, 30),
            ("USER_D1_010", "产品数据一致性比对", 980, 30),
            ("USER_D1_011", "账务数据一致性比对", 1020, 30),
            ("USER_D1_012", "结算数据一致性比对", 1060, 30),
            ("USER_D1_013", "收入与计费交叉校验", 1100, 20),
            ("USER_D1_014", "用户与产品交叉校验", 1130, 20),
            ("USER_D1_015", "账务与结算交叉校验", 1160, 20),
            ("USER_D1_016", "月账数据质量评分", 1190, 15),
            ("USER_D1_017", "月账数据异常处理", 1210, 30),
            ("USER_D1_018", "月账数据复核确认", 1250, 15),
            ("USER_D1_019", "月账数据归档准备", 1270, 20),
            ("USER_D1_020", "月账数据正式归档", 1300, 15),
            ("USER_D2_001", "日认领基础表波动量审核", 1350, 20),
            ("USER_D2_002", "日认领收入波动量审核", 1380, 20),
            ("USER_D2_003", "日认领产品波动量审核", 1410, 20),
            ("USER_D2_004", "日认领用户波动量审核", 1440, 20),
            ("USER_D2_005", "日稽核数据完整性检查", 1470, 15),
            ("USER_D2_006", "日稽核数据一致性检查", 1490, 15),
            ("USER_D2_007", "日稽核异常处理", 1510, 20),
            ("USER_D2_008", "日稽核结果确认", 1540, 10),
            ("USER_D3_001", "月账数据汇总统计", 1560, 30),
            ("USER_D3_002", "月账数据报表生成", 1600, 30),
            ("USER_D3_003", "月账数据分析报告", 1640, 20),
            ("USER_D3_004", "月账数据质量报告", 1670, 20),
            ("USER_D3_005", "月账数据整改跟踪", 1700, 20),
            ("USER_D3_006", "月账数据最终确认", 1730, 10),
        ]
        for i, (code, name, offset, dur) in enumerate(user_tasks):
            deps = []
            if i > 0:
                deps.append(user_tasks[i-1][0])
            task_defs.append((code, name, "用户作业", offset, offset + dur, deps))

        # ========== 实收作业 (INCOME) - ~33 tasks ==========
        income_tasks = [
            ("INC_D1_001", "调度前置任务点击立即执行", 630, 5),
            ("INC_D1_002", "实收数据接口层采集", 645, 10),
            ("INC_D1_003", "实收数据服务层采集", 660, 10),
            ("INC_D1_004", "实收数据同步", 675, 10),
            ("INC_D1_005", "实收数据接口核查", 690, 5),
            ("INC_D1_006", "实收数据服务核查", 700, 5),
            ("INC_D1_007", "实收数据质量检查", 710, 10),
            ("INC_D1_008", "实收数据汇总计算", 730, 15),
            ("INC_D1_009", "实收数据异常处理", 750, 20),
            ("INC_D1_010", "实收数据稽核", 780, 15),
            ("INC_D1_011", "实收数据确认", 800, 5),
            ("INC_D2_001", "2号批次实收接口采集", 830, 10),
            ("INC_D2_002", "2号批次实收服务采集", 845, 10),
            ("INC_D2_003", "2号批次实收数据同步", 860, 10),
            ("INC_D2_004", "2号批次实收数据核查", 875, 10),
            ("INC_D2_005", "2号批次实收数据汇总", 890, 15),
            ("INC_D2_006", "2号批次实收数据稽核", 910, 15),
            ("INC_D2_007", "2号批次实收异常处理", 930, 15),
            ("INC_D2_008", "2号批次实收数据确认", 950, 5),
            ("INC_D3_001", "3号批次实收接口采集", 980, 10),
            ("INC_D3_002", "3号批次实收服务采集", 995, 10),
            ("INC_D3_003", "3号批次实收数据同步", 1010, 10),
            ("INC_D3_004", "3号批次实收数据核查", 1025, 10),
            ("INC_D3_005", "3号批次实收数据汇总", 1040, 15),
            ("INC_D3_006", "3号批次实收数据稽核", 1060, 15),
            ("INC_D3_007", "3号批次实收异常处理", 1080, 15),
            ("INC_D3_008", "3号批次实收综合确认", 1100, 10),
            ("INC_D4_001", "实收数据综合汇总", 1130, 20),
            ("INC_D4_002", "实收数据交叉校验", 1155, 15),
            ("INC_D4_003", "实收数据最终审核", 1175, 15),
            ("INC_D4_004", "实收异常综合处理", 1195, 20),
            ("INC_D4_005", "实收数据归档", 1220, 10),
            ("INC_D4_006", "实收数据完成确认", 1235, 5),
        ]
        for i, (code, name, offset, dur) in enumerate(income_tasks):
            deps = []
            if i > 0:
                deps.append(income_tasks[i-1][0])
            task_defs.append((code, name, "实收作业", offset, offset + dur, deps))

        # ========== 应收作业 (REC) - ~33 tasks ==========
        rec_tasks = [
            ("REC_D1_001", "D153的1号批次处理", 840, 30),
            ("REC_D1_002", "D154的1号批次处理", 880, 30),
            ("REC_D1_003", "D155的1号批次处理", 920, 30),
            ("REC_D1_004", "D156的1号批次处理", 960, 30),
            ("REC_D1_005", "1号应收批次汇总", 1000, 20),
            ("REC_D1_006", "1号应收批次稽核", 1030, 20),
            ("REC_D1_007", "1号应收批次异常处理", 1060, 30),
            ("REC_D1_008", "1号应收批次确认", 1100, 10),
            ("REC_D2_001", "D153的2号批次处理", 1140, 30),
            ("REC_D2_002", "D154的2号批次处理", 1180, 30),
            ("REC_D2_003", "D155的2号批次处理", 1220, 30),
            ("REC_D2_004", "D156的2号批次处理", 1260, 30),
            ("REC_D2_005", "2号应收批次汇总", 1300, 20),
            ("REC_D2_006", "2号应收批次稽核", 1330, 20),
            ("REC_D2_007", "2号应收批次异常处理", 1360, 30),
            ("REC_D2_008", "2号应收批次确认", 1400, 10),
            ("REC_D3_001", "D153的3号批次处理", 1430, 30),
            ("REC_D3_002", "D154的3号批次处理", 1470, 30),
            ("REC_D3_003", "D155的3号批次处理", 1510, 30),
            ("REC_D3_004", "D156的3号批次处理", 1550, 30),
            ("REC_D3_005", "3号应收批次汇总", 1590, 20),
            ("REC_D3_006", "3号应收批次稽核", 1620, 20),
            ("REC_D3_007", "3号应收批次异常处理", 1650, 30),
            ("REC_D3_008", "3号应收批次确认", 1690, 10),
            ("REC_D4_001", "应收数据综合对账", 1720, 20),
            ("REC_D4_002", "应收数据交叉稽核", 1750, 20),
            ("REC_D4_003", "应收异常综合处理", 1780, 20),
            ("REC_D4_004", "应收数据最终审核", 1810, 15),
            ("REC_D4_005", "应收数据质量评分", 1830, 15),
            ("REC_D4_006", "应收数据归档", 1850, 15),
            ("REC_D4_007", "应收数据综合报表", 1870, 20),
            ("REC_D4_008", "应收数据完成确认", 1900, 5),
        ]
        for i, (code, name, offset, dur) in enumerate(rec_tasks):
            deps = []
            if i > 0:
                deps.append(rec_tasks[i-1][0])
            task_defs.append((code, name, "应收作业", offset, offset + dur, deps))

        # ========== 集团作业 (GRP) - ~5 tasks ==========
        grp_tasks = [
            ("GRP_D1_001", "集团数据同步接口检查", 600, 15),
            ("GRP_D1_002", "集团报表数据上传", 650, 20),
            ("GRP_D1_003", "集团数据一致性校验", 800, 15),
            ("GRP_D2_001", "集团数据汇总上报", 1200, 20),
            ("GRP_D3_001", "集团考核数据准备", 1600, 30),
        ]
        for i, (code, name, offset, dur) in enumerate(grp_tasks):
            deps = []
            if i > 0:
                deps.append(grp_tasks[i-1][0])
            task_defs.append((code, name, "集团作业", offset, offset + dur, deps))

        # Build task objects with realistic status distribution
        tasks = []
        statuses_pool = ["未开始", "进行中", "已完成", "已完成", "已完成", "异常"]
        now = datetime.now()
        for idx, (code, name, work_type, start_offset, end_offset, deps) in enumerate(task_defs):
            planned_start = s + timedelta(minutes=start_offset)
            planned_end = s + timedelta(minutes=end_offset)

            # Determine status based on planned time vs now
            if planned_end < now:
                # Past tasks are mostly completed, some failed
                status = random.choice(["已完成", "已完成", "已完成", "已完成", "已完成", "已完成", "异常"])
            elif planned_start < now:
                # Currently active window
                status = random.choice(["进行中", "进行中", "已完成", "未开始"])
            else:
                # Future tasks
                status = random.choice(["未开始", "未开始", "未开始", "未开始", "未开始", "进行中"])

            actual_start = None
            actual_end = None
            if status == "已完成":
                actual_start = planned_start - timedelta(minutes=random.randint(0, 10))
                actual_end = planned_end - timedelta(minutes=random.randint(-5, 15))
            elif status == "进行中":
                actual_start = planned_start - timedelta(minutes=random.randint(0, 5))

            tasks.append({
                "task_id": idx + 1,
                "cycle_id": cycle_id,
                "task_code": code,
                "task_name": name,
                "work_type": work_type,
                "planned_start": planned_start.isoformat(),
                "planned_end": planned_end.isoformat(),
                "duration_minutes": end_offset - start_offset,
                "dependency_codes": ",".join(deps) if deps else None,
                "assignee": self.random_name(),
                "status": status,
                "actual_start": actual_start.isoformat() if actual_start else None,
                "actual_end": actual_end.isoformat() if actual_end else None,
                "remark": None,
            })

        return tasks

    def get_billing_progress_gantt(self, cycle_id="202601"):
        """Get billing progress Gantt chart data."""
        tasks = self._build_billing_tasks(cycle_id)
        base_time = None
        for t in tasks:
            if base_time is None or t["planned_start"] < base_time:
                base_time = t["planned_start"]
        return {
            "cycle": cycle_id,
            "base_time": base_time,
            "tasks": tasks,
        }

    def get_billing_progress_tasks(self, cycle_id="202601", page=1, page_size=200):
        """Get paginated billing progress tasks."""
        tasks = self._build_billing_tasks(cycle_id)
        return self.paginate(tasks, page, page_size)

    def create_billing_progress_task(self, cycle_id, data):
        """Create a billing progress task."""
        # Return a mock created task
        return {
            "task_id": 999,
            "cycle_id": cycle_id,
            "task_code": data.get("task_code", "NEW_001"),
            "task_name": data.get("task_name", "新任务"),
            "work_type": data.get("work_type", "前置作业"),
            "planned_start": data.get("planned_start"),
            "planned_end": data.get("planned_end"),
            "duration_minutes": data.get("duration_minutes", 0),
            "dependency_codes": data.get("dependency_codes"),
            "assignee": data.get("assignee"),
            "status": "未开始",
            "actual_start": None,
            "actual_end": None,
            "remark": None,
        }

    def update_billing_progress_task(self, task_id, data):
        """Update a billing progress task."""
        tasks = self._build_billing_tasks("202605")
        return self.update_item(tasks, task_id, data, id_field="task_id")

    def update_billing_progress_task_status(self, task_id, status, actual_end=None):
        """Update task status."""
        tasks = self._build_billing_tasks("202605")
        task = self.get_item(tasks, task_id, id_field="task_id")
        if task:
            task["status"] = status
            if actual_end:
                task["actual_end"] = actual_end
            if status == "进行中" and not task.get("actual_start"):
                task["actual_start"] = datetime.now().isoformat()
            if status == "已完成" and not task.get("actual_end"):
                task["actual_end"] = datetime.now().isoformat()
            return task
        # Return a mock success response if task not found (since mock generates fresh data each call)
        return {
            "task_id": task_id,
            "status": status,
            "actual_start": datetime.now().isoformat() if status in ("进行中", "已完成") else None,
            "actual_end": actual_end or (datetime.now().isoformat() if status == "已完成" else None),
            "message": "Mock update successful",
        }

    def generate_billing_brief(self, cycle_id="202601"):
        """Generate progress brief text."""
        tasks = self._build_billing_tasks(cycle_id)
        work_types = ["前置作业", "用户作业", "实收作业", "应收作业"]

        lines = [f"【月账进度 {cycle_id} {datetime.now().strftime('%m-%d %H:%M')}】"]

        total_all = len(tasks)
        completed_all = sum(1 for t in tasks if t["status"] == "已完成")
        running_all = sum(1 for t in tasks if t["status"] == "进行中")
        abnormal_all = sum(1 for t in tasks if t["status"] == "异常")

        lines.append(f"📊 总进度：{completed_all}/{total_all}（{round(completed_all/total_all*100)}%）")

        for wt in work_types:
            wt_tasks = [t for t in tasks if t["work_type"] == wt]
            total = len(wt_tasks)
            completed = sum(1 for t in wt_tasks if t["status"] == "已完成")
            running = sum(1 for t in wt_tasks if t["status"] == "进行中")
            abnormal = sum(1 for t in wt_tasks if t["status"] == "异常")
            pct = round(completed / total * 100) if total > 0 else 0
            icon = "✅" if pct == 100 else "🔄" if pct > 0 else "⏳"

            line = f"{icon}{wt}：已完成 {completed}/{total}（{pct}%）"
            if running > 0:
                running_names = [t["task_name"] for t in wt_tasks if t["status"] == "进行中"]
                line += f"\n   进行中：{', '.join(running_names[:3])}"
            if abnormal > 0:
                abnormal_names = [t["task_name"] for t in wt_tasks if t["status"] == "异常"]
                line += f"\n   ⚠️异常：{', '.join(abnormal_names[:2])}"
            lines.append(line)

        if abnormal_all > 0:
            lines.append(f"\n⚠️异常任务：共 {abnormal_all} 项，请及时处理")
        elif running_all > 0:
            lines.append(f"\n当前进度正常，{running_all} 项任务进行中。")
        else:
            lines.append(f"\n✅ 全部任务已完成！")

        return "\n".join(lines)

    def update_billing_progress_task_detail(self, task_id, data):
        """Update billing progress task details."""
        tasks = self._build_billing_tasks("202605")
        task = self.get_item(tasks, task_id, id_field="task_id")
        if task:
            task.update({k: v for k, v in data.items() if v is not None})
            return task
        return {
            "task_id": task_id,
            **{k: v for k, v in data.items() if v is not None},
            "message": "Mock update successful",
        }

    def delete_billing_progress_task(self, task_id):
        """Delete a billing progress task."""
        tasks = self._build_billing_tasks("202605")
        deleted = self.delete_item(tasks, task_id, id_field="task_id")
        if deleted:
            return {"success": True, "task_id": task_id}
        return {"success": True, "task_id": task_id, "message": "Mock delete successful"}

    def import_billing_progress_tasks(self, cycle_id, tasks_data):
        """Import billing progress tasks from Excel data."""
        imported = []
        for item in tasks_data:
            imported.append({
                "task_id": 2000 + len(imported),
                "cycle_id": cycle_id,
                "task_code": item.get("task_code", f"IMP_{len(imported)+1:04d}"),
                "task_name": item.get("task_name", "导入任务"),
                "work_type": item.get("work_type", "前置作业"),
                "planned_start": item.get("planned_start"),
                "planned_end": item.get("planned_end"),
                "duration_minutes": item.get("duration_minutes", 0),
                "dependency_codes": item.get("dependency_codes"),
                "assignee": item.get("assignee"),
                "status": "未开始",
                "actual_start": None,
                "actual_end": None,
                "remark": None,
            })
        return {"imported_count": len(imported), "tasks": imported}

# ==================== Common CRUD helpers ====================

    def create_item(self, items_list, data, id_field="id"):
        new_id = max((item[id_field] for item in items_list), default=0) + 1
        new_item = {id_field: new_id, **data}
        items_list.append(new_item)
        return new_item

    def update_item(self, items_list, item_id, data, id_field="id"):
        for item in items_list:
            if item[id_field] == item_id:
                item.update({k: v for k, v in data.items() if v is not None})
                return item
        return None

    def delete_item(self, items_list, item_id, id_field="id"):
        for i, item in enumerate(items_list):
            if item[id_field] == item_id:
                return items_list.pop(i)
        return None

    def get_item(self, items_list, item_id, id_field="id"):
        for item in items_list:
            if item[id_field] == item_id:
                return item
        return None
