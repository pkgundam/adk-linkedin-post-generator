"""User preference management service."""

from typing import Optional, Dict, Any, List
import logging

from database.db_manager import DatabaseManager
from database.models import User

logger = logging.getLogger(__name__)


class UserPreferenceService:
    """Service for managing user preferences."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize user preference service.

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    def create_user(
        self,
        name: str,
        email: Optional[str] = None,
        job_title: Optional[str] = None,
        industry: Optional[str] = None,
        company: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Create a new user with initial preferences.

        Args:
            name: User's name
            email: User's email
            job_title: User's job title
            industry: User's industry
            company: User's company
            preferences: Initial preferences dictionary

        Returns:
            User ID
        """
        user_id = self.db.create_user(
            name=name,
            email=email,
            job_title=job_title,
            industry=industry,
            company=company,
            preferences=preferences or {},
        )

        # Save initial preferences to history
        if preferences:
            self.db.save_preferences_history(user_id, preferences)

        logger.info(f"Created user {user_id}: {name}")
        return user_id

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.get_user(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.get_user_by_email(email)

    def update_user_preferences(
        self, user_id: int, preferences: Dict[str, Any]
    ) -> bool:
        """
        Update user preferences and save to history.

        Args:
            user_id: User ID
            preferences: New preferences dictionary

        Returns:
            True if successful
        """
        # Get current preferences to compare
        user = self.db.get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False

        # Update preferences
        success = self.db.update_user(user_id, preferences=preferences)
        if success:
            # Save to history
            self.db.save_preferences_history(user_id, preferences)
            logger.info(f"Updated preferences for user {user_id}")
        else:
            logger.error(f"Failed to update preferences for user {user_id}")

        return success

    def update_user_preference_field(
        self, user_id: int, field: str, value: Any
    ) -> bool:
        """
        Update a single preference field.

        Args:
            user_id: User ID
            field: Preference field name (e.g., 'writing_style', 'tone')
            value: New value for the field

        Returns:
            True if successful
        """
        user = self.db.get_user(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False

        # Get current preferences and update the field
        current_preferences = user.preferences
        current_preferences[field] = value

        return self.update_user_preferences(user_id, current_preferences)

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        Get user preferences.

        Args:
            user_id: User ID

        Returns:
            Preferences dictionary, empty dict if user not found
        """
        user = self.db.get_user(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            return {}
        return user.preferences

    def get_preferences_history(
        self, user_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get user preferences history.

        Args:
            user_id: User ID
            limit: Maximum number of history entries to return

        Returns:
            List of preference history entries
        """
        return self.db.get_preferences_history(user_id, limit)

    def set_writing_style(self, user_id: int, style: str) -> bool:
        """
        Set user's writing style preference.

        Args:
            user_id: User ID
            style: Writing style ('formal', 'casual', 'technical', 'storytelling')

        Returns:
            True if successful
        """
        return self.update_user_preference_field(user_id, "writing_style", style)

    def set_tone(self, user_id: int, tone: str) -> bool:
        """
        Set user's tone preference.

        Args:
            user_id: User ID
            tone: Tone ('enthusiastic', 'analytical', 'inspirational', 'professional')

        Returns:
            True if successful
        """
        return self.update_user_preference_field(user_id, "tone", tone)

    def set_post_length(
        self,
        user_id: int,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ) -> bool:
        """
        Set user's post length preferences.

        Args:
            user_id: User ID
            min_length: Minimum post length in characters
            max_length: Maximum post length in characters

        Returns:
            True if successful
        """
        user = self.db.get_user(user_id)
        if not user:
            return False

        current_preferences = user.preferences
        if "post_length" not in current_preferences:
            current_preferences["post_length"] = {}

        if min_length is not None:
            current_preferences["post_length"]["min"] = min_length
        if max_length is not None:
            current_preferences["post_length"]["max"] = max_length

        return self.update_user_preferences(user_id, current_preferences)

    def set_topics(self, user_id: int, topics: List[str]) -> bool:
        """
        Set user's topics/interests.

        Args:
            user_id: User ID
            topics: List of topics/interests

        Returns:
            True if successful
        """
        return self.update_user_preference_field(user_id, "topics", topics)

    def set_industry_template(self, user_id: int, template: str) -> bool:
        """
        Set user's industry-specific template preference.

        Args:
            user_id: User ID
            template: Template name

        Returns:
            True if successful
        """
        return self.update_user_preference_field(user_id, "industry_template", template)

    def get_default_preferences(self) -> Dict[str, Any]:
        """
        Get default preferences structure.

        Returns:
            Default preferences dictionary
        """
        return {
            "writing_style": "professional",  # 'storytelling', 'technical', 'casual', 'formal', 'professional'
            "post_structure": None,  # 'storytelling', 'list-based', 'problem-solution', 'narrative', 'custom' (optional)
            "custom_instructions": None,  # Optional: detailed custom format instructions
            "tone": "professional",  # 'enthusiastic', 'analytical', 'inspirational', 'professional'
            "post_length": {
                "min": 100,
                "max": 3000,
            },
            "topics": [],
            "industry_template": None,
            "emoji_usage": "moderate",  # 'none', 'moderate', 'frequent'
            "hashtag_usage": "moderate",  # 'none', 'moderate', 'frequent'
            "sentence_structure": "mixed",  # 'short', 'long', 'mixed'
            "opening_hook_style": "statement",  # 'question', 'statement', 'story'
        }

    def initialize_user_preferences(self, user_id: int) -> bool:
        """
        Initialize user with default preferences if they don't have any.

        Args:
            user_id: User ID

        Returns:
            True if successful
        """
        user = self.db.get_user(user_id)
        if not user:
            return False

        if not user.preferences:
            default_prefs = self.get_default_preferences()
            return self.update_user_preferences(user_id, default_prefs)

        return True

    def merge_preferences_with_defaults(
        self, user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge user preferences with defaults, ensuring all fields are present.

        Args:
            user_preferences: User's current preferences

        Returns:
            Merged preferences dictionary
        """
        defaults = self.get_default_preferences()
        merged = defaults.copy()
        merged.update(user_preferences)

        # Ensure nested dictionaries are properly merged
        if "post_length" in user_preferences:
            merged["post_length"] = {
                **defaults.get("post_length", {}),
                **user_preferences["post_length"],
            }

        return merged
