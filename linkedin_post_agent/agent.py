"""Root agent for LinkedIn Post Generator - SequentialAgent pipeline with LoopAgent refinement."""

import os
from dotenv import load_dotenv

from google.adk.agents import LoopAgent, SequentialAgent

# Load environment variables
load_dotenv()

from .subagents.input_processor.agent import create_input_processor_agent
from .subagents.user_preference_loader.agent import create_user_preference_loader_agent
from .subagents.style_analyzer.agent import create_style_analyzer_agent
from .subagents.post_generator.agent import create_initial_post_generator_agent
from .subagents.post_reviewer.agent import create_post_reviewer_agent
from .subagents.post_refiner.agent import create_post_refiner_agent
from .subagents.image_generator.agent import create_image_generator_agent
from .subagents.post_finalizer.agent import create_post_finalizer_agent


def create_linkedin_post_pipeline() -> SequentialAgent:
    """
    Create the complete LinkedIn Post Generation Pipeline.

    This SequentialAgent orchestrates all sub-agents in the correct order:
    1. InputProcessorAgent - Processes user input (URL/topic/YouTube/text)
    2. UserPreferenceLoader - Loads user preferences from database
    3. StyleAnalyzerAgent - Analyzes LinkedIn profiles (if provided)
    4. InitialPostGenerator - Generates first draft
    5. RefinementLoop (LoopAgent) - Iteratively reviews and refines until quality is met
       - PostReviewer - Reviews post quality
       - PostRefiner - Refines post based on feedback
    6. ImageGeneratorAgent - Generates image for the final post
    7. PostFinalizerAgent - Saves the final post to database

    Returns:
        Configured SequentialAgent
    """
    # Create all sub-agents
    input_processor = create_input_processor_agent()
    preference_loader = create_user_preference_loader_agent()
    style_analyzer = create_style_analyzer_agent()
    post_generator = create_initial_post_generator_agent()
    post_reviewer = create_post_reviewer_agent()
    post_refiner = create_post_refiner_agent()
    image_generator = create_image_generator_agent()
    post_finalizer = create_post_finalizer_agent()

    # Create the Refinement Loop Agent
    refinement_loop = LoopAgent(
        name="PostRefinementLoop",
        max_iterations=5,  # Reduced from 10 to prevent excessive looping
        sub_agents=[
            post_reviewer,  # Review post quality
            post_refiner,  # Refine based on feedback
        ],
        description="Iteratively reviews and refines a LinkedIn post until quality requirements are met",
    )

    # Create SequentialAgent pipeline
    pipeline = SequentialAgent(
        name="LinkedInPostGenerationPipeline",
        sub_agents=[
            input_processor,  # Step 0: Process input
            preference_loader,  # Step 1: Load preferences
            style_analyzer,  # Step 2: Analyze style (optional)
            post_generator,  # Step 3: Generate initial post
            refinement_loop,  # Step 4: Review and refine in a loop
            image_generator,  # Step 5: Generate image for final post
            post_finalizer,  # Step 6: Save final post to database
        ],
        description="A pipeline that processes input, loads preferences, generates, iteratively refines, creates images, and saves posts to database",
    )

    return pipeline


# Create the root agent - the complete pipeline
root_agent = create_linkedin_post_pipeline()
