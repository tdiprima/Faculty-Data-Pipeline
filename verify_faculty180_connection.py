#!/usr/bin/env python3
"""
Verify connection to Faculty180 API.
Tests authentication and basic data retrieval.
Tests:
  - Environment variables configuration
  - API authentication with token
  - JSON response parsing
  - Data structure analysis
"""
import requests
import json
import os
import sys
from datetime import datetime

# Configuration
FACULTY_API_URL = os.getenv("FACULTY_API_URL", "https://api.faculty180.com/v1/faculty")
FACULTY_API_TOKEN = os.getenv("FACULTY_API_TOKEN")
REQUEST_TIMEOUT = 30

def print_status(message, status="INFO"):
    """Print formatted status message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def verify_config():
    """Verify required configuration is present."""
    print_status("Checking configuration...")
    
    if not FACULTY_API_TOKEN:
        print_status("❌ FACULTY_API_TOKEN environment variable not set", "ERROR")
        print_status("Please set: export FACULTY_API_TOKEN='your_token_here'", "INFO")
        return False
    
    print_status(f"✅ API URL: {FACULTY_API_URL}")
    print_status(f"✅ API Token: {'*' * 20}...{FACULTY_API_TOKEN[-4:]}")
    return True

def test_api_connection():
    """Test basic API connectivity."""
    print_status("Testing API connection...")
    
    headers = {
        "Authorization": f"Bearer {FACULTY_API_TOKEN}",
        "Accept": "application/json",
        "User-Agent": "Faculty180-Drupal-Sync/1.0"
    }
    
    try:
        response = requests.get(
            FACULTY_API_URL, 
            headers=headers, 
            timeout=REQUEST_TIMEOUT,
            verify=True  # Verify SSL certificates
        )
        
        print_status(f"Response Status: {response.status_code}")
        print_status(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print_status("✅ API connection successful!")
            return response
        elif response.status_code == 401:
            print_status("❌ Authentication failed - check your API token", "ERROR")
            return None
        elif response.status_code == 403:
            print_status("❌ Access forbidden - check API permissions", "ERROR")
            return None
        elif response.status_code == 404:
            print_status("❌ API endpoint not found - check URL", "ERROR")
            return None
        else:
            print_status(f"❌ Unexpected status code: {response.status_code}", "ERROR")
            print_status(f"Response: {response.text}", "ERROR")
            return None
            
    except requests.exceptions.SSLError as e:
        print_status(f"❌ SSL certificate error: {e}", "ERROR")
        return None
    except requests.exceptions.Timeout:
        print_status(f"❌ Request timeout after {REQUEST_TIMEOUT} seconds", "ERROR")
        return None
    except requests.exceptions.ConnectionError as e:
        print_status(f"❌ Connection error: {e}", "ERROR")
        return None
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Request error: {e}", "ERROR")
        return None

def analyze_response(response):
    """Analyze and display API response data."""
    print_status("Analyzing API response...")
    
    try:
        content_type = response.headers.get('content-type', '')
        print_status(f"Content Type: {content_type}")
        
        if 'application/json' in content_type:
            data = response.json()
            print_status("✅ Valid JSON response received")
            
            if isinstance(data, list):
                print_status(f"📊 Response contains {len(data)} faculty records")
                
                if data:
                    sample_record = data[0]
                    print_status("Sample record structure:")
                    for key, value in sample_record.items():
                        value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"  - {key}: {value_preview}")
                        
                    # Check for common expected fields
                    expected_fields = ['name', 'email', 'department', 'title', 'bio']
                    found_fields = [field for field in expected_fields if field in sample_record]
                    missing_fields = [field for field in expected_fields if field not in sample_record]
                    
                    if found_fields:
                        print_status(f"✅ Found expected fields: {', '.join(found_fields)}")
                    if missing_fields:
                        print_status(f"⚠️  Missing common fields: {', '.join(missing_fields)}")
                        
            elif isinstance(data, dict):
                print_status("📊 Response is a single object")
                print_status(f"Object keys: {list(data.keys())}")
            else:
                print_status(f"📊 Response type: {type(data)}")
                
        else:
            print_status("⚠️  Response is not JSON")
            preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
            print_status(f"Response preview: {preview}")
            
    except json.JSONDecodeError as e:
        print_status(f"❌ Invalid JSON response: {e}", "ERROR")
        preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
        print_status(f"Response preview: {preview}")

def main():
    """Main verification function."""
    print_status("=" * 60)
    print_status("Faculty180 API Connection Verification")
    print_status("=" * 60)
    
    # Step 1: Verify configuration
    if not verify_config():
        sys.exit(1)
    
    print_status("-" * 40)
    
    # Step 2: Test API connection
    response = test_api_connection()
    if not response:
        print_status("❌ Connection verification failed", "ERROR")
        sys.exit(1)
    
    print_status("-" * 40)
    
    # Step 3: Analyze response
    analyze_response(response)
    
    print_status("-" * 40)
    print_status("✅ Faculty180 connection verification completed successfully!")
    print_status("You can now use this configuration in faculty180_to_drupal.py")

if __name__ == "__main__":
    main()
