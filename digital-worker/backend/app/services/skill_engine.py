"""Skill Engine — mock execution for all registered skills.

Each skill maps to one of the interfaces defined in the product spec.
Hermes Agent calls POST /hermes/execute-skill {skill_code, params}
and this engine returns structured mock data.
"""
import json
import random
from typing import Any

from app.utils.logger import logger


# ── helper for random data ──────────────────────────────────────────

def _rand_choice(items):
    return random.choice(items)

def _rand_date():
    return f"2026-{random.randint(1,6):02d}-{random.randint(1,28):02d}"

def _rand_time():
    return f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"

def _rand_datetime():
    return f"{_rand_date()}T{_rand_time()}:00"



class SkillEngine:
    """Stateless skill executor — each method maps to one skill_code."""

    @staticmethod
    def execute(skill_code: str, params: dict | None = None) -> dict:
        """Dispatch to the correct mock handler by skill_code."""
        handler = _HANDLERS.get(skill_code)
        if not handler:
            return {"error": f"Unknown skill: {skill_code}", "success": False}
        try:
            return handler(params or {})
        except Exception as e:
            logger.error(f"Skill {skill_code} execution failed: {e}")
            return {"error": str(e), "success": False}


# ══════════════════════════════════════════════════════════════════════
# 8.2.1  数据质量稽核  handlers
# ══════════════════════════════════════════════════════════════════════

def _dq_field_create(params):
    return {"success": True, "data": {"field_id": f"FLD_{random.randint(10000,99999)}", "status": "created", "field_name": params.get("field_name", "")}}


def _dq_field_update(params):
    return {"success": True, "data": {"field_id": params.get("field_id"), "status": "updated"}}


def _dq_field_list(params):
    items = []
    for i in range(1, 13):
        items.append({
            "field_id": f"FLD_{i:04d}",
            "field_name": _rand_choice(["用户ID", "手机号", "身份证", "账户余额", "套餐金额", "通话时长", "流量使用", "短信条数", "入网时间", "离网时间", "品牌", "ARPU值"]),
            "datasource": _rand_choice(["CRM", "BOSS", "BILLING", "ORDERING"]),
            "data_type": _rand_choice(["string", "int", "float", "date"]),
            "status": _rand_choice(["active", "active", "active", "inactive"]),
            "created_at": _rand_datetime(),
        })
    return {"success": True, "data": {"items": items, "total": len(items)}}



def _dq_rule_ai_generate(params):
    rules = []
    templates = ["非空校验", "唯一性校验", "格式校验", "范围校验", "枚举值校验", "逻辑校验", "一致性校验", "时效性校验"]
    for i, t in enumerate(templates[:random.randint(4, 8)]):
        rules.append({
            "rule_id": f"RULE_{i+1:04d}",
            "rule_name": f"{params.get('table_name', 'TABLE')}{t}",
            "rule_type": _rand_choice(["null_check", "duplicate", "format", "range", "logic"]),
            "severity": _rand_choice(["high", "high", "medium", "low"]),
            "ai_generated": True,
        })
    return {"success": True, "data": {"rules": rules, "total": len(rules)}}


def _dq_rule_confirm(params):
    return {"success": True, "data": {"rule_id": params.get("rule_id"), "status": "confirmed"}}


def _dq_task_create(params):
    return {"success": True, "data": {"task_id": f"DQ_TASK_{random.randint(1000,9999)}", "status": "created"}}


def _dq_task_execute(params):
    return {"success": True, "data": {"task_id": params.get("task_id"), "execution_id": f"EXEC_{random.randint(10000,99999)}", "status": "running", "progress": 0}}


def _dq_alert_config(params):
    return {"success": True, "data": {"alert_id": f"ALT_{random.randint(1000,9999)}", "status": "configured"}}


def _dq_alert_notify(params):
    return {"success": True, "data": {"notified": True, "channel": _rand_choice(["system", "email", "dingtalk"]), "receivers": params.get("receivers", [])}}


