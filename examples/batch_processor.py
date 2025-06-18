#!/usr/bin/env python3
"""
Batch processor for Call Replay Analyzer

This script processes multiple call transcripts from a directory
and sends them to the analyzer API for processing.
"""

import os
import json
import requests
import logging
from typing import List, Dict, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchProcessor:
    """Process multiple call transcripts in batch"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.session = requests.Session()
    
    def process_directory(self, transcript_dir: str) -> Dict[str, Any]:
        """
        Process all JSON files in a directory as call transcripts
        
        Args:
            transcript_dir: Path to directory containing transcript JSON files
            
        Returns:
            Dictionary with processing results and statistics
        """
        transcript_dir = Path(transcript_dir)
        
        if not transcript_dir.exists():
            raise ValueError(f"Directory does not exist: {transcript_dir}")
        
        # Find all JSON files
        json_files = list(transcript_dir.glob("*.json"))
        
        if not json_files:
            logger.warning(f"No JSON files found in {transcript_dir}")
            return {"error": "No JSON files found"}
        
        logger.info(f"Found {len(json_files)} transcript files to process")
        
        # Load all transcripts
        transcripts = []
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    transcript_data = json.load(f)
                    transcripts.append(transcript_data)
                logger.info(f"Loaded transcript: {json_file.name}")
            except Exception as e:
                logger.error(f"Error loading {json_file}: {str(e)}")
        
        if not transcripts:
            return {"error": "No valid transcripts loaded"}
        
        # Process in batch
        return self.process_transcripts(transcripts)
    
    def process_transcripts(self, transcripts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a list of transcript dictionaries
        
        Args:
            transcripts: List of transcript dictionaries
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Prepare batch request
            batch_request = {
                "transcripts": transcripts
            }
            
            # Send to API
            logger.info(f"Sending {len(transcripts)} transcripts for batch analysis")
            
            response = self.session.post(
                f"{self.api_url}/analyze-batch",
                json=batch_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Batch analysis completed successfully")
                return result
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return {"error": f"API request failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return {"error": str(e)}
    
    def process_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single transcript file
        
        Args:
            file_path: Path to transcript JSON file
            
        Returns:
            Dictionary with analysis result
        """
        try:
            with open(file_path, 'r') as f:
                transcript_data = json.load(f)
            
            logger.info(f"Processing single transcript: {file_path}")
            
            response = self.session.post(
                f"{self.api_url}/analyze-call",
                json=transcript_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Single analysis completed successfully")
                return result
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return {"error": f"API request failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return {"error": str(e)}
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """
        Save analysis results to a JSON file
        
        Args:
            results: Analysis results dictionary
            output_file: Path to output file
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to: {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process call transcripts")
    parser.add_argument("input", help="Input directory or file path")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    
    args = parser.parse_args()
    
    processor = BatchProcessor(args.api_url)
    
    # Check if input is file or directory
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Process single file
        results = processor.process_single_file(args.input)
    elif input_path.is_dir():
        # Process directory
        results = processor.process_directory(args.input)
    else:
        logger.error(f"Input path does not exist: {args.input}")
        return
    
    # Print results
    if "error" in results:
        logger.error(f"Processing failed: {results['error']}")
    else:
        logger.info("Processing completed successfully")
        print(json.dumps(results, indent=2))
        
        # Save results if output file specified
        if args.output:
            processor.save_results(results, args.output)

if __name__ == "__main__":
    main() 