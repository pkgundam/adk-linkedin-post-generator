"""Test script to verify Phase 1A setup."""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import DatabaseManager
from services import UserPreferenceService


def test_database_initialization():
    """Test database initialization."""
    print("Testing database initialization...")
    db_path = os.getenv("DATABASE_PATH", "./database.db")
    db = DatabaseManager(db_path)
    db.initialize()
    print("✅ Database initialized successfully")
    return db


def load_user_from_json(json_path: str = "user.json") -> dict:
    """Load user data from JSON file."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"User JSON file not found: {json_path}\n"
            f"Please create {json_path} with your user data."
        )

    with open(json_path, "r") as f:
        return json.load(f)


def create_user_from_json(db_manager, json_path: str = "user.json") -> int:
    """
    Create a user from JSON file.

    Args:
        db_manager: Database manager instance
        json_path: Path to user JSON file

    Returns:
        User ID
    """
    pref_service = UserPreferenceService(db_manager)
    user_data = load_user_from_json(json_path)

    # Extract LinkedIn profiles if present
    linkedin_profiles = user_data.pop("linkedin_profiles", [])

    # Create user
    user_id = pref_service.create_user(
        name=user_data.get("name", ""),
        email=user_data.get("email"),
        job_title=user_data.get("job_title"),
        industry=user_data.get("industry"),
        company=user_data.get("company"),
        preferences=user_data.get("preferences", {}),
    )

    # Create LinkedIn profile entries if provided
    if linkedin_profiles:
        from services.style_analysis_service import StyleAnalysisService

        style_service = StyleAnalysisService(db_manager)

        for profile in linkedin_profiles:
            profile_id = db_manager.create_linkedin_profile(
                user_id=user_id,
                profile_url=profile.get("profile_url", ""),
                profile_name=profile.get("profile_name"),
            )
            # Analyze profile immediately (day-0 activity)
            style_service.analyze_linkedin_profile(
                profile_id, profile.get("profile_url", "")
            )
        print(f"   Added {len(linkedin_profiles)} LinkedIn profile(s)")
        print(f"   Analyzed {len(linkedin_profiles)} profile(s) for style patterns")

    return user_id


def test_user_creation(db_manager):
    """Test user creation from JSON file."""
    print("\nTesting user creation from JSON...")

    try:
        user_id = create_user_from_json(db_manager)
        print(f"✅ User created with ID: {user_id}")
        return user_id
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\nCreating user with default test data instead...")
        # Fallback to hardcoded data if JSON doesn't exist
        pref_service = UserPreferenceService(db_manager)
        user_id = pref_service.create_user(
            name="Test User",
            email="test@example.com",
            job_title="Software Engineer",
            industry="Technology",
            company="Test Corp",
            preferences={
                "writing_style": "technical",
                "tone": "professional",
                "post_length": {"min": 200, "max": 1000},
                "topics": ["AI", "Machine Learning"],
            },
        )
        print(f"✅ User created with ID: {user_id} (using fallback data)")
        return user_id


def test_user_retrieval(db_manager, user_id):
    """Test user retrieval."""
    print("\nTesting user retrieval...")
    pref_service = UserPreferenceService(db_manager)

    user = pref_service.get_user(user_id)
    if user:
        print(f"✅ User retrieved: {user.name} ({user.email or 'No email'})")
        print(f"   Preferences: {user.preferences}")
    else:
        print("❌ Failed to retrieve user")
        return False

    # Test getting by email (if email was provided)
    if user.email:
        user_by_email = pref_service.get_user_by_email(user.email)
        if user_by_email and user_by_email.id == user_id:
            print("✅ User retrieved by email successfully")
        else:
            print("❌ Failed to retrieve user by email")
            return False

    # Test LinkedIn profiles if any were added
    profiles = db_manager.get_linkedin_profiles(user_id)
    if profiles:
        print(f"✅ Found {len(profiles)} LinkedIn profile(s) for user")
        for profile in profiles:
            print(f"   - {profile.profile_name or 'Unnamed'}: {profile.profile_url}")

    return True


def test_preference_updates(db_manager, user_id):
    """Test preference updates."""
    print("\nTesting preference updates...")
    pref_service = UserPreferenceService(db_manager)

    # Update preferences
    success = pref_service.update_user_preferences(
        user_id,
        {
            "writing_style": "casual",
            "tone": "enthusiastic",
            "post_length": {"min": 1200, "max": 2000},
        },
    )
    if success:
        print("✅ Preferences updated successfully")
    else:
        print("❌ Failed to update preferences")
        return False

    # Verify update
    updated_prefs = pref_service.get_user_preferences(user_id)
    if updated_prefs.get("writing_style") == "casual":
        print("✅ Preference update verified")
    else:
        print("❌ Preference update not reflected")
        return False

    # Test individual field update
    pref_service.set_writing_style(user_id, "storytelling")
    pref_service.set_tone(user_id, "inspirational")
    final_prefs = pref_service.get_user_preferences(user_id)
    if (
        final_prefs.get("writing_style") == "storytelling"
        and final_prefs.get("tone") == "inspirational"
    ):
        print("✅ Individual field updates work")
    else:
        print("❌ Individual field updates failed")
        return False

    return True


def test_preference_history(db_manager, user_id):
    """Test preference history."""
    print("\nTesting preference history...")
    pref_service = UserPreferenceService(db_manager)

    history = pref_service.get_preferences_history(user_id, limit=5)
    if len(history) > 0:
        print(f"✅ Retrieved {len(history)} history entries")
        print(f"   Latest: {history[0].get('changed_at')}")
    else:
        print("❌ No history found")
        return False

    return True


def test_default_preferences():
    """Test default preferences."""
    print("\nTesting default preferences...")
    db = DatabaseManager()
    pref_service = UserPreferenceService(db)

    defaults = pref_service.get_default_preferences()
    if defaults:
        print("✅ Default preferences structure:")
        for key, value in defaults.items():
            print(f"   {key}: {value}")
    else:
        print("❌ Failed to get default preferences")
        return False

    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("Phase 1A: Foundation - Setup Test")
    print("=" * 50)

    try:
        # Test database
        db = test_database_initialization()

        # Test user operations
        user_id = test_user_creation(db)
        if not test_user_retrieval(db, user_id):
            sys.exit(1)

        # Test preferences
        if not test_preference_updates(db, user_id):
            sys.exit(1)

        # Test history
        if not test_preference_history(db, user_id):
            sys.exit(1)

        # Test defaults
        if not test_default_preferences():
            sys.exit(1)

        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
