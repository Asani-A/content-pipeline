"""
Utility functions for the Sports Content Pipeline.

This module contains helper functions used across multiple pipeline components.
"""

import json
import re

def extract_json_from_response(response_text, context="API response"):
    """
    Robustly extract JSON from an LLM API response.
    
    LLMs sometimes wrap JSON in markdown, add preamble text, or include
    trailing commentary. This function handles common cases.
    
    Args:
        response_text: The raw text response from the API
        context: Description of what this is for (used in error messages)
        
    Returns:
        dict or list: The parsed JSON object
        
    Raises:
        ValueError: If no valid JSON can be extracted
    """
    
    if not response_text or not response_text.strip():
        raise ValueError(f"Empty response received for {context}")
    
    original_text = response_text
    cleaned_text = response_text.strip()
    
    # Strategy 1: Try parsing as-is
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Remove markdown code fences (```json ... ```)
    if "```" in cleaned_text:
        # Find content between ``` markers
        pattern = r'```(?:json)?\s*\n(.*?)\n```'
        matches = re.findall(pattern, cleaned_text, re.DOTALL)
        
        if matches:
            # Try parsing the first match
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Alternative: Just remove all ``` lines
        lines = cleaned_text.split('\n')
        cleaned_lines = [line for line in lines if not line.strip().startswith('```')]
        try:
            return json.loads('\n'.join(cleaned_lines))
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Look for JSON object/array markers and extract
    # Find the first { or [ and last } or ]
    first_brace = cleaned_text.find('{')
    first_bracket = cleaned_text.find('[')
    
    # Determine which comes first (or only one exists)
    if first_brace == -1 and first_bracket == -1:
        raise ValueError(
            f"No JSON found in {context}. Response: {original_text[:200]}..."
        )
    
    if first_brace == -1:
        start = first_bracket
        end_char = ']'
    elif first_bracket == -1:
        start = first_brace
        end_char = '}'
    else:
        start = min(first_brace, first_bracket)
        end_char = '}' if start == first_brace else ']'
    
    # Find the matching closing brace/bracket
    end = cleaned_text.rfind(end_char)
    
    if end == -1 or end < start:
        raise ValueError(
            f"Malformed JSON in {context}. Response: {original_text[:200]}..."
        )
    
    json_str = cleaned_text[start:end+1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON from {context}. "
            f"Extracted: {json_str[:100]}... "
            f"Error: {e}"
        )


def validate_dict_keys(data, required_keys, context="data"):
    """
    Validate that a dictionary contains required keys.
    
    Args:
        data: Dictionary to validate
        required_keys: List of required key names
        context: Description for error messages
        
    Raises:
        ValueError: If any required keys are missing
    """
    if not isinstance(data, dict):
        raise ValueError(f"{context} must be a dictionary, got {type(data)}")
    
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        raise ValueError(
            f"{context} missing required keys: {missing_keys}. "
            f"Available keys: {list(data.keys())}"
        )