def _dq_result_dashboard(params):
    return {
        "success": True,
        "data": {
            "overall_score": round(random.uniform(85, 99), 1),
            "total_checks": random.randint(500, 2000),
            "passed": random.randint(450, 1900),
            "failed": random.randint(5, 100),
            "by_severity": {"high": random.randint(1, 10), "medium": random.randint(5, 30), "low": random.randint(10, 60)},
            "trend": [{"date": f"2026-{random.randint(1,6):02d}-{d:02d}", "score": round(random.uniform(85, 99), 1)} for d in range(1, 8)],
        }
    }


def _dq_report_generate(params):
    return {"success": True, "data": {"report_id": f"DQ_RPT_{random.randint(10000,99999)}", "status": "generated", "format": "pdf"}}



# ══════════════════════════════════════════════════════════════════════
# 8.2.2  根因分析  handlers
# ══════════════════════════════════════════════════════════════════════

def _rca_intent_recognize(params):
    return {
        "success": True,
        "data": {
            "intent": _rand_choice(["task_delay", "metric_anomaly", "data_quality", "system_fault"]),
            "confidence": round(random.uniform(0.85, 0.99), 2),
            "problem_type": _rand_choice(["任务延迟", "指标波动", "数据异常", "系统故障"]),
            "suggested_path": _rand_choice(["上游依赖追溯", "多维下钻分析", "数据质量检查", "日志分析"]),
        }
    }


def _rca_task_trace(params):
    task_id = params.get("task_id", "UNKNOWN")
    depth = random.randint(1, 3)
    upstream = []
    for i in range(depth):
        upstream.append({
            "task_id": f"UPSTREAM_{i+1}_{random.randint(100,999)}",
            "task_name": f"上游任务_{i+1}",
            "status": _rand_choice(["completed", "completed", "failed", "waiting"]),
            "duration": f"{random.randint(1,60)}分钟",
        })
    return {
        "success": True,
        "data": {
            "task_id": task_id,
            "status": _rand_choice(["waiting", "running", "failed", "delayed"]),
            "upstream_dependencies": upstream,
            "downstream_impact": [f"下游任务_{i}" for i in range(1, random.randint(1, 4))],
            "trace_chain": " → ".join([t["task_id"] for t in upstream] + [task_id]),
        }
    }


def _rca_task_analyze(params):
    return {
        "success": True,
        "data": {
            "task_id": params.get("task_id", ""),
            "analysis_result": _rand_choice([
                "上游文件未按时送达",
                "数据源接口超时",
                "资源竞争导致任务排队",
                "数据量突增超出处理能力",
                "依赖任务执行失败",
            ]),
            "error_type": _rand_choice(["FILE_NOT_ARRIVED", "TIMEOUT", "RESOURCE_CONTENTION", "DATA_SURGE", "DEPENDENCY_FAILURE"]),
            "severity": _rand_choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
            "confidence": round(random.uniform(0.8, 0.99), 2),
        }
    }


def _rca_file_check(params):
    return {
        "success": True,
        "data": {
            "file_path": params.get("file_path", "/data/unknown.dat"),
            "exists": random.random() > 0.3,
            "file_size_mb": round(random.uniform(10, 5000), 2),
            "expected_arrival": "05:30",
            "delay_minutes": random.randint(0, 300),
            "last_7_days_on_time_rate": f"{round(random.uniform(85, 100), 1)}%",
        }
    }


def _rca_metric_analyze(params):
    return {
        "success": True,
        "data": {
            "metric_name": params.get("metric_name", "新增用户数"),
            "baseline": 1000,
            "current": random.randint(1200, 3000),
            "change_pct": f"+{random.randint(10, 200)}%",
            "dimensions": {
                "time": _rand_choice(["14:00-15:00", "09:00-10:00", "20:00-21:00"]),
                "region": _rand_choice(["渝北区", "江北区", "南岸区", "渝中区"]),
                "channel": _rand_choice(["线上渠道", "线下营业厅", "代理商"]),
                "product": _rand_choice(["0元体验卡", "99元套餐", "199元套餐"]),
            },
            "anomaly_type": _rand_choice(["CHANNEL_FRAUD", "PROMOTION_EFFECT", "DATA_CALIBRATION", "SYSTEM_ERROR"]),
        }
    }



