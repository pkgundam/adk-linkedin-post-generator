"""Quality check tools for post review."""

from typing import Dict, Any
import re


def count_characters(text: str) -> Dict[str, Any]:
    """
    Count characters in the post text.

    Args:
        text: The post text to analyze

    Returns:
        Dictionary with character count and analysis
    """
    char_count = len(text)
    word_count = len(text.split())
    line_count = len(text.split("\n"))

    # LinkedIn post limits
    linkedin_max = 3000
    linkedin_optimal_min = 1300
    linkedin_optimal_max = 1600

    status = "good"
    if char_count > linkedin_max:
        status = "too_long"
    elif char_count < linkedin_optimal_min:
        status = "too_short"
    elif char_count > linkedin_optimal_max:
        status = "long_but_ok"

    return {
        "character_count": char_count,
        "word_count": word_count,
        "line_count": line_count,
        "status": status,
        "linkedin_max": linkedin_max,
        "optimal_range": f"{linkedin_optimal_min}-{linkedin_optimal_max}",
        "feedback": _get_length_feedback(
            char_count, linkedin_optimal_min, linkedin_optimal_max, linkedin_max
        ),
    }


def _get_length_feedback(
    char_count: int, optimal_min: int, optimal_max: int, max_limit: int
) -> str:
    """Generate feedback about post length."""
    if char_count > max_limit:
        return f"Post is {char_count - max_limit} characters over LinkedIn's limit. Must be shortened."
    elif char_count < optimal_min:
        return f"Post is quite short ({char_count} chars). Consider expanding to 1,300-1,600 characters for optimal engagement."
    elif char_count > optimal_max:
        return f"Post is long ({char_count} chars). This is acceptable but posts around 1,300-1,600 chars tend to perform best for engagement."
    else:
        return f"Post length is optimal ({char_count} chars) for LinkedIn engagement."


def check_hashtags(text: str) -> Dict[str, Any]:
    """
    Check hashtag usage in the post.

    Args:
        text: The post text

    Returns:
        Dictionary with hashtag analysis
    """
    hashtags = re.findall(r"#\w+", text)
    hashtag_count = len(hashtags)

    # LinkedIn best practices
    optimal_range = (3, 5)
    max_recommended = 10

    status = "good"
    if hashtag_count == 0:
        status = "no_hashtags"
    elif hashtag_count > max_recommended:
        status = "too_many"
    elif hashtag_count < optimal_range[0]:
        status = "few_hashtags"

    return {
        "hashtag_count": hashtag_count,
        "hashtags": hashtags,
        "status": status,
        "optimal_range": optimal_range,
        "max_recommended": max_recommended,
        "feedback": _get_hashtag_feedback(
            hashtag_count, optimal_range, max_recommended
        ),
    }


def _get_hashtag_feedback(
    count: int, optimal_range: tuple, max_recommended: int
) -> str:
    """Generate feedback about hashtag usage."""
    if count == 0:
        return "No hashtags found. Consider adding 3-5 relevant hashtags for better discoverability."
    elif count > max_recommended:
        return f"Too many hashtags ({count}). LinkedIn recommends 3-5 hashtags for optimal engagement."
    elif count < optimal_range[0]:
        return f"Only {count} hashtag(s). Consider adding a few more (3-5 total) for better reach."
    else:
        return f"Hashtag usage is good ({count} hashtags)."


def check_emoji_usage(text: str) -> Dict[str, Any]:
    """
    Check emoji usage in the post.

    Args:
        text: The post text

    Returns:
        Dictionary with emoji analysis
    """
    # Simple emoji detection (basic Unicode ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )
    emojis = emoji_pattern.findall(text)
    emoji_count = len(emojis)

    char_count = len(text)
    emoji_density = (emoji_count / char_count * 100) if char_count > 0 else 0

    status = "good"
    if emoji_count == 0:
        status = "no_emojis"
    elif emoji_density > 5:  # More than 5% emojis
        status = "too_many"
    elif emoji_density < 0.5:
        status = "few_emojis"

    return {
        "emoji_count": emoji_count,
        "emoji_density_percent": round(emoji_density, 2),
        "status": status,
        "feedback": _get_emoji_feedback(emoji_count, emoji_density),
    }


def _get_emoji_feedback(count: int, density: float) -> str:
    """Generate feedback about emoji usage."""
    if count == 0:
        return "No emojis found. Consider adding a few emojis for visual appeal (but keep it professional)."
    elif density > 5:
        return f"High emoji density ({density:.1f}%). Consider reducing emojis for a more professional tone."
    elif density < 0.5:
        return (
            f"Low emoji usage ({count} emoji(s)). This is fine for professional posts."
        )
    else:
        return f"Emoji usage is balanced ({count} emoji(s), {density:.1f}% density)."


def exit_loop(
    character_status: str = "good",
    hashtag_status: str = "good",
    emoji_status: str = "good",
    reason: str = "",
    post_text: str = "",
) -> Dict[str, Any]:
    """
    Exit the refinement loop when post quality is acceptable.

    This tool should be called when the post meets quality standards and no further
    refinement is needed.

    Args:
        post_text: The current post text
        character_status: Status from count_characters ("good", "too_short", "too_long", "long_but_ok")
        hashtag_status: Status from check_hashtags ("good", "no_hashtags", "few_hashtags", "too_many")
        emoji_status: Status from check_emoji ("good", "no_emojis", "few_emojis", "too_many")
        reason: Optional reason for exiting the loop

    Returns:
        Dictionary indicating the loop should exit
    """
    # Determine if quality is acceptable
    # Exit if all checks are "good" or minor issues only
    acceptable_statuses = ["good", "long_but_ok", "few_hashtags", "few_emojis"]

    should_exit = (
        character_status in acceptable_statuses
        and hashtag_status in acceptable_statuses
        and emoji_status in acceptable_statuses
    )

    return {
        "exit_loop": should_exit,
        "reason": reason or "Post quality is acceptable",
        "character_status": character_status,
        "hashtag_status": hashtag_status,
        "emoji_status": emoji_status,
        "message": (
            "Refinement loop will exit" if should_exit else "Continue refinement"
        ),
    }
