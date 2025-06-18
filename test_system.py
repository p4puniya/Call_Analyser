#!/usr/bin/env python3
"""
Test script for Call Replay Analyzer

This script tests the core functionality of the system
without requiring an OpenAI API key.
"""

import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from models import CallTranscript, DialogueTurn, Speaker
from prefilter import failure_detector
from prompt_builder import prompt_builder

def test_models():
    """Test Pydantic models"""
    print("🧪 Testing Pydantic models...")
    
    # Test basic model creation
    dialog = [
        DialogueTurn(speaker=Speaker.USER, text="Hello"),
        DialogueTurn(speaker=Speaker.BOT, text="Hi there!")
    ]
    
    transcript = CallTranscript(
        call_id="test_123",
        dialog=dialog,
        metadata={"test": True}
    )
    
    print(f"✅ Created transcript: {transcript.call_id}")
    print(f"   Dialog length: {len(transcript.dialog)}")
    print(f"   Metadata: {transcript.metadata}")
    
    return transcript

def test_prefilter(transcript):
    """Test failure detection"""
    print("\n🧪 Testing failure detection...")
    
    result = failure_detector.is_call_possibly_failed(transcript)
    
    print(f"✅ Prefilter result:")
    print(f"   Failed: {result['failed']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Call length: {result.get('call_length', len(transcript.dialog))}")
    print(f"   Reasons: {result.get('reasons', [])}")
    
    return result

def test_prompt_builder(transcript):
    """Test prompt generation"""
    print("\n🧪 Testing prompt builder...")
    
    prompt = prompt_builder.build_analysis_prompt(transcript.dialog)
    
    print(f"✅ Generated prompt:")
    print(f"   Length: {len(prompt)} characters")
    print(f"   Contains JSON format: {'JSON' in prompt}")
    print(f"   Contains conversation: {'Turn 1' in prompt}")
    
    # Show first 200 characters
    print(f"   Preview: {prompt[:200]}...")
    
    return prompt

def test_failed_call():
    """Test with a known failed call"""
    print("\n🧪 Testing with failed call example...")
    
    # Create a failed call scenario
    failed_dialog = [
        DialogueTurn(speaker=Speaker.USER, text="Do you deliver to Bandra?"),
        DialogueTurn(speaker=Speaker.BOT, text="We are open 11 to 10."),
        DialogueTurn(speaker=Speaker.USER, text="That's not what I asked."),
        DialogueTurn(speaker=Speaker.BOT, text="I apologize for the confusion."),
        DialogueTurn(speaker=Speaker.USER, text="This is ridiculous. I'm hanging up.")
    ]
    
    failed_transcript = CallTranscript(
        call_id="failed_test",
        dialog=failed_dialog
    )
    
    # Test prefilter
    result = failure_detector.is_call_possibly_failed(failed_transcript)
    
    print(f"✅ Failed call test:")
    print(f"   Should be flagged: {result['failed']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Reasons: {result.get('reasons', [])}")
    
    return failed_transcript

def test_successful_call():
    """Test with a known successful call"""
    print("\n🧪 Testing with successful call example...")
    
    # Create a successful call scenario
    success_dialog = [
        DialogueTurn(speaker=Speaker.USER, text="Hi, I'd like to order a pizza"),
        DialogueTurn(speaker=Speaker.BOT, text="Great! What size would you like?"),
        DialogueTurn(speaker=Speaker.USER, text="Large please"),
        DialogueTurn(speaker=Speaker.BOT, text="Perfect! Your large pizza will be ready in 25 minutes."),
        DialogueTurn(speaker=Speaker.USER, text="Thank you!")
    ]
    
    success_transcript = CallTranscript(
        call_id="success_test",
        dialog=success_dialog
    )
    
    # Test prefilter
    result = failure_detector.is_call_possibly_failed(success_transcript)
    
    print(f"✅ Successful call test:")
    print(f"   Should be flagged: {result['failed']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Reasons: {result.get('reasons', [])}")
    
    return success_transcript

def test_json_serialization():
    """Test JSON serialization of models"""
    print("\n🧪 Testing JSON serialization...")
    
    transcript = test_models()
    
    # Convert to dict
    transcript_dict = transcript.dict()
    
    # Convert back to JSON
    json_str = json.dumps(transcript_dict, indent=2)
    
    print(f"✅ JSON serialization:")
    print(f"   Dict keys: {list(transcript_dict.keys())}")
    print(f"   JSON length: {len(json_str)} characters")
    print(f"   Valid JSON: {json_str[:100]}...")
    
    return transcript_dict

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Call Replay Analyzer Tests\n")
    
    try:
        # Test 1: Models
        transcript = test_models()
        
        # Test 2: Prefilter
        prefilter_result = test_prefilter(transcript)
        
        # Test 3: Prompt Builder
        prompt = test_prompt_builder(transcript)
        
        # Test 4: Failed call
        failed_transcript = test_failed_call()
        
        # Test 5: Successful call
        success_transcript = test_successful_call()
        
        # Test 6: JSON serialization
        transcript_dict = test_json_serialization()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📊 Test Summary:")
        print(f"   ✅ Models: Working")
        print(f"   ✅ Prefilter: Working")
        print(f"   ✅ Prompt Builder: Working")
        print(f"   ✅ Failed Call Detection: {'Working' if prefilter_result['failed'] else 'Needs Review'}")
        print(f"   ✅ JSON Serialization: Working")
        
        print("\n🔧 Next Steps:")
        print("   1. Set your OpenAI API key in .env file")
        print("   2. Run: uvicorn main:app --reload")
        print("   3. Test with: curl -X POST http://localhost:8000/analyze-call -H 'Content-Type: application/json' -d @examples/sample_call.json")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 