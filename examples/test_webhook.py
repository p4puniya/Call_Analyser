#!/usr/bin/env python3
"""
Webhook Testing Script for Certus Integration

This script tests the webhook endpoint with various scenarios to ensure
the Certus integration is working correctly.
"""

import requests
import json
import time
from pathlib import Path

# Configuration
WEBHOOK_URL = "http://localhost:8000/webhook"
HEALTH_URL = "http://localhost:8000/health"
HISTORY_URL = "http://localhost:8000/analysis-history"

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

def test_webhook_basic():
    """Test basic webhook functionality"""
    payload = {
        "call_id": "test_webhook_001",
        "dialog": [
            {"speaker": "user", "text": "Do you deliver to Bandra?"},
            {"speaker": "bot", "text": "We are open 11 to 10."},
            {"speaker": "user", "text": "That's not what I asked!"}
        ],
        "metadata": {
            "certus_call_id": "certus_test_001",
            "failure_reason": "intent_misunderstanding",
            "call_duration": 45,
            "customer_satisfaction": "low"
        }
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Basic webhook test passed")
            print(f"   Call ID: {result.get('call_id')}")
            print(f"   Webhook ID: {result.get('webhook_id')}")
            return True
        else:
            print(f"❌ Basic webhook test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Basic webhook test error: {e}")
        return False

def test_webhook_with_file():
    """Test webhook with the sample file"""
    test_file = Path("examples/certus_webhook_test.json")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        with open(test_file, 'r') as f:
            payload = json.load(f)
        
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File-based webhook test passed")
            print(f"   Call ID: {result.get('call_id')}")
            print(f"   Webhook ID: {result.get('webhook_id')}")
            return True
        else:
            print(f"❌ File-based webhook test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ File-based webhook test error: {e}")
        return False

def test_webhook_error_handling():
    """Test webhook error handling with invalid payload"""
    invalid_payloads = [
        # Missing call_id
        {
            "dialog": [{"speaker": "user", "text": "Hello"}]
        },
        # Missing dialog
        {
            "call_id": "test_error_001"
        },
        # Empty dialog
        {
            "call_id": "test_error_002",
            "dialog": []
        },
        # Invalid speaker
        {
            "call_id": "test_error_003",
            "dialog": [{"speaker": "invalid", "text": "Hello"}]
        }
    ]
    
    for i, payload in enumerate(invalid_payloads):
        try:
            response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code in [400, 422]:
                print(f"✅ Error handling test {i+1} passed (expected error)")
            else:
                print(f"⚠️ Error handling test {i+1} unexpected: {response.status_code}")
        except Exception as e:
            print(f"❌ Error handling test {i+1} failed: {e}")

def check_analysis_results():
    """Check if analysis results are being stored"""
    try:
        # Wait a bit for background processing
        print("⏳ Waiting for background processing...")
        time.sleep(3)
        
        response = requests.get(f"{HISTORY_URL}?limit=5", timeout=10)
        if response.status_code == 200:
            result = response.json()
            total_results = result.get('total_results', 0)
            print(f"✅ Found {total_results} analysis results in storage")
            
            if total_results > 0:
                latest = result.get('results', [])[0] if result.get('results') else None
                if latest:
                    print(f"   Latest call: {latest.get('call_id')}")
                    print(f"   Status: {latest.get('status')}")
                    if latest.get('analysis'):
                        print(f"   Issue detected: {latest.get('analysis', {}).get('issue_detected')}")
            return True
        else:
            print(f"❌ Failed to check analysis results: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking analysis results: {e}")
        return False

def test_multiple_webhooks():
    """Test sending multiple webhooks quickly"""
    print("🔄 Testing multiple webhooks...")
    
    success_count = 0
    for i in range(3):
        payload = {
            "call_id": f"multi_test_{i+1:03d}",
            "dialog": [
                {"speaker": "user", "text": f"Test call {i+1}"},
                {"speaker": "bot", "text": "I understand"},
                {"speaker": "user", "text": "This is a test"}
            ],
            "metadata": {
                "certus_call_id": f"certus_multi_{i+1}",
                "failure_reason": "test_scenario",
                "call_duration": 30 + i,
                "customer_satisfaction": "low"
            }
        }
        
        try:
            response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code == 200:
                success_count += 1
                print(f"   ✅ Webhook {i+1} sent successfully")
            else:
                print(f"   ❌ Webhook {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Webhook {i+1} error: {e}")
    
    print(f"📊 Multiple webhook test: {success_count}/3 successful")

def main():
    """Run all webhook tests"""
    print("🔗 Certus Webhook Integration Test Suite")
    print("=" * 50)
    
    # Test server health
    if not test_server_health():
        print("\n❌ Server is not available. Please start the server first:")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    print("\n🧪 Running webhook tests...")
    
    # Basic webhook test
    test_webhook_basic()
    
    # File-based webhook test
    test_webhook_with_file()
    
    # Error handling test
    print("\n🔍 Testing error handling...")
    test_webhook_error_handling()
    
    # Multiple webhooks test
    print("\n🔄 Testing multiple webhooks...")
    test_multiple_webhooks()
    
    # Check results
    print("\n📊 Checking analysis results...")
    check_analysis_results()
    
    print("\n🎉 Webhook testing completed!")
    print("\n📋 Next steps:")
    print("   1. Check the logs for processing details")
    print("   2. View analysis results: curl http://localhost:8000/analysis-history")
    print("   3. Check statistics: curl http://localhost:8000/analysis-stats")
    print("   4. Configure Certus to use the webhook URL")

if __name__ == "__main__":
    main() 