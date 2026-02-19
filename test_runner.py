"""
Test Runner - Demonstrates Pipeline with Diverse Inputs

This file runs the pipeline on 5 different test cases to prove it works
across different content types and scenarios:

1. Match Report (Manchester United) - Happy path
2. Transfer News (Lakers) - Basketball content  
3. Injury Update - Negative sentiment, medical terminology
4. Opinion Piece - Subjective content, analysis
5. Edge Case - Ambiguous content that's hard to classify

WHY 5 DIVERSE TESTS?
- Proves the pipeline isn't brittle
- Shows it handles both football and basketball
- Demonstrates different sentiment handling
- Tests edge cases (not just happy path)
- Portfolio projects need thorough testing to look production-ready
"""

from main import ContentPipeline

# Initialize pipeline
pipeline = ContentPipeline()

# Test Case 1: Match Report (Football)
test_1_content = """
Manchester United secured a crucial 2-1 victory over Liverpool at Old Trafford 
on Saturday evening in a thrilling Premier League encounter. Marcus Rashford 
opened the scoring in the 23rd minute with a clinical finish after a brilliant 
through ball from Bruno Fernandes. Fernandes himself doubled the lead just 
before halftime with a stunning 25-yard strike. Liverpool pulled one back 
through Mohamed Salah in the 85th minute, but it was too little too late. 

The win moves United to within three points of the top four, keeping their 
Champions League hopes alive. Manager Erik ten Hag praised his team's 
resilience, stating "This was a statement win against one of our biggest 
rivals." The attendance of 74,879 witnessed one of the season's most 
important derby clashes.
"""

# Test Case 2: Transfer News (Basketball)
test_2_content = """
The Los Angeles Lakers have completed the signing of point guard James Smith 
from the Brooklyn Nets in a blockbuster mid-season trade deal. The 27-year-old 
joins the Lakers on a four-year contract worth approximately $85 million. 

Lakers General Manager Rob Pelinka said: "James brings exactly what we need - 
elite playmaking and championship experience. He's going to be a perfect fit 
alongside LeBron and AD." Smith averaged 18.5 points and 8.2 assists per game 
this season before the trade.

The Nets received two first-round draft picks and guard Dennis Johnson in 
return. Smith is expected to make his Lakers debut on Tuesday against the 
Phoenix Suns at Crypto.com Arena.
"""

# Test Case 3: Injury Update (Football)
test_3_content = """
Manchester United have confirmed that midfielder Casemiro will be sidelined 
for approximately eight weeks after sustaining a hamstring injury during 
training on Wednesday. The Brazilian midfielder will undergo surgery next 
week and is expected to miss crucial fixtures including the FA Cup semifinal 
and several key Premier League matches.

Medical staff have classified the injury as a Grade 2 hamstring tear, which 
typically requires 6-8 weeks of recovery. Manager Erik ten Hag described the 
news as "a significant blow to our squad depth" at a critical point in the 
season. Casemiro had been in excellent form recently, starting in United's 
last 12 consecutive matches. The club is now exploring short-term options 
in the January transfer window to cover the defensive midfield position.
"""

# Test Case 4: Opinion Piece (Basketball)
test_4_content = """
Why the Lakers' Championship Window Is Closing Faster Than We Think

LeBron James turns 40 next season. Anthony Davis has played 70+ games just 
twice in his career. The Lakers' championship window isn't just closing - 
it's slamming shut before our eyes, and the front office seems paralyzed 
to act.

Let's be honest: this roster, as currently constructed, is not good enough. 
The role players are inconsistent at best, and the lack of a reliable third 
scorer is glaring. While teams like Boston and Denver have built deep, 
balanced rosters, the Lakers continue to mortgage their future for aging 
veterans who may not even make it through a playoff run.

The analytics paint an even bleaker picture. The Lakers rank 22nd in 
defensive efficiency and 18th in three-point shooting - two metrics that 
are non-negotiable in today's NBA. Unless dramatic changes are made this 
offseason, we may have already seen the last Lakers championship of the 
LeBron era.
"""

