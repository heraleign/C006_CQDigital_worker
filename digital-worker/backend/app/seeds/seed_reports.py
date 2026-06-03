#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seed script for ma_daily_report and ma_summary_report tables.

出账日报和报表发布数据生成。
根据月账进度和业务逻辑生成真实感数据。

Run: python -m app.seeds.seed_reports
"""
import json
import random
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.monthly import MaDailyReport, MaSummaryReport

random.seed(123)
NOW = datetime.now()
TODAY = NOW.date()


# ================================================================
# Helper: generate daily report content matching frontend shape
# ================================================================

def make_daily_content(report_date: date, day_index: int):
    """Generate JSON content for a daily report."""
    # Simulate gradual progress over the month
    days_into_month = report_date.day
    month_total_days = 30
    progress_pct = round(min(days_into_month / month_total_days * 100, 100), 1)

    # Receivable varies with progress
    rec_total = int(10000 + days_into_month * 150 + random.randint(-200, 200))
    rec_amount_val = rec_total * 980 + random.randint(-50000, 50000)
    rec_amount = f"{rec_amount_val:,}"
    rec_pass = round(97 + random.uniform(0, 3), 1)
    rec_anomalies = random.choices([0, 0, 1, 2, 3], weights=[3, 2, 2, 2, 1])[0]

    # Received data
    rcv_total = int(rec_total * random.uniform(0.75, 0.92))
    rcv_amount_val = rcv_total * 1020 + random.randint(-30000, 30000)
    rcv_amount = f"{rcv_amount_val:,}"
    rcv_pass = round(96 + random.uniform(0, 3.5), 1)
    rcv_anomalies = random.choices([0, 1, 2, 3, 4, 5], weights=[2, 3, 2, 2, 1, 1])[0]

    # Audit rules
    audit_total = 24 + random.randint(0, 8)
    audit_passed = audit_total - random.randint(0, max(1, audit_total // 15))
    audit_failed = audit_total - audit_passed
    audit_pass_rate = round(audit_passed / audit_total * 100, 1) if audit_total > 0 else 100

    # Alerts
    n_alerts = random.choices([0, 0, 1, 1, 2, 3], weights=[2, 3, 2, 2, 1, 1])[0]
    alert_pool = [
        ("high", "应收稽核-金额一致性检查发现{}条异常".format(random.randint(1, 5)),
         f"{random.randint(9,11)}:{random.randint(0,59):02d}"),
        ("high", "计费批价结果与预期偏差超过阈值({}%)".format(round(random.uniform(0.5, 3), 2)),
         f"{random.randint(10,12)}:{random.randint(0,59):02d}"),
        ("medium", "实收稽核-账龄分析逾期率超过阈值",
         f"{random.randint(9,11)}:{random.randint(0,59):02d}"),
        ("medium", "数据同步延迟超过{}分钟".format(random.randint(10, 60)),
         f"{random.randint(8,10)}:{random.randint(0,59):02d}"),
        ("medium", "用户数据完整性检查发现{}条缺失记录".format(random.randint(1, 20)),
         f"{random.randint(11,14)}:{random.randint(0,59):02d}"),
        ("low", "系统资源使用率超过{}%".format(random.randint(75, 92)),
         f"{random.randint(7,9)}:{random.randint(0,59):02d}"),
        ("low", "上游接口响应时间超过{}ms".format(random.randint(2000, 5000)),
         f"{random.randint(10,15)}:{random.randint(0,59):02d}"),
    ]
    alerts = [alert_pool[i % len(alert_pool)] for i in range(n_alerts)]
    alerts_json = [
        {"level": lv, "msg": msg, "time": tm}
        for lv, msg, tm in alerts
    ]

    # Conclusion varies
    if rec_anomalies > 2 or rcv_anomalies > 3:
        conclusion = "重点关注应收和实收稽核异常项，建议各责任人在今日内完成异常数据修复。整体进度可控，但质量需提升。"
    elif progress_pct > 80:
        conclusion = "月账处理已进入收尾阶段，各项指标达标。建议关注最终数据归档和报表生成的时效性，确保按时完成。"
    elif progress_pct > 50:
        conclusion = "月账处理过半，运行平稳。建议持续关注稽核异常项的及时处理，避免影响后续流程。"
    else:
        conclusion = "月账处理初期阶段，各项准备工作有序推进。建议按计划稳步推进各批次数据采集和处理。"

    t = random.choice(["运行平稳", "进度正常", "有序推进", "整体可控", "高效运行"])
    q = round(94 + random.uniform(0, 5.5), 1)
    summary = (
        f"本期出账处理整体{t}，共处理应收数据{rec_total}笔、实收数据{rcv_total}笔，"
        f"稽核通过率{audit_pass_rate}%，质量评分{q}分。"
        f"任务完成进度{progress_pct}%。"
    )

    return {
        "summary": summary,
        "receivable": {"total": rec_total, "amount": rec_amount, "passRate": str(rec_pass), "anomalies": rec_anomalies},
        "received": {"total": rcv_total, "amount": rcv_amount, "passRate": str(rcv_pass), "anomalies": rcv_anomalies},
        "audit": {"total": audit_total, "passed": audit_passed, "failed": audit_failed, "passRate": str(audit_pass_rate)},
        "alerts": alerts_json,
        "conclusion": conclusion,
    }


# ================================================================
# Daily data for multiple months
# ================================================================

def build_daily_reports():
    """Build daily report rows for recent months."""
    rows = []
    # Generate for 2026-04 and 2026-05 (full months) and 2026-06 (partial)
    for month, max_day in [("2026-04", 30), ("2026-05", 31), ("2026-06", min(TODAY.day, 3))]:
        if max_day < 1:
            continue
        # Generate ~70% of days (not every day has a report)
        report_days = sorted(random.sample(range(1, max_day + 1), max(1, int(max_day * 0.7))))
        for day in report_days:
            rd = date(2026, int(month.split("-")[1]), day)
            # Skip future dates
            if rd > TODAY:
                continue
            day_index = (rd - date(2026, 1, 1)).days
            title = f"{month.replace('-', '')}月{day:02d}日出账日报"
            content = make_daily_content(rd, day_index)
            content_obj = content
            completed = random.randint(15, 35)
            total = completed + random.randint(0, 5)
            exception_count = random.randint(0, 4)
            quality = round(94 + random.uniform(0, 5.5), 1)
            progress = round(min(day / 30 * 100, 100), 1)
            created_at = datetime.combine(rd, datetime.min.time()) + timedelta(
                hours=random.randint(17, 20), minutes=random.randint(0, 59)
            )
            rows.append(MaDailyReport(
                report_date=rd,
                account_month=month,
                title=title,
                content=content,
                summary=content_obj.get("summary", ""),
                task_completed=completed,
                task_total=total,
                exception_count=exception_count,
                quality_score=quality,
                progress=progress,
                ai_generated=random.choice([True, True, False]),
                status=random.choices(["published", "published", "published", "draft"], weights=[4, 3, 2, 1])[0],
                created_by=random.choice(["系统", "张三", "李四", "王五"]),
                created_at=created_at,
                updated_at=created_at + timedelta(minutes=random.randint(5, 60)),
            ))
    return rows


# ================================================================
# Summary reports
# ================================================================

def build_summary_reports():
    """Build summary report rows for recent months."""
    rows = []
    now = datetime.now()

    reports_config = [
        {
            "account_month": "2026-01",
            "report_name": "2026年1月账期月账结算报告",
            "overview": "1月账期顺利完成，整体运行平稳。本月共处理应收数据125,000笔，实收数据98,000笔。",
            "metrics": {"task_completion": 100, "data_quality": 98.5, "on_time_rate": 100, "exception_count": 2},
            "progress": {"total": 134, "completed": 134, "failed": 0},
            "problems": "本月无重大异常。个别批次数据同步存在轻微延迟，已及时处理。",
            "achievements": "提前完成全部出账任务，质量评分98.5分，连续3个月保持优秀水平。",
            "plan": "下月继续优化数据稽核流程，重点关注应收数据准确性。",
            "status": "published",
            "exception": False,
            "publisher": "赵明",
            "publish_time": datetime(2026, 2, 5, 10, 30, 0),
        },
        {
            "account_month": "2026-02",
            "report_name": "2026年2月账期月账结算报告",
            "overview": "2月账期处理完成，涉及春节假期，整体进度受一定影响，但通过加班调度确保按期完成。",
            "metrics": {"task_completion": 100, "data_quality": 97.2, "on_time_rate": 95, "exception_count": 5},
            "progress": {"total": 134, "completed": 134, "failed": 0},
            "problems": "春节假期导致部分人工审核环节延迟，通过加班完成。数据同步服务层出现2次超时重试。",
            "achievements": "克服假期影响完成全部出账任务，质量评分97.2分。",
            "plan": "优化节假日调度预案，增加自动重试机制覆盖率。",
            "status": "published",
            "exception": False,
            "publisher": "赵明",
            "publish_time": datetime(2026, 3, 3, 11, 0, 0),
        },
        {
            "account_month": "2026-03",
            "report_name": "2026年3月账期月账结算报告",
            "overview": "3月账期处理正常，各项指标达标。启动新的自动稽核规则，效率提升15%。",
            "metrics": {"task_completion": 100, "data_quality": 98.0, "on_time_rate": 98, "exception_count": 3},
            "progress": {"total": 134, "completed": 134, "failed": 0},
            "problems": "实收数据3号批次发现1笔金额异常，已追溯修正。应收稽核规则误报2条，已调整阈值。",
            "achievements": "自动稽核规则覆盖度提升至92%，稽核效率提升15%。",
            "plan": "继续完善自动稽核规则，降低误报率。",
            "status": "published",
            "exception": False,
            "publisher": "赵明",
            "publish_time": datetime(2026, 4, 2, 9, 45, 0),
        },
        {
            "account_month": "2026-04",
            "report_name": "2026年4月账期月账结算报告",
            "overview": "4月账期出现部分异常，主要涉及计费系统接口升级导致的兼容性问题。",
            "metrics": {"task_completion": 98, "data_quality": 95.1, "on_time_rate": 90, "exception_count": 8},
            "progress": {"total": 134, "completed": 131, "failed": 3},
            "problems": "计费系统接口升级导致1号批次数据采集延迟2小时，3项任务执行失败需手动补录。应收稽核发现3条数据不一致记录。",
            "achievements": "快速定位接口兼容性问题，及时切换备用采集通道，将影响降到最低。",
            "plan": "协调计费系统团队制定接口变更兼容方案，增加采集通道冗余。",
            "status": "published",
            "exception": True,
            "exception_detail": "计费接口升级导致3项任务失败，已手动补录完成。",
            "publisher": "赵明",
            "publish_time": datetime(2026, 5, 2, 14, 20, 0),
        },
        {
            "account_month": "2026-05",
            "report_name": "2026年5月账期月账结算报告",
            "overview": "5月账期已全部完成。本月采用新的并行调度策略，整体出账时间缩短8小时。",
            "metrics": {"task_completion": 100, "data_quality": 97.8, "on_time_rate": 100, "exception_count": 3},
            "progress": {"total": 134, "completed": 134, "failed": 0},
            "problems": "实收数据稽核发现2笔跨月对账差异，已确认为上月遗留问题并调整。集团数据上传接口偶发超时。",
            "achievements": "新并行调度策略成功应用，出账时间缩短8小时，效率提升25%。",
            "plan": "继续优化调度策略，推广至全部账期处理流程。",
            "status": "published",
            "exception": False,
            "publisher": "赵明",
            "publish_time": datetime(2026, 6, 1, 10, 0, 0),
        },
        {
            "account_month": "2026-06",
            "report_name": "2026年6月账期月账结算报告（进行中）",
            "overview": "6月账期正在处理中，当前进度30%。各项前置作业和用户作业有序推进。",
            "metrics": {"task_completion": 30, "data_quality": 98.2, "on_time_rate": 100, "exception_count": 1},
            "progress": {"total": 134, "completed": 40, "failed": 0},
            "problems": "暂无重大异常。用户数据波动量审核发现轻微波动，已标记关注。",
            "achievements": "正在进行中...",
            "plan": "按计划推进各批次数据采集和稽核工作。",
            "status": "draft",
            "exception": False,
            "publisher": None,
            "publish_time": None,
        },
    ]

    for cfg in reports_config:
        am = cfg["account_month"]
        rows.append(MaSummaryReport(
            account_month=am,
            title=cfg["report_name"],
            report_type="monthly",
            overview=cfg["overview"],
            key_metrics=cfg["metrics"],
            progress_summary=cfg["progress"],
            problem_analysis=cfg["problems"],
            achievements=cfg["achievements"],
            improvement_plan=cfg["plan"],
            attachments=[],
            status=cfg["status"],
            exception_flag=cfg.get("exception", False),
            exception_detail=cfg.get("exception_detail"),
            publisher=cfg["publisher"],
            publish_time=cfg.get("publish_time"),
            created_by="系统",
            created_at=now - timedelta(hours=random.randint(24, 168)),
            updated_at=now - timedelta(hours=random.randint(1, 48)),
        ))

    # Add a few more report types for variety
    extra_reports = [
        {
            "account_month": "2026-05",
            "title": "2026年5月账期营收分析报告",
            "report_type": "monthly",
            "overview": "基于5月账期数据生成的营收分析报告。",
            "status": "published",
            "metrics": {"total_revenue": 125000000, "growth_rate": 3.2, "arpu": 78.5},
            "progress": {"total": 50, "completed": 50, "failed": 0},
        },
        {
            "account_month": "2026-Q2",
            "title": "2026年第二季度数据质量报告",
            "report_type": "quarterly",
            "overview": "2026年Q2数据质量全面评估，覆盖4月、5月、6月账期数据。",
            "status": "draft",
            "metrics": {"avg_quality": 97.1, "total_exceptions": 16, "trend": "up"},
            "progress": {"total": 180, "completed": 160, "failed": 2},
        },
        {
            "account_month": "2026-06",
            "title": "出账日报-2026年6月3日发布版",
            "report_type": "daily",
            "overview": "6月3日出账进度汇总，今日为账期第3天。",
            "status": "scheduled",
            "metrics": {"daily_progress": 30, "tasks_today": 12, "completed_today": 8},
            "progress": {"total": 134, "completed": 40, "failed": 0},
        },
    ]

    for extra in extra_reports:
        rows.append(MaSummaryReport(
            account_month=extra["account_month"],
            title=extra["title"],
            report_type=extra["report_type"],
            overview=extra["overview"],
            key_metrics=extra["metrics"],
            progress_summary=extra["progress"],
            status=extra["status"],
            created_by="系统",
            created_at=now - timedelta(hours=random.randint(24, 168)),
            updated_at=now - timedelta(hours=random.randint(1, 48)),
        ))

    return rows


# ================================================================
# Main
# ================================================================

def seed():
    engine = create_engine(settings.DATABASE_URL_SYNC, echo=False)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        # Check existing counts
        existing_daily = db.execute(text("SELECT COUNT(*) FROM ma_daily_report")).scalar() or 0
        existing_summary = db.execute(text("SELECT COUNT(*) FROM ma_summary_report")).scalar() or 0
        print(f"Existing data: ma_daily_report={existing_daily} rows, ma_summary_report={existing_summary} rows")

        if existing_daily > 0:
            print("Clearing existing daily reports...")
            db.execute(text("DELETE FROM ma_daily_report"))
        if existing_summary > 0:
            print("Clearing existing summary reports...")
            db.execute(text("DELETE FROM ma_summary_report"))
        db.commit()

        # --- Seed daily reports ---
        print("Seeding ma_daily_report ...")
        dailies = build_daily_reports()
        for r in dailies:
            db.add(r)
        db.flush()
        print(f"  {len(dailies)} rows inserted.")

        # --- Seed summary reports ---
        print("Seeding ma_summary_report ...")
        summaries = build_summary_reports()
        for r in summaries:
            db.add(r)
        db.flush()
        print(f"  {len(summaries)} rows inserted.")

        db.commit()
        print("Done. All report data seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
