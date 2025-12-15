"""User Preference Loader Agent - Loads user preferences from database."""

import os
import logging
from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

from database import DatabaseManager
from services import UserPreferenceService

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize database manager (singleton pattern)
_db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        db_path = os.getenv("DATABASE_PATH", "./database.db")
        _db_manager = DatabaseManager(db_path)
        _db_manager.initialize()
    return _db_manager


def create_load_user_preferences_tool() -> FunctionTool:
    """Create tool for loading user preferences from database."""

    def load_user_preferences_tool(user_id: int) -> Dict[str, Any]:
        """
        Load user preferences from the database.

        Args:
            user_id: The user ID to load preferences for

        Returns:
            Dictionary with user information and preferences
        """
        try:
            db = get_db_manager()
            pref_service = UserPreferenceService(db)

            user = pref_service.get_user(user_id)
            if not user:
                return {
                    "success": False,
                    "error": f"User {user_id} not found",
                }

            # Get preferences and merge with defaults
            preferences = pref_service.get_user_preferences(user_id)
            merged_preferences = pref_service.merge_preferences_with_defaults(
                preferences
            )

            return {
                "success": True,
                "user_id": user_id,
                "user_info": {
                    "name": user.name,
                    "email": user.email,
                    "job_title": user.job_title,
                    "industry": user.industry,
                    "company": user.company,
                },
                "preferences": merged_preferences,
            }
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
            return {
                "success": False,
                "error": f"Error loading preferences: {str(e)}",
            }

    return FunctionTool(load_user_preferences_tool)


def create_user_preference_loader_agent() -> Agent:
    """
    Create the User Preference Loader Agent.

    This agent loads user preferences from the database for use in post generation.

    Returns:
        Configured Agent
    """
    tools = [create_load_user_preferences_tool()]

    instructions = """
You are a User Preference Loader Agent responsible for loading user preferences from the database.

Your tasks:
1. Load preferences for the first available user (user_id=1) or use the default user
2. Use the load_user_preferences tool with user_id=1 to fetch user data and preferences
3. Provide a clear summary of:
   - User information (name, job title, industry, company)
   - Writing style preferences
   - Tone preferences
   - Post length preferences
   - Topics/interests
   - Any other relevant preferences

4. Format the output so it can be easily used by the post generator agent.

Always load preferences for user_id=1 (the primary user). Handle errors gracefully if user is not found.
"""

    agent = Agent(
        name="UserPreferenceLoader",
        model="gemini-2.0-flash",
        description="Loads user preferences from database for post generation",
        instruction=instructions,
        tools=tools,
    )

    return agent