# Test Case 5: Edge Case - Ambiguous/Mixed Content
test_5_content = """
Manchester United Training Ground Incident Raises Questions

Footage emerged yesterday showing a heated exchange between manager Erik ten Hag 
and forward Cristiano Ronaldo during training at Carrington. While the club has 
downplayed the incident as "a normal competitive moment," sources close to the 
squad suggest tensions have been building for weeks.

Ronaldo, who recently returned from injury, has started just one of United's 
last five matches. Some analysts speculate this could indicate an imminent 
January transfer, with clubs in Saudi Arabia reportedly interested. However, 
other insiders claim the reduced playing time is purely tactical and related 
to United's recent shift to a more pressing-based system.

The situation remains fluid, with neither the club nor Ronaldo's representatives 
willing to comment publicly. Whatever the truth, it's clear that Manchester 
United's season could hinge on resolving this uncertainty quickly.
"""

# Test cases formatted for batch processing
test_cases = [
    {
        "content": test_1_content,
        "input_id": "test_001_match_report",
        "source": "test_suite"
    },
    {
        "content": test_2_content,
        "input_id": "test_002_transfer_news",
        "source": "test_suite"
    },
    {
        "content": test_3_content,
        "input_id": "test_003_injury_update",
        "source": "test_suite"
    },
    {
        "content": test_4_content,
        "input_id": "test_004_opinion_piece",
        "source": "test_suite"
    },
    {
        "content": test_5_content,
        "input_id": "test_005_edge_case",
        "source": "test_suite"
    }
]

def run_tests():
    """
    Run all test cases through the pipeline.
    """
    print("\n" + "="*70)
    print("SPORTS CONTENT PIPELINE - TEST SUITE")
    print("="*70)
    print("\nRunning 5 diverse test cases to demonstrate pipeline robustness...")
    print("\nTest Coverage:")
    print("  1. Match Report (Football) - Standard happy path")
    print("  2. Transfer News (Basketball) - Cross-sport handling")
    print("  3. Injury Update (Football) - Negative sentiment, medical terms")
    print("  4. Opinion Piece (Basketball) - Subjective analysis")
    print("  5. Edge Case - Ambiguous/mixed content type")
    print("\n" + "="*70 + "\n")
    
    # Run batch processing
    results = pipeline.process_batch(test_cases)
    
    # Detailed result analysis
    print("\n" + "="*70)
    print("DETAILED TEST RESULTS")
    print("="*70 + "\n")
    
    for i, result in enumerate(results, 1):
        test_id = result.get("input_id")
        status = result.get("status")
        
        print(f"Test {i}: {test_id}")
        print(f"Status: {'✓ PASSED' if status == 'success' else '✗ FAILED'}")
        
        if status == "success":
            classification = result.get("classification", {})
            headlines = result.get("headlines", {})
            
            print(f"  - Classified as: {classification.get('content_type')}")
            print(f"  - Confidence: {classification.get('confidence')}")
            print(f"  - Sample headline: {headlines.get('neutral', 'N/A')[:80]}...")
        else:
            print(f"  - Error: {result.get('error')}")
        
        print()
    
    # Success rate
    success_count = sum(1 for r in results if r.get("status") == "success")
    success_rate = (success_count / len(results)) * 100
    
    print("="*70)
    print(f"SUCCESS RATE: {success_count}/{len(results)} ({success_rate:.1f}%)")
    print("="*70 + "\n")
    
    return results

if __name__ == "__main__":
    results = run_tests()
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Check the 'outputs/' directory to see routed content")
    print("2. Check the 'logs/pipeline_processing.log' file for detailed logging")
    print("3. Inspect individual output files to see full metadata and headlines")
    print("\nEach output file contains:")
    print("  - Original content")
    print("  - Classification results")
    print("  - Extracted metadata")
    print("  - All three headline variations")
    print("  - Processing timestamps")
    print("\n" + "="*70 + "\n")
