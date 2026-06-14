"""Add sys_tool_config table for skill/tool management.

Revision ID: 003
Revises: 002
Create Date: 2026-06-14
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sys_tool_config",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tool_code", sa.String(100), nullable=False, comment="技能编码"),
        sa.Column("tool_name", sa.String(200), nullable=False, comment="技能名称"),
        sa.Column("description", sa.Text(), nullable=True, comment="描述"),
        sa.Column("category", sa.String(50), nullable=True, comment="分类"),
        sa.Column("method", sa.String(10), nullable=True, comment="HTTP方法"),
        sa.Column("priority", sa.String(10), nullable=True, comment="优先级"),
        sa.Column("status", sa.String(20), server_default="active", comment="状态"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── Seed 46 skills ──────────────────────────────────────────
    now = datetime.now()
    skills = [
        ("dq/field/create",     "新增稽核指标",     "新增数据质量稽核指标字段",         "数据质量稽核", "POST", "P0"),
        ("dq/field/update",     "更新稽核指标",     "更新已有稽核指标字段配置",         "数据质量稽核", "PUT",  "P0"),
        ("dq/field/list",       "查询指标列表",     "查询所有稽核指标字段列表",         "数据质量稽核", "GET",  "P0"),
        ("dq/rule/ai-generate", "AI生成稽核规则",   "AI自动生成数据质量稽核规则",       "数据质量稽核", "POST", "P0"),
        ("dq/rule/confirm",     "确认稽核规则",     "确认或驳回AI生成的稽核规则",       "数据质量稽核", "POST", "P0"),
        ("dq/task/create",      "创建稽核任务",     "创建数据质量稽核执行任务",         "数据质量稽核", "POST", "P0"),
        ("dq/task/execute",     "执行稽核任务",     "执行已创建的数据质量稽核任务",     "数据质量稽核", "POST", "P0"),
        ("dq/alert/config",     "配置告警规则",     "配置数据质量告警规则和阈值",       "数据质量稽核", "POST", "P1"),
        ("dq/alert/notify",     "发送告警通知",     "发送数据质量告警通知消息",         "数据质量稽核", "POST", "P1"),
        ("dq/result/dashboard", "获取稽核看板",     "获取数据质量稽核结果看板数据",     "数据质量稽核", "GET",  "P1"),
        ("dq/report/generate",  "生成稽核报告",     "生成数据质量稽核报告文档",         "数据质量稽核", "POST", "P1"),
        ("rca/intent/recognize","识别问题意图",     "识别用户问题的根因分析意图类型",   "根因分析", "POST", "P0"),
        ("rca/task/trace",      "追溯依赖链路",     "追溯任务的上游依赖链路和阻塞点",   "根因分析", "POST", "P0"),
        ("rca/task/analyze",    "分析任务异常",     "分析任务的异常原因和错误类型",     "根因分析", "POST", "P0"),
        ("rca/file/check",      "检查文件状态",     "检查数据文件的到达状态和完整性",   "根因分析", "POST", "P0"),
        ("rca/metric/analyze",  "分析指标波动",     "分析业务指标的异常波动和多维下钻", "根因分析", "POST", "P1"),
        ("rca/case/match",      "匹配历史案例",     "根据问题描述匹配相似的历史根因案例","根因分析", "POST", "P0"),
        ("rca/case/deposit",    "沉淀案例",         "将分析结果沉淀为案例入库",         "根因分析", "POST", "P0"),
        ("rca/report/generate", "生成分析报告",     "生成结构化的根因分析报告",         "根因分析", "POST", "P0"),
        ("rca/report/push",     "推送分析报告",     "将分析报告推送到指定渠道",         "根因分析", "POST", "P0"),
        ("rca/history/list",    "查询分析历史",     "查询历史根因分析记录列表",         "根因分析", "GET",  "P1"),
        ("rca/feedback/submit", "提交用户反馈",     "提交用户对分析结果的反馈评价",     "根因分析", "POST", "P1"),
        ("ops/lineage/query",   "查询数据血缘",     "查询任务/表之间的血缘依赖关系",     "根因分析", "POST", "P0"),
        ("ops/alert/query",     "查询告警信息",     "查询系统告警信息和告警详情",       "根因分析", "POST", "P0"),
        ("ops/task/status",     "查询任务状态",     "查询数据运维任务的当前状态",       "根因分析", "POST", "P0"),
        ("ops/task/logs",       "获取任务日志",     "获取任务的执行日志详情",           "根因分析", "POST", "P0"),
        ("ma/monitor/progress", "获取月账进度",     "获取月账处理整体进度",             "月账数字员工", "GET", "P0"),
        ("ma/monitor/tasks",    "获取任务列表",     "获取月账处理任务列表",             "月账数字员工", "GET", "P0"),
        ("ma/audit/revenue",    "执行收入稽核",     "执行月账收入数据稽核",             "月账数字员工", "POST", "P0"),
        ("ma/audit/user",       "执行用户稽核",     "执行月账用户数据稽核",             "月账数字员工", "POST", "P0"),
        ("ma/audit/balance",    "执行平衡稽核",     "执行月账借贷平衡稽核",             "月账数字员工", "POST", "P0"),
        ("ma/adjustment/auto",  "自动调账",         "自动执行差异调账操作",             "月账数字员工", "POST", "P1"),
        ("ma/adjustment/approve","调账审批",        "审批调账申请单",                   "月账数字员工", "POST", "P1"),
        ("ma/report/daily",     "生成日报",         "生成月账处理日报",                 "月账数字员工", "POST", "P1"),
        ("ma/report/summary",   "生成总结报告",     "生成月账处理总结报告",             "月账数字员工", "POST", "P1"),
        ("ma/kpi/calculate",    "计算KPI指标",      "计算月账处理KPI指标数据",          "月账数字员工", "POST", "P1"),
        ("tdp/task/status",     "TDP任务状态查询",  "查询TDP调度平台任务状态",          "外部系统集成", "POST", "P0"),
        ("tdp/task/rerun",      "TDP任务重跑",      "触发TDP调度平台任务重跑",          "外部系统集成", "POST", "P0"),
        ("tdp/task/dependencies","TDP依赖查询",     "查询TDP任务依赖关系",              "外部系统集成", "POST", "P0"),
        ("dpaas/metadata/query","DPAAS元数据查询",  "查询DPAAS系统元数据信息",          "外部系统集成", "POST", "P0"),
        ("dpaas/lineage/query", "DPAAS血缘查询",    "查询DPAAS系统数据血缘关系",        "外部系统集成", "POST", "P0"),
        ("dpaas/model/info",    "DPAAS模型信息",    "查询DPAAS系统模型信息",            "外部系统集成", "POST", "P0"),
        ("aiops/alert/query",   "智能运维告警",     "查询智能运维平台告警信息",          "外部系统集成", "POST", "P0"),
        ("aiops/performance/query","性能指标查询",  "查询智能运维平台性能指标",          "外部系统集成", "POST", "P0"),
        ("qiming/message/push", "启明消息推送",     "向启明APP推送消息通知",            "外部系统集成", "POST", "P0"),
        ("qiming/feedback/receive","启明反馈接收",  "接收启明APP用户反馈",              "外部系统集成", "POST", "P0"),
    ]
    for code, name, desc, cat, method, priority in skills:
        op.execute(
            f"""INSERT INTO sys_tool_config
                (tool_code, tool_name, description, category, method, priority, status, created_at, updated_at)
                VALUES ('{code}', '{name}', '{desc}', '{cat}', '{method}', '{priority}', 'active', '{now}', '{now}')"""
        )


def downgrade() -> None:
    op.drop_table("sys_tool_config")
