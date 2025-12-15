"""Database tools for storing post sources and content."""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def save_post_source(
    db_manager,
    post_id: int,
    source_type: str,
    source_content: Optional[str] = None,
    extracted_content: Optional[str] = None,
) -> int:
    """
    Save post source to database.
    
    Args:
        db_manager: Database manager instance
        post_id: Post ID
        source_type: Type of source ('topic', 'url', 'youtube', 'text')
        source_content: Original input or URL
        extracted_content: Processed/extracted content
        
    Returns:
        Source ID
    """
    try:
        source_id = db_manager.create_post_source(
            post_id=post_id,
            source_type=source_type,
            source_content=source_content,
            extracted_content=extracted_content,
        )
        logger.info(f"Saved post source: {source_type} for post {post_id}")
        return source_id
    except Exception as e:
        logger.error(f"Error saving post source: {e}")
        raise


def save_processed_content_to_source(
    db_manager,
    post_id: int,
    input_type: str,
    original_input: str,
    processed_content: Dict[str, Any],
) -> int:
    """
    Save processed content as a post source.
    
    Args:
        db_manager: Database manager instance
        post_id: Post ID
        input_type: Detected input type
        original_input: Original user input
        processed_content: Processed content dictionary
        
    Returns:
        Source ID
    """
    # Extract relevant content based on input type
    extracted_content = None
    
    if input_type == 'url':
        extracted_content = processed_content.get('content', '')
    elif input_type == 'youtube':
        extracted_content = processed_content.get('transcript', '')
    elif input_type == 'text':
        extracted_content = processed_content.get('text', original_input)
    elif input_type == 'topic':
        extracted_content = processed_content.get('summary', original_input)
    
    return save_post_source(
        db_manager=db_manager,
        post_id=post_id,
        source_type=input_type,
        source_content=original_input,
        extracted_content=extracted_content,
    )

