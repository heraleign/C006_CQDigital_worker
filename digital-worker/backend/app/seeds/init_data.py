"""Initial data seeder for the database."""
from app.utils.logger import logger
from app.seeds.seed_all import seed


def seed_database():
    """Seed initial data into the database."""
    logger.info("Seeding database with initial data...")
    seed()
    logger.info("Database seeding completed")
    return {"status": "completed", "mode": "real", "message": "Database seeded with real data"}


if __name__ == "__main__":
    seed_database()