def _rca_case_match(params):
    cases = []
    for i in range(1, random.randint(3, 6)):
        cases.append({
            "case_id": f"CASE_{i:04d}",
            "case_title": _rand_choice([
                "集团上传产品实例表延迟", "新增用户数异常波动",
                "账单数据同步失败", "收入稽核不平",
                "客户信息缺失", "月账处理超时",
            ]),
            "similarity": round(random.uniform(0.6, 0.98), 2),
            "root_cause": _rand_choice(["源文件未送达", "接口超时", "数据量突增", "任务依赖死锁"]),
            "solution": _rand_choice(["联系上游确认文件", "重启任务", "扩展资源", "调整依赖顺序"]),
        })
    return {"success": True, "data": {"matches": cases, "total": len(cases)}}


def _rca_case_deposit(params):
    return {"success": True, "data": {"case_id": f"CASE_{random.randint(10000,99999)}", "status": "deposited"}}


def _rca_report_generate(params):
    return {
        "success": True,
        "data": {
            "report_id": f"RCA_RPT_{random.randint(10000,99999)}",
            "task_id": params.get("task_id", ""),
            "root_cause": _rand_choice(["源文件未送达", "接口超时", "数据量突增", "渠道虚假发展"]),
            "confidence": round(random.uniform(0.85, 0.99), 2),
            "suggestions": [
                "联系上游确认数据文件送达时间",
                "增加接口超时监控和自动重试机制",
                "设置数据量突增告警阈值",
            ],
            "generated_at": _rand_datetime(),
        }
    }


def _rca_report_push(params):
    return {"success": True, "data": {"report_id": params.get("report_id"), "pushed": True, "channels": ["量子密信", "启明APP"]}}


def _rca_history_list(params):
    items = []
    for i in range(1, 11):
        items.append({
            "analysis_id": f"AR_{i:04d}",
            "problem_description": _rand_choice(["任务延迟", "指标异常", "数据质量", "系统告警"]),
            "analysis_status": _rand_choice(["completed", "completed", "completed", "failed"]),
            "root_cause_result": _rand_choice(["源文件未送达", "接口超时", "渠道虚假发展", "数据量突增"]),
            "created_at": _rand_datetime(),
        })
    return {"success": True, "data": {"items": items, "total": len(items)}}


def _rca_feedback_submit(params):
    return {"success": True, "data": {"feedback_id": f"FB_{random.randint(10000,99999)}", "status": "submitted"}}



# ── OPS sub-handlers (under 根因分析) ──────────────────────────────

def _ops_lineage_query(params):
    nodes = []
    edges = []
    for i in range(1, 9):
        nodes.append({"id": f"TASK_{i}", "name": f"任务_{i}", "type": _rand_choice(["etl", "sync", "collect", "report"])})
    for _ in range(random.randint(5, 10)):
        src = _rand_choice([n["id"] for n in nodes])
        tgt = _rand_choice([n["id"] for n in nodes])
        if src != tgt:
            edges.append({"source": src, "target": tgt, "relation": "depends_on"})
    return {"success": True, "data": {"nodes": nodes, "edges": edges}}


def _ops_alert_query(params):
    items = []
    for i in range(1, 9):
        items.append({
            "alert_id": f"ALT_{i:04d}",
            "alert_type": _rand_choice(["task_failure", "data_delay", "metric_anomaly", "system_warning"]),
            "severity": _rand_choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
            "title": _rand_choice(["任务执行失败", "数据同步延迟", "指标异常告警", "磁盘空间不足"]),
            "status": _rand_choice(["open", "acknowledged", "resolved"]),
            "created_at": _rand_datetime(),
        })
    return {"success": True, "data": {"items": items, "total": len(items)}}


def _ops_task_status(params):
    return {
        "success": True,
        "data": {
            "task_id": params.get("task_id", ""),
            "status": _rand_choice(["running", "completed", "failed", "waiting", "delayed"]),
            "progress": random.randint(0, 100),
            "start_time": _rand_datetime(),
            "estimated_end": _rand_datetime(),
            "duration": f"{random.randint(1, 180)}分钟",
        }
    }


