"""
Configuration file for the Sports Content Pipeline.

This module handles API keys, model settings, and pipeline configuration.
In a real production system, you'd use environment variables or a secrets manager.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Anthropic API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model Configuration
# Using Claude Sonnet for a balance of speed and quality
# For production at scale, you might use Haiku for classification (faster/cheaper)
# and Sonnet for generation (higher quality)
MODEL_NAME = "claude-sonnet-4-20250514"

# Pipeline Settings
MAX_TOKENS = 2000  # Maximum tokens for each API response
TEMPERATURE = 0.3   # Lower temperature for more consistent/deterministic outputs

# Logging Configuration
LOG_DIR = "logs"
LOG_FILE = "pipeline_processing.log"

# Output Routing Configuration
OUTPUT_DIR = "outputs"
CONTENT_TYPE_DIRS = {
    "match_report": "match_reports",
    "transfer_news": "transfer_news",
    "injury_update": "injury_updates",
    "opinion_piece": "opinion_pieces",
    "other": "other"  # Fallback for unclassified content
}

# Validate API key is present
if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY not found. Please set it in your .env file or environment variables."
    )
