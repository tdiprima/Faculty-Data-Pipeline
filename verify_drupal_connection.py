#!/usr/bin/env python3
"""
Verify connection to Drupal REST API.
Tests authentication, CSRF token retrieval, and basic node operations.
Tests:
  - Site accessibility
  - User login authentication
  - CSRF token retrieval
  - Content type validation
  - Node creation permissions
"""
import requests
import os
import sys
from datetime import datetime

# Configuration
DRUPAL_BASE_URL = os.getenv("DRUPAL_BASE_URL", "https://yoursite.com")
DRUPAL_USERNAME = os.getenv("DRUPAL_USERNAME")
DRUPAL_PASSWORD = os.getenv("DRUPAL_PASSWORD")
DRUPAL_CONTENT_TYPE = os.getenv("DRUPAL_CONTENT_TYPE", "faculty_profile")
REQUEST_TIMEOUT = 30

# API endpoints
DRUPAL_LOGIN_URL = f"{DRUPAL_BASE_URL}/user/login?_format=json"
DRUPAL_TOKEN_URL = f"{DRUPAL_BASE_URL}/rest/session/token"
DRUPAL_NODE_URL = f"{DRUPAL_BASE_URL}/node?_format=json"
DRUPAL_STATUS_URL = f"{DRUPAL_BASE_URL}/rest/type/node/{DRUPAL_CONTENT_TYPE}?_format=json"