def _ops_task_logs(params):
    items = []
    for i in range(1, random.randint(5, 15)):
        items.append({
            "line": i,
            "timestamp": _rand_datetime(),
            "level": _rand_choice(["INFO", "INFO", "INFO", "WARN", "ERROR"]),
            "message": _rand_choice([
                "开始执行任务", "读取配置文件", "连接数据源成功",
                "数据抽取完成", "数据转换开始", "数据加载完成",
                "连接超时，重试第1次", "连接超时，重试第2次",
                "任务执行失败：文件未找到", "内存使用率85%",
            ]),
        })
    return {"success": True, "data": {"task_id": params.get("task_id", ""), "logs": items, "total": len(items)}}



# ══════════════════════════════════════════════════════════════════════
# 8.2.3  月账数字员工  handlers
# ══════════════════════════════════════════════════════════════════════

def _ma_monitor_progress(params):
    total = random.randint(80, 150)
    completed = random.randint(40, total - 5)
    return {
        "success": True,
        "data": {
            "acct_month": params.get("acct_month", "202606"),
            "total_tasks": total,
            "completed_tasks": completed,
            "progress_pct": round(completed / total * 100, 1),
            "running_tasks": random.randint(3, 15),
            "failed_tasks": random.randint(0, 5),
            "estimated_completion": _rand_datetime(),
        }
    }


def _ma_monitor_tasks(params):
    items = []
    for i in range(1, 16):
        items.append({
            "task_id": f"MA_TASK_{i:04d}",
            "task_name": _rand_choice([
                "出账数据准备", "收入数据稽核", "用户数据稽核",
                "平衡稽核", "调账处理", "报表生成",
                "KPI计算", "日报生成", "月报汇总",
            ]),
            "stage": _rand_choice(["数据准备", "数据稽核", "调账", "报表生成", "发布"]),
            "status": _rand_choice(["pending", "running", "completed", "running", "completed", "failed"]),
            "progress_pct": random.randint(0, 100),
            "start_time": _rand_datetime(),
        })
    return {"success": True, "data": {"items": items, "total": len(items)}}


def _ma_audit_revenue(params):
    return {
        "success": True,
        "data": {
            "audit_id": f"REV_AUDIT_{random.randint(10000,99999)}",
            "total_revenue": round(random.uniform(1e8, 1e9), 2),
            "anomaly_count": random.randint(0, 50),
            "anomaly_amount": round(random.uniform(0, 1e6), 2),
            "status": _rand_choice(["passed", "passed", "warning", "failed"]),
        }
    }


def _ma_audit_user(params):
    return {
        "success": True,
        "data": {
            "audit_id": f"USR_AUDIT_{random.randint(10000,99999)}",
            "total_users": random.randint(500000, 2000000),
            "anomaly_count": random.randint(0, 5000),
            "anomaly_rate": f"{round(random.uniform(0, 0.5), 3)}%",
            "issues": _rand_choice(["重复用户", "身份证异常", "手机号格式错误", "无"]),
        }
    }


def _ma_audit_balance(params):
    return {
        "success": True,
        "data": {
            "audit_id": f"BAL_AUDIT_{random.randint(10000,99999)}",
            "balance_diff": round(random.uniform(-1e6, 1e6), 2),
            "is_balanced": random.random() > 0.2,
            "details": {"应收": round(random.uniform(1e8, 1e9), 2), "实收": round(random.uniform(1e8, 1e9), 2)},
        }
    }



def _ma_adjustment_auto(params):
    return {
        "success": True,
        "data": {
            "adjustment_id": f"ADJ_{random.randint(10000,99999)}",
            "amount": round(random.uniform(-50000, 50000), 2),
            "reason": _rand_choice(["收入差异调账", "用户数据修正", "系统误差调整"]),
            "status": "auto_adjusted",
        }
    }


def _ma_adjustment_approve(params):
    return {"success": True, "data": {"adjustment_id": params.get("adjustment_id"), "status": "approved"}}


def _ma_report_daily(params):
    return {
        "success": True,
        "data": {
            "report_id": f"DAILY_{random.randint(10000,99999)}",
            "report_date": params.get("report_date", _rand_date()),
            "summary": _rand_choice(["月账处理进度正常", "存在少量稽核差异", "所有任务已完成"]),
            "task_completion": {"total": 42, "completed": random.randint(35, 42), "failed": random.randint(0, 3)},
            "quality_metrics": {"overall_score": round(random.uniform(90, 99), 1)},
        }
    }


