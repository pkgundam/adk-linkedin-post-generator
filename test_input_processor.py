"""Test script for Input Processor Agent."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from linkedin_post_agent.subagents.input_processor.agent import (
    create_input_processor_agent,
)
from linkedin_post_agent.subagents.input_processor.tools import (
    detect_input_type,
    extract_url_content,
    extract_youtube_transcript,
)


def test_tools():
    """Test the content extraction tools directly."""
    print("=" * 60)
    print("Testing Content Extraction Tools")
    print("=" * 60)

    # Test input type detection
    print("\n1. Testing Input Type Detection:")
    test_inputs = [
        "https://techcrunch.com/2025/12/13/indias-spinny-lines-up-160m-funding-to-acquire-gomechanic-sources-say",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "Generate a post about AI agents",
        "This is a long piece of text that I want to convert into a LinkedIn post...",
    ]

    for test_input in test_inputs:
        input_type = detect_input_type(test_input)
        print(f"   Input: {test_input[:50]}...")
        print(f"   Type: {input_type}")
        print()

    print("\n2. Testing URL Content Extraction:")
    # Find URL inputs from test_inputs
    url_inputs = [inp for inp in test_inputs if detect_input_type(inp) == "url"]
    if url_inputs:
        test_url = url_inputs[0]
        print(f"   Testing URL: {test_url}")
        result = extract_url_content(test_url)
        if result.get("success"):
            print(f"   ✅ Success! Title: {result.get('title', 'N/A')}")
            print(f"   Content length: {result.get('content_length', 0)} characters")
            content_preview = (
                result.get("content", "")[:200] if result.get("content") else ""
            )
            if content_preview:
                print(f"   Preview: {content_preview}...")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
    else:
        print("   ⚠️  No URL inputs found in test_inputs to test")
        print("   Uncomment a URL in test_inputs to test URL extraction")

    print("\n3. Testing YouTube Transcript Extraction:")
    # Find YouTube inputs from test_inputs
    youtube_inputs = [inp for inp in test_inputs if detect_input_type(inp) == "youtube"]
    if youtube_inputs:
        test_youtube = youtube_inputs[0]
        print(f"   Testing YouTube URL: {test_youtube}")
        result = extract_youtube_transcript(test_youtube)
        if result.get("success"):
            print(
                f"   ✅ Success! Transcript length: {result.get('transcript_length', 0)} characters"
            )
            print(f"   Language: {result.get('language', 'N/A')}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
            print("   (This is expected if the video doesn't have transcripts)")
    else:
        print("   ⚠️  No YouTube inputs found in test_inputs to test")
        print("   Uncomment a YouTube URL in test_inputs to test transcript extraction")


def test_input_processor_agent():
    """Test the Input Processor Agent."""
    print("\n" + "=" * 60)
    print("Testing Input Processor Agent")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("   Please set it in your .env file")
        return

    try:
        # Create agent
        agent = create_input_processor_agent(api_key)
        print("✅ Input Processor Agent created successfully")

        # Test with different input types
        test_cases = [
            {
                "name": "Topic Input",
                "input": "Generate a post about what I learned from building AI agents",
            },
            {
                "name": "URL Input",
                "input": "https://techcrunch.com/2024/01/15/ai-agents",
            },
            {
                "name": "YouTube Input",
                "input": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            },
        ]

        print(
            "\nNote: To fully test the agent, you would need to run it through ADK's session."
        )
        print("For now, the agent is created and ready to use.")
        print("\nYou can test it using:")
        print("  adk web  # To use ADK's web interface")
        print("  Or integrate it into a SequentialAgent pipeline")

    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        import traceback

        traceback.print_exc()


def main():
    """Run all tests."""
    print("Phase 1B: Input Processing - Test Script")
    print()

    # Test tools first
    test_tools()

    # Test agent
    test_input_processor_agent()

    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test the agent with real URLs/YouTube videos")
    print("2. Integrate with database to store sources")
    print("3. Create the main pipeline with SequentialAgent")


if __name__ == "__main__":
    main()
