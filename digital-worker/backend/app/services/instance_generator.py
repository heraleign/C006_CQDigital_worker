# -*- coding: utf-8 -*-
"""Generate ma_task_monitor instances from config hierarchy."""
from datetime import datetime, timedelta, date
from sqlalchemy import select, func
from app.models.monthly import (
    MaMonthAccountConfig, MaTaskMonitor,
    MaConfigStage, MaConfigMilestone, MaConfigWorkPlan, MaConfigTask,
)


async def generate_instance(db, account_month: str) -> dict:
    """Generate instance data for a given account_month from config."""
    # Ensure account config exists
    q = await db.execute(select(MaMonthAccountConfig).where(MaMonthAccountConfig.account_month == account_month))
    cfg = q.scalar_one_or_none()
    if not cfg:
        raise ValueError(f"Account month {account_month} not configured")

    # Delete existing instance data for this month
    existing = await db.execute(select(MaTaskMonitor).where(MaTaskMonitor.account_month == account_month))
    for row in existing.scalars(): await db.delete(row)
    await db.commit()

    # Load config hierarchy
    stages_q = await db.execute(
        select(MaConfigStage).order_by(MaConfigStage.sort_order)
    )
    stages = stages_q.scalars().all()

    total = 0
    now = datetime.now()

    for stage in stages:
        ms_q = await db.execute(
            select(MaConfigMilestone).where(MaConfigMilestone.stage_id == stage.id).order_by(MaConfigMilestone.sort_order)
        )
        milestones = ms_q.scalars().all()

        for ms in milestones:
            wp_q = await db.execute(
                select(MaConfigWorkPlan).where(MaConfigWorkPlan.milestone_id == ms.id).order_by(MaConfigWorkPlan.seq_no)
            )
            plans = wp_q.scalars().all()

            for wp in plans:
                t_q = await db.execute(
                    select(MaConfigTask).where(MaConfigTask.plan_id == wp.id).order_by(MaConfigTask.sort_order)
                )
                tasks = t_q.scalars().all()

                for t in tasks:
                    mon = MaTaskMonitor(
                        account_month=account_month,
                        stage_code=stage.stage_code,
                        stage_name=stage.name,
                        milestone_code=ms.milestone_code,
                        milestone_name=ms.name,
                        plan_code=wp.plan_code,
                        plan_name=wp.name,
                        task_code=t.task_code,
                        task_name=t.content[:200] if t.content else None,
                        task_type=t.task_type,
                        sort_order=t.sort_order,
                        content=t.content,
                        time_point=wp.time_point,
                        task_mode=wp.task_mode,
                        is_system_task=wp.is_system_task,
                        priority="normal",
                        status="pending",
                        progress=0,
                        max_retries=3,
                        created_at=now,
                    )
                    db.add(mon)
                    total += 1

    await db.commit()
    print(f"Generated {total} tasks for {account_month}")

    # Update account config totals
    cfg.total_tasks = total
    cfg.status = "processing"
    await db.commit()

    return {"account_month": account_month, "total_tasks": total}


async def generate_next_month(db) -> dict:
    """Generate instance for the next month."""
    today = date.today()
    year = today.year
    month = today.month + 1
    if month > 12:
        month = 1
        year += 1
    am = f"{year}-{month:02d}"

    # Auto-create month config if not exists
    q = await db.execute(select(MaMonthAccountConfig).where(MaMonthAccountConfig.account_month == am))
    if not q.scalar_one_or_none():
        start = date(year, month, 1)
        if month == 12: ed = date(year, 12, 31)
        else: ed = date(year, month+1, 1) - timedelta(days=1)
        db.add(MaMonthAccountConfig(
            account_month=am, account_name=f"{am}月账期",
            start_date=start, end_date=ed,
            status="pending", created_by="system"
        ))
        await db.commit()

    return await generate_instance(db, am)