"""
Content Classifier - Stage 1 of the Pipeline

This module classifies sports content into categories:
- match_report: Live or post-match reporting
- transfer_news: Player transfers, signings, contract news
- injury_update: Player injury reports, return timelines
- opinion_piece: Analysis, editorials, opinion columns
- other: Anything that doesn't fit the above

WHY CLASSIFY FIRST?
- Different content types need different extraction logic
- You can route to different downstream systems based on type
- You can skip expensive processing for irrelevant content

PROMPT ENGINEERING STRATEGY:
- Clear instructions with explicit categories
- Examples of each category (few-shot learning)
- Request structured output (JSON) for easy parsing
- Low temperature (0.3) for consistent classification
"""

import json
from anthropic import Anthropic
import config
from .logger import pipeline_logger
from .utils import extract_json_from_response, validate_dict_keys

class ContentClassifier:
    """
    Classifies sports content using Claude API.
    """
    
    def __init__(self):
        """Initialize the Anthropic client."""
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def classify(self, content, input_id):
        """
        Classify sports content into one of the predefined categories.
        
        Args:
            content: The raw text content to classify
            input_id: Unique identifier for tracking this item
            
        Returns:
            dict with keys:
                - content_type: The classification (match_report, transfer_news, etc.)
                - confidence: How confident the model is (0-1)
                - reasoning: Brief explanation of why this classification
                
        Raises:
            Exception: If API call fails or response is invalid
        """
        
        # Construct the classification prompt
        # Note: We use XML-style tags for clear structure (Claude performs well with this)
        prompt = f"""You are a sports content classifier. Analyze the following sports content and classify it into ONE of these categories:

1. match_report - Live game coverage, post-match reports, match summaries
2. transfer_news - Player transfers, signings, contract extensions, loan deals
3. injury_update - Player injuries, recovery timelines, fitness updates
4. opinion_piece - Analysis, editorials, opinion columns, tactical breakdowns
5. other - Anything that doesn't fit the above categories

<content>
{content}
</content>

Respond in JSON format with this exact structure:
{{
    "content_type": "one of the 5 categories above",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why you chose this category"
}}

Examples:
- "Manchester United defeated Liverpool 2-1 at Old Trafford..." → match_report
- "Chelsea have signed striker John Doe for £50m..." → transfer_news  
- "Star player ruled out for 6 weeks with hamstring injury..." → injury_update
- "Why Manchester United's tactics are failing this season..." → opinion_piece

Now classify the content above."""

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
            
            # Extract the text response
            response_text = response.content[0].text
            
            # Parse JSON response with robust extraction
            result = extract_json_from_response(
                response_text,
                context=f"classification for {input_id}"
            )
            
            # Validate the response has required fields
            validate_dict_keys(
                result, 
                ["content_type", "confidence", "reasoning"],
                context="Classification result"
            )
            
            # Validate content_type is one of our allowed categories
            valid_types = ["match_report", "transfer_news", "injury_update", "opinion_piece", "other"]
            if result["content_type"] not in valid_types:
                raise ValueError(f"Invalid content_type: {result['content_type']}")
            
            # Log success
            pipeline_logger.log_stage(
                "CLASSIFY", "SUCCESS", input_id,
                {
                    "content_type": result["content_type"],
                    "confidence": result["confidence"]
                }
            )
            
            return result
            
        except json.JSONDecodeError as e:
            # API returned non-JSON response
            pipeline_logger.log_error(input_id, "CLASSIFY", e)
            raise Exception(f"Failed to parse classification response as JSON: {e}")
        
        except Exception as e:
            # Any other error (API failure, validation error, etc.)
            pipeline_logger.log_error(input_id, "CLASSIFY", e)
            raise Exception(f"Classification failed: {e}")

# Create a singleton instance for easy importing
classifier = ContentClassifier()
