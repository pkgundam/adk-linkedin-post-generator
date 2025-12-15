"""Style templates for different writing styles and post structures."""

from typing import Dict, Any


def get_writing_style_template(writing_style: str) -> str:
    """
    Get template instructions for a writing style.

    Args:
        writing_style: One of 'storytelling', 'technical', 'casual', 'formal', 'professional'

    Returns:
        Template instructions for that style
    """
    templates = {
        "storytelling": """
STORYTELLING STYLE:
- Use narrative elements: personal moments, realizations, turning points
- Include emotions, lessons learned, or insights gained
- Make it conversational and reflective
- Connect ideas through personal experience or observation
- Use vivid language to paint a picture
""",
        "technical": """
TECHNICAL STYLE:
- Focus on facts, data, and logical progression
- Use precise terminology and clear explanations
- Structure: problem → solution → takeaways
- Include specific details, examples, or metrics
- Maintain professional objectivity
""",
        "casual": """
CASUAL STYLE:
- Write as if talking to a friend or colleague
- Use contractions and conversational language
- Share personal anecdotes or experiences
- Keep it light and approachable
- Include relatable examples
""",
        "formal": """
FORMAL STYLE:
- Use professional, polished language
- Avoid contractions and casual expressions
- Structure ideas logically and systematically
- Maintain respectful, authoritative tone
- Include well-reasoned arguments
""",
        "professional": """
PROFESSIONAL STYLE:
- Balance professionalism with approachability
- Use clear, concise language
- Structure: context → insights → actionable takeaways
- Maintain credibility and expertise
- Include relevant examples or case studies
""",
    }

    return templates.get(writing_style.lower(), templates["professional"])


def get_post_structure_template(post_structure: str) -> str:
    """
    Get template instructions for a post structure.

    Args:
        post_structure: One of 'storytelling', 'list-based', 'problem-solution', 'narrative', 'custom'

    Returns:
        Template instructions for that structure
    """
    templates = {
        "storytelling": """
STORYTELLING STRUCTURE (REQUIRED FORMAT):
1. **Opening Hook** (1-2 sentences):
   - Start with a strong personal moment or realization related to the content
   - Make it feel immediate and relatable
   - Example: "Last week, I had a moment that changed how I think about..."

2. **Story Section** (50%+ of post):
   - Tell a short story: what you noticed, what problem the audience faces, why you're sharing this now
   - Include emotions, lessons, or turning points
   - Be conversational and reflective
   - Connect the content to personal experience

3. **Key Takeaways** (3-6 concise bullets):
   - Briefly summarize main ideas or 'roadmap' from the content
   - Keep bullets concise and actionable
   - Use bullet points or numbered list

4. **Closing** (optional):
   - End with a question, call-to-action, or reflection

CRITICAL: At least 50% of the post must be narrative/story. Do NOT output a dry summary or pure list.
""",
        "list-based": """
LIST-BASED STRUCTURE:
1. **Hook**: Engaging opening statement or question
2. **Main Content**: Organized as a numbered or bulleted list
   - Each item should be clear and actionable
   - Use 3-7 items for optimal engagement
3. **Closing**: Summary or call-to-action
""",
        "problem-solution": """
PROBLEM-SOLUTION STRUCTURE:
1. **Problem Statement**: Clearly define the problem or challenge
2. **Context**: Why this problem matters
3. **Solution/Approach**: Present the solution or approach
4. **Results/Insights**: Share outcomes or key learnings
5. **Takeaways**: Actionable insights for the reader
""",
        "narrative": """
NARRATIVE STRUCTURE:
1. **Opening**: Set the scene or context
2. **Journey**: Walk through the experience or process chronologically
3. **Insights**: Share what you learned along the way
4. **Reflection**: Connect back to broader implications
5. **Closing**: End with a thought-provoking conclusion
""",
        "custom": """
CUSTOM STRUCTURE:
Follow the custom_instructions provided in user preferences if available.
Otherwise, use a flexible structure that best fits the content.
""",
    }

    return templates.get(post_structure.lower(), templates["custom"])


