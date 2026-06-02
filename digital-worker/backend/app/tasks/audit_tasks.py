"""Celery tasks for audit module."""
import random
from datetime import datetime
from app.utils.logger import logger

try:
    from celery import Celery
    from app.config import settings

    celery_app = Celery(
        "digital_worker",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
    )

    @celery_app.task(bind=True, max_retries=3)
    def execute_audit_task(self, task_id: int, task_config: dict = None):
        """Execute an audit task."""
        logger.info(f"Starting audit task {task_id}")
        try:
            # Simulate task execution
            total = random.randint(10000, 1000000)
            failed = random.randint(0, int(total * 0.05))
            import time
            time.sleep(random.randint(1, 5))
            result = {
                "task_id": task_id,
                "status": "completed",
                "total_records": total,
                "failed_records": failed,
                "pass_rate": round((total - failed) / total * 100, 2) if total > 0 else 100,
                "executed_at": datetime.now().isoformat(),
            }
            logger.info(f"Audit task {task_id} completed: {result}")
            return result
        except Exception as exc:
            logger.error(f"Audit task {task_id} failed: {exc}")
            raise self.retry(exc=exc)

    @celery_app.task(bind=True, max_retries=3)
    def ai_generate_rules_task(self, task_id: str, params: dict):
        """AI generate rules task."""
        logger.info(f"Starting AI rule generation task {task_id}")
        try:
            import time
            time.sleep(random.randint(3, 8))
            rules = [
                {
                    "rule_name": f"{params.get('table_name', 'table')}_非空校验",
                    "rule_type": "null_check",
                    "severity": "high",
                    "ai_generated": True,
                }
            ]
            return {"task_id": task_id, "status": "completed", "rules": rules}
        except Exception as exc:
            raise self.retry(exc=exc)

except ImportError:
    logger.warning("Celery not available, audit tasks will not be registered")

    def execute_audit_task(task_id, task_config=None):
        logger.info(f"Mock: Executing audit task {task_id}")
        return {"task_id": task_id, "status": "completed", "mock": True}

    def ai_generate_rules_task(task_id, params):
        logger.info(f"Mock: AI generating rules for task {task_id}")
        return {"task_id": task_id, "status": "completed", "mock": True}
