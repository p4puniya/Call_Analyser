from typing import List
from models import DialogueTurn

class PromptBuilder:
    """Builds structured prompts for LLM analysis of call transcripts"""
    
    def __init__(self):
        self.system_prompt = """You are an expert AI call quality analyst specializing in restaurant customer service calls. 
Your job is to analyze conversations between customers and AI bots to identify issues and suggest improvements.

Key areas to focus on:
1. Intent recognition accuracy
2. Response relevance and helpfulness
3. Conversation flow and naturalness
4. Problem resolution effectiveness
5. Customer satisfaction indicators

Always respond in valid JSON format with the exact fields specified."""

    def build_analysis_prompt(self, dialog: List[DialogueTurn]) -> str:
        """Build a comprehensive analysis prompt for a call transcript"""
        
        # Format the conversation
        conversation_text = self._format_conversation(dialog)
        
        prompt = f"""{self.system_prompt}

ANALYZE THIS RESTAURANT CUSTOMER SERVICE CALL:

{conversation_text}

Please provide a detailed analysis in the following JSON format:

{{
    "intent": "Brief description of what the customer was trying to accomplish",
    "bot_response_summary": "Summary of how the bot responded throughout the conversation",
    "issue_detected": true/false,
    "issue_reason": "Detailed explanation of what went wrong (or 'No issues detected' if successful)",
    "suggested_fix": "Specific, actionable suggestions to improve the bot's performance",
    "confidence_score": 0.0-1.0,
    "severity": "low/medium/high",
    "categories": ["list", "of", "issue", "categories"],
    "key_moments": [
        {{
            "turn": "turn number",
            "speaker": "user/bot",
            "issue": "description of what happened"
        }}
    ]
}}

Focus on:
- Did the bot understand the customer's intent correctly?
- Were the responses relevant and helpful?
- Did the conversation flow naturally?
- Was the customer's problem resolved?
- What specific improvements would make this better?

Respond only with valid JSON."""

        return prompt.strip()
    
    def build_fix_suggestion_prompt(self, analysis_result: dict) -> str:
        """Build a prompt specifically for generating detailed fix suggestions"""
        
        prompt = f"""{self.system_prompt}

BASED ON THIS ANALYSIS, GENERATE SPECIFIC FIXES:

{analysis_result}

Please provide detailed, actionable suggestions in JSON format:

{{
    "prompt_improvements": [
        {{
            "issue": "description of the prompt problem",
            "current_prompt": "what the current prompt likely says",
            "suggested_prompt": "improved prompt text",
            "rationale": "why this change would help"
        }}
    ],
    "logic_improvements": [
        {{
            "issue": "description of the logic problem",
            "current_behavior": "what the bot currently does",
            "suggested_behavior": "what the bot should do",
            "implementation": "how to implement this change"
        }}
    ],
    "training_suggestions": [
        {{
            "scenario": "type of scenario to train on",
            "examples": ["example", "conversations"],
            "expected_outcome": "what should happen"
        }}
    ],
    "priority": "high/medium/low",
    "estimated_impact": "description of expected improvement"
}}"""

        return prompt.strip()
    
    def build_summary_prompt(self, multiple_analyses: List[dict]) -> str:
        """Build a prompt to summarize multiple call analyses"""
        
        analyses_text = "\n\n".join([
            f"Call {i+1}:\n{self._format_analysis(analysis)}"
            for i, analysis in enumerate(multiple_analyses)
        ])
        
        prompt = f"""{self.system_prompt}

SUMMARIZE THESE CALL ANALYSES:

{analyses_text}

Provide a summary in JSON format:

{{
    "common_issues": [
        {{
            "issue": "description",
            "frequency": "how often it occurs",
            "impact": "severity level"
        }}
    ],
    "top_improvements": [
        {{
            "improvement": "description",
            "priority": "high/medium/low",
            "expected_benefit": "what this would achieve"
        }}
    ],
    "overall_quality_score": 0.0-1.0,
    "trends": "description of patterns across calls",
    "recommendations": [
        "specific action items"
    ]
}}"""

        return prompt.strip()
    
    def _format_conversation(self, dialog: List[DialogueTurn]) -> str:
        """Format the conversation for the prompt"""
        formatted_turns = []
        
        for i, turn in enumerate(dialog):
            speaker = turn.speaker.value.capitalize()
            text = turn.text.strip()
            formatted_turns.append(f"Turn {i+1} - {speaker}: {text}")
        
        return "\n".join(formatted_turns)
    
    def _format_analysis(self, analysis: dict) -> str:
        """Format an analysis result for summary prompts"""
        return f"""
Intent: {analysis.get('intent', 'N/A')}
Issue Detected: {analysis.get('issue_detected', 'N/A')}
Issue Reason: {analysis.get('issue_reason', 'N/A')}
Confidence: {analysis.get('confidence_score', 'N/A')}
"""

# Global instance for easy access
prompt_builder = PromptBuilder() 