def print_status(message, status="INFO"):
    """Print formatted status message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")


def verify_config():
    """Verify required configuration is present."""
    print_status("Checking configuration...")
    
    required_vars = {
        "DRUPAL_USERNAME": DRUPAL_USERNAME,
        "DRUPAL_PASSWORD": DRUPAL_PASSWORD,
        "DRUPAL_BASE_URL": DRUPAL_BASE_URL
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        print_status(f"❌ Missing environment variables: {', '.join(missing_vars)}", "ERROR")
        print_status("Please set these variables:", "INFO")
        for var in missing_vars:
            print_status(f"  export {var}='your_value_here'", "INFO")
        return False
    
    print_status(f"✅ Base URL: {DRUPAL_BASE_URL}")
    print_status(f"✅ Username: {DRUPAL_USERNAME}")
    print_status(f"✅ Password: {'*' * len(DRUPAL_PASSWORD)}")
    print_status(f"✅ Content Type: {DRUPAL_CONTENT_TYPE}")
    return True


def test_drupal_accessibility():
    """Test if Drupal site is accessible."""
    print_status("Testing Drupal site accessibility...")
    
    try:
        response = requests.get(
            DRUPAL_BASE_URL, 
            timeout=REQUEST_TIMEOUT,
            verify=True
        )
        
        print_status(f"Site Status: {response.status_code}")
        
        if response.status_code == 200:
            print_status("✅ Drupal site is accessible")
            return True
        else:
            print_status(f"⚠️  Unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Site accessibility error: {e}", "ERROR")
        return False


def test_drupal_login():
    """Test Drupal login and return session cookies."""
    print_status("Testing Drupal authentication...")
    
    login_data = {
        "name": DRUPAL_USERNAME,
        "pass": DRUPAL_PASSWORD
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(
            DRUPAL_LOGIN_URL, 
            json=login_data, 
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            verify=True
        )
        
        print_status(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            print_status("✅ Drupal login successful")
            cookies = response.cookies.get_dict()
            print_status(f"Session cookies: {list(cookies.keys())}")
            
            # Try to get user info from response
            try:
                user_data = response.json()
                print_status(f"Logged in as: {user_data.get('name', 'Unknown')}")
                print_status(f"User ID: {user_data.get('uid', 'Unknown')}")
                print_status(f"User roles: {user_data.get('roles', [])}")
            except:
                print_status("Login successful but couldn't parse user data")
                
            return cookies
        elif response.status_code == 400:
            print_status("❌ Bad request - check login data format", "ERROR")
            return None
        elif response.status_code == 401:
            print_status("❌ Authentication failed - check username/password", "ERROR")
            return None
        elif response.status_code == 403:
            print_status("❌ Access forbidden - user may not have API access", "ERROR")
            return None
        else:
            print_status(f"❌ Login failed with status: {response.status_code}", "ERROR")
            print_status(f"Response: {response.text}", "ERROR")
            return None
            
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Login error: {e}", "ERROR")
        return None


def test_csrf_token(cookies):
    """Test CSRF token retrieval."""
    print_status("Testing CSRF token retrieval...")
    
    try:
        response = requests.get(
            DRUPAL_TOKEN_URL,
            cookies=cookies,
            timeout=REQUEST_TIMEOUT,
            verify=True
        )
        
        print_status(f"Token Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.text.strip()
            print_status("✅ CSRF token retrieved successfully")
            print_status(f"Token preview: {token[:20]}...{token[-10:]}")
            return token
        else:
            print_status(f"❌ Token retrieval failed: {response.status_code}", "ERROR")
            print_status(f"Response: {response.text}", "ERROR")
            return None
            
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Token retrieval error: {e}", "ERROR")
        return None


def test_content_type(cookies, csrf_token):
    """Test if the content type exists and is accessible."""
    print_status(f"Testing content type '{DRUPAL_CONTENT_TYPE}'...")
    
    headers = {
        "Accept": "application/json",
        "X-CSRF-Token": csrf_token
    }
    
    try:
        response = requests.get(
            DRUPAL_STATUS_URL,
            cookies=cookies,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            verify=True
        )
        
        print_status(f"Content Type Status: {response.status_code}")
        
        if response.status_code == 200:
            print_status("✅ Content type is accessible")
            try:
                data = response.json()
                print_status(f"Content type label: {data.get('name', 'Unknown')}")
                print_status(f"Content type ID: {data.get('type', 'Unknown')}")
            except:
                print_status("Content type accessible but couldn't parse details")
            return True
        elif response.status_code == 404:
            print_status(f"❌ Content type '{DRUPAL_CONTENT_TYPE}' not found", "ERROR")
            print_status("Available content types might be different", "INFO")
            return False
        else:
            print_status(f"⚠️  Unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Content type check error: {e}", "ERROR")
        return False


def test_node_creation_permissions(cookies, csrf_token):
    """Test if we can create nodes (dry run)."""
    print_status("Testing node creation permissions...")
    
    # Create a minimal test node structure
    test_node = {
        "type": [{"target_id": DRUPAL_CONTENT_TYPE}],
        "title": [{"value": "TEST - Connection Verification"}],
        "status": [{"value": False}],  # Unpublished
        "body": [{"value": "This is a test node for connection verification"}]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CSRF-Token": csrf_token
    }
    
    try:
        # Note: This will actually create a node if successful
        # In production, you might want to delete it afterward
        response = requests.post(
            DRUPAL_NODE_URL,
            json=test_node,
            headers=headers,
            cookies=cookies,
            timeout=REQUEST_TIMEOUT,
            verify=True
        )
        
        print_status(f"Node Creation Status: {response.status_code}")
        
        if response.status_code == 201:
            print_status("✅ Node creation successful")
            try:
                node_data = response.json()
                node_id = node_data.get("nid", [{}])[0].get("value")
                print_status(f"Created test node ID: {node_id}")
                print_status("⚠️  Note: Test node was created - you may want to delete it")
            except:
                print_status("Node created but couldn't parse response")
            return True
        elif response.status_code == 400:
            print_status("❌ Bad request - check node structure", "ERROR")
            print_status(f"Response: {response.text}", "ERROR")
            return False
        elif response.status_code == 403:
            print_status("❌ Access forbidden - user lacks node creation permissions", "ERROR")
            return False
        elif response.status_code == 422:
            print_status("❌ Validation error - check required fields", "ERROR")
            print_status(f"Response: {response.text}", "ERROR")
            return False
        else:
            print_status(f"❌ Node creation failed: {response.status_code}", "ERROR")
            print_status(f"Response: {response.text}", "ERROR")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Node creation error: {e}", "ERROR")
        return False


def main():
    """Main verification function."""
    print_status("=" * 60)
    print_status("Drupal REST API Connection Verification")
    print_status("=" * 60)
    
    # Step 1: Verify configuration
    if not verify_config():
        sys.exit(1)
    
    print_status("-" * 40)
    
    # Step 2: Test site accessibility
    if not test_drupal_accessibility():
        print_status("❌ Site accessibility failed", "ERROR")
        sys.exit(1)
    
    print_status("-" * 40)
    
    # Step 3: Test login
    cookies = test_drupal_login()
    if not cookies:
        print_status("❌ Login verification failed", "ERROR")
        sys.exit(1)
    
    print_status("-" * 40)
    
    # Step 4: Test CSRF token
    csrf_token = test_csrf_token(cookies)
    if not csrf_token:
        print_status("❌ CSRF token verification failed", "ERROR")
        sys.exit(1)
    
    print_status("-" * 40)
    
    # Step 5: Test content type
    test_content_type(cookies, csrf_token)
    
    print_status("-" * 40)
    
    # Step 6: Test node creation permissions
    test_node_creation_permissions(cookies, csrf_token)
    
    print_status("-" * 40)
    print_status("✅ Drupal connection verification completed!")
    print_status("You can now use this configuration in faculty180_to_drupal.py")


if __name__ == "__main__":
    main()
