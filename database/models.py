"""Database models and schema definitions."""

from typing import Optional, Dict, Any
from datetime import datetime
import json


class User:
    """User model representing a user in the system."""

    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        email: Optional[str] = None,
        job_title: Optional[str] = None,
        industry: Optional[str] = None,
        company: Optional[str] = None,
        preferences_json: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.job_title = job_title
        self.industry = industry
        self.company = company
        self.preferences_json = preferences_json
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def preferences(self) -> Dict[str, Any]:
        """Parse preferences JSON into a dictionary."""
        if self.preferences_json:
            try:
                return json.loads(self.preferences_json)
            except json.JSONDecodeError:
                return {}
        return {}

    @preferences.setter
    def preferences(self, value: Dict[str, Any]):
        """Set preferences as JSON string."""
        self.preferences_json = json.dumps(value) if value else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "job_title": self.job_title,
            "industry": self.industry,
            "company": self.company,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LinkedInProfile:
    """LinkedIn profile model for style analysis."""

    def __init__(
        self,
        id: Optional[int] = None,
        user_id: int = 0,
        profile_url: str = "",
        profile_name: Optional[str] = None,
        style_data_json: Optional[str] = None,
        analyzed_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.profile_url = profile_url
        self.profile_name = profile_name
        self.style_data_json = style_data_json
        self.analyzed_at = analyzed_at

    @property
    def style_data(self) -> Dict[str, Any]:
        """Parse style data JSON into a dictionary."""
        if self.style_data_json:
            try:
                return json.loads(self.style_data_json)
            except json.JSONDecodeError:
                return {}
        return {}

    @style_data.setter
    def style_data(self, value: Dict[str, Any]):
        """Set style data as JSON string."""
        self.style_data_json = json.dumps(value) if value else None


class Post:
    """Post model for generated LinkedIn posts."""

    def __init__(
        self,
        id: Optional[int] = None,
        user_id: int = 0,
        content: str = "",
        image_path: Optional[str] = None,
        status: str = "draft",
        engagement_score: Optional[float] = None,
        created_at: Optional[datetime] = None,
        published_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.content = content
        self.image_path = image_path
        self.status = status
        self.engagement_score = engagement_score
        self.created_at = created_at
        self.published_at = published_at


# SQL Schema definitions
SCHEMA = """
-- Users and preferences
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    job_title TEXT,
    industry TEXT,
    company TEXT,
    preferences_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LinkedIn profile analysis
CREATE TABLE IF NOT EXISTS linkedin_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    profile_url TEXT NOT NULL,
    profile_name TEXT,
    style_data_json TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Style analysis results
CREATE TABLE IF NOT EXISTS style_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    analysis_data_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES linkedin_profiles(id)
);

-- Generated posts
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    image_path TEXT,
    status TEXT DEFAULT 'draft',
    engagement_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Post versions (track refinement iterations)
CREATE TABLE IF NOT EXISTS post_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    feedback TEXT,
    iteration_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- Post images
CREATE TABLE IF NOT EXISTS post_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    image_url TEXT,
    style TEXT,
    alt_text TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- User preferences history
CREATE TABLE IF NOT EXISTS user_preferences_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    preferences_json TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Post sources (for multi-input support)
CREATE TABLE IF NOT EXISTS post_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    source_content TEXT,
    extracted_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_linkedin_profiles_user_id ON linkedin_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);
CREATE INDEX IF NOT EXISTS idx_post_versions_post_id ON post_versions(post_id);
CREATE INDEX IF NOT EXISTS idx_post_sources_post_id ON post_sources(post_id);
"""

