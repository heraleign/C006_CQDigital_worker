"""Ledger service for monthly 4-level hierarchy."""
from typing import Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monthly import (
    MaConfigStage,
    MaConfigMilestone,
    MaConfigWorkPlan,
    MaConfigTask,
)


class LedgerService:
    """Service for ledger config and overview operations."""

    # ==================== Stage CRUD ====================

    async def list_stages(self, db: AsyncSession, page: int = 1, page_size: int = 200):
        offset = (page - 1) * page_size
        total_result = await db.execute(select(func.count()).select_from(MaConfigStage))
        total = total_result.scalar() or 0

        result = await db.execute(
            select(MaConfigStage)
            .order_by(MaConfigStage.sort_order)
            .offset(offset)
            .limit(page_size)
        )
        items = result.scalars().all()
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return {
            "items": [self._stage_to_dict(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_stage(self, db: AsyncSession, stage_id: int):
        result = await db.execute(select(MaConfigStage).where(MaConfigStage.id == stage_id))
        item = result.scalar_one_or_none()
        return self._stage_to_dict(item) if item else None

    async def create_stage(self, db: AsyncSession, data: dict):
        item = MaConfigStage(**data)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return self._stage_to_dict(item)

    async def update_stage(self, db: AsyncSession, stage_id: int, data: dict):
        result = await db.execute(select(MaConfigStage).where(MaConfigStage.id == stage_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        for key, value in data.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return self._stage_to_dict(item)

    async def delete_stage(self, db: AsyncSession, stage_id: int):
        result = await db.execute(select(MaConfigStage).where(MaConfigStage.id == stage_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        await db.delete(item)
        await db.commit()
        return self._stage_to_dict(item)

    # ==================== Milestone CRUD ====================

    async def list_milestones(self, db: AsyncSession, stage_id: Optional[int] = None, page: int = 1, page_size: int = 200):
        offset = (page - 1) * page_size
        query = select(MaConfigMilestone)
        if stage_id is not None:
            query = query.where(MaConfigMilestone.stage_id == stage_id)

        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar() or 0

        result = await db.execute(
            query.order_by(MaConfigMilestone.sort_order).offset(offset).limit(page_size)
        )
        items = result.scalars().all()
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return {
            "items": [self._milestone_to_dict(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_milestone(self, db: AsyncSession, milestone_id: int):
        result = await db.execute(select(MaConfigMilestone).where(MaConfigMilestone.id == milestone_id))
        item = result.scalar_one_or_none()
        return self._milestone_to_dict(item) if item else None

    async def create_milestone(self, db: AsyncSession, data: dict):
        item = MaConfigMilestone(**data)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return self._milestone_to_dict(item)

    async def update_milestone(self, db: AsyncSession, milestone_id: int, data: dict):
        result = await db.execute(select(MaConfigMilestone).where(MaConfigMilestone.id == milestone_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        for key, value in data.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return self._milestone_to_dict(item)

    async def delete_milestone(self, db: AsyncSession, milestone_id: int):
        result = await db.execute(select(MaConfigMilestone).where(MaConfigMilestone.id == milestone_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        await db.delete(item)
        await db.commit()
        return self._milestone_to_dict(item)

    # ==================== Work Plan CRUD ====================

    async def list_work_plans(self, db: AsyncSession, milestone_id: Optional[int] = None, page: int = 1, page_size: int = 200):
        offset = (page - 1) * page_size
        query = select(MaConfigWorkPlan)
        if milestone_id is not None:
            query = query.where(MaConfigWorkPlan.milestone_id == milestone_id)

        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar() or 0

        result = await db.execute(
            query.order_by(MaConfigWorkPlan.seq_no).offset(offset).limit(page_size)
        )
        items = result.scalars().all()
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return {
            "items": [self._work_plan_to_dict(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_work_plan(self, db: AsyncSession, plan_id: int):
        result = await db.execute(select(MaConfigWorkPlan).where(MaConfigWorkPlan.id == plan_id))
        item = result.scalar_one_or_none()
        return self._work_plan_to_dict(item) if item else None

    async def create_work_plan(self, db: AsyncSession, data: dict):
        item = MaConfigWorkPlan(**data)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return self._work_plan_to_dict(item)

    async def update_work_plan(self, db: AsyncSession, plan_id: int, data: dict):
        result = await db.execute(select(MaConfigWorkPlan).where(MaConfigWorkPlan.id == plan_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        for key, value in data.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return self._work_plan_to_dict(item)

    async def delete_work_plan(self, db: AsyncSession, plan_id: int):
        result = await db.execute(select(MaConfigWorkPlan).where(MaConfigWorkPlan.id == plan_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        await db.delete(item)
        await db.commit()
        return self._work_plan_to_dict(item)

    # ==================== Task CRUD ====================

    async def list_tasks(self, db: AsyncSession, plan_id: Optional[int] = None, page: int = 1, page_size: int = 200):
        offset = (page - 1) * page_size
        query = select(MaConfigTask)
        if plan_id is not None:
            query = query.where(MaConfigTask.plan_id == plan_id)

        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar() or 0

        result = await db.execute(
            query.order_by(MaConfigTask.sort_order).offset(offset).limit(page_size)
        )
        items = result.scalars().all()
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return {
            "items": [self._task_to_dict(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_task(self, db: AsyncSession, task_id: int):
        result = await db.execute(select(MaConfigTask).where(MaConfigTask.id == task_id))
        item = result.scalar_one_or_none()
        return self._task_to_dict(item) if item else None

    async def create_task(self, db: AsyncSession, data: dict):
        item = MaConfigTask(**data)
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return self._task_to_dict(item)

    async def update_task(self, db: AsyncSession, task_id: int, data: dict):
        result = await db.execute(select(MaConfigTask).where(MaConfigTask.id == task_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        return await self._apply_task_update(db, item, data)

    async def update_task_by_code(self, db: AsyncSession, task_code: str, data: dict):
        """Update a config task by its task_code (string).
        Falls back to MaTaskMonitor when no matching config task exists
        (e.g. when the overview is built from runtime monitor data).
        """
        # First try: MaConfigTask
        result = await db.execute(select(MaConfigTask).where(MaConfigTask.task_code == task_code))
        item = result.scalar_one_or_none()
        if item:
            return await self._apply_task_update(db, item, data)

        # Fallback: update MaTaskMonitor directly (monitor-based overview)
        # A task_code may appear in multiple months — update all matching records
        from app.models.monthly import MaTaskMonitor
        m_result = await db.execute(select(MaTaskMonitor).where(MaTaskMonitor.task_code == task_code))
        monitor_items = m_result.scalars().all()
        if not monitor_items:
            return None
        return await self._apply_monitor_update(db, monitor_items, data)

    async def _apply_monitor_update(self, db: AsyncSession, items: list, data: dict) -> Optional[dict]:
        """Directly update MaTaskMonitor records (fallback path, multiple months)."""
        if not items:
            return None
        now = datetime.now()
        status = data.get("status")
        for item in items:
            if status:
                item.status = status
            if status == "completed":
                if item.actual_end_time is None:
                    item.actual_end_time = now
                if item.actual_start_time is None:
                    item.actual_start_time = now
                item.progress = 100
            elif status == "running":
                if item.actual_start_time is None:
                    item.actual_start_time = now
                item.progress = max(item.progress or 0, 50)
            elif status == "manual_skipped":
                if item.actual_end_time is None:
                    item.actual_end_time = now
                item.progress = 100
            elif status == "pending":
                item.progress = 0
            for key, value in data.items():
                if value is not None and hasattr(item, key):
                    setattr(item, key, value)
        await db.commit()
        await db.refresh(items[0])
        return self._monitor_to_dict(items[0])

    async def _apply_task_update(self, db: AsyncSession, item: MaConfigTask, data: dict) -> Optional[dict]:
        """Common task update logic shared by update_task and update_task_by_code."""
        now = datetime.now()

        for key, value in data.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        # If status changed to completed and no end_time, set it now
        if data.get("status") == "completed" and item.end_time is None:
            item.end_time = now
        await db.commit()
        await db.refresh(item)
        # Cascade completion times up the config hierarchy
        await self._cascade_completion_times(db, item)
        # Sync status to MaTaskMonitor so the ledger overview reflects the change
        await self._sync_task_status_to_monitor(db, item.task_code, data, now)
        return self._task_to_dict(item)

    async def _sync_task_status_to_monitor(self, db: AsyncSession, task_code: str, data: dict, now: datetime):
        """Sync status/end_time from config task update to runtime MaTaskMonitor records."""
        from app.models.monthly import MaTaskMonitor
        q = await db.execute(
            select(MaTaskMonitor).where(MaTaskMonitor.task_code == task_code)
        )
        monitors = q.scalars().all()
        updated = False
        status = data.get("status")
        for mon in monitors:
            if status:
                mon.status = status
            if status == "completed":
                if mon.actual_end_time is None:
                    mon.actual_end_time = now
                if mon.actual_start_time is None:
                    mon.actual_start_time = now
                mon.progress = 100
            elif status == "running":
                if mon.actual_start_time is None:
                    mon.actual_start_time = now
                mon.progress = max(mon.progress or 0, 50)
            elif status == "manual_skipped":
                if mon.actual_end_time is None:
                    mon.actual_end_time = now
                mon.progress = 100
            elif status == "pending":
                mon.progress = 0
            updated = True
        if updated:
            await db.commit()

    async def delete_task(self, db: AsyncSession, task_id: int):
        result = await db.execute(select(MaConfigTask).where(MaConfigTask.id == task_id))
        item = result.scalar_one_or_none()
        if not item:
            return None
        await db.delete(item)
        await db.commit()
        return self._task_to_dict(item)

    # ==================== Ledger Overview ====================

    async def get_ledger_overview(self, db: AsyncSession, account_month: Optional[str] = None):
        """Fetch 4-level ledger hierarchy from MaTaskMonitor.
        Falls back to config tables (MaConfigStage→Milestone→WorkPlan→Task)
        when no monitor data exists for the given month.
        """

        # ── Normalise account_month: "202606" → "2026-06" ──
        am = account_month or datetime.now().strftime("%Y-%m")
        if am and len(am) == 6 and '-' not in am:
            am = f"{am[:4]}-{am[4:]}"

        # ── Try runtime data (MaTaskMonitor) first ──
        from app.models.monthly import MaTaskMonitor
        q = await db.execute(
            select(MaTaskMonitor)
            .where(MaTaskMonitor.account_month == am)
            .order_by(MaTaskMonitor.stage_code, MaTaskMonitor.milestone_code,
                      MaTaskMonitor.plan_code, MaTaskMonitor.sort_order)
        )
        all_tasks = q.scalars().all()

        if all_tasks:
            return self._build_overview_from_monitor(all_tasks, am)

        # ── Fallback to config hierarchy when no runtime data exists ──
        return await self._build_overview_from_config(db, am)

    def _build_overview_from_monitor(self, all_tasks: list, account_month: str) -> dict:
        """Build overview from MaTaskMonitor records (runtime data)."""
        # Group by stage → milestone → plan
        stage_map = {}
        for t in all_tasks:
            sk = t.stage_code or t.task_type or "unknown"
            if sk not in stage_map:
                stage_map[sk] = {"stage_id": sk, "name": t.stage_name or t.task_type or sk,
                    "sort_order": len(stage_map) + 1, "status": "pending",
                    "progress_pct": 0, "milestones": {}}
            mk = t.milestone_code or "milestone"
            if mk not in stage_map[sk]["milestones"]:
                stage_map[sk]["milestones"][mk] = {"milestone_id": mk,
                    "name": t.milestone_name or t.stage_name or sk, "sort_order": len(stage_map[sk]["milestones"]) + 1,
                    "status": "pending", "progress_pct": 0, "work_plans": {}}
            pk = t.plan_code or "plan"
            if pk not in stage_map[sk]["milestones"][mk]["work_plans"]:
                stage_map[sk]["milestones"][mk]["work_plans"][pk] = {"plan_id": pk,
                    "name": t.plan_name or t.milestone_name or sk, "seq_no": len(stage_map[sk]["milestones"][mk]["work_plans"]) + 1,
                    "time_point": t.time_point, "status": "pending", "tasks": []}
            stage_map[sk]["milestones"][mk]["work_plans"][pk]["tasks"].append(
                self._task_to_monitor_dict(t))

        # Compute status/progress for each level
        total_tasks = 0
        completed_tasks = 0
        stages_json = []
        for sk in sorted(stage_map.keys()):
            st = stage_map[sk]
            ms_list = []
            for mk in sorted(st["milestones"].keys()):
                ms = st["milestones"][mk]
                wp_list = []
                for pk in sorted(ms["work_plans"].keys()):
                    wp = ms["work_plans"][pk]
                    ts = wp["tasks"]
                    t_statuses = [t["status"] for t in ts]
                    t_comp = sum(1 for s in t_statuses if s == "completed")
                    total_tasks += len(ts)
                    completed_tasks += t_comp
                    wp["status"] = self._aggregate_status(t_statuses)
                    starts = [t.get("start_time") for t in ts if t.get("start_time")]
                    ends = [t.get("end_time") for t in ts if t.get("end_time")]
                    wp["start_time"] = min(starts) if starts else None
                    wp["end_time"] = max(ends) if ends else None
                    wp_list.append(wp)
                wp_statuses = [w["status"] for w in wp_list]
                ms["status"] = self._aggregate_status(wp_statuses)
                ms["progress_pct"] = round(sum(1 for s in wp_statuses if s == "completed") / len(wp_statuses) * 100) if wp_statuses else 0
                ms["work_plans"] = wp_list
                mst = [w["start_time"] for w in wp_list if w.get("start_time")]
                mse = [w["end_time"] for w in wp_list if w.get("end_time")]
                ms["start_time"] = min(mst) if mst else None
                ms["end_time"] = max(mse) if mse else None
                ms_list.append(ms)
            ms_statuses = [m["status"] for m in ms_list]
            st["status"] = self._aggregate_status(ms_statuses)
            st["progress_pct"] = round(sum(1 for s in ms_statuses if s == "completed") / len(ms_statuses) * 100) if ms_statuses else 0
            st["milestones"] = ms_list
            st["milestone_count"] = len(ms_list)
            st["completed_milestone_count"] = sum(1 for s in ms_statuses if s == "completed")
            sst = [m["start_time"] for m in ms_list if m.get("start_time")]
            sse = [m["end_time"] for m in ms_list if m.get("end_time")]
            st["start_time"] = min(sst) if sst else None
            st["end_time"] = max(sse) if sse else None
            stages_json.append(st)

        overall = round(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        now = datetime.now()
        summary = self._compute_progress_summary(stages_json, account_month, now)
        return {
            "acct_month": account_month, "total_stages": len(stages_json),
            "completed_stages": sum(1 for s in stages_json if s["status"] == "completed"),
            "total_milestones": sum(s["milestone_count"] for s in stages_json),
            "completed_milestones": sum(s["completed_milestone_count"] for s in stages_json),
            "total_work_plans": sum(len(m["work_plans"]) for s in stages_json for m in s["milestones"]),
            "completed_work_plans": sum(sum(1 for w in m["work_plans"] if w["status"] == "completed") for s in stages_json for m in s["milestones"]),
            "total_tasks": total_tasks, "completed_tasks": completed_tasks,
            "overall_progress_pct": overall, "stages": stages_json,
            "progress_summary": summary,
        }

    async def _build_overview_from_config(self, db: AsyncSession, account_month: str) -> dict:
        """Build overview from config hierarchy tables when no runtime data exists."""
        stages_q = await db.execute(
            select(MaConfigStage).order_by(MaConfigStage.sort_order)
        )
        stages_db = stages_q.scalars().all()

        total_tasks = 0
        completed_tasks = 0
        stages_json = []

        for st in stages_db:
            ms_q = await db.execute(
                select(MaConfigMilestone)
                .where(MaConfigMilestone.stage_id == st.id)
                .order_by(MaConfigMilestone.sort_order)
            )
            milestones_db = ms_q.scalars().all()

            ms_list = []
            for ms in milestones_db:
                wp_q = await db.execute(
                    select(MaConfigWorkPlan)
                    .where(MaConfigWorkPlan.milestone_id == ms.id)
                    .order_by(MaConfigWorkPlan.seq_no)
                )
                plans_db = wp_q.scalars().all()

                wp_list = []
                for wp in plans_db:
                    t_q = await db.execute(
                        select(MaConfigTask)
                        .where(MaConfigTask.plan_id == wp.id)
                        .order_by(MaConfigTask.sort_order)
                    )
                    tasks_db = t_q.scalars().all()

                    t_list = []
                    for t in tasks_db:
                        t_list.append({
                            "task_id": t.task_code,
                            "task_type": t.task_type,
                            "content": t.content,
                            "sort_order": t.sort_order,
                            "status": t.status,
                            "start_time": t.start_time.isoformat() if t.start_time else None,
                            "end_time": t.end_time.isoformat() if t.end_time else None,
                        })
                        total_tasks += 1
                        if t.status == "completed":
                            completed_tasks += 1

                    t_statuses = [tx["status"] for tx in t_list]
                    wp_starts = [tx["start_time"] for tx in t_list if tx.get("start_time")]
                    wp_ends = [tx["end_time"] for tx in t_list if tx.get("end_time")]

                    wp_list.append({
                        "plan_id": wp.plan_code,
                        "name": wp.name,
                        "seq_no": wp.seq_no,
                        "time_point": wp.time_point,
                        "task_mode": wp.task_mode,
                        "is_system_task": wp.is_system_task,
                        "status": self._aggregate_status(t_statuses),
                        "start_time": min(wp_starts) if wp_starts else None,
                        "end_time": max(wp_ends) if wp_ends else None,
                        "tasks": t_list,
                    })

                wp_statuses = [w["status"] for w in wp_list]
                ms_starts = [w["start_time"] for w in wp_list if w.get("start_time")]
                ms_ends = [w["end_time"] for w in wp_list if w.get("end_time")]

                ms_list.append({
                    "milestone_id": ms.milestone_code,
                    "name": ms.name,
                    "sort_order": ms.sort_order,
                    "status": self._aggregate_status(wp_statuses),
                    "progress_pct": round(sum(1 for s in wp_statuses if s == "completed") / len(wp_statuses) * 100) if wp_statuses else 0,
                    "start_time": min(ms_starts) if ms_starts else None,
                    "end_time": max(ms_ends) if ms_ends else None,
                    "work_plans": wp_list,
                })

            ms_statuses = [m["status"] for m in ms_list]
            st_starts = [m["start_time"] for m in ms_list if m.get("start_time")]
            st_ends = [m["end_time"] for m in ms_list if m.get("end_time")]

            stages_json.append({
                "stage_id": st.stage_code,
                "name": st.name,
                "sort_order": st.sort_order,
                "status": self._aggregate_status(ms_statuses),
                "progress_pct": round(sum(1 for s in ms_statuses if s == "completed") / len(ms_statuses) * 100) if ms_statuses else 0,
                "start_time": min(st_starts) if st_starts else None,
                "end_time": max(st_ends) if st_ends else None,
                "milestone_count": len(ms_list),
                "completed_milestone_count": sum(1 for s in ms_statuses if s == "completed"),
                "milestones": ms_list,
            })

        overall = round(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        return {
            "acct_month": account_month,
            "total_stages": len(stages_json),
            "completed_stages": sum(1 for s in stages_json if s["status"] == "completed"),
            "total_milestones": sum(s["milestone_count"] for s in stages_json),
            "completed_milestones": sum(s["completed_milestone_count"] for s in stages_json),
            "total_work_plans": sum(len(m["work_plans"]) for s in stages_json for m in s["milestones"]),
            "completed_work_plans": sum(sum(1 for w in m["work_plans"] if w["status"] == "completed") for s in stages_json for m in s["milestones"]),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overall_progress_pct": overall,
            "stages": stages_json,
            "progress_summary": self._compute_progress_summary(stages_json, account_month, datetime.now()),
        }

    @staticmethod
    def _compute_progress_summary(stages: list, account_month: str, now: datetime) -> dict:
        """Compute expected vs actual progress by comparing time_point with current time.

        time_point format: 'X日HH:MM' (e.g. '1日10:00').
        Parsed relative to account_month to get a deadline datetime.
        """
        import re
        total_expected = 0
        actual_completed = 0
        delayed = 0
        alerts = 0

        # Parse account_month: "2026-06" → year=2026, month=6
        parts = account_month.split("-")
        base_year = int(parts[0])
        base_month = int(parts[1])

        for stage in stages:
            for ms in stage.get("milestones", []):
                for wp in ms.get("work_plans", []):
                    tp = wp.get("time_point")
                    if not tp:
                        continue
                    # Parse "N日HH:MM" → datetime(year, month, day, hour, minute)
                    m = re.match(r"(\d+)日(\d+):(\d+)", tp)
                    if not m:
                        continue
                    day, hour, minute = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    try:
                        deadline = datetime(base_year, base_month, day, hour, minute)
                    except ValueError:
                        continue

                    # Tasks in this work_plan
                    tasks = wp.get("tasks", [])
                    task_statuses = [t["status"] for t in tasks]
                    all_completed = all(s == "completed" for s in task_statuses)

                    # If deadline has passed, these tasks should ideally be done
                    if deadline <= now:
                        total_expected += len(tasks)
                        actual_completed += sum(1 for s in task_statuses if s == "completed")
                        if not all_completed:
                            delayed += len([s for s in task_statuses if s != "completed"])
                        alerts += sum(1 for s in task_statuses if s == "failed")

        return {
            "total_expected": total_expected,
            "actual_completed": actual_completed,
            "delayed": delayed,
            "alerts": alerts,
        }

    @staticmethod
    def _task_to_monitor_dict(t):
        """Convert MaTaskMonitor ORM row to dict. Status stays in English (前端负责翻译).
        Falls back content → task_name when content is null (monitor data often lacks content).
        """
        content = t.content or t.task_name or ""
        return {
            "task_id": t.task_code or str(t.id),
            "task_type": t.task_type or t.stage_name or "",
            "content": content,
            "sort_order": t.sort_order or 0,
            "status": t.status or "pending",
            "start_time": t.actual_start_time.isoformat() if t.actual_start_time else None,
            "end_time": t.actual_end_time.isoformat() if t.actual_end_time else None,
        }

    @staticmethod
    def _aggregate_status(child_statuses: list) -> str:
        """Aggregate child statuses into parent status.

        Priority (highest first): failed > running > paused > manual_skipped > completed > pending.
        - If ALL children are completed → completed
        - Otherwise pick the highest-priority active status among children.
        """
        if not child_statuses:
            return "pending"
        # All completed → completed
        if all(s == "completed" for s in child_statuses):
            return "completed"
        # Check active statuses in priority order
        for status in ("failed", "running", "paused", "manual_skipped"):
            if any(s == status for s in child_statuses):
                return status
        return "pending"

    async def _cascade_completion_times(self, db: AsyncSession, task: MaConfigTask):
        """Recalculate completed_at for work_plan, milestone, and stage
        based on the latest completed child.
        """
        # --- Work Plan ---
        wp_result = await db.execute(
            select(MaConfigWorkPlan).where(MaConfigWorkPlan.id == task.plan_id)
        )
        work_plan = wp_result.scalar_one_or_none()
        if not work_plan:
            return

        # Find latest completed task under this work plan
        t_result = await db.execute(
            select(MaConfigTask)
            .where(MaConfigTask.plan_id == work_plan.id, MaConfigTask.status == "completed")
            .order_by(MaConfigTask.sort_order.desc())
        )
        latest_task = t_result.scalars().first()
        work_plan.completed_at = latest_task.end_time if latest_task else None
        await db.commit()

        # --- Milestone ---
        ms_result = await db.execute(
            select(MaConfigMilestone).where(MaConfigMilestone.id == work_plan.milestone_id)
        )
        milestone = ms_result.scalar_one_or_none()
        if not milestone:
            return

        wp_result2 = await db.execute(
            select(MaConfigWorkPlan)
            .where(MaConfigWorkPlan.milestone_id == milestone.id, MaConfigWorkPlan.status == "completed")
            .order_by(MaConfigWorkPlan.seq_no.desc())
        )
        latest_wp = wp_result2.scalars().first()
        milestone.completed_at = latest_wp.completed_at if latest_wp else None
        await db.commit()

        # --- Stage ---
        st_result = await db.execute(
            select(MaConfigStage).where(MaConfigStage.id == milestone.stage_id)
        )
        stage = st_result.scalar_one_or_none()
        if not stage:
            return

        ms_result2 = await db.execute(
            select(MaConfigMilestone)
            .where(MaConfigMilestone.stage_id == stage.id, MaConfigMilestone.status == "completed")
            .order_by(MaConfigMilestone.sort_order.desc())
        )
        latest_ms = ms_result2.scalars().first()
        stage.completed_at = latest_ms.completed_at if latest_ms else None
        await db.commit()

    # ==================== Helpers ====================

    @staticmethod
    def _stage_to_dict(item: MaConfigStage):
        return {
            "id": item.id,
            "stage_code": item.stage_code,
            "name": item.name,
            "sort_order": item.sort_order,
            "status": item.status,
            "completed_at": item.completed_at.isoformat() if item.completed_at else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }

    @staticmethod
    def _milestone_to_dict(item: MaConfigMilestone):
        return {
            "id": item.id,
            "stage_id": item.stage_id,
            "milestone_code": item.milestone_code,
            "name": item.name,
            "sort_order": item.sort_order,
            "status": item.status,
            "progress_pct": item.progress_pct,
            "completed_at": item.completed_at.isoformat() if item.completed_at else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }

    @staticmethod
    def _work_plan_to_dict(item: MaConfigWorkPlan):
        return {
            "id": item.id,
            "milestone_id": item.milestone_id,
            "plan_code": item.plan_code,
            "seq_no": item.seq_no,
            "name": item.name,
            "time_point": item.time_point,
            "task_mode": item.task_mode,
            "is_system_task": item.is_system_task,
            "status": item.status,
            "completed_at": item.completed_at.isoformat() if item.completed_at else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }

    @staticmethod
    def _task_to_dict(item: MaConfigTask):
        return {
            "id": item.id,
            "plan_id": item.plan_id,
            "task_code": item.task_code,
            "task_type": item.task_type,
            "content": item.content,
            "sort_order": item.sort_order,
            "status": item.status,
            "start_time": item.start_time.isoformat() if item.start_time else None,
            "end_time": item.end_time.isoformat() if item.end_time else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        }

    @staticmethod
    def _monitor_to_dict(item) -> dict:
        """Convert MaTaskMonitor ORM row to dict (fallback update response)."""
        return {
            "id": item.id,
            "task_code": item.task_code,
            "task_name": item.task_name,
            "status": item.status,
            "progress": item.progress,
            "actual_start_time": item.actual_start_time.isoformat() if item.actual_start_time else None,
            "actual_end_time": item.actual_end_time.isoformat() if item.actual_end_time else None,
        }
