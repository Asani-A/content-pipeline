"""
Content Router - Output Management

This module routes processed content to different destinations based on content type.
In production, these "destinations" might be:
- Different database tables
- Different microservices  
- Different content management systems
- Different API endpoints

For this pipeline, we simulate routing by saving to different directories.

WHY ROUTING MATTERS:
- Match reports go to the live scores system
- Transfer news goes to the transfer tracker
- Injury updates go to fantasy football APIs
- Opinion pieces go to the editorial CMS

Each downstream system needs different content types.
"""

import json
from pathlib import Path
from datetime import datetime
import config
from .logger import pipeline_logger

class ContentRouter:
    """
    Routes processed content to appropriate output destinations.
    """
    
    def __init__(self):
        """Initialize router and ensure output directories exist."""
        self.output_dir = Path(config.OUTPUT_DIR)
        self.content_type_dirs = config.CONTENT_TYPE_DIRS
        
        # Create all output directories if they don't exist
        for dir_name in self.content_type_dirs.values():
            (self.output_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    def route(self, input_id, content_type, original_content, classification, metadata, headlines):
        """
        Route processed content to the appropriate destination.
        
        Args:
            input_id: Unique identifier for this content
            content_type: Classification result
            original_content: The raw input content
            classification: Full classification result from Stage 1
            metadata: Extracted metadata from Stage 2
            headlines: Generated headlines from Stage 3
            
        Returns:
            str: Path where the file was saved
        """
        
        try:
            # Determine output directory based on content type
            # If content_type not in our mapping, use "other"
            dir_name = self.content_type_dirs.get(content_type, "other")
            output_path = self.output_dir / dir_name
            
            # Create the output package - all pipeline results in one JSON
            output_package = {
                "input_id": input_id,
                "processed_at": datetime.now().isoformat(),
                "content_type": content_type,
                "classification": classification,
                "metadata": metadata,
                "headlines": headlines,
                "original_content": original_content,
                "pipeline_version": "1.0"  # For tracking if you update the pipeline
            }
            
            # Create filename with timestamp for uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{input_id}_{timestamp}.json"
            file_path = output_path / filename
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output_package, f, indent=2, ensure_ascii=False)
            
            # Log successful routing
            pipeline_logger.log_stage(
                "ROUTE", "SUCCESS", input_id,
                {
                    "destination": dir_name,
                    "output_file": str(file_path)
                }
            )
            
            return str(file_path)
            
        except Exception as e:
            # Routing should rarely fail (just file I/O), but catch it anyway
            pipeline_logger.log_error(input_id, "ROUTE", e)
            raise Exception(f"Routing failed: {e}")
    
    def get_routing_stats(self):
        """
        Get statistics about routed content (useful for monitoring).
        
        Returns:
            dict: Count of files in each output directory
        """
        stats = {}
        for content_type, dir_name in self.content_type_dirs.items():
            dir_path = self.output_dir / dir_name
            # Count .json files in directory
            file_count = len(list(dir_path.glob("*.json")))
            stats[content_type] = file_count
        
        return stats

# Create singleton instance
router = ContentRouter()