def _ma_report_summary(params):
    return {
        "success": True,
        "data": {
            "report_id": f"SUMMARY_{random.randint(10000,99999)}",
            "acct_month": params.get("acct_month", "202606"),
            "total_revenue": round(random.uniform(5e8, 5e9), 2),
            "user_count": random.randint(500000, 2000000),
            "completion_rate": f"{round(random.uniform(85, 100), 1)}%",
            "key_issues": [_rand_choice(["收入差异", "用户数据异常", "平衡不平"]), _rand_choice(["调账完成", "稽核通过", "报表已发布"])],
        }
    }


def _ma_kpi_calculate(params):
    return {
        "success": True,
        "data": {
            "period": params.get("period", "202606"),
            "kpis": {
                "completion_rate": round(random.uniform(85, 100), 1),
                "accuracy_rate": round(random.uniform(95, 100), 2),
                "timeliness_rate": round(random.uniform(90, 100), 1),
                "auto_adjustment_rate": round(random.uniform(60, 95), 1),
                "report_generation_time": f"{random.randint(5, 60)}分钟",
            }
        }
    }



# ══════════════════════════════════════════════════════════════════════
# 8.2.4  外部系统集成  handlers
# ══════════════════════════════════════════════════════════════════════

def _tdp_task_status(params):
    return {
        "success": True,
        "data": {
            "task_id": params.get("task_id", ""),
            "status": _rand_choice(["running", "completed", "failed", "pending"]),
            "schedule_time": _rand_datetime(),
            "actual_start": _rand_datetime(),
            "duration_sec": random.randint(30, 3600),
            "exit_code": _rand_choice(["0", "0", "0", "-1"]),
        }
    }


def _tdp_task_rerun(params):
    return {"success": True, "data": {"task_id": params.get("task_id"), "new_execution_id": f"EXEC_{random.randint(10000,99999)}", "status": "rerun_submitted"}}


def _tdp_task_dependencies(params):
    items = []
    for i in range(1, random.randint(3, 8)):
        items.append({
            "task_id": f"DEP_{i:04d}",
            "task_name": f"依赖任务_{i}",
            "status": _rand_choice(["completed", "completed", "completed", "failed", "waiting"]),
            "is_blocking": random.random() > 0.7,
        })
    return {"success": True, "data": {"task_id": params.get("task_id", ""), "dependencies": items}}


def _dpaas_metadata_query(params):
    return {
        "success": True,
        "data": {
            "table_name": params.get("table_name", "UNKNOWN"),
            "schema_name": params.get("schema_name", "public"),
            "columns": [
                {"name": "id", "type": "bigint", "nullable": False, "primary_key": True},
                {"name": "user_id", "type": "varchar(64)", "nullable": False},
                {"name": "user_name", "type": "varchar(128)", "nullable": True},
                {"name": "created_at", "type": "timestamp", "nullable": False},
                {"name": "updated_at", "type": "timestamp", "nullable": True},
            ],
            "row_count": random.randint(10000, 5000000),
            "storage_size_mb": round(random.uniform(100, 5000), 2),
        }
    }


def _dpaas_lineage_query(params):
    nodes = []
    for i in range(1, 7):
        nodes.append({"id": f"TBL_{i}", "name": f"表_{i}", "type": _rand_choice(["source", "etl", "target", "report"])})
    edges = []
    for _ in range(random.randint(3, 8)):
        src = _rand_choice([n["id"] for n in nodes])
        tgt = _rand_choice([n["id"] for n in nodes])
        if src != tgt:
            edges.append({"source": src, "target": tgt, "relation": _rand_choice(["etl", "sync", "view"])})
    return {"success": True, "data": {"nodes": nodes, "edges": edges, "total_nodes": len(nodes)}}


