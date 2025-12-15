"""Database manager for SQLite operations."""

import sqlite3
import os
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from datetime import datetime
import logging

from .models import SCHEMA, User, LinkedInProfile, Post

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    def __init__(self, db_path: str = "database.db"):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialized = False

    def initialize(self) -> None:
        """Initialize database schema if not already initialized."""
        if self._initialized:
            return

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executescript(SCHEMA)
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
            self._initialized = True
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Get database connection with proper transaction handling.

        Usage:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0,
        )
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction error: {e}")
            raise
        finally:
            conn.close()

    # User CRUD operations
    def create_user(
        self,
        name: str,
        email: Optional[str] = None,
        job_title: Optional[str] = None,
        industry: Optional[str] = None,
        company: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Create a new user.

        Args:
            name: User's name
            email: User's email (optional, must be unique)
            job_title: User's job title
            industry: User's industry
            company: User's company
            preferences: User preferences dictionary

        Returns:
            ID of created user
        """
        import json

        preferences_json = json.dumps(preferences) if preferences else None

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (name, email, job_title, industry, company, preferences_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, email, job_title, industry, company, preferences_json),
            )
            return cursor.lastrowid

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row)
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return self._row_to_user(row)
            return None

    def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        job_title: Optional[str] = None,
        industry: Optional[str] = None,
        company: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update user information.

        Args:
            user_id: User ID to update
            name: New name (optional)
            email: New email (optional)
            job_title: New job title (optional)
            industry: New industry (optional)
            company: New company (optional)
            preferences: New preferences dictionary (optional)

        Returns:
            True if update successful, False otherwise
        """
        import json

        updates = []
        values = []

        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if email is not None:
            updates.append("email = ?")
            values.append(email)
        if job_title is not None:
            updates.append("job_title = ?")
            values.append(job_title)
        if industry is not None:
            updates.append("industry = ?")
            values.append(industry)
        if company is not None:
            updates.append("company = ?")
            values.append(company)
        if preferences is not None:
            updates.append("preferences_json = ?")
            values.append(json.dumps(preferences))

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(user_id)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                values,
            )
            return cursor.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return cursor.rowcount > 0

    def list_users(self) -> List[User]:
        """List all users."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            return [self._row_to_user(row) for row in cursor.fetchall()]

    # User Preferences History
    def save_preferences_history(self, user_id: int, preferences: Dict[str, Any]) -> int:
        """Save user preferences to history."""
        import json

        preferences_json = json.dumps(preferences)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_preferences_history (user_id, preferences_json)
                VALUES (?, ?)
                """,
                (user_id, preferences_json),
            )
            return cursor.lastrowid

    def get_preferences_history(
        self, user_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user preferences history."""
        import json

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT preferences_json, changed_at
                FROM user_preferences_history
                WHERE user_id = ?
                ORDER BY changed_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
            return [
                {
                    "preferences": json.loads(row["preferences_json"])
                    if row["preferences_json"]
                    else {},
                    "changed_at": row["changed_at"],
                }
                for row in cursor.fetchall()
            ]

    # LinkedIn Profile operations
    def create_linkedin_profile(
        self,
        user_id: int,
        profile_url: str,
        profile_name: Optional[str] = None,
        style_data: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Create a LinkedIn profile entry."""
        import json

        style_data_json = json.dumps(style_data) if style_data else None

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO linkedin_profiles (user_id, profile_url, profile_name, style_data_json)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, profile_url, profile_name, style_data_json),
            )
            return cursor.lastrowid

    def get_linkedin_profiles(self, user_id: int) -> List[LinkedInProfile]:
        """Get all LinkedIn profiles for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM linkedin_profiles WHERE user_id = ? ORDER BY analyzed_at DESC",
                (user_id,),
            )
            return [self._row_to_linkedin_profile(row) for row in cursor.fetchall()]

    def update_linkedin_profile_style(
        self, profile_id: int, style_data: Dict[str, Any]
    ) -> bool:
        """Update LinkedIn profile style data."""
        import json

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE linkedin_profiles
                SET style_data_json = ?, analyzed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (json.dumps(style_data), profile_id),
            )
            return cursor.rowcount > 0

    # Post operations
    def create_post(
        self,
        user_id: int,
        content: str,
        image_path: Optional[str] = None,
        status: str = "draft",
        engagement_score: Optional[float] = None,
    ) -> int:
        """Create a new post."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO posts (user_id, content, image_path, status, engagement_score)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, content, image_path, status, engagement_score),
            )
            return cursor.lastrowid

    def get_post(self, post_id: int) -> Optional[Post]:
        """Get post by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_post(row)
            return None

    def get_user_posts(
        self, user_id: int, status: Optional[str] = None
    ) -> List[Post]:
        """Get all posts for a user, optionally filtered by status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    "SELECT * FROM posts WHERE user_id = ? AND status = ? ORDER BY created_at DESC",
                    (user_id, status),
                )
            else:
                cursor.execute(
                    "SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC",
                    (user_id,),
                )
            return [self._row_to_post(row) for row in cursor.fetchall()]

    def update_post(
        self,
        post_id: int,
        content: Optional[str] = None,
        image_path: Optional[str] = None,
        status: Optional[str] = None,
        engagement_score: Optional[float] = None,
    ) -> bool:
        """Update post."""
        updates = []
        values = []

        if content is not None:
            updates.append("content = ?")
            values.append(content)
        if image_path is not None:
            updates.append("image_path = ?")
            values.append(image_path)
        if status is not None:
            updates.append("status = ?")
            values.append(status)
        if engagement_score is not None:
            updates.append("engagement_score = ?")
            values.append(engagement_score)
        if status == "published":
            updates.append("published_at = CURRENT_TIMESTAMP")
            values.append(post_id)

        if not updates:
            return False

        values.append(post_id)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE posts SET {', '.join(updates)} WHERE id = ?",
                values,
            )
            return cursor.rowcount > 0

    # Post Version operations
    def create_post_version(
        self,
        post_id: int,
        version_number: int,
        content: str,
        feedback: Optional[str] = None,
        iteration_count: Optional[int] = None,
    ) -> int:
        """Create a post version."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO post_versions (post_id, version_number, content, feedback, iteration_count)
                VALUES (?, ?, ?, ?, ?)
                """,
                (post_id, version_number, content, feedback, iteration_count),
            )
            return cursor.lastrowid

    def get_post_versions(self, post_id: int) -> List[Dict[str, Any]]:
        """Get all versions of a post."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM post_versions
                WHERE post_id = ?
                ORDER BY version_number ASC
                """,
                (post_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    # Post Image operations
    def create_post_image(
        self,
        post_id: int,
        image_path: str,
        image_url: Optional[str] = None,
        style: Optional[str] = None,
        alt_text: Optional[str] = None,
    ) -> int:
        """Create a post image entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO post_images (post_id, image_path, image_url, style, alt_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (post_id, image_path, image_url, style, alt_text),
            )
            return cursor.lastrowid

    def get_post_images(self, post_id: int) -> List[Dict[str, Any]]:
        """Get all images for a post."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM post_images WHERE post_id = ? ORDER BY generated_at DESC",
                (post_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    # Post Source operations
    def create_post_source(
        self,
        post_id: int,
        source_type: str,
        source_content: Optional[str] = None,
        extracted_content: Optional[str] = None,
    ) -> int:
        """Create a post source entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO post_sources (post_id, source_type, source_content, extracted_content)
                VALUES (?, ?, ?, ?)
                """,
                (post_id, source_type, source_content, extracted_content),
            )
            return cursor.lastrowid

    def get_post_sources(self, post_id: int) -> List[Dict[str, Any]]:
        """Get all sources for a post."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM post_sources WHERE post_id = ? ORDER BY created_at DESC",
                (post_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    # Style Analysis operations
    def create_style_analysis(
        self, profile_id: int, analysis_data: Dict[str, Any]
    ) -> int:
        """Create a style analysis entry."""
        import json

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO style_analyses (profile_id, analysis_data_json)
                VALUES (?, ?)
                """,
                (profile_id, json.dumps(analysis_data)),
            )
            return cursor.lastrowid

    def get_style_analyses(self, profile_id: int) -> List[Dict[str, Any]]:
        """Get all style analyses for a profile."""
        import json

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM style_analyses
                WHERE profile_id = ?
                ORDER BY created_at DESC
                """,
                (profile_id,),
            )
            return [
                {
                    **dict(row),
                    "analysis_data": json.loads(row["analysis_data_json"])
                    if row["analysis_data_json"]
                    else {},
                }
                for row in cursor.fetchall()
            ]

    # Helper methods for row conversion
    def _row_to_user(self, row: sqlite3.Row) -> User:
        """Convert database row to User object."""
        return User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            job_title=row["job_title"],
            industry=row["industry"],
            company=row["company"],
            preferences_json=row["preferences_json"],
            created_at=self._parse_timestamp(row["created_at"]),
            updated_at=self._parse_timestamp(row["updated_at"]),
        )

    def _row_to_linkedin_profile(self, row: sqlite3.Row) -> LinkedInProfile:
        """Convert database row to LinkedInProfile object."""
        return LinkedInProfile(
            id=row["id"],
            user_id=row["user_id"],
            profile_url=row["profile_url"],
            profile_name=row["profile_name"],
            style_data_json=row["style_data_json"],
            analyzed_at=self._parse_timestamp(row["analyzed_at"]),
        )

    def _row_to_post(self, row: sqlite3.Row) -> Post:
        """Convert database row to Post object."""
        return Post(
            id=row["id"],
            user_id=row["user_id"],
            content=row["content"],
            image_path=row["image_path"],
            status=row["status"],
            engagement_score=row["engagement_score"],
            created_at=self._parse_timestamp(row["created_at"]),
            published_at=self._parse_timestamp(row["published_at"]),
        )

    @staticmethod
    def _parse_timestamp(timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        if not timestamp_str:
            return None
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

