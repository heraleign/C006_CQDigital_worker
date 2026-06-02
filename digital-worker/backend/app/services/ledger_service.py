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
        """Fetch full 4-level hierarchy and compute aggregates."""
        # Query all stages with nested relations
        result = await db.execute(
            select(MaConfigStage)
            .options(
                selectinload(MaConfigStage.milestones).selectinload(
                    MaConfigMilestone.work_plans
                ).selectinload(MaConfigWorkPlan.tasks)
            )
            .order_by(MaConfigStage.sort_order)
        )
        stages = result.scalars().all()

        total_stages = len(stages)
        completed_stages = 0
        total_milestones = 0
        completed_milestones = 0
        total_work_plans = 0
        completed_work_plans = 0
        total_tasks = 0
        completed_tasks = 0

        stage_responses = []
        for stage in stages:
            stage_completed = stage.status == "completed"
            if stage_completed:
                completed_stages += 1

            milestones = stage.milestones or []
            milestone_count = len(milestones)
            completed_milestone_count = sum(1 for m in milestones if m.status == "completed")
            total_milestones += milestone_count
            completed_milestones += completed_milestone_count

            milestone_responses = []
            for ms in milestones:
                work_plans = ms.work_plans or []
                wp_completed = sum(1 for wp in work_plans if wp.status == "completed")
                total_work_plans += len(work_plans)
                completed_work_plans += wp_completed

                plan_responses = []
                for wp in work_plans:
                    tasks = wp.tasks or []
                    t_completed = sum(1 for t in tasks if t.status == "completed")
                    total_tasks += len(tasks)
                    completed_tasks += t_completed

                    # Aggregate start/end times from child tasks
                    task_starts = [t.start_time for t in tasks if t.start_time]
                    task_ends = [t.end_time for t in tasks if t.end_time]
                    wp_start = min(task_starts) if task_starts else None
                    wp_end = max(task_ends) if task_ends else None

                    task_responses = []
                    for t in tasks:
                        task_responses.append({
                            "task_id": t.task_code,
                            "task_type": t.task_type,
                            "content": t.content,
                            "sort_order": t.sort_order,
                            "status": t.status,
                            "start_time": t.start_time.isoformat() if t.start_time else None,
                            "end_time": t.end_time.isoformat() if t.end_time else None,
                        })

                    plan_responses.append({
                        "plan_id": wp.plan_code,
                        "seq_no": wp.seq_no,
                        "name": wp.name,
                        "time_point": wp.time_point,
                        "task_mode": wp.task_mode,
                        "is_system_task": wp.is_system_task,
                        "status": wp.status,
                        "start_time": wp_start.isoformat() if wp_start else None,
                        "end_time": wp_end.isoformat() if wp_end else None,
                        "tasks": task_responses,
                    })

                # Compute milestone progress
                ms_progress = (wp_completed / len(work_plans) * 100) if work_plans else 0

                # Aggregate milestone start/end from all child work plan tasks
                ms_task_starts = []
                ms_task_ends = []
                for wp2 in work_plans:
                    for t2 in (wp2.tasks or []):
                        if t2.start_time: ms_task_starts.append(t2.start_time)
                        if t2.end_time: ms_task_ends.append(t2.end_time)
                ms_start = min(ms_task_starts) if ms_task_starts else None
                ms_end = max(ms_task_ends) if ms_task_ends else None

                milestone_responses.append({
                    "milestone_id": ms.milestone_code,
                    "name": ms.name,
                    "sort_order": ms.sort_order,
                    "status": ms.status,
                    "progress_pct": round(ms_progress, 1),
                    "start_time": ms_start.isoformat() if ms_start else None,
                    "end_time": ms_end.isoformat() if ms_end else None,
                    "work_plans": plan_responses,
                })

            # Compute stage progress
            stage_progress = (completed_milestone_count / milestone_count * 100) if milestone_count else 0

            # Aggregate stage start/end from all child tasks
            stg_starts = []
            stg_ends = []
            for ms2 in milestones:
                for wp2 in (ms2.work_plans or []):
                    for t2 in (wp2.tasks or []):
                        if t2.start_time: stg_starts.append(t2.start_time)
                        if t2.end_time: stg_ends.append(t2.end_time)
            stg_start = min(stg_starts) if stg_starts else None
            stg_end = max(stg_ends) if stg_ends else None

            stage_responses.append({
                "stage_id": stage.stage_code,
                "name": stage.name,
                "sort_order": stage.sort_order,
                "status": stage.status,
                "progress_pct": round(stage_progress, 1),
                "start_time": stg_start.isoformat() if stg_start else None,
                "end_time": stg_end.isoformat() if stg_end else None,
                "milestone_count": milestone_count,
                "completed_milestone_count": completed_milestone_count,
                "milestones": milestone_responses,
            })

        overall_progress = (completed_tasks / total_tasks * 100) if total_tasks else 0

        return {
            "acct_month": account_month or "2026-06",
            "total_stages": total_stages,
            "completed_stages": completed_stages,
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "total_work_plans": total_work_plans,
            "completed_work_plans": completed_work_plans,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overall_progress_pct": round(overall_progress, 1),
            "stages": stage_responses,
        }

    # ==================== Cascade Completion Times ====================

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
