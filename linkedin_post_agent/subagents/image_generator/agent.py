"""Image Generator Agent - Generates images for LinkedIn posts."""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .tools import (
    generate_image_prompt,
    generate_image_with_imagen,
    generate_alt_text,
    LINKEDIN_IMAGE_WIDTH,
    LINKEDIN_IMAGE_HEIGHT,
)

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize database manager (singleton pattern)
_db_manager = None


def get_db_manager():
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        from database import DatabaseManager

        db_path = os.getenv("DATABASE_PATH", "./database.db")
        _db_manager = DatabaseManager(db_path)
        _db_manager.initialize()
    return _db_manager


def create_generate_image_tool() -> FunctionTool:
    """Create tool for generating post images."""

    def generate_image_tool(
        post_content: str,
        post_id: Optional[int] = None,
        style: str = "professional",
    ) -> Dict[str, Any]:
        """
        Generate an image for a LinkedIn post.

        Args:
            post_content: The LinkedIn post content
            post_id: Optional post ID to associate the image with
            style: Image style (professional, creative, minimal, branded)

        Returns:
            Dictionary with image generation results
        """
        try:
            # Generate image prompt
            prompt = generate_image_prompt(post_content, style)

            # Create images directory (use absolute path)
            # Get project root: go up from agent.py -> image_generator -> subagents -> linkedin_post_agent -> project root
            project_root = Path(__file__).parent.parent.parent.parent.resolve()
            images_dir = project_root / "images"
            images_dir.mkdir(exist_ok=True)

            # Generate filename
            if post_id:
                filename = f"post_{post_id}_{style}.png"
            else:
                import hashlib

                content_hash = hashlib.md5(post_content.encode()).hexdigest()[:8]
                filename = f"post_{content_hash}_{style}.png"

            # Use absolute path for the image
            output_path = str(images_dir / filename)

            # Generate image
            result = generate_image_with_imagen(
                prompt=prompt,
                output_path=output_path,
                width=LINKEDIN_IMAGE_WIDTH,
                height=LINKEDIN_IMAGE_HEIGHT,
            )

            if not result.get("success"):
                return result

            # Generate alt text
            alt_text = generate_alt_text(post_content)

            # Store in database if post_id provided
            if post_id:
                try:
                    db = get_db_manager()
                    db.create_post_image(
                        post_id=post_id,
                        image_path=output_path,
                        image_url=None,  # Could be set if using cloud storage
                        style=style,
                        alt_text=alt_text,
                    )
                except Exception as e:
                    logger.warning(f"Could not save image to database: {e}")

            return {
                "success": True,
                "image_path": output_path,
                "alt_text": alt_text,
                "style": style,
                "prompt": prompt,
                "dimensions": f"{LINKEDIN_IMAGE_WIDTH}x{LINKEDIN_IMAGE_HEIGHT}",
            }

        except Exception as e:
            logger.error(f"Error in generate_image_tool: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    return FunctionTool(generate_image_tool)


def create_image_generator_agent() -> Agent:
    """
    Create the Image Generator Agent.

    This agent generates images for LinkedIn posts based on post content.

    Returns:
        Configured Agent
    """
    tools = [create_generate_image_tool()]

    instructions = """
You are an Image Generator Agent responsible for creating images for LinkedIn posts.

Your tasks:
1. Analyze the post content to understand the main themes and topics
2. Determine the appropriate image style based on:
   - Post content and tone
   - User preferences (if available)
   - Default to "professional" style
3. Generate an image using the generate_image tool with:
   - The post content
   - An appropriate style (professional, creative, minimal, branded)
   - LinkedIn-optimized dimensions (1200x627px)
4. Generate appropriate alt text for accessibility
5. Output the image information clearly so PostFinalizer can save it:
   - image_path: The path to the generated image file
   - image_style: The style used (professional, creative, minimal, branded)
   - image_alt_text: The alt text for accessibility
   - image_dimensions: The dimensions (1200x627px)

Image Style Guidelines:
- professional: Clean, modern, business-focused imagery
- creative: Vibrant, engaging, visually striking
- minimal: Simple, elegant, clean design
- branded: Consistent, corporate, polished

The generated image should:
- Be relevant to the post content
- Be professional and appropriate for LinkedIn
- Not include text overlay (text is in the post itself)
- Be optimized for LinkedIn's recommended dimensions (1200x627px)
- Have appropriate alt text for accessibility

OUTPUT FORMAT:
After generating the image, you MUST output the image information in a clear, structured format:
- image_path: [absolute path to the generated image file, e.g., /path/to/project/images/post_123_professional.png]
- image_style: [style used: professional, creative, minimal, or branded]
- image_alt_text: [alt text for accessibility]
- image_dimensions: [dimensions, e.g., 1200x627px]

CRITICAL: The image_path MUST be the exact path returned by the generate_image tool. Do NOT modify or create a different path. Use the image_path value directly from the tool's response.

This information will be used by PostFinalizer to save the image to the database and link it to the post.
"""

    agent = Agent(
        name="ImageGenerator",
        model="gemini-2.0-flash",
        description="Generates images for LinkedIn posts based on content",
        instruction=instructions,
        tools=tools,
    )

    return agent
