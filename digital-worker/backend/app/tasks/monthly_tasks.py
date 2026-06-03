# -*- coding: utf-8 -*-
"""Monthly module scheduled tasks.
- Every 15 min: sync TDP_TASK status from scheduling system
- On 28th: generate next month instance
"""
import asyncio
from datetime import date, datetime, timedelta
from sqlalchemy import select
from app.database import get_session_factory
from app.models.monthly import MaTaskMonitor


async def sync_tdp_task_status():
    """Sync TDP_TASK status from scheduling system (every 15 min).
    Reads TDP_TASK type tasks in "running" or "pending" status,
    queries external scheduling system, and updates status.
    """
    factory = get_session_factory()
    if not factory:
        print("[sync_tdp] DB not available")
        return

    async with factory() as db:
        now = datetime.now()
        # Find active TDP_TASK tasks
        q = await db.execute(
            select(MaTaskMonitor).where(
                MaTaskMonitor.task_type == "TDP_TASK",
                MaTaskMonitor.status.in_(["pending", "running"]),
                MaTaskMonitor.account_month <= now.strftime("%Y-%m"),
            )
        )
        tasks = q.scalars().all()

        updated = 0
        for t in tasks:
            # TODO: Replace with actual TDP scheduling system API call
            # For now, simulate: if plan_start_time has passed, move to running
            if t.status == "pending" and t.plan_start_time and t.plan_start_time <= now:
                t.status = "running"
                t.actual_start_time = t.actual_start_time or now
                updated += 1
            # Simulate completion for tasks past their end time
            if t.status == "running" and t.plan_end_time and t.plan_end_time <= now:
                t.status = "completed"
                t.actual_end_time = t.actual_end_time or now
                t.progress = 100
                updated += 1

        if updated > 0:
            await db.commit()
            print(f"[sync_tdp] Updated {updated} TDP_TASK(s)")
        else:
            print(f"[sync_tdp] No TDP_TASK to update ({len(tasks)} checked)")


async def check_monthly_instance():
    """Check if today is ~28th, generate next month instance if so."""
    today = date.today()
    # On 27th-29th, generate next month instance
    if 27 <= today.day <= 29:
        from app.services.instance_generator import generate_next_month
        factory = get_session_factory()
        if not factory: return
        async with factory() as db:
            result = await generate_next_month(db)
            print(f"[instance_gen] {result}")
    else:
        print(f"[instance_gen] Today is {today.day}, not generation window (27-29)")


# Synchronous wrappers for scheduler
def run_sync_tdp():
    asyncio.run(sync_tdp_task_status())


def run_check_instance():
    asyncio.run(check_monthly_instance())