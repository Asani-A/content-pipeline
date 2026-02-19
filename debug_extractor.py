"""
Debug script to test metadata extraction in isolation.

This helps us see exactly what Claude is returning so we can fix the parsing.
"""

import sys
import os

# Add parent directory to path so we can import pipeline modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.extractor import extractor

# Simple test content
test_content = """
Manchester United secured a crucial 2-1 victory over Liverpool at Old Trafford 
on Saturday evening. Goals from Marcus Rashford and Bruno Fernandes sealed the 
win for the Red Devils, with Mohamed Salah scoring a consolation goal for the 
visitors in the 85th minute.
"""

print("="*70)
print("DEBUG: Testing Metadata Extraction")
print("="*70)

try:
    result = extractor.extract(
        content=test_content,
        content_type="match_report",
        input_id="debug_test"
    )
    
    print("\n✓ SUCCESS! Extraction worked.")
    print(f"\nExtracted metadata:")
    import json
    print(json.dumps(result, indent=2))
    
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    print(f"\nThis helps us understand what needs to be fixed.")

print("\n" + "="*70)
