from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from typing import List, Dict, Any, Optional

from models import (
    CallTranscript, 
    CallAnalysisResponse, 
    BatchAnalysisRequest, 
    BatchAnalysisResponse
)
from analyzer import analyzer
from prefilter import failure_detector
from pipeline import pipeline
from storage import get_analysis_history, get_analysis_stats, clear_analysis_data, backup_analysis_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Call Replay Analyzer",
    description="AI-powered system for analyzing restaurant customer service calls and detecting failures",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Call Replay Analyzer API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "analyze_single": "/analyze-call",
            "analyze_batch": "/analyze-batch",
            "pipeline": "/pipeline",
            "ingest": "/ingest-transcript",
            "analysis_history": "/analysis-history",
            "analysis_stats": "/analysis-stats",
            "analysis_backup": "/analysis-backup",
            "call_history": "/analysis-history/{call_id}",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "call-replay-analyzer"
    }

@app.post("/analyze-call", response_model=CallAnalysisResponse)
async def analyze_single_call(transcript: CallTranscript):
    """
    Analyze a single call transcript
    
    This endpoint:
    1. Checks if the call likely failed using heuristics
    2. If failed, analyzes it with LLM to detect issues
    3. Returns detailed analysis with suggested fixes
    """
    try:
        logger.info(f"Analyzing call: {transcript.call_id}")
        
        # Analyze the transcript
        result = analyzer.analyze_transcript(transcript)
        
        logger.info(f"Call {transcript.call_id} analysis complete: {result.status}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing call {transcript.call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-batch", response_model=BatchAnalysisResponse)
async def analyze_batch_calls(request: BatchAnalysisRequest):
    """
    Analyze multiple call transcripts in batch
    
    This endpoint processes multiple calls efficiently and provides
    summary statistics for the batch.
    """
    try:
        logger.info(f"Starting batch analysis of {len(request.transcripts)} calls")
        
        # Analyze all transcripts
        results = analyzer.analyze_batch(request.transcripts)
        
        # Generate summary statistics
        stats = analyzer.get_analysis_stats(results)
        
        logger.info(f"Batch analysis complete. Stats: {stats}")
        
        return BatchAnalysisResponse(
            results=results,
            summary=stats
        )
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.post("/pipeline")
async def run_complete_pipeline(request: BatchAnalysisRequest):
    """
    🚀 COMPLETE PIPELINE: Analyze → Generate Fixes → Create Summary
    
    This is the main endpoint that does everything automatically:
    1. Analyzes all transcripts in the batch
    2. Generates detailed fixes for problematic calls
    3. Creates a comprehensive summary of all results
    4. Saves everything to files
    5. Returns complete results
    
    Perfect for processing large batches of calls with full analysis.
    """
    try:
        logger.info(f"Starting complete pipeline for {len(request.transcripts)} calls")
        
        # Run the complete pipeline
        result = await pipeline.process_batch_pipeline(request.transcripts)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        logger.info(f"Pipeline completed successfully. Pipeline ID: {result['pipeline_id']}")
        return result
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

