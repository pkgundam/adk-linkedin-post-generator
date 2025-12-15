"""Post Finalizer Agent - Saves final post to database."""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

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


def create_save_post_tool() -> FunctionTool:
    """Create tool for saving post to database."""

    def save_post_tool(
        post_content: str,
        user_id: int = 1,
        image_path: Optional[str] = None,
        image_style: Optional[str] = None,
        image_alt_text: Optional[str] = None,
        status: str = "draft",
    ) -> Dict[str, Any]:
        """
        Save the final post to the database and link the image if available.

        Args:
            post_content: The final LinkedIn post content
            user_id: User ID (defaults to 1)
            image_path: Optional path to generated image
            image_style: Optional image style (if image was generated)
            image_alt_text: Optional alt text for the image
            status: Post status (default: "draft")

        Returns:
            Dictionary with save results including post_id
        """
        try:
            db = get_db_manager()

            # Create the post in database
            post_id = db.create_post(
                user_id=user_id,
                content=post_content,
                image_path=image_path,
                status=status,
            )

            logger.info(f"Saved post {post_id} to database for user {user_id}")

            # If image was generated, save it to post_images table
            if image_path:
                try:
                    db.create_post_image(
                        post_id=post_id,
                        image_path=image_path,
                        image_url=None,
                        style=image_style or "professional",
                        alt_text=image_alt_text or "",
                    )
                    logger.info(f"Saved image {image_path} for post {post_id}")
                except Exception as e:
                    logger.warning(f"Could not save image to database: {e}")

            return {
                "success": True,
                "post_id": post_id,
                "user_id": user_id,
                "status": status,
                "image_saved": bool(image_path),
                "message": f"Post saved successfully with ID {post_id}",
            }

        except Exception as e:
            logger.error(f"Error saving post to database: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    return FunctionTool(save_post_tool)


def create_post_finalizer_agent() -> Agent:
    """
    Create the Post Finalizer Agent.

    This agent saves the final post to the database after refinement is complete.

    Returns:
        Configured Agent
    """
    tools = [create_save_post_tool()]

    instructions = """
You are a Post Finalizer Agent responsible for saving the final LinkedIn post to the database.

Your tasks:
1. Read the final post content from the state (from PostRefiner or the refinement loop)
2. Read the image information if available (from ImageGenerator):
   - image_path: Path to the generated image
   - image_style: Style of the image (if available)
   - image_alt_text: Alt text for the image (if available)
3. Save the post to the database using the save_post tool with:
   - The post content
   - User ID (use user_id=1 as default)
   - Image path if available
   - Image style if available
   - Image alt text if available
   - Status: "draft" (default)
4. The tool will automatically:
   - Save the post to the posts table
   - Save the image to the post_images table (if image_path is provided)
   - Link the image to the post using the post_id
5. Confirm the post and image (if any) were saved successfully

The post should be saved after the refinement loop completes and the image is generated (if applicable).

Output a confirmation that the post has been saved with its post_id, and whether the image was also saved.
"""

    agent = Agent(
        name="PostFinalizer",
        model="gemini-2.0-flash",
        description="Saves the final LinkedIn post to the database",
        instruction=instructions,
        tools=tools,
    )

    return agent
