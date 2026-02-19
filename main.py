"""
Sports Content Pipeline - Main Orchestrator

This is the entry point that chains all pipeline stages together:
1. Classify content
2. Extract metadata
3. Generate headlines
4. Route to appropriate destination
5. Log everything for observability

ORCHESTRATION PATTERN:
- Sequential execution: Each stage depends on the previous one
- Error handling: If any stage fails, log it and skip downstream stages
- Context passing: Each stage's output becomes the next stage's input

This demonstrates the "chaining" concept - multiple AI calls in sequence,
each building on the previous one's output.
"""

import sys
from pathlib import Path
from datetime import datetime

# Import pipeline components
from pipeline.classifier import classifier
from pipeline.extractor import extractor
from pipeline.generator import generator
from pipeline.router import router
from pipeline.logger import pipeline_logger

class ContentPipeline:
    """
    Main pipeline orchestrator that chains all stages together.
    """
    
    def __init__(self):
        """Initialize pipeline components."""
        self.classifier = classifier
        self.extractor = extractor
        self.generator = generator
        self.router = router
        self.logger = pipeline_logger
    
    def process(self, content, input_id=None, source=None):
        """
        Process a single piece of content through the entire pipeline.
        
        Args:
            content: Raw text content to process
            input_id: Optional unique identifier (auto-generated if not provided)
            source: Optional source description for logging
            
        Returns:
            dict: Processing results with all intermediate outputs
            None: If processing failed at any stage
        """
        
        # Generate input_id if not provided
        if not input_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            input_id = f"content_{timestamp}"
        
        # Log start of processing
        self.logger.log_start(input_id, source)
        
        try:
            # STAGE 1: CLASSIFY
            print(f"\n{'='*60}")
            print(f"Processing: {input_id}")
            print(f"{'='*60}")
            print("\n[Stage 1/4] Classifying content...")
            
            classification = self.classifier.classify(content, input_id)
            content_type = classification["content_type"]
            
            print(f"✓ Content classified as: {content_type}")
            print(f"  Confidence: {classification['confidence']}")
            print(f"  Reasoning: {classification['reasoning']}")
            
            # STAGE 2: EXTRACT METADATA
            print("\n[Stage 2/4] Extracting metadata...")
            
            metadata = self.extractor.extract(content, content_type, input_id)
            
            print(f"✓ Metadata extracted:")
            print(f"  Teams: {', '.join(metadata.get('teams', [])) or 'None'}")
            print(f"  Players: {', '.join(metadata.get('players', [])[:3]) or 'None'}")
            print(f"  Competition: {metadata.get('competition', 'N/A')}")
            print(f"  Sentiment: {metadata.get('sentiment', 'N/A')}")
            
            # STAGE 3: GENERATE HEADLINES
            print("\n[Stage 3/4] Generating headlines...")
            
            headlines = self.generator.generate(content, metadata, content_type, input_id)
            
            print(f"✓ Headlines generated:")
            print(f"  Neutral: {headlines['neutral']}")
            print(f"  Fan-oriented: {headlines['fan_oriented']}")
            print(f"  Casual viewer: {headlines['casual_viewer']}")
            
            # STAGE 4: ROUTE TO DESTINATION
            print("\n[Stage 4/4] Routing to output...")
            
            output_path = self.router.route(
                input_id=input_id,
                content_type=content_type,
                original_content=content,
                classification=classification,
                metadata=metadata,
                headlines=headlines
            )
            
            print(f"✓ Content routed to: {output_path}")
            
            # Log completion
            self.logger.log_complete(input_id, output_path)
            
            print(f"\n{'='*60}")
            print(f"✓ Pipeline completed successfully for {input_id}")
            print(f"{'='*60}\n")
            
            # Return all results
            return {
                "input_id": input_id,
                "status": "success",
                "classification": classification,
                "metadata": metadata,
                "headlines": headlines,
                "output_path": output_path
            }
            
        except Exception as e:
            # If any stage fails, log and return None
            print(f"\n✗ Pipeline failed for {input_id}")
            print(f"  Error: {str(e)}\n")
            
            return {
                "input_id": input_id,
                "status": "failed",
                "error": str(e)
            }
    
    def process_batch(self, contents):
        """
        Process multiple pieces of content in sequence.
        
        Args:
            contents: List of dicts with keys 'content', 'input_id', 'source'
            
        Returns:
            list: Results for each item processed
        """
        results = []
        
        print(f"\n{'#'*60}")
        print(f"BATCH PROCESSING: {len(contents)} items")
        print(f"{'#'*60}\n")
        
        for item in contents:
            result = self.process(
                content=item.get("content"),
                input_id=item.get("input_id"),
                source=item.get("source")
            )
            results.append(result)
        
        # Print summary
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = len(results) - successful
        
        print(f"\n{'#'*60}")
        print(f"BATCH SUMMARY")
        print(f"{'#'*60}")
        print(f"Total processed: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        
        # Show routing statistics
        routing_stats = self.router.get_routing_stats()
        print(f"\nRouting statistics:")
        for content_type, count in routing_stats.items():
            if count > 0:
                print(f"  {content_type}: {count} items")
        
        print(f"{'#'*60}\n")
        
        return results

def main():
    """
    Main entry point for running the pipeline.
    """
    
    # Example usage - process a single piece of content
    pipeline = ContentPipeline()
    
    # Sample content for testing
    sample_content = """
    Manchester United secured a crucial 2-1 victory over Liverpool at Old Trafford 
    on Saturday evening. Goals from Marcus Rashford and Bruno Fernandes sealed the 
    win for the Red Devils, with Mohamed Salah scoring a consolation goal for the 
    visitors in the 85th minute. The victory moves United to within three points 
    of the top four in the Premier League standings. Manager Erik ten Hag praised 
    his team's resilience and determination in what was a hard-fought derby match.
    """
    
    result = pipeline.process(
        content=sample_content,
        input_id="sample_001",
        source="manual_test"
    )
    
    if result.get("status") == "success":
        print("✓ Test run completed successfully!")
        print(f"Check the outputs directory to see the routed content.")
    else:
        print("✗ Test run failed")
        print(f"Error: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