@app.post("/ingest-transcript")
async def ingest_transcript(transcript: CallTranscript, metadata: Dict[str, Any] = None):
    """
    📥 Ingest a single transcript with optional metadata
    
    This endpoint:
    1. Receives a transcript (from Certus webhook, etc.)
    2. Stores it for processing
    3. Optionally triggers immediate analysis if marked as failed
    4. Returns status of ingestion
    
    Use this for real-time transcript ingestion from call systems.
    """
    try:
        logger.info(f"Ingesting transcript: {transcript.call_id}")
        
        # Ingest the transcript
        result = await pipeline.ingest_transcript(transcript, metadata)
        
        logger.info(f"Transcript {transcript.call_id} ingested: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"Error ingesting transcript {transcript.call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/prefilter-check")
async def check_prefilter(transcript: CallTranscript):
    """
    Check if a call would be flagged by the prefilter without doing full analysis
    
    Useful for testing the failure detection heuristics.
    """
    try:
        failure_check = failure_detector.is_call_possibly_failed(transcript)
        
        return {
            "call_id": transcript.call_id,
            "would_analyze": failure_check["failed"],
            "confidence": failure_check["confidence"],
            "reasons": failure_check["reasons"],
            "call_length": failure_check["call_length"]
        }
        
    except Exception as e:
        logger.error(f"Error in prefilter check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prefilter check failed: {str(e)}")

@app.post("/generate-fixes")
async def generate_detailed_fixes(analysis_result: Dict[str, Any]):
    """
    Generate detailed fix suggestions based on an analysis result
    
    This endpoint takes an existing analysis and generates more detailed,
    actionable suggestions for improving the bot.
    """
    try:
        logger.info("Generating detailed fixes")
        
        result = analyzer.generate_detailed_fixes(analysis_result)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating fixes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fix generation failed: {str(e)}")

@app.post("/generate-summary")
async def generate_summary(analyses: List[Dict[str, Any]]):
    """
    Generate a summary of multiple call analyses
    
    This endpoint provides insights across multiple calls to identify
    patterns and common issues.
    """
    try:
        logger.info(f"Generating summary for {len(analyses)} analyses")
        
        result = analyzer.generate_summary(analyses)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@app.get("/stats")
async def get_system_stats():
    """
    Get system statistics and configuration
    
    Returns information about the analyzer configuration and capabilities.
    """
    return {
        "model": analyzer.model,
        "temperature": analyzer.temperature,
        "max_retries": analyzer.max_retries,
        "frustration_keywords_count": len(failure_detector.frustration_keywords),
        "bot_confusion_patterns_count": len(failure_detector.bot_confusion_patterns),
        "short_response_threshold": failure_detector.short_response_threshold
    }

@app.get("/analysis-history")
async def get_analysis_history_endpoint(
    start_date: Optional[str] = Query(None, description="Start date in ISO format (e.g., 2024-01-01T00:00:00Z)"),
    end_date: Optional[str] = Query(None, description="End date in ISO format (e.g., 2024-12-31T23:59:59Z)"),
    call_id: Optional[str] = Query(None, description="Filter by specific call ID"),
    status: Optional[str] = Query(None, description="Filter by status: analyzed, skipped, or error"),
    limit: Optional[int] = Query(None, description="Maximum number of results to return", ge=1, le=1000)
):
    """
    📊 Get analysis history with optional filtering
    
    This endpoint retrieves all stored analysis results with powerful filtering options:
    - Date range filtering (start_date, end_date)
    - Call ID filtering
    - Status filtering (analyzed, skipped, error)
    - Result limiting
    
    Examples:
    - GET /analysis-history (all results)
    - GET /analysis-history?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z
    - GET /analysis-history?status=analyzed&limit=10
    - GET /analysis-history?call_id=call_123
    """
    try:
        logger.info(f"Retrieving analysis history with filters: start_date={start_date}, end_date={end_date}, call_id={call_id}, status={status}, limit={limit}")
        
        results = get_analysis_history(
            start_date=start_date,
            end_date=end_date,
            call_id=call_id,
            status=status,
            limit=limit
        )
        
        return {
            "total_results": len(results),
            "filters_applied": {
                "start_date": start_date,
                "end_date": end_date,
                "call_id": call_id,
                "status": status,
                "limit": limit
            },
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error retrieving analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis history: {str(e)}")

@app.get("/analysis-stats")
async def get_analysis_statistics():
    """
    📈 Get comprehensive statistics about stored analysis data
    
    Returns detailed statistics including:
    - Total number of analyses
    - Date range of stored data
    - Breakdown by status
    - Unique call IDs
    """
    try:
        stats = get_analysis_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving analysis statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@app.delete("/analysis-history")
async def clear_analysis_history():
    """
    🗑️ Clear all analysis history (use with caution!)
    
    This will permanently delete all stored analysis data.
    Consider creating a backup first using /analysis-backup.
    """
    try:
        success = clear_analysis_data()
        
        if success:
            return {"message": "Analysis history cleared successfully", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear analysis history")
        
    except Exception as e:
        logger.error(f"Error clearing analysis history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear analysis history: {str(e)}")

@app.post("/analysis-backup")
async def create_analysis_backup(backup_path: Optional[str] = None):
    """
    💾 Create a backup of analysis data
    
    Creates a timestamped backup of all analysis data.
    Useful before clearing data or for data migration.
    """
    try:
        success = backup_analysis_data(backup_path)
        
        if success:
            return {"message": "Analysis backup created successfully", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create analysis backup")
        
    except Exception as e:
        logger.error(f"Error creating analysis backup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@app.get("/analysis-history/{call_id}")
async def get_call_analysis_history(call_id: str):
    """
    📋 Get analysis history for a specific call ID
    
    Returns all analysis records for the specified call ID.
    Useful for tracking how a specific call was processed over time.
    """
    try:
        results = get_analysis_history(call_id=call_id)
        
        return {
            "call_id": call_id,
            "total_records": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error retrieving analysis history for call {call_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve call history: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 