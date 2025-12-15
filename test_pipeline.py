"""Test script for Phase 1C: Core Agents Pipeline."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import DatabaseManager
from services import UserPreferenceService
from linkedin_post_agent.agent import root_agent


def test_pipeline_creation():
    """Test that the pipeline is created successfully."""
    print("=" * 60)
    print("Testing Pipeline Creation")
    print("=" * 60)

    try:
        print(f"\n✅ Root agent type: {type(root_agent).__name__}")
        print(f"✅ Agent name: {root_agent.name}")
        print(f"✅ Description: {root_agent.description}")

        if hasattr(root_agent, "sub_agents"):
            print(f"\n✅ Pipeline has {len(root_agent.sub_agents)} sub-agents:")
            for i, agent in enumerate(root_agent.sub_agents):
                print(f"   {i+1}. {agent.name}")

        print("\n✅ Pipeline created successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error creating pipeline: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_user_preference_loader():
    """Test UserPreferenceLoader agent."""
    print("\n" + "=" * 60)
    print("Testing UserPreferenceLoader")
    print("=" * 60)

    try:
        # Initialize database
        db = DatabaseManager()
        db.initialize()

        # Get first user
        users = db.list_users()
        if not users:
            print("\n⚠️  No users found. Run test_setup.py first to create a user.")
            return False

        user = users[0]
        print(f"\n✅ Found user: {user.name} (ID: {user.id})")

        # Test preference service
        pref_service = UserPreferenceService(db)
        preferences = pref_service.get_user_preferences(user.id)

        print(f"✅ User preferences loaded:")
        print(f"   Writing style: {preferences.get('writing_style', 'N/A')}")
        print(f"   Tone: {preferences.get('tone', 'N/A')}")
        print(f"   Post length: {preferences.get('post_length', {})}")

        return True

    except Exception as e:
        print(f"\n❌ Error testing preference loader: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_quality_check_tools():
    """Test quality check tools."""
    print("\n" + "=" * 60)
    print("Testing Quality Check Tools")
    print("=" * 60)

    try:
        from linkedin_post_agent.subagents.post_reviewer.tools import (
            count_characters,
            check_hashtags,
            check_emoji_usage,
        )

        # Test post
        test_post = """
        Exciting news! 🚀 I just learned about AI agents and how they're transforming software engineering.
        
        #AI #SoftwareEngineering #Innovation #TechTrends
        
        The future is here!
        """

        # Test character count
        char_result = count_characters(test_post)
        print(f"\n✅ Character count: {char_result['character_count']}")
        print(f"   Status: {char_result['status']}")
        print(f"   Feedback: {char_result['feedback']}")

        # Test hashtags
        hashtag_result = check_hashtags(test_post)
        print(f"\n✅ Hashtag count: {hashtag_result['hashtag_count']}")
        print(f"   Hashtags: {hashtag_result['hashtags']}")
        print(f"   Feedback: {hashtag_result['feedback']}")

        # Test emojis
        emoji_result = check_emoji_usage(test_post)
        print(f"\n✅ Emoji count: {emoji_result['emoji_count']}")
        print(f"   Density: {emoji_result['emoji_density_percent']}%")
        print(f"   Feedback: {emoji_result['feedback']}")

        return True

    except Exception as e:
        print(f"\n❌ Error testing quality tools: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Phase 1C: Core Agents - Pipeline Test")
    print()

    try:
        # Test pipeline creation
        if not test_pipeline_creation():
            sys.exit(1)

        # Test user preference loader
        if not test_user_preference_loader():
            sys.exit(1)

        # Test quality check tools
        if not test_quality_check_tools():
            sys.exit(1)

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test the full pipeline with: uv run adk web")
        print("2. The pipeline will process input through all agents")
        print("3. Add refinement loop (Phase 1D) for iterative improvement")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
