"""
Logging module for the Sports Content Pipeline.

This provides structured logging for observability - tracking what happens
at each stage so you can debug failures and monitor performance.

Key concepts:
- Structured logging: Each log entry has consistent fields (timestamp, level, stage, etc.)
- Multiple outputs: Logs go to both console (for development) and file (for production)
- Context tracking: Each processed item has an ID that appears in all its log entries
"""

import logging
import json
from datetime import datetime
from pathlib import Path
import config

class PipelineLogger:
    """
    Custom logger for the content pipeline.
    
    This wraps Python's built-in logging with pipeline-specific functionality
    like tracking processing stages and writing structured JSON logs.
    """
    
    def __init__(self, log_dir=config.LOG_DIR, log_file=config.LOG_FILE):
        """
        Initialize the logger with both file and console outputs.
        
        Args:
            log_dir: Directory to store log files
            log_file: Name of the log file
        """
        # Create logs directory if it doesn't exist
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Set up the logger
        self.logger = logging.getLogger("SportsPipeline")
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate logs if logger already has handlers
        if not self.logger.handlers:
            # File handler - writes detailed logs to file
            file_handler = logging.FileHandler(f"{log_dir}/{log_file}")
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler - shows info/warning/error in terminal
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Format: [timestamp] LEVEL - message
            formatter = logging.Formatter(
                '[%(asctime)s] %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_stage(self, stage, status, input_id, details=None):
        """
        Log a pipeline stage completion.
        
        Args:
            stage: Which stage (CLASSIFY, EXTRACT, GENERATE, ROUTE)
            status: SUCCESS or FAILURE
            input_id: Unique identifier for the input being processed
            details: Additional information (dict)
        
        Example:
            logger.log_stage("CLASSIFY", "SUCCESS", "article_001", 
                           {"content_type": "match_report", "confidence": 0.95})
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "status": status,
            "input_id": input_id,
        }
        
        if details:
            log_entry["details"] = details
        
        # Log as JSON for easy parsing later
        message = json.dumps(log_entry)
        
        if status == "SUCCESS":
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_start(self, input_id, source=None):
        """Log the start of processing for a new item."""
        details = {"source": source} if source else {}
        self.log_stage("PROCESS_START", "SUCCESS", input_id, details)
    
    def log_complete(self, input_id, output_path):
        """Log successful completion of entire pipeline."""
        self.log_stage("PROCESS_COMPLETE", "SUCCESS", input_id, 
                      {"output_path": output_path})
    
    def log_error(self, input_id, stage, error):
        """Log an error that occurred during processing."""
        self.log_stage(stage, "FAILURE", input_id, 
                      {"error": str(error), "error_type": type(error).__name__})

# Create a singleton instance that can be imported by other modules
pipeline_logger = PipelineLogger()
