"""Content Summarizer Agent for summarizing long-form content."""

import logging

logger = logging.getLogger(__name__)

try:
    from google.adk.agents import Agent
except ImportError as e:
    logger.warning(
        f"ADK imports not available: {e}. Make sure google-adk is installed."
    )

    # Create placeholder class for development
    class Agent:
        def __init__(self, *args, **kwargs):
            pass


def create_content_summarizer_agent(api_key: str = None) -> Agent:
    """
    Create the Content Summarizer Agent.

    This agent takes long-form content and summarizes it into key points
    suitable for LinkedIn post generation.

    Args:
        api_key: Google API key

    Returns:
        Configured LlmAgent
    """
    instructions = """
You are a Content Summarizer Agent responsible for summarizing long-form content into key points suitable for LinkedIn posts.

Your tasks:
1. Analyze the provided content (from URL, YouTube transcript, or raw text)
2. Extract the main themes and key points
3. Identify the most important takeaways
4. Summarize in a way that:
   - Captures the essence of the content
   - Highlights 3-5 key points
   - Maintains the original message and tone
   - Is suitable for conversion to a LinkedIn post

Output format:
- Main theme/topic
- 3-5 key points or takeaways
- Important quotes or statistics (if any)
- Target audience insights
- Ready for LinkedIn post generation

Keep summaries concise but comprehensive. Focus on actionable insights and valuable information.
"""

    agent = Agent(
        name="ContentSummarizerAgent",
        model="gemini-2.0-flash",
        description="Content Summarizer Agent for summarizing long-form content",
        instruction=instructions,
    )

    return agent
