# Enhanced LinkedIn Post Generator

A LinkedIn post generator using Google's Agent Development Kit (ADK) that creates personalized, high-quality LinkedIn posts with automatic image generation and iterative refinement.

## Features

-   **Multi-input support**: Generate posts from topics, URLs, YouTube videos, or raw text
-   **Multi-agent orchestration**: Specialized agents for input processing, content generation, quality review, and image generation
-   **Iterative refinement**: Posts are automatically reviewed and refined until quality standards are met
-   **User preferences**: Customize writing style, tone, post length, and more
-   **Image generation**: Automatic image generation for posts using Google's Gemini API
-   **Persistent storage**: SQLite database for posts, preferences, and history

## Prerequisites

-   Python 3.9+
-   [uv](https://github.com/astral-sh/uv) package manager
-   Google API key with access to Gemini 2.0 Flash & 2.5 flash for image

## Setup

1. **Clone the repository:**

```bash
git clone <repository-url>
cd enhanced-linkedin-post-generator
```

2. **Install dependencies with uv:**

```bash
uv sync
```

3. **Set up environment variables:**

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

4. **Create your user profile:**

```bash
cp user.json.example user.json
# Edit user.json with your information and preferences
```

5. **Initialize the database:**

```bash
uv run python -c "from database import DatabaseManager; db = DatabaseManager(); db.initialize()"
```

Or create a user from JSON:

```bash
uv run python test_setup.py
```

## Running the Agent

### Using ADK Web Interface

Start the ADK web interface to interact with the agent:

```bash
uv run adk web
```

Then provide input in one of these formats:

-   **Topic**: "Generate a post about AI agents"
-   **URL**: "https://example.com/article"
-   **YouTube**: "https://www.youtube.com/watch?v=VIDEO_ID"
-   **Text**: Raw text content

### Programmatic Usage

```python
from linkedin_post_agent.agent import create_linkedin_post_pipeline

# Create the pipeline
pipeline = create_linkedin_post_pipeline()

# Run with input
result = pipeline.run("Generate a post about multi-agent systems")
print(result)
```

## User Configuration

Edit `user.json` to customize your preferences:

```json
{
    "name": "Your Name",
    "email": "your.email@example.com",
    "preferences": {
        "writing_style": "storytelling", // (formal/casual/technical/storytelling)
        "tone": "professional", // (enthusiastic/analytical/inspirational/professional)
        "post_length": { "min": 1300, "max": 1600 },
        "post_structure": "storytelling",
        "custom_instructions": "Write in first person, use bullet points for lists"
    }
}
```

### Writing Styles

-   `storytelling` - Narrative style with personal moments
-   `technical` - Fact-based, data-driven
-   `casual` - Conversational, friendly
-   `professional` - Balanced and polished
-   `formal` - Formal language, structured

### Post Structures

-   `storytelling` - Story section (50%+) + bullet points + question CTA
-   `list-based` - Bulleted list format
-   `problem-solution` - Problem → Solution → Takeaways
-   `narrative` - Chronological journey

## Project Structure

```
enhanced-linkedin-post-generator/
├── linkedin_post_agent/      # Main agent package
│   ├── agent.py              # Root SequentialAgent pipeline
│   └── subagents/            # Specialized agents
│       ├── input_processor/  # Input detection and extraction
│       ├── post_generator/   # Initial post generation
│       ├── post_reviewer/    # Quality checks
│       ├── post_refiner/     # Post refinement
│       ├── image_generator/   # Image generation
│       └── post_finalizer/   # Database persistence
├── database/                 # SQLite database management
├── services/                 # Business logic services
└── images/                   # Generated images storage
```

## How It Works

1. **Input Processing**: Detects input type and extracts content (URL scraping, YouTube transcripts, etc.)
2. **Preference Loading**: Loads user preferences and writing style
3. **Post Generation**: Creates initial post draft based on content and preferences
4. **Iterative Refinement**: LoopAgent reviews and refines post until quality standards are met
5. **Image Generation**: Generates LinkedIn-optimized image (1200x627px)
6. **Finalization**: Saves post and image to database

## Database

The SQLite database stores:

-   User profiles and preferences
-   Generated posts and versions
-   Post images and metadata
-   Source content references

View the database:

```bash
sqlite3 database.db
```

## Development

Run tests:

```bash
uv run python test_setup.py
uv run python test_input_processor.py
```
