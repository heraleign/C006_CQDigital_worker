"""Celery tasks for monthly module."""
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
    def generate_monthly_report(self, account_month: str, params: dict = None):
        """Generate monthly summary report."""
        logger.info(f"Starting monthly report generation for {account_month}")
        try:
            import time
            time.sleep(random.randint(2, 8))
            result = {
                "account_month": account_month,
                "status": "completed",
                "generated_at": datetime.now().isoformat(),
                "report_id": random.randint(1000, 9999),
            }
            logger.info(f"Monthly report for {account_month} generated: {result}")
            return result
        except Exception as exc:
            logger.error(f"Monthly report generation failed: {exc}")
            raise self.retry(exc=exc)

    @celery_app.task(bind=True, max_retries=3)
    def execute_monthly_task(self, task_id: int, task_config: dict = None):
        """Execute a monthly operation task."""
        logger.info(f"Starting monthly task {task_id}")
        try:
            import time
            time.sleep(random.randint(1, 10))
            result = {
                "task_id": task_id,
                "status": random.choice(["completed", "completed", "failed"]),
                "executed_at": datetime.now().isoformat(),
            }
            logger.info(f"Monthly task {task_id} completed")
            return result
        except Exception as exc:
            raise self.retry(exc=exc)

except ImportError:
    logger.warning("Celery not available, monthly tasks will not be registered")

    def generate_monthly_report(account_month, params=None):
        logger.info(f"Mock: Generating monthly report for {account_month}")
        return {"account_month": account_month, "status": "completed", "mock": True}

    def execute_monthly_task(task_id, task_config=None):
        logger.info(f"Mock: Executing monthly task {task_id}")
        return {"task_id": task_id, "status": "completed", "mock": True}