def _dpaas_model_info(params):
    return {
        "success": True,
        "data": {
            "model_name": params.get("model_name", "UNKNOWN"),
            "model_type": _rand_choice(["物理模型", "逻辑模型", "维度模型", "事实表"]),
            "fields": random.randint(5, 50),
            "description": f"{params.get('model_name', '模型')}的描述信息",
            "update_frequency": _rand_choice(["实时", "小时级", "天级", "月级"]),
        }
    }


def _aiops_alert_query(params):
    return _ops_alert_query(params)


def _aiops_performance_query(params):
    return {
        "success": True,
        "data": {
            "metric": params.get("metric", "cpu_usage"),
            "current_value": round(random.uniform(10, 95), 1),
            "avg_value_7d": round(random.uniform(30, 70), 1),
            "peak_value": round(random.uniform(80, 99), 1),
            "status": _rand_choice(["normal", "warning", "critical"]),
            "trend": [{"time": f"{h:02d}:00", "value": round(random.uniform(20, 90), 1)} for h in range(0, 24, 2)],
        }
    }


def _qiming_message_push(params):
    return {"success": True, "data": {"message_id": f"MSG_{random.randint(10000,99999)}", "pushed": True, "channel": "启明APP"}}


def _qiming_feedback_receive(params):
    return {"success": True, "data": {"feedback_id": f"FB_{random.randint(10000,99999)}", "received": True}}



# ══════════════════════════════════════════════════════════════════════
# Handler registry — maps skill_code → handler function
# ══════════════════════════════════════════════════════════════════════

_HANDLERS: dict[str, callable] = {
    # 8.2.1 数据质量稽核
    "dq/field/create": _dq_field_create,
    "dq/field/update": _dq_field_update,
    "dq/field/list": _dq_field_list,
    "dq/rule/ai-generate": _dq_rule_ai_generate,
    "dq/rule/confirm": _dq_rule_confirm,
    "dq/task/create": _dq_task_create,
    "dq/task/execute": _dq_task_execute,
    "dq/alert/config": _dq_alert_config,
    "dq/alert/notify": _dq_alert_notify,
    "dq/result/dashboard": _dq_result_dashboard,
    "dq/report/generate": _dq_report_generate,
    # 8.2.2 根因分析
    "rca/intent/recognize": _rca_intent_recognize,
    "rca/task/trace": _rca_task_trace,
    "rca/task/analyze": _rca_task_analyze,
    "rca/file/check": _rca_file_check,
    "rca/metric/analyze": _rca_metric_analyze,
    "rca/case/match": _rca_case_match,
    "rca/case/deposit": _rca_case_deposit,
    "rca/report/generate": _rca_report_generate,
    "rca/report/push": _rca_report_push,
    "rca/history/list": _rca_history_list,
    "rca/feedback/submit": _rca_feedback_submit,
    "ops/lineage/query": _ops_lineage_query,
    "ops/alert/query": _ops_alert_query,
    "ops/task/status": _ops_task_status,
    "ops/task/logs": _ops_task_logs,
    # 8.2.3 月账数字员工
    "ma/monitor/progress": _ma_monitor_progress,
    "ma/monitor/tasks": _ma_monitor_tasks,
    "ma/audit/revenue": _ma_audit_revenue,
    "ma/audit/user": _ma_audit_user,
    "ma/audit/balance": _ma_audit_balance,
    "ma/adjustment/auto": _ma_adjustment_auto,
    "ma/adjustment/approve": _ma_adjustment_approve,
    "ma/report/daily": _ma_report_daily,
    "ma/report/summary": _ma_report_summary,
    "ma/kpi/calculate": _ma_kpi_calculate,
    # 8.2.4 外部系统集成
    "tdp/task/status": _tdp_task_status,
    "tdp/task/rerun": _tdp_task_rerun,
    "tdp/task/dependencies": _tdp_task_dependencies,
    "dpaas/metadata/query": _dpaas_metadata_query,
    "dpaas/lineage/query": _dpaas_lineage_query,
    "dpaas/model/info": _dpaas_model_info,
    "aiops/alert/query": _aiops_alert_query,
    "aiops/performance/query": _aiops_performance_query,
    "qiming/message/push": _qiming_message_push,
    "qiming/feedback/receive": _qiming_feedback_receive,
}


# Convenience singleton
skill_engine = SkillEngine()
