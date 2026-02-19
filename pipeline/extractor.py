"""
Metadata Extractor - Stage 2 of the Pipeline

This module extracts structured metadata from sports content.
The extraction logic is CONDITIONAL - different content types need different fields.

EXTRACTED FIELDS (vary by content type):
- teams: List of team names mentioned
- players: List of player names mentioned  
- competition: League/tournament name
- sentiment: positive/negative/neutral
- key_stats: Important numbers (score, transfer fee, injury timeline, etc.)

WHY CONDITIONAL EXTRACTION?
A match report needs: score, goalscorers, possession
A transfer needs: player, old club, new club, fee
An injury update needs: player, injury type, timeline

PROMPT ENGINEERING TECHNIQUES:
1. Content-type-specific prompts (different prompts for different content)
2. Explicit output schema (tell Claude exactly what JSON structure to return)
3. Handling missing data gracefully (not all fields exist in all content)
"""

import json
from anthropic import Anthropic
import config
from .logger import pipeline_logger
from .utils import extract_json_from_response, validate_dict_keys

class MetadataExtractor:
    """
    Extracts structured metadata from sports content using Claude API.
    """
    
    def __init__(self):
        """Initialize the Anthropic client."""
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def extract(self, content, content_type, input_id):
        """
        Extract metadata from content based on its type.
        
        Args:
            content: The raw text content
            content_type: The classification from Stage 1
            input_id: Unique identifier for tracking
            
        Returns:
            dict with metadata fields (structure varies by content_type)
        """
        
        # Build a content-type-specific prompt
        prompt = self._build_extraction_prompt(content, content_type)
        
        try:
            # Make the API call
            response = self.client.messages.create(
                model=config.MODEL_NAME,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract and parse response
            response_text = response.content[0].text
            
            # Use robust JSON extraction (handles markdown, preamble, etc.)
            metadata = extract_json_from_response(
                response_text, 
                context=f"metadata extraction for {input_id}"
            )
            
            # Validate we got a dict back
            if not isinstance(metadata, dict):
                raise ValueError(f"Expected a JSON object, got {type(metadata).__name__}")
            
            # Log success with key metadata
            pipeline_logger.log_stage(
                "EXTRACT", "SUCCESS", input_id,
                {
                    "teams_found": len(metadata.get("teams", [])),
                    "players_found": len(metadata.get("players", [])),
                    "competition": metadata.get("competition", "N/A")
                }
            )
            
            return metadata
            
        except json.JSONDecodeError as e:
            pipeline_logger.log_error(input_id, "EXTRACT", e)
            raise Exception(f"Failed to parse metadata extraction response: {e}")
        
        except Exception as e:
            pipeline_logger.log_error(input_id, "EXTRACT", e)
            raise Exception(f"Metadata extraction failed: {e}")
    
    def _build_extraction_prompt(self, content, content_type):
        """
        Build a content-type-specific extraction prompt.
        
        This demonstrates CONDITIONAL PROMPTING - the prompt changes based on
        what type of content we're processing.
        """
        
        # Base instruction (same for all types)
        base_prompt = f"""Extract structured metadata from this sports content.

<content>
{content}
</content>

"""
        
        # Type-specific extraction instructions
        if content_type == "match_report":
            specific_prompt = """Extract the following in JSON format:
{
    "teams": ["Team 1", "Team 2"],
    "players": ["Player names mentioned"],
    "competition": "League/tournament name",
    "sentiment": "positive/negative/neutral",
    "key_stats": {
        "score": "2-1",
        "goalscorers": ["Player names who scored"],
        "attendance": "75,000",
        "other_notable_stats": ["Any other important numbers"]
    }
}

If a field is not present in the content, use null or empty list as appropriate."""

        elif content_type == "transfer_news":
            specific_prompt = """Extract the following in JSON format:
{
    "teams": ["Clubs involved in transfer"],
    "players": ["Player(s) being transferred"],
    "competition": "League context if mentioned",
    "sentiment": "positive/negative/neutral",
    "key_stats": {
        "transfer_fee": "£50 million or unknown",
        "contract_length": "5 years or unknown",
        "previous_club": "Club name",
        "new_club": "Club name"
    }
}

If a field is not present, use null or empty list as appropriate."""

        elif content_type == "injury_update":
            specific_prompt = """Extract the following in JSON format:
{
    "teams": ["Team the player belongs to"],
    "players": ["Injured player(s)"],
    "competition": "League/tournament context",
    "sentiment": "negative (injuries are bad news)",
    "key_stats": {
        "injury_type": "hamstring/ACL/etc or unknown",
        "expected_absence": "6 weeks or unknown",
        "matches_to_miss": "Number or unknown",
        "injury_severity": "minor/moderate/severe"
    }
}

If a field is not present, use null or empty list as appropriate."""

        elif content_type == "opinion_piece":
            specific_prompt = """Extract the following in JSON format:
{
    "teams": ["Teams discussed"],
    "players": ["Players discussed"],
    "competition": "League/tournament context",
    "sentiment": "positive/negative/neutral (author's overall stance)",
    "key_stats": {
        "author_stance": "brief description of opinion",
        "main_arguments": ["Key points made"],
        "statistics_cited": ["Any numbers/stats mentioned"]
    }
}

If a field is not present, use null or empty list as appropriate."""

        else:  # other
            specific_prompt = """Extract whatever metadata is relevant in JSON format:
{
    "teams": ["Any teams mentioned"],
    "players": ["Any players mentioned"],
    "competition": "League/tournament if mentioned",
    "sentiment": "positive/negative/neutral",
    "key_stats": {
        "summary": "Brief description of what this content is about"
    }
}

If a field is not present, use null or empty list as appropriate."""

        return base_prompt + specific_prompt

# Create singleton instance
extractor = MetadataExtractor()
