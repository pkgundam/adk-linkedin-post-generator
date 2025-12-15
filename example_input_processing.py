"""Example script showing how to use the Input Processor Agent."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import DatabaseManager
from linkedin_post_agent.subagents.input_processor import (
    create_input_processor_agent,
    detect_input_type,
    extract_url_content,
    extract_youtube_transcript,
)


def example_direct_tool_usage():
    """Example of using tools directly without ADK agent."""
    print("=" * 60)
    print("Example: Direct Tool Usage")
    print("=" * 60)
    
    # Example 1: Detect input type
    user_input = "https://techcrunch.com/2024/01/15/ai-agents"
    input_type = detect_input_type(user_input)
    print(f"\nInput: {user_input}")
    print(f"Detected type: {input_type}")
    
    # Example 2: Extract URL content
    if input_type == 'url':
        print("\nExtracting content from URL...")
        result = extract_url_content(user_input)
        if result.get('success'):
            print(f"✅ Success!")
            print(f"Title: {result.get('title')}")
            print(f"Content length: {result.get('content_length')} characters")
            print(f"Preview: {result.get('content', '')[:200]}...")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    # Example 3: Extract YouTube transcript
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"\n\nExtracting transcript from YouTube: {youtube_url}")
    result = extract_youtube_transcript(youtube_url)
    if result.get('success'):
        print(f"✅ Success!")
        print(f"Transcript length: {result.get('transcript_length')} characters")
        print(f"Language: {result.get('language')}")
    else:
        print(f"❌ Error: {result.get('error')}")
        print("(This is expected if the video doesn't have transcripts)")


def example_with_agent():
    """Example of using the ADK agent (requires API key)."""
    print("\n" + "=" * 60)
    print("Example: Using Input Processor Agent")
    print("=" * 60)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY not found in environment variables")
        print("   Skipping agent example. Set GOOGLE_API_KEY in .env to test the agent.")
        return
    
    try:
        # Create the agent
        agent = create_input_processor_agent(api_key)
        print("\n✅ Input Processor Agent created successfully!")
        print("\nTo use the agent, you would:")
        print("1. Create an ADK session")
        print("2. Run the agent with user input")
        print("3. Get processed_content from the output")
        print("\nExample code:")
        print("""
from adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
session = session_service.create_session()

# Run agent
result = agent.run(
    session=session,
    user_input="https://example.com/article"
)

# Get processed content
processed_content = result.get("processed_content")
        """)
        
    except Exception as e:
        print(f"\n❌ Error creating agent: {e}")
        print("Make sure google-adk is installed: pip install google-adk[database]")


def example_with_database():
    """Example of integrating with database."""
    print("\n" + "=" * 60)
    print("Example: Database Integration")
    print("=" * 60)
    
    # Initialize database
    db = DatabaseManager()
    db.initialize()
    
    # Get first user (for example)
    users = db.list_users()
    if not users:
        print("\n⚠️  No users found. Run test_setup.py first to create a user.")
        return
    
    user = users[0]
    print(f"\nUsing user: {user.name} (ID: {user.id})")
    
    # Example: Process input and create a post source
    user_input = "Generate a post about AI agents"
    input_type = detect_input_type(user_input)
    
    print(f"\nInput: {user_input}")
    print(f"Type: {input_type}")
    
    # Create a post (for demonstration)
    post_id = db.create_post(
        user_id=user.id,
        content="This is a placeholder post",
        status="draft",
    )
    
    print(f"\n✅ Created post ID: {post_id}")
    
    # Save source
    source_id = db.create_post_source(
        post_id=post_id,
        source_type=input_type,
        source_content=user_input,
        extracted_content=f"Processed {input_type} input",
    )
    
    print(f"✅ Saved source ID: {source_id}")
    
    # Retrieve sources
    sources = db.get_post_sources(post_id)
    print(f"\nPost sources: {len(sources)}")
    for source in sources:
        print(f"  - {source['source_type']}: {source['source_content']}")


def main():
    """Run all examples."""
    print("Phase 1B: Input Processing - Examples")
    print()
    
    # Example 1: Direct tool usage
    example_direct_tool_usage()
    
    # Example 2: Using agent
    example_with_agent()
    
    # Example 3: Database integration
    example_with_database()
    
    print("\n" + "=" * 60)
    print("✅ Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

