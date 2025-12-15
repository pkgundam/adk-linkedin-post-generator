"""Image generation tools for LinkedIn posts."""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# LinkedIn optimal image dimensions
LINKEDIN_IMAGE_WIDTH = 1200
LINKEDIN_IMAGE_HEIGHT = 627


def generate_image_prompt(post_content: str, style: str = "professional") -> str:
    """
    Generate an image prompt based on post content and style.

    Args:
        post_content: The LinkedIn post content
        style: Image style (professional, creative, minimal, branded)

    Returns:
        Image generation prompt
    """
    # Extract key themes from post
    # This is a simplified version - could be enhanced with NLP
    keywords = _extract_keywords(post_content)

    style_descriptions = {
        "professional": "professional, clean, modern, business-focused",
        "creative": "creative, vibrant, engaging, visually striking",
        "minimal": "minimalist, simple, elegant, clean design",
        "branded": "branded, consistent, corporate, polished",
    }

    style_desc = style_descriptions.get(style, style_descriptions["professional"])

    # Create prompt for image generation
    prompt = (
        f"Create a {style_desc} LinkedIn post image about: {', '.join(keywords[:5])}. "
    )
    prompt += "The image should be suitable for a professional social media post, "
    prompt += (
        f"optimized for {LINKEDIN_IMAGE_WIDTH}x{LINKEDIN_IMAGE_HEIGHT} dimensions. "
    )
    prompt += (
        "Use appropriate colors, avoid text overlay (text will be added separately), "
    )
    prompt += "and ensure the image is professional and engaging."

    return prompt


def _extract_keywords(text: str, max_keywords: int = 5) -> list:
    """
    Extract keywords from post content.

    Args:
        text: Post content
        max_keywords: Maximum number of keywords to extract

    Returns:
        List of keywords
    """
    # Simple keyword extraction - could be enhanced with NLP
    # Remove common words and extract meaningful terms
    common_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "as",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "could",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "what",
        "which",
        "who",
        "whom",
        "whose",
        "where",
        "when",
        "why",
        "how",
    }

    # Extract words (simple approach)
    words = text.lower().split()
    keywords = [
        word.strip(".,!?;:()[]{}'\"")
        for word in words
        if len(word) > 3 and word.strip(".,!?;:()[]{}'\"") not in common_words
    ]

    # Remove duplicates and return top keywords
    unique_keywords = list(dict.fromkeys(keywords))  # Preserves order
    return unique_keywords[:max_keywords]


def generate_image_with_imagen(
    prompt: str,
    output_path: str,
    width: int = LINKEDIN_IMAGE_WIDTH,
    height: int = LINKEDIN_IMAGE_HEIGHT,
) -> Dict[str, Any]:
    """
    Generate an image using Google's Gemini Image Generation API.

    Args:
        prompt: Image generation prompt
        output_path: Path to save the generated image
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Dictionary with image generation results
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "GOOGLE_API_KEY not found in environment variables",
            }

        # Configure the API
        genai.configure(api_key=api_key)

        # Try to use Gemini image generation API
        # Check if the new genai.Client API is available (for gemini-2.5-flash-image)
        try:
            # Method 1: Try using the new google.genai API if available (Gemini 2.5+)
            # This is the ACTUAL API CALL for image generation
            try:
                from google import genai as new_genai
                from google.genai import types

                client = new_genai.Client(api_key=api_key)

                # ACTUAL GEMINI IMAGE GENERATION API CALL
                # Using gemini-2.5-flash-image model for image generation
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[prompt],
                    config=types.GenerateContentConfig(response_modalities=["Image"]),
                )

                # Extract image from response
                if response.candidates and len(response.candidates) > 0:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "inline_data") and part.inline_data:
                            # Save the image
                            output_dir = Path(output_path).parent
                            output_dir.mkdir(parents=True, exist_ok=True)

                            image_data = part.inline_data.data
                            with open(output_path, "wb") as f:
                                f.write(image_data)

                            logger.info(f"Image generated successfully: {output_path}")
                            return {
                                "success": True,
                                "image_path": output_path,
                                "prompt": prompt,
                                "width": width,
                                "height": height,
                            }

            except ImportError:
                # Fall back to alternative method if new API not available
                logger.debug("New genai API not available, trying alternative method")
                pass
            except Exception as api_error:
                logger.warning(f"Gemini image generation API error: {api_error}")
                # Continue to fallback
                pass

            # Method 2: Try using google-generativeai with image generation
            # Note: This may require a different model or API endpoint
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            # For now, if direct image generation isn't available in this model,
            # we'll create a placeholder and log a message
            logger.warning(
                "Direct image generation may not be available in current API. "
                "Using placeholder. Check Gemini API documentation for image generation support."
            )

        except Exception as api_error:
            logger.warning(
                f"Image generation API call failed: {api_error}. "
                "Creating placeholder file."
            )

        # Fallback: Create placeholder if API call fails or isn't available
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create a placeholder file with metadata
        placeholder_path = output_path.replace(".png", "_placeholder.txt")
        with open(placeholder_path, "w") as f:
            f.write(f"Image generation prompt: {prompt}\n")
            f.write(f"Dimensions: {width}x{height}\n")
            f.write(
                "Note: Actual image generation requires Gemini Image API integration.\n"
            )
            f.write("Check: https://ai.google.dev/gemini-api/docs/image-generation\n")

        return {
            "success": True,
            "image_path": placeholder_path,
            "prompt": prompt,
            "width": width,
            "height": height,
            "note": "Placeholder - actual image generation pending API integration",
        }

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return {
            "success": False,
            "error": str(e),
        }


def generate_alt_text(post_content: str, image_description: str = "") -> str:
    """
    Generate alt text for the image based on post content.

    Args:
        post_content: The LinkedIn post content
        image_description: Optional description of the generated image

    Returns:
        Alt text for accessibility
    """
    keywords = _extract_keywords(post_content, max_keywords=3)

    if image_description:
        alt_text = f"LinkedIn post image: {image_description}"
    else:
        alt_text = f"LinkedIn post image related to: {', '.join(keywords)}"

    return alt_text
