"""Ledger service for monthly 4-level hierarchy."""
from typing import Optional
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
        for key, value in data.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        # If status changed to completed and no end_time, set it now
        if data.get("status") == "completed" and item.end_time is None:
            from datetime import datetime
            item.end_time = datetime.now()
        await db.commit()
        await db.refresh(item)
        # Cascade completion times up the hierarchy
        await self._cascade_completion_times(db, item)
        return self._task_to_dict(item)

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
        """Fetch flattened overview from ma_task_monitor (single table)."""
        from app.models.monthly import MaTaskMonitor
        from datetime import datetime
        am = account_month or datetime.now().strftime("%Y-%m")

        q = await db.execute(
            select(MaTaskMonitor)
            .where(MaTaskMonitor.account_month == am)
            .order_by(MaTaskMonitor.stage_code, MaTaskMonitor.milestone_code,
                      MaTaskMonitor.plan_code, MaTaskMonitor.sort_order)
        )
        all_tasks = q.scalars().all()

        # Group by stage -> milestone -> plan
        stage_map = {}
        for t in all_tasks:
            sk = t.stage_code or "unknown"
            if sk not in stage_map:
                stage_map[sk] = {"stage_id": sk, "name": t.stage_name or sk,
                    "sort_order": len(stage_map) + 1, "status": "pending",
                    "progress_pct": 0, "milestones": {}}
            mk = t.milestone_code or "unknown"
            if mk not in stage_map[sk]["milestones"]:
                stage_map[sk]["milestones"][mk] = {"milestone_id": mk,
                    "name": t.milestone_name or mk, "sort_order": len(stage_map[sk]["milestones"]) + 1,
                    "status": "pending", "progress_pct": 0, "work_plans": {}}
            pk = t.plan_code or "unknown"
            if pk not in stage_map[sk]["milestones"][mk]["work_plans"]:
                stage_map[sk]["milestones"][mk]["work_plans"][pk] = {"plan_id": pk,
                    "name": t.plan_name or pk, "seq_no": len(stage_map[sk]["milestones"][mk]["work_plans"]) + 1,
                    "status": "pending", "tasks": []}
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
                    t_comp = sum(1 for t in ts if t["status"] == "completed")
                    t_run = sum(1 for t in ts if t["status"] == "running")
                    total_tasks += len(ts)
                    completed_tasks += t_comp
                    wp["status"] = "completed" if t_comp == len(ts) else ("running" if t_run > 0 else "pending")
                    starts = [t.get("start_time") for t in ts if t.get("start_time")]
                    ends = [t.get("end_time") for t in ts if t.get("end_time")]
                    wp["start_time"] = min(starts) if starts else None
                    wp["end_time"] = max(ends) if ends else None
                    wp_list.append(wp)
                wp_comp = sum(1 for w in wp_list if w["status"] == "completed")
                ms["status"] = "completed" if wp_comp == len(wp_list) else ("running" if any(w["status"] == "running" for w in wp_list) else "pending")
                ms["progress_pct"] = round(wp_comp / len(wp_list) * 100) if wp_list else 0
                ms["work_plans"] = wp_list
                mst = [w["start_time"] for w in wp_list if w.get("start_time")]
                mse = [w["end_time"] for w in wp_list if w.get("end_time")]
                ms["start_time"] = min(mst) if mst else None
                ms["end_time"] = max(mse) if mse else None
                ms_list.append(ms)
            ms_comp = sum(1 for m in ms_list if m["status"] == "completed")
            st["status"] = "completed" if ms_comp == len(ms_list) else ("running" if any(m["status"] == "running" for m in ms_list) else "pending")
            st["progress_pct"] = round(ms_comp / len(ms_list) * 100) if ms_list else 0
            st["milestones"] = ms_list
            st["milestone_count"] = len(ms_list)
            st["completed_milestone_count"] = ms_comp
            sst = [m["start_time"] for m in ms_list if m.get("start_time")]
            sse = [m["end_time"] for m in ms_list if m.get("end_time")]
            st["start_time"] = min(sst) if sst else None
            st["end_time"] = max(sse) if sse else None
            stages_json.append(st)

        overall = round(completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        return {
            "acct_month": am, "total_stages": len(stages_json),
            "completed_stages": sum(1 for s in stages_json if s["status"] == "completed"),
            "total_milestones": sum(s["milestone_count"] for s in stages_json),
            "completed_milestones": sum(s["completed_milestone_count"] for s in stages_json),
            "total_work_plans": sum(len(m["work_plans"]) for s in stages_json for m in s["milestones"]),
            "completed_work_plans": sum(sum(1 for w in m["work_plans"] if w["status"] == "completed") for s in stages_json for m in s["milestones"]),
            "total_tasks": total_tasks, "completed_tasks": completed_tasks,
            "overall_progress_pct": overall, "stages": stages_json,
        }

    @staticmethod
    def _task_to_monitor_dict(t):
        return {
            "task_id": t.task_code,
            "task_type": t.task_type,
            "content": t.content,
            "sort_order": t.sort_order,
            "status": t.status,
            "start_time": t.actual_start_time.isoformat() if t.actual_start_time else None,
            "end_time": t.actual_end_time.isoformat() if t.actual_end_time else None,
        }

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
