"""
Headline Generator - Stage 3 of the Pipeline

This module generates THREE versions of a headline for different audiences:
1. Neutral: For general sports news aggregators (ESPN, BBC Sport)
2. Fan-oriented: For team-specific apps/sites (Man United app, Lakers fansite)
3. Casual viewer: For people who need context (social media, casual fans)

WHY MULTIPLE HEADLINES?
Different audiences need different framing:
- Neutral: "Manchester United defeat Liverpool 2-1"
- Fan: "Red Devils secure vital derby victory!"
- Casual: "Man United beat rivals Liverpool in Premier League clash"

PROMPT ENGINEERING TECHNIQUES:
1. Persona-based prompting (imagine you're writing for X audience)
2. Style guidelines (tone, length, context level)
3. Leveraging metadata from Stage 2 (teams, players, sentiment)
"""

import json
from anthropic import Anthropic
import config
from .logger import pipeline_logger
from .utils import extract_json_from_response, validate_dict_keys

class HeadlineGenerator:
    """
    Generates audience-specific headlines using Claude API.
    """
    
    def __init__(self):
        """Initialize the Anthropic client."""
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def generate(self, content, metadata, content_type, input_id):
        """
        Generate three headline variations for different audiences.
        
        Args:
            content: The original content text
            metadata: Extracted metadata from Stage 2
            content_type: Classification from Stage 1
            input_id: Unique identifier for tracking
            
        Returns:
            dict with keys:
                - neutral: Objective headline for general audience
                - fan_oriented: Exciting headline for team supporters
                - casual_viewer: Context-rich headline for casual fans
        """
        
        # Build the generation prompt using metadata for context
        prompt = self._build_generation_prompt(content, metadata, content_type)
        
        try:
            # Make the API call
            response = self.client.messages.create(
                model=config.MODEL_NAME,
                max_tokens=config.MAX_TOKENS,
                temperature=0.7,  # Higher temperature for creativity in headline writing
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract and parse response
            response_text = response.content[0].text
            
            # Parse JSON response with robust extraction
            headlines = extract_json_from_response(
                response_text,
                context=f"headline generation for {input_id}"
            )
            
            # Validate structure
            validate_dict_keys(
                headlines,
                ["neutral", "fan_oriented", "casual_viewer"],
                context="Headline generation result"
            )
            
            # Log success
            pipeline_logger.log_stage(
                "GENERATE", "SUCCESS", input_id,
                {"headline_count": 3}
            )
            
            return headlines
            
        except json.JSONDecodeError as e:
            pipeline_logger.log_error(input_id, "GENERATE", e)
            raise Exception(f"Failed to parse headline generation response: {e}")
        
        except Exception as e:
            pipeline_logger.log_error(input_id, "GENERATE", e)
            raise Exception(f"Headline generation failed: {e}")
    
    def _build_generation_prompt(self, content, metadata, content_type):
        """
        Build a context-aware prompt for headline generation.
        
        Uses metadata to inform headline writing - this is where CHAINING shows value.
        Stage 2's output makes Stage 3's output better.
        """
        
        # Extract useful context from metadata
        teams = metadata.get("teams", [])
        players = metadata.get("players", [])
        competition = metadata.get("competition", "")
        sentiment = metadata.get("sentiment", "neutral")
        
        # Build context string
        context = f"""
Content type: {content_type}
Teams involved: {', '.join(teams) if teams else 'N/A'}
Key players: {', '.join(players[:3]) if players else 'N/A'}  
Competition: {competition if competition else 'N/A'}
Sentiment: {sentiment}
"""
        
        prompt = f"""You are a sports headline writer. Generate THREE versions of a headline for this content.

CONTEXT:
{context}

CONTENT:
<content>
{content[:500]}...
</content>

Generate three headlines in JSON format:

{{
    "neutral": "Objective, factual headline for general sports news sites (BBC Sport, ESPN). Formal tone. 8-12 words.",
    "fan_oriented": "Exciting headline for team supporters. Can use nicknames, show emotion. 6-10 words.",
    "casual_viewer": "Context-rich headline for casual fans who may not follow closely. Explain what's significant. 10-15 words."
}}

GUIDELINES:
- Neutral: Focus on facts, scores, key events. No emotion.
- Fan-oriented: Celebrate/commiserate with fans. Use team nicknames ("Red Devils", "Lakers"). Show passion.
- Casual viewer: Add context they need ("rivals", "title race", "playoff push"). Explain significance.

Examples for a Man United win:
{{
    "neutral": "Manchester United defeat Liverpool 2-1 at Old Trafford",
    "fan_oriented": "Red Devils sink Liverpool with late winner!",
    "casual_viewer": "Manchester United beat historic rivals Liverpool 2-1 in crucial Premier League match"
}}

Now generate headlines for the content above:"""

        return prompt

# Create singleton instance
generator = HeadlineGenerator()
