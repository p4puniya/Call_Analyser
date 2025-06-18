from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from typing import List, Dict, Any

from models import (
    CallTranscript, 
    CallAnalysisResponse, 
    BatchAnalysisRequest, 
    BatchAnalysisResponse
)
from analyzer import analyzer
from prefilter import failure_detector

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