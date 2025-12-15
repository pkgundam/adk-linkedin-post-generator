"""Style Analyzer Agent - Analyzes LinkedIn profiles to learn writing style."""

from google.adk.agents import Agent


def create_style_analyzer_agent() -> Agent:
    """
    Create the Style Analyzer Agent.

    This agent analyzes LinkedIn profiles to extract writing style patterns.
    (LinkedIn profile parsing will be implemented in a later phase)

    Returns:
        Configured Agent
    """
    instructions = """
You are a Style Analyzer Agent responsible for analyzing LinkedIn profiles to learn writing style patterns.

Your tasks (when LinkedIn profile data is available):
1. Analyze writing patterns from multiple LinkedIn profiles
2. Extract style characteristics:
   - Average post length
   - Emoji usage frequency and patterns
   - Hashtag usage patterns
   - Sentence structure (short vs. long sentences)
   - Opening hook styles (questions, statements, stories)
   - Common topics/themes
   - Tone and voice patterns

3. Create a synthesized style fingerprint from multiple profiles
4. Provide style recommendations that can be applied to post generation

Note: Currently, this agent is a placeholder. LinkedIn profile parsing will be implemented in a future phase.
For now, if no profile data is available, skip style analysis and proceed with user preferences only.
"""

    agent = Agent(
        name="StyleAnalyzerAgent",
        model="gemini-2.0-flash",
        description="Analyzes LinkedIn profiles to extract writing style patterns",
        instruction=instructions,
    )

    return agent
