"""
Call Replay Analyzer Pipeline

This module provides a seamless pipeline for processing call transcripts
with automatic analysis, fix generation, and summary creation.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from models import CallTranscript, CallAnalysisResponse
from analyzer import analyzer
from prefilter import failure_detector

logger = logging.getLogger(__name__)

class CallPipeline:
    """Orchestrates the complete call analysis workflow"""
    
    def __init__(self, storage_path: str = "data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_batch_pipeline(self, transcripts: List[CallTranscript]) -> Dict[str, Any]:
        """
        Complete pipeline: analyze batch → generate fixes → create summary
        
        This is the main endpoint that does everything automatically.
        """
        try:
            logger.info(f"Starting pipeline for {len(transcripts)} transcripts")
            
            # Step 1: Analyze all transcripts
            analysis_results = await self._analyze_batch(transcripts)
            
            # Step 2: Generate detailed fixes for problematic calls
            fix_results = await self._generate_fixes_for_issues(analysis_results)
            
            # Step 3: Create comprehensive summary
            summary = await self._generate_comprehensive_summary(analysis_results, fix_results)
            
            # Step 4: Save results
            pipeline_result = {
                "pipeline_id": f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "input_count": len(transcripts),
                "analysis_results": analysis_results,
                "fix_results": fix_results,
                "summary": summary,
                "statistics": self._calculate_pipeline_stats(analysis_results)
            }
            
            # Save to file
            await self._save_pipeline_result(pipeline_result)
            
            logger.info(f"Pipeline completed successfully. Processed {len(transcripts)} calls.")
            return pipeline_result
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            return {"error": str(e), "pipeline_id": f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}
    
    async def ingest_transcript(self, transcript: CallTranscript, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ingest a single transcript with optional metadata
        
        This endpoint receives transcripts and can trigger analysis based on metadata.
        """
        try:
            # Add metadata
            if metadata:
                transcript.metadata = metadata
            
            # Store transcript
            await self._store_transcript(transcript)
            
            # Check if immediate analysis is needed
            should_analyze = metadata.get("status") == "failed" if metadata else False
            
            if should_analyze:
                # Trigger background analysis
                asyncio.create_task(self._analyze_single_background(transcript))
                return {
                    "status": "received_and_analyzing",
                    "call_id": transcript.call_id,
                    "message": "Transcript received and analysis started"
                }
            else:
                return {
                    "status": "received",
                    "call_id": transcript.call_id,
                    "message": "Transcript stored for batch processing"
                }
                
        except Exception as e:
            logger.error(f"Error ingesting transcript {transcript.call_id}: {str(e)}")
            return {"error": str(e), "call_id": transcript.call_id}
    
    async def _analyze_batch(self, transcripts: List[CallTranscript]) -> List[CallAnalysisResponse]:
        """Analyze a batch of transcripts"""
        logger.info(f"Analyzing {len(transcripts)} transcripts")
        
        # Use the existing analyzer
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            self.executor, 
            analyzer.analyze_batch, 
            transcripts
        )
        
        return results
    
    async def _generate_fixes_for_issues(self, analysis_results: List[CallAnalysisResponse]) -> Dict[str, Any]:
        """Generate detailed fixes for calls with issues"""
        logger.info("Generating detailed fixes for problematic calls")
        
        fix_results = {}
        
        for result in analysis_results:
            if result.status == "analyzed" and result.analysis and result.analysis.issue_detected:
                try:
                    # Convert analysis to dict for fix generation
                    analysis_dict = {
                        "intent": result.analysis.intent,
                        "bot_response_summary": result.analysis.bot_response_summary,
                        "issue_detected": result.analysis.issue_detected,
                        "issue_reason": result.analysis.issue_reason,
                        "suggested_fix": result.analysis.suggested_fix,
                        "confidence_score": result.analysis.confidence_score
                    }
                    
                    # Generate detailed fixes
                    loop = asyncio.get_event_loop()
                    fixes = await loop.run_in_executor(
                        self.executor,
                        analyzer.generate_detailed_fixes,
                        analysis_dict
                    )
                    
                    fix_results[result.call_id] = fixes
                    
                except Exception as e:
                    logger.error(f"Error generating fixes for {result.call_id}: {str(e)}")
                    fix_results[result.call_id] = {"error": str(e)}
        
        return fix_results
    
    async def _generate_comprehensive_summary(self, analysis_results: List[CallAnalysisResponse], fix_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive summary of all results"""
        logger.info("Generating comprehensive summary")
        
        # Extract analysis objects for summary
        analysis_objects = []
        for result in analysis_results:
            if result.analysis:
                analysis_objects.append({
                    "intent": result.analysis.intent,
                    "bot_response_summary": result.analysis.bot_response_summary,
                    "issue_detected": result.analysis.issue_detected,
                    "issue_reason": result.analysis.issue_reason,
                    "suggested_fix": result.analysis.suggested_fix,
                    "confidence_score": result.analysis.confidence_score
                })
        
        if analysis_objects:
            loop = asyncio.get_event_loop()
            summary = await loop.run_in_executor(
                self.executor,
                analyzer.generate_summary,
                analysis_objects
            )
        else:
            summary = {"error": "No analysis results to summarize"}
        
        return summary
    
    async def _analyze_single_background(self, transcript: CallTranscript):
        """Background analysis for single transcript"""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                analyzer.analyze_transcript,
                transcript
            )
            
            # Store the result
            await self._store_analysis_result(transcript.call_id, result)
            
            logger.info(f"Background analysis completed for {transcript.call_id}")
            
        except Exception as e:
            logger.error(f"Background analysis failed for {transcript.call_id}: {str(e)}")
    
    async def _store_transcript(self, transcript: CallTranscript):
        """Store transcript to file"""
        try:
            transcript_file = self.storage_path / f"transcript_{transcript.call_id}.json"
            with open(transcript_file, 'w') as f:
                json.dump(transcript.dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error storing transcript {transcript.call_id}: {str(e)}")
    
    async def _store_analysis_result(self, call_id: str, result: CallAnalysisResponse):
        """Store analysis result to file"""
        try:
            result_file = self.storage_path / f"analysis_{call_id}.json"
            with open(result_file, 'w') as f:
                json.dump(result.dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error storing analysis result {call_id}: {str(e)}")
    
    async def _save_pipeline_result(self, pipeline_result: Dict[str, Any]):
        """Save complete pipeline result"""
        try:
            pipeline_id = pipeline_result["pipeline_id"]
            result_file = self.storage_path / f"pipeline_{pipeline_id}.json"
            with open(result_file, 'w') as f:
                json.dump(pipeline_result, f, indent=2, default=str)
            logger.info(f"Pipeline result saved: {result_file}")
        except Exception as e:
            logger.error(f"Error saving pipeline result: {str(e)}")
    
    def _calculate_pipeline_stats(self, analysis_results: List[CallAnalysisResponse]) -> Dict[str, Any]:
        """Calculate comprehensive pipeline statistics"""
        total = len(analysis_results)
        analyzed = len([r for r in analysis_results if r.status == "analyzed"])
        skipped = len([r for r in analysis_results if r.status == "skipped"])
        errors = len([r for r in analysis_results if r.status == "error"])
        
        issues_detected = 0
        confidence_scores = []
        
        for result in analysis_results:
            if result.analysis:
                if result.analysis.issue_detected:
                    issues_detected += 1
                confidence_scores.append(result.analysis.confidence_score)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            "total_calls": total,
            "analyzed": analyzed,
            "skipped": skipped,
            "errors": errors,
            "issues_detected": issues_detected,
            "issue_rate": issues_detected / analyzed if analyzed > 0 else 0,
            "average_confidence": avg_confidence,
            "success_rate": analyzed / total if total > 0 else 0,
            "processing_efficiency": (analyzed + skipped) / total if total > 0 else 0
        }

# Global pipeline instance
pipeline = CallPipeline() 