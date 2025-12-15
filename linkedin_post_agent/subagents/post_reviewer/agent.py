"""Post Reviewer Agent - Reviews post quality and provides feedback."""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .tools import count_characters, check_hashtags, check_emoji_usage, exit_loop


def create_count_characters_tool() -> FunctionTool:
    """Create tool for counting characters."""

    def count_chars_tool(post_text: str) -> dict:
        """
        Count characters, words, and lines in the post.

        Args:
            post_text: The LinkedIn post text to analyze

        Returns:
            Dictionary with character count and feedback
        """
        return count_characters(post_text)

    return FunctionTool(count_chars_tool)


def create_check_hashtags_tool() -> FunctionTool:
    """Create tool for checking hashtag usage."""

    def check_hashtags_tool(post_text: str) -> dict:
        """
        Check hashtag usage in the post.

        Args:
            post_text: The LinkedIn post text to analyze

        Returns:
            Dictionary with hashtag analysis and feedback
        """
        return check_hashtags(post_text)

    return FunctionTool(check_hashtags_tool)


def create_check_emoji_tool() -> FunctionTool:
    """Create tool for checking emoji usage."""

    def check_emoji_tool(post_text: str) -> dict:
        """
        Check emoji usage in the post.

        Args:
            post_text: The LinkedIn post text to analyze

        Returns:
            Dictionary with emoji analysis and feedback
        """
        return check_emoji_usage(post_text)

    return FunctionTool(check_emoji_tool)


def create_exit_loop_tool() -> FunctionTool:
    """Create tool for exiting the refinement loop."""

    def exit_loop_tool(
        character_status: str = "good",
        hashtag_status: str = "good",
        emoji_status: str = "good",
        reason: str = "",
        post_text: str = "",
    ) -> dict:
        """
        Exit the refinement loop when post quality is acceptable.

        Call this tool when the post meets quality standards and no further
        refinement is needed. The loop will exit after this call.

        Args:
            post_text: The current post text
            character_status: Status from count_characters ("good", "too_short", "too_long", "long_but_ok")
            hashtag_status: Status from check_hashtags ("good", "no_hashtags", "few_hashtags", "too_many")
            emoji_status: Status from check_emoji ("good", "no_emojis", "few_emojis", "too_many")
            reason: Optional reason for exiting the loop

        Returns:
            Dictionary indicating the loop should exit
        """
        return exit_loop(
            character_status, hashtag_status, emoji_status, reason, post_text
        )

    return FunctionTool(exit_loop_tool)


def create_post_reviewer_agent() -> Agent:
    """
    Create the Post Reviewer Agent.

    This agent reviews the generated post and provides quality feedback.

    Returns:
        Configured Agent
    """
    tools = [
        create_count_characters_tool(),
        create_check_hashtags_tool(),
        create_check_emoji_tool(),
        create_exit_loop_tool(),
    ]

    instructions = """
You are a Post Reviewer Agent responsible for reviewing LinkedIn posts and providing quality feedback.

CRITICAL RULES:
- NEVER recommend adding links to videos, articles, or external sources
- NEVER suggest referencing creators, authors, or external content
- The post should read as the user's original content, not a review or reference to external sources

Your tasks:
1. Review the post using the available quality check tools:
   - count_characters: Check if post length is appropriate for LinkedIn
   - check_hashtags: Analyze hashtag usage
   - check_emoji: Analyze emoji usage

2. Provide comprehensive feedback on:
   - Post length (check against user preferences, typically 1300-3000 characters, optimal 1300-1600 for best engagement)
   - Hashtag usage (recommended 3-5 hashtags based on user preferences)
   - Emoji usage (should be balanced, not excessive, based on user preferences)
   - Overall quality and LinkedIn best practices

3. Identify specific issues that need to be fixed
4. Provide actionable recommendations for improvement
5. Determine if the post is ready or needs refinement

6. EXIT LOOP DECISION (CRITICAL):
   - After reviewing with all tools, evaluate if the post quality is acceptable
   - You MUST call exit_loop tool when quality is good enough to stop the refinement loop
   - Call exit_loop when:
     * character_status is "good" or "long_but_ok"
     * AND hashtag_status is "good" or "few_hashtags"  
     * AND emoji_status is "good" or "few_emojis"
   - Pass the actual status values from your tool calls to exit_loop
   - Example: exit_loop(character_status="good", hashtag_status="good", emoji_status="good", reason="All quality checks passed")
   - If there are significant issues (too_short, too_long, too_many hashtags/emojis, no_hashtags), do NOT call exit_loop - let the refiner fix the issues first
   - IMPORTANT: If you don't call exit_loop when quality is acceptable, the loop will continue unnecessarily

FORBIDDEN RECOMMENDATIONS:
- DO NOT suggest adding video links
- DO NOT suggest adding article links
- DO NOT suggest referencing creators or authors
- DO NOT suggest mentioning external sources

Output your review in a clear, structured format that can guide the PostRefiner agent.
"""

    agent = Agent(
        name="PostReviewer",
        model="gemini-2.0-flash",
        description="Reviews LinkedIn posts and provides quality feedback",
        instruction=instructions,
        tools=tools,
    )

    return agent
