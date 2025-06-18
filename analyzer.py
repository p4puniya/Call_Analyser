import openai
import os
import json
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from models import CallTranscript, AnalysisResult, CallAnalysisResponse
from prompt_builder import prompt_builder
from prefilter import failure_detector
from storage import save_analysis

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallAnalyzer:
    """Main analyzer class that processes call transcripts using LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.2
        self.max_retries = 3
    
    def analyze_transcript(self, transcript: CallTranscript) -> CallAnalysisResponse:
        """
        Analyze a single call transcript
        Returns a CallAnalysisResponse with analysis results
        """
        try:
            # First, check if this call needs analysis
            failure_check = failure_detector.is_call_possibly_failed(transcript)
            
            if not failure_check["failed"]:
                result = CallAnalysisResponse(
                    call_id=transcript.call_id,
                    status="skipped",
                    reason=f"No issues detected (confidence: {failure_check['confidence']:.2f})"
                )
                
                # Save the skipped result to storage
                save_analysis(result.dict())
                return result
            
            # Build the analysis prompt
            prompt = prompt_builder.build_analysis_prompt(transcript.dialog)
            
            # Get LLM analysis
            analysis_result = self._call_llm(prompt)
            
            if "error" in analysis_result:
                result = CallAnalysisResponse(
                    call_id=transcript.call_id,
                    status="error",
                    error=analysis_result["error"]
                )
                
                # Save the error result to storage
                save_analysis(result.dict())
                return result
            
            # Convert to AnalysisResult model
            analysis = AnalysisResult(
                intent=analysis_result.get("intent", "Unknown"),
                bot_response_summary=analysis_result.get("bot_response_summary", "No summary"),
                issue_detected=analysis_result.get("issue_detected", False),
                issue_reason=analysis_result.get("issue_reason", "No issues detected"),
                suggested_fix=analysis_result.get("suggested_fix", "No suggestions"),
                confidence_score=analysis_result.get("confidence_score", 0.5)
            )
            
            result = CallAnalysisResponse(
                call_id=transcript.call_id,
                status="analyzed",
                analysis=analysis
            )
            
            # Save the successful analysis to storage
            save_analysis(result.dict())
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing transcript {transcript.call_id}: {str(e)}")
            result = CallAnalysisResponse(
                call_id=transcript.call_id,
                status="error",
                error=str(e)
            )
            
            # Save the error result to storage
            save_analysis(result.dict())
            return result
    
    def analyze_batch(self, transcripts: List[CallTranscript]) -> List[CallAnalysisResponse]:
        """
        Analyze multiple call transcripts
        Returns a list of CallAnalysisResponse objects
        """
        results = []
        
        for transcript in transcripts:
            try:
                result = self.analyze_transcript(transcript)
                results.append(result)
                logger.info(f"Analyzed call {transcript.call_id}: {result.status}")
            except Exception as e:
                logger.error(f"Error in batch analysis for call {transcript.call_id}: {str(e)}")
                results.append(CallAnalysisResponse(
                    call_id=transcript.call_id,
                    status="error",
                    error=str(e)
                ))
        
        return results
    
    def generate_detailed_fixes(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed fix suggestions based on an analysis result
        """
        try:
            prompt = prompt_builder.build_fix_suggestion_prompt(analysis_result)
            return self._call_llm(prompt)
        except Exception as e:
            logger.error(f"Error generating detailed fixes: {str(e)}")
            return {"error": str(e)}
    
    def generate_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of multiple call analyses
        """
        try:
            prompt = prompt_builder.build_summary_prompt(analyses)
            return self._call_llm(prompt)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {"error": str(e)}
    
    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """
        Make a call to the LLM with retry logic
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that always responds with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=2000
                )
                
                reply = response.choices[0].message.content.strip()
                
                # Try to parse JSON response
                try:
                    return json.loads(reply)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON response on attempt {attempt + 1}: {e}")
                    if attempt == self.max_retries - 1:
                        return {"error": f"Failed to parse JSON response: {reply[:200]}..."}
                    continue
                    
            except Exception as e:
                logger.warning(f"LLM call failed on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return {"error": f"LLM call failed after {self.max_retries} attempts: {str(e)}"}
                continue
        
        return {"error": "Unexpected error in LLM call"}
    
    def get_analysis_stats(self, results: List[CallAnalysisResponse]) -> Dict[str, Any]:
        """
        Generate statistics from analysis results
        """
        total = len(results)
        analyzed = len([r for r in results if r.status == "analyzed"])
        skipped = len([r for r in results if r.status == "skipped"])
        errors = len([r for r in results if r.status == "error"])
        
        issues_detected = 0
        confidence_scores = []
        
        for result in results:
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
            "success_rate": analyzed / total if total > 0 else 0
        }

# Global instance for easy access
analyzer = CallAnalyzer() 