def build_post_instructions(preferences: Dict[str, Any]) -> str:
    """
    Build dynamic post generation instructions based on user preferences.

    Args:
        preferences: User preferences dictionary

    Returns:
        Complete instruction string for the PostGenerator
    """
    writing_style = preferences.get("writing_style", "professional")
    post_structure = preferences.get("post_structure", None)
    custom_instructions = preferences.get("custom_instructions", None)
    tone = preferences.get("tone", "professional")
    post_length = preferences.get("post_length", {"min": 200, "max": 1000})
    emoji_usage = preferences.get("emoji_usage", "moderate")
    hashtag_usage = preferences.get("hashtag_usage", "moderate")
    sentence_structure = preferences.get("sentence_structure", "mixed")
    opening_hook_style = preferences.get("opening_hook_style", "statement")

    # Base instructions
    base_instructions = """
You are an Initial Post Generator Agent responsible for creating the first draft of a LinkedIn post.

CRITICAL WRITING RULES:

1. **First Person Voice**: Write the post as if the user is the original speaker/creator of the content, NOT as someone who watched or reviewed it.

2. **For YouTube Videos/Content**: 
   - DO NOT write: "I watched a video about..." or "I learned from this video..." or "The creator explains..."
   - DO write: As if YOU are explaining the concepts yourself
   - The transcript content should be presented as YOUR thoughts and explanations
   - Example: Instead of "I watched a video where someone built an app", write "I built an app using..."

3. **For URLs/Articles**:
   - DO NOT write: "I read an article about..." or "This article discusses..."
   - DO write: Present the ideas as YOUR insights and thoughts
   - Summarize key points as if YOU are sharing YOUR knowledge

4. **For Topics**:
   - Write as YOUR perspective and thoughts on the topic
   - Share YOUR insights and experiences

5. **AVOID**:
   - "I loved how he..."
   - "I was inspired by..."
   - "he explains..."
   - "this video shows..."
   - "the creator mentions..."
   - Any third-person references to content creators

6. **DO**:
   - Use first person singular ("I", "my", "me")
   - Speak directly to the reader
   - Present ideas as if they are YOUR original thoughts
   - Write as if YOU are the one explaining/teaching/sharing

"""

    # Add custom instructions if provided (highest priority)
    if custom_instructions:
        base_instructions += f"""
CUSTOM INSTRUCTIONS (HIGHEST PRIORITY - FOLLOW THESE EXACTLY):
{custom_instructions}

"""

    # Add post structure template
    if post_structure:
        base_instructions += get_post_structure_template(post_structure)
        base_instructions += "\n"
    else:
        # Default structure guidance
        base_instructions += """
STRUCTURE GUIDANCE:
- Start with an engaging opening hook
- Organize content in clear paragraphs
- End with a strong conclusion or call-to-action
"""

    # Add writing style template
    base_instructions += get_writing_style_template(writing_style)
    base_instructions += "\n"

    # Add tone guidance
    tone_guidance = {
        "enthusiastic": "Use energetic, positive language. Show excitement and passion.",
        "analytical": "Focus on data, logic, and systematic thinking. Be objective and thorough.",
        "inspirational": "Uplift and motivate. Share insights that inspire action or reflection.",
        "professional": "Maintain credibility and expertise. Be polished and respectful.",
    }
    if tone in tone_guidance:
        base_instructions += f"TONE: {tone_guidance[tone]}\n\n"

    # Add formatting preferences
    base_instructions += f"""
FORMATTING PREFERENCES:
- Post length: {post_length.get('min', 200)}-{post_length.get('max', 1000)} characters
- Emoji usage: {emoji_usage} ({'use sparingly' if emoji_usage == 'none' else 'use appropriately' if emoji_usage == 'moderate' else 'feel free to use'})
- Hashtag usage: {hashtag_usage} ({'no hashtags' if hashtag_usage == 'none' else '3-5 hashtags' if hashtag_usage == 'moderate' else '5-10 hashtags'})
- Sentence structure: {sentence_structure} ({'short, punchy sentences' if sentence_structure == 'short' else 'longer, flowing sentences' if sentence_structure == 'long' else 'mix of short and long'})
- Opening hook style: {opening_hook_style}

Your tasks:
1. Use the processed_content from the InputProcessor
2. Transform it into a first-person post as if the user is the original speaker
3. Apply ALL the style, structure, and formatting preferences above
4. Apply style patterns from style_analysis if available
5. Generate a LinkedIn post that matches ALL specified preferences

Remember: The user is posting THEIR content, not reviewing someone else's content.
"""

    return base_instructions
