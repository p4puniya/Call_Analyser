from typing import Dict, List, Any
from models import CallTranscript, DialogueTurn

class FailureDetector:
    """Heuristic-based system to detect potentially failed calls"""
    
    def __init__(self):
        # Keywords that indicate user frustration or confusion
        self.frustration_keywords = [
            "not helpful", "hello?", "what?", "you there?", "makes no sense",
            "that's not what i asked", "i don't understand", "wrong answer",
            "that doesn't help", "can you hear me", "are you listening",
            "this is ridiculous", "useless", "stupid", "idiot"
        ]
        
        # Patterns that suggest bot confusion
        self.bot_confusion_patterns = [
            "i don't understand", "could you repeat", "i'm not sure",
            "let me try to help", "i apologize", "i'm sorry"
        ]
        
        # Short responses that might indicate issues
        self.short_response_threshold = 10
        
    def is_call_possibly_failed(self, transcript: CallTranscript) -> Dict[str, Any]:
        """
        Analyze a call transcript to determine if it likely failed
        Returns a dict with failure probability and reasons
        """
        dialog = transcript.dialog
        
        if len(dialog) < 3:
            return {
                "failed": True,
                "confidence": 0.8,
                "reasons": ["Call too short - likely incomplete"]
            }
        
        failure_indicators = []
        confidence_score = 0.0
        
        # Check for user frustration
        user_frustration = self._detect_user_frustration(dialog)
        if user_frustration["detected"]:
            failure_indicators.extend(user_frustration["reasons"])
            confidence_score += 0.4
        
        # Check for bot repetition
        bot_repetition = self._detect_bot_repetition(dialog)
        if bot_repetition["detected"]:
            failure_indicators.extend(bot_repetition["reasons"])
            confidence_score += 0.3
        
        # Check for conversation flow issues
        flow_issues = self._detect_flow_issues(dialog)
        if flow_issues["detected"]:
            failure_indicators.extend(flow_issues["reasons"])
            confidence_score += 0.2
        
        # Check for bot confusion
        bot_confusion = self._detect_bot_confusion(dialog)
        if bot_confusion["detected"]:
            failure_indicators.extend(bot_confusion["reasons"])
            confidence_score += 0.3
        
        # Check for abrupt endings
        abrupt_ending = self._detect_abrupt_ending(dialog)
        if abrupt_ending["detected"]:
            failure_indicators.extend(abrupt_ending["reasons"])
            confidence_score += 0.2
        
        failed = confidence_score >= 0.3
        
        return {
            "failed": failed,
            "confidence": min(confidence_score, 1.0),
            "reasons": failure_indicators,
            "call_length": len(dialog)
        }
    
    def _detect_user_frustration(self, dialog: List[DialogueTurn]) -> Dict[str, Any]:
        """Detect signs of user frustration or confusion"""
        reasons = []
        frustration_count = 0
        
        for turn in dialog:
            if turn.speaker.value == "user":
                text_lower = turn.text.lower()
                for keyword in self.frustration_keywords:
                    if keyword in text_lower:
                        frustration_count += 1
                        reasons.append(f"User frustration detected: '{keyword}'")
                        break
        
        return {
            "detected": frustration_count > 0,
            "reasons": reasons,
            "count": frustration_count
        }
    
    def _detect_bot_repetition(self, dialog: List[DialogueTurn]) -> Dict[str, Any]:
        """Detect if bot is repeating the same responses"""
        bot_responses = {}
        reasons = []
        
        for turn in dialog:
            if turn.speaker.value == "bot":
                text = turn.text.strip()
                if text in bot_responses:
                    bot_responses[text] += 1
                else:
                    bot_responses[text] = 1
        
        repeated_responses = [text for text, count in bot_responses.items() if count >= 2]
        
        if repeated_responses:
            reasons.append(f"Bot repeated responses: {len(repeated_responses)} unique responses repeated")
        
        return {
            "detected": len(repeated_responses) > 0,
            "reasons": reasons,
            "repeated_count": len(repeated_responses)
        }
    
    def _detect_flow_issues(self, dialog: List[DialogueTurn]) -> Dict[str, Any]:
        """Detect conversation flow problems"""
        reasons = []
        
        # Check for very short bot responses
        short_responses = 0
        for turn in dialog:
            if turn.speaker.value == "bot" and len(turn.text.strip()) < self.short_response_threshold:
                short_responses += 1
        
        if short_responses > 2:
            reasons.append(f"Multiple very short bot responses: {short_responses}")
        
        # Check for long gaps in conversation (if timestamps available)
        # This would require timestamp analysis
        
        return {
            "detected": len(reasons) > 0,
            "reasons": reasons
        }
    
    def _detect_bot_confusion(self, dialog: List[DialogueTurn]) -> Dict[str, Any]:
        """Detect if bot seems confused or uncertain"""
        reasons = []
        confusion_count = 0
        
        for turn in dialog:
            if turn.speaker.value == "bot":
                text_lower = turn.text.lower()
                for pattern in self.bot_confusion_patterns:
                    if pattern in text_lower:
                        confusion_count += 1
                        reasons.append(f"Bot confusion detected: '{pattern}'")
                        break
        
        return {
            "detected": confusion_count > 0,
            "reasons": reasons,
            "count": confusion_count
        }
    
    def _detect_abrupt_ending(self, dialog: List[DialogueTurn]) -> Dict[str, Any]:
        """Detect if conversation ended abruptly"""
        reasons = []
        
        if len(dialog) < 5:
            reasons.append("Conversation ended very early")
        
        # Check if last user message suggests unresolved issue
        if dialog and dialog[-1].speaker.value == "user":
            last_text = dialog[-1].text.lower()
            if any(keyword in last_text for keyword in ["?", "help", "what", "how"]):
                reasons.append("Conversation ended with user question/request")
        
        return {
            "detected": len(reasons) > 0,
            "reasons": reasons
        }

# Global instance for easy access
failure_detector = FailureDetector() 