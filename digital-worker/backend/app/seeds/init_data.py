"""Initial data seeder for the database."""
import random
from datetime import datetime, timedelta, date
from app.utils.logger import logger


async def seed_database():
    """Seed initial data into the database.

    This function populates the database with initial reference data.
    In mock mode, data is generated on-the-fly by MockDataService.
    """
    logger.info("Seeding database with initial data...")
    logger.info("Mock mode enabled - data will be generated dynamically")
    logger.info("To seed real database, set USE_MOCK=false and configure database connection")

    return {
        "status": "completed",
        "mode": "mock",
        "message": "Data is generated dynamically by MockDataService",
    }


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())
