"""Main entry point for LinkedIn Post Generator."""

import os
import logging
from dotenv import load_dotenv

from database import DatabaseManager
from services import UserPreferenceService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize the database."""
    db_path = os.getenv("DATABASE_PATH", "./database.db")
    db = DatabaseManager(db_path)
    db.initialize()
    logger.info(f"Database initialized at {db_path}")
    return db


def main():
    """Main function."""
    logger.info("Starting LinkedIn Post Generator...")

    # Initialize database
    db = initialize_database()

    # Initialize services
    pref_service = UserPreferenceService(db)

    logger.info("System ready!")
    logger.info("Phase 1A: Foundation complete")
    logger.info("Next: Implement input processing and agents")


if __name__ == "__main__":
    main()

