"""Tools for input processing and content extraction."""

import re
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    CouldNotRetrieveTranscript,
)

logger = logging.getLogger(__name__)


def is_youtube_url(url: str) -> bool:
    """Check if URL is a YouTube URL."""
    youtube_patterns = [
        r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in youtube_patterns:
        if re.search(pattern, url):
            return True
    return False


def extract_youtube_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    patterns = [
        r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_url_content(url: str) -> Dict[str, Any]:
    """
    Extract content from a URL (blog/article).

    Args:
        url: URL to extract content from

    Returns:
        Dictionary with title, content, and metadata
    """
    try:
        # Set headers to avoid blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml")

        # Extract title
        title = None
        for tag in ["title", "h1", 'meta[property="og:title"]']:
            element = soup.select_one(tag)
            if element:
                title = (
                    element.get_text()
                    if hasattr(element, "get_text")
                    else element.get("content", "")
                )
                if title:
                    break

        # Extract main content
        # Try common article content selectors
        content_selectors = [
            "article",
            '[role="main"]',
            ".post-content",
            ".article-content",
            ".entry-content",
            "main",
            ".content",
        ]

        main_content = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                main_content = element.get_text(separator="\n", strip=True)
                if len(main_content) > 200:  # Ensure we got substantial content
                    break

        # Fallback: get all paragraph text
        if not main_content:
            paragraphs = soup.find_all("p")
            main_content = "\n\n".join(
                [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            )

        # Clean up content
        if main_content:
            main_content = re.sub(r"\s+", " ", main_content)  # Normalize whitespace
            main_content = main_content.strip()

        return {
            "success": True,
            "url": url,
            "title": title or "Untitled",
            "content": main_content or "",
            "content_length": len(main_content) if main_content else 0,
        }

    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return {
            "success": False,
            "url": url,
            "error": f"Failed to fetch URL: {str(e)}",
        }
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {e}")
        return {
            "success": False,
            "url": url,
            "error": f"Error extracting content: {str(e)}",
        }


def extract_youtube_transcript(
    url: str, cookies: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract transcript from YouTube video.

    Args:
        url: YouTube video URL

    Returns:
        Dictionary with transcript and metadata
    """
    try:
        video_id = extract_youtube_video_id(url)
        if not video_id:
            return {
                "success": False,
                "url": url,
                "error": "Could not extract video ID from URL",
            }

        # Use the instance method approach that matches the working example
        # Create API instance and fetch transcript
        ytt_api = YouTubeTranscriptApi()

        # Try to use fetch() method (instance method approach)
        try:
            transcript = ytt_api.fetch(video_id)
            # Extract text from transcript snippets
            full_text = " ".join([snippet.text for snippet in transcript])
            language = getattr(transcript, "language", "unknown")
            is_generated = getattr(transcript, "is_generated", False)
        except AttributeError:
            # If fetch() doesn't exist, fall back to static method
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(
                    video_id, languages=("en",)
                )
                full_text = " ".join([item["text"] for item in transcript_data])
                language = "en"
                is_generated = False
            except (NoTranscriptFound, CouldNotRetrieveTranscript):
                # Try without language preference
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                full_text = " ".join([item["text"] for item in transcript_data])
                language = "unknown"
                is_generated = False

        return {
            "success": True,
            "url": url,
            "video_id": video_id,
            "transcript": full_text,
            "transcript_length": len(full_text),
            "language": language,
            "is_generated": is_generated,
        }

    except TranscriptsDisabled:
        return {
            "success": False,
            "url": url,
            "error": "Transcripts are disabled for this video",
        }
    except NoTranscriptFound:
        return {
            "success": False,
            "url": url,
            "error": "No transcript found for this video",
        }
    except CouldNotRetrieveTranscript as e:
        return {
            "success": False,
            "url": url,
            "error": f"Could not retrieve transcript: {str(e)}",
        }
    except Exception as e:
        error_type = type(e).__name__
        logger.error(
            f"Error extracting YouTube transcript from {url}: {error_type}: {e}"
        )
        return {
            "success": False,
            "url": url,
            "error": f"Error extracting transcript ({error_type}): {str(e)}",
        }


def detect_input_type(user_input: str) -> str:
    """
    Detect the type of input provided by the user.

    Args:
        user_input: User's input string

    Returns:
        Input type: 'url', 'youtube', 'topic', or 'text'
    """
    user_input = user_input.strip()

    # Check if it's a URL
    try:
        parsed = urlparse(user_input)
        if parsed.scheme in ["http", "https"]:
            # Check if it's YouTube
            if is_youtube_url(user_input):
                return "youtube"
            return "url"
    except Exception:
        pass

    # Check if it's a short YouTube URL pattern
    if is_youtube_url(user_input):
        return "youtube"

    # Check if it looks like a topic (short, question-like, or prompt-like)
    # Topics are typically short prompts or questions
    if len(user_input) < 200 and (
        user_input.endswith("?")
        or user_input.startswith(
            (
                "Generate",
                "Create",
                "Write",
                "Make",
                "Tell me about",
                "What is",
                "How to",
            )
        )
    ):
        return "topic"

    # Otherwise, treat as raw text content
    return "text"
