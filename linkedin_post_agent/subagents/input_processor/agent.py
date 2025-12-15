"""Input Processor Agent for detecting and processing different input types."""

import os
import logging
from typing import Dict, Any

import logging

logger = logging.getLogger(__name__)

try:
    from google.adk.agents import Agent
    from google.adk.tools import FunctionTool
except ImportError as e:
    logger.warning(
        f"ADK imports not available: {e}. Make sure google-adk is installed."
    )

    # Create placeholder classes for development
    class Agent:
        def __init__(self, *args, **kwargs):
            pass

    class FunctionTool:
        def __init__(self, *args, **kwargs):
            pass


from .tools import (
    detect_input_type,
    extract_url_content,
    extract_youtube_transcript,
    is_youtube_url,
)


# ADK Tools for content extraction
def create_url_extractor_tool() -> FunctionTool:
    """Create tool for extracting content from URLs."""

    def extract_url_tool(url: str) -> Dict[str, Any]:
        """
        Extract content from a blog or article URL.

        Args:
            url: The URL to extract content from

        Returns:
            Dictionary with extracted content, title, and metadata
        """
        logger.info(f"Extracting content from URL: {url}")
        result = extract_url_content(url)
        return result

    return FunctionTool(extract_url_tool)


def create_youtube_extractor_tool() -> FunctionTool:
    """Create tool for extracting YouTube transcripts."""

    def extract_youtube_tool(url: str) -> Dict[str, Any]:
        """
        Extract transcript from a YouTube video URL.

        Args:
            url: The YouTube video URL

        Returns:
            Dictionary with transcript text and metadata
        """
        logger.info(f"Extracting transcript from YouTube URL: {url}")
        result = extract_youtube_transcript(url)
        return result

    return FunctionTool(extract_youtube_tool)


def create_input_type_detector_tool() -> FunctionTool:
    """Create tool for detecting input type."""

    def detect_type_tool(user_input: str) -> Dict[str, Any]:
        """
        Detect the type of input provided by the user.

        Args:
            user_input: The user's input string

        Returns:
            Dictionary with detected input type and details
        """
        input_type = detect_input_type(user_input)
        result = {
            "input_type": input_type,
            "input": user_input,
        }

        if input_type == "youtube":
            result["is_youtube"] = True
            result["note"] = (
                "This is a YouTube URL. Use extract_youtube_transcript to get the transcript."
            )
        elif input_type == "url":
            result["is_url"] = True
            result["note"] = (
                "This is a URL. Use extract_url_content to get the article content."
            )
        elif input_type == "topic":
            result["is_topic"] = True
            result["note"] = (
                "This is a topic/prompt. You can use google_search for research if needed."
            )
        else:
            result["is_text"] = True
            result["note"] = (
                "This is raw text content. Process it directly for summarization."
            )

        return result

    return FunctionTool(detect_type_tool)


def create_input_processor_agent(api_key: str = None) -> Agent:
    """
    Create the Input Processor Agent.

    This agent detects the input type and extracts/processes content accordingly.

    Args:
        api_key: Google API key (optional, can be set via environment variable)

    Returns:
        Configured Agent
    """
    # Create tools
    tools = [
        create_input_type_detector_tool(),
        create_url_extractor_tool(),
        create_youtube_extractor_tool(),
    ]

    # Agent instructions
    instructions = """
You are an Input Processor Agent responsible for detecting and processing different types of user inputs.

Your tasks:
1. Detect the input type using detect_input_type tool
2. Based on the input type:
   - If URL: Extract content using extract_url_content
   - If YouTube: Extract transcript using extract_youtube_transcript
   - If topic: Note that it's a topic (can be researched later if needed)
   - If text: Process the text directly

3. After extracting content, provide a summary of:
   - Input type detected
   - Content extracted (or topic identified)
   - Key points or main themes
   - Ready for post generation

Output your findings in a clear, structured format that can be used by the next agent in the pipeline.
Always handle errors gracefully and inform the user if content extraction fails.
"""

    agent = Agent(
        name="InputProcessorAgent",
        model="gemini-2.0-flash",
        description="Input Processor Agent for detecting and processing different input types",
        instruction=instructions,
        tools=tools,
    )

    return agent
