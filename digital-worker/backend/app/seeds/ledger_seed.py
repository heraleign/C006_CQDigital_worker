"""Seed script for ledger config tables."""
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session_factory
from app.models.monthly import (
    MaConfigStage,
    MaConfigMilestone,
    MaConfigWorkPlan,
    MaConfigTask,
)


STAGE_NAMES = ["用户作业", "前置作业", "实收作业", "应收作业", "集团作业"]

MILESTONE_NAMES = {
    0: ["用户作业-1号任务", "用户作业-2号任务", "用户作业-3号任务"],
    1: ["前置作业-1号任务", "前置作业-2号任务", "前置作业-3号任务", "前置作业-4号任务"],
    2: [
        "实收作业-1号任务", "实收作业-2号任务", "实收作业-3号任务",
        "实收作业-4号任务", "实收作业-5号任务", "实收作业-6号任务",
        "实收作业-7号任务", "实收作业-8号任务", "实收作业-9号任务",
    ],
    3: ["应收作业-1号任务", "应收作业-2号任务", "应收作业-3号任务"],
    4: ["集团作业-1号任务", "集团作业-2号任务", "集团作业-3号任务"],
}

PLAN_TEMPLATES = [
    ("截图计费1号批次接口层采集任务启动情况", "1日10:00", "人工", False),
    ("检查用户数据完整性并发送通知", "1日12:00", "数字员工", True),
    ("实收数据核对与稽核", "2日09:00", "数字员工", False),
    ("应收账单生成与校验", "3日08:00", "数字员工", False),
    ("集团数据汇总上报", "5日14:00", "数字员工", False),
]

TASK_TEMPLATES = [
    ("MANUAL_OP", "截图计费1号批次接口层采集任务启动情况"),
    ("TDP_TASK", "[TDP][统一处理][序号2251][月]INFBSN一号批次_1"),
    ("PUBLISH_MSG", "前置作业3：计费1号批次接口层采集任务已启动"),
    ("SQL_SCRIPT", "select count(*) from T_USER where status = 'ACTIVE'"),
    ("MANUAL_OP", "核对实收数据与银行对账单一致性"),
    ("TDP_TASK", "[TDP][统一处理][序号2252][月]INFBSN二号批次_1"),
    ("SQL_SCRIPT", "update T_BILL set status = 'PROCESSED' where bill_date = '2026-06-01'"),
    ("PUBLISH_MSG", "实收作业完成通知：本月实收数据已核对完毕"),
]


def _get_stage_status(stage_idx: int) -> str:
    if stage_idx < 2:
        return "completed"
    if stage_idx == 2:
        return "running"
    return "pending"


def _get_ms_status(stage_idx: int, ms_idx: int) -> str:
    if stage_idx < 2:
        return "completed"
    if stage_idx == 2:
        if ms_idx < 3:
            return "completed"
        if ms_idx == 3:
            return "running"
        return "pending"
    return "pending"


def _get_plan_status(ms_status: str, plan_idx: int) -> str:
    if ms_status == "completed":
        return "completed"
    if ms_status == "running":
        if plan_idx < 2:
            return "completed"
        if plan_idx == 2:
            return "running"
        return "pending"
    return "pending"


def _get_task_status(plan_status: str, task_idx: int) -> str:
    if plan_status == "completed":
        return "completed"
    if plan_status == "running":
        if task_idx < 2:
            return "completed"
        return "pending"
    return "pending"


def _random_time():
    base = datetime(2026, 6, 1, 9, 0, 0)
    offset = random.randint(0, 48)
    return base + timedelta(hours=offset)


async def seed_ledger_data(db: AsyncSession):
    """Populate ledger config tables with seed data."""
    # Check if already seeded
    from sqlalchemy import select, func
    result = await db.execute(select(func.count()).select_from(MaConfigStage))
    if result.scalar() or 0 > 0:
        print("Ledger data already seeded, skipping.")
        return

    random.seed(42)

    stages = []
    for s_idx, s_name in enumerate(STAGE_NAMES):
        status = _get_stage_status(s_idx)
        stage = MaConfigStage(
            stage_code=f"ST_{s_idx}",
            name=s_name,
            sort_order=s_idx + 1,
            status=status,
        )
        db.add(stage)
        stages.append(stage)

    await db.flush()

    milestones = []
    for s_idx, stage in enumerate(stages):
        ms_names = MILESTONE_NAMES.get(s_idx, [])
        for m_idx, ms_name in enumerate(ms_names):
            status = _get_ms_status(s_idx, m_idx)
            ms = MaConfigMilestone(
                stage_id=stage.id,
                milestone_code=f"MS_{s_idx}_{m_idx}",
                name=ms_name,
                sort_order=m_idx + 1,
                status=status,
                progress_pct=100.0 if status == "completed" else (50.0 if status == "running" else 0.0),
            )
            db.add(ms)
            milestones.append((s_idx, m_idx, ms))

    await db.flush()

    work_plans = []
    for s_idx, m_idx, ms in milestones:
        plan_count = random.randint(2, 5)
        for p_idx in range(plan_count):
            template = PLAN_TEMPLATES[(s_idx + m_idx + p_idx) % len(PLAN_TEMPLATES)]
            status = _get_plan_status(ms.status, p_idx)
            wp = MaConfigWorkPlan(
                milestone_id=ms.id,
                plan_code=f"PL_{s_idx}_{m_idx}_{p_idx}",
                seq_no=p_idx + 1,
                name=template[0],
                time_point=template[1],
                task_mode=template[2],
                is_system_task=template[3],
                status=status,
            )
            db.add(wp)
            work_plans.append((s_idx, m_idx, p_idx, wp))

    await db.flush()

    for s_idx, m_idx, p_idx, wp in work_plans:
        task_count = random.randint(1, 4)
        for t_idx in range(task_count):
            template = TASK_TEMPLATES[(s_idx + m_idx + p_idx + t_idx) % len(TASK_TEMPLATES)]
            status = _get_task_status(wp.status, t_idx)
            start_time = None
            end_time = None
            if status == "completed":
                start_time = _random_time()
                end_time = start_time + timedelta(minutes=random.randint(10, 120))
            elif status == "running":
                start_time = _random_time()

            task = MaConfigTask(
                plan_id=wp.id,
                task_code=f"TK_{s_idx}_{m_idx}_{p_idx}_{t_idx}",
                task_type=template[0],
                content=template[1],
                sort_order=t_idx + 1,
                status=status,
                start_time=start_time,
                end_time=end_time,
            )
            db.add(task)

    await db.commit()
    print("Ledger seed data inserted successfully.")


async def main():
    factory = get_session_factory()
    async with factory() as db:
        await seed_ledger_data(db)


if __name__ == "__main__":
    asyncio.run(main())
