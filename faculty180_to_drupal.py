"""
Grabs faculty data and creates Drupal nodes.
"""
import requests
import json
import os
import logging
import time
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API settings from environment variables
FACULTY_API_URL = os.getenv("FACULTY_API_URL", "https://api.faculty180.com/v1/faculty")
FACULTY_API_TOKEN = os.getenv("FACULTY_API_TOKEN")

DRUPAL_BASE_URL = os.getenv("DRUPAL_BASE_URL", "https://yoursite.com")
DRUPAL_USERNAME = os.getenv("DRUPAL_USERNAME")
DRUPAL_PASSWORD = os.getenv("DRUPAL_PASSWORD")
DRUPAL_CONTENT_TYPE = os.getenv("DRUPAL_CONTENT_TYPE", "faculty_profile")

# API endpoints
DRUPAL_LOGIN_URL = f"{DRUPAL_BASE_URL}/user/login?_format=json"
DRUPAL_TOKEN_URL = f"{DRUPAL_BASE_URL}/rest/session/token"
DRUPAL_NODE_URL = f"{DRUPAL_BASE_URL}/node?_format=json"

# Request timeout and retry settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2


def validate_config() -> bool:
    """Validate required environment variables are set."""
    required_vars = {
        "FACULTY_API_TOKEN": FACULTY_API_TOKEN,
        "DRUPAL_USERNAME": DRUPAL_USERNAME,
        "DRUPAL_PASSWORD": DRUPAL_PASSWORD
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True


def make_request_with_retry(method: str, url: str, **kwargs) -> Optional[requests.Response]:
    """Make HTTP request with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"All retry attempts failed for {method} {url}")
                return None


def get_faculty_data() -> List[Dict]:
    """Get data from Faculty 180 API."""
    if not FACULTY_API_TOKEN:
        logger.error("Faculty API token not configured")
        return []
    
    headers = {"Authorization": f"Bearer {FACULTY_API_TOKEN}"}
    
    logger.info("Fetching faculty data from Faculty 180 API...")
    response = make_request_with_retry("GET", FACULTY_API_URL, headers=headers)
    
    if response:
        try:
            data = response.json()
            logger.info(f"Successfully retrieved {len(data)} faculty records")
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Faculty 180: {e}")
            return []
    return []


def authenticate_drupal() -> Tuple[Optional[str], Optional[Dict]]:
    """Authenticate with Drupal and get CSRF token and session."""
    logger.info("Authenticating with Drupal...")
    
    # Step 1: Login to get session
    login_data = {
        "name": DRUPAL_USERNAME,
        "pass": DRUPAL_PASSWORD
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = make_request_with_retry("POST", DRUPAL_LOGIN_URL, json=login_data, headers=headers)
    if not response:
        return None, None
    
    cookies = response.cookies.get_dict()
    
    # Step 2: Get CSRF token
    token_response = make_request_with_retry("GET", DRUPAL_TOKEN_URL, cookies=cookies)
    if not token_response:
        return None, None
    
    csrf_token = token_response.text.strip()
    logger.info("Successfully authenticated with Drupal")
    return csrf_token, cookies


def validate_faculty_data(faculty: Dict) -> bool:
    """Validate faculty data has required fields."""
    required_fields = ['name']  # Add other required fields as needed
    
    for field in required_fields:
        if not faculty.get(field):
            logger.warning(f"Faculty record missing required field '{field}': {faculty}")
            return False
    return True


def create_drupal_node(faculty: Dict, csrf_token: str, cookies: Dict) -> bool:
    """Create a Drupal node for faculty member."""
    if not validate_faculty_data(faculty):
        return False
    
    # Map faculty data to Drupal node structure
    node_data = {
        "type": [{"target_id": DRUPAL_CONTENT_TYPE}],
        "title": [{"value": faculty.get("name", "Unknown Faculty")}],
        "status": [{"value": True}],  # Published
    }
    
    # Add body field if bio exists
    if faculty.get("bio"):
        node_data["body"] = [{
            "value": faculty.get("bio"),
            "format": "basic_html"  # Adjust format as needed
        }]
    
    # Add additional fields based on Faculty 180 data structure
    field_mapping = {
        "email": "field_email",
        "phone": "field_phone", 
        "department": "field_department",
        "title": "field_job_title",
        "office": "field_office_location"
    }
    
    for faculty_field, drupal_field in field_mapping.items():
        if faculty.get(faculty_field):
            node_data[drupal_field] = [{"value": faculty[faculty_field]}]
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CSRF-Token": csrf_token
    }
    
    logger.info(f"Creating Drupal node for {faculty.get('name')}")
    response = make_request_with_retry("POST", DRUPAL_NODE_URL, json=node_data, headers=headers, cookies=cookies)
    
    if response and response.status_code == 201:
        node_id = response.json().get("nid", [{}])[0].get("value")
        logger.info(f"Successfully created node {node_id} for {faculty.get('name')}")
        return True
    else:
        error_msg = response.text if response else "No response"
        logger.error(f"Failed to create node for {faculty.get('name')}: {error_msg}")
        return False


def main():
    """Main function to sync Faculty 180 data to Drupal."""
    logger.info("Starting Faculty 180 to Drupal sync...")
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed. Exiting.")
        return
    
    # Get faculty data from Faculty 180
    faculty_list = get_faculty_data()
    if not faculty_list:
        logger.error("No faculty data retrieved from Faculty 180. Exiting.")
        return
    
    # Authenticate with Drupal
    csrf_token, cookies = authenticate_drupal()
    if not csrf_token:
        logger.error("Drupal authentication failed. Exiting.")
        return
    
    # Create nodes for each faculty member
    success_count = 0
    total_count = len(faculty_list)
    
    for i, faculty in enumerate(faculty_list, 1):
        logger.info(f"Processing faculty {i}/{total_count}: {faculty.get('name', 'Unknown')}")
        
        if create_drupal_node(faculty, csrf_token, cookies):
            success_count += 1
        
        # Add small delay to avoid overwhelming the server
        if i < total_count:
            time.sleep(1)
    
    logger.info(f"Sync completed: {success_count}/{total_count} faculty members processed successfully")


if __name__ == "__main__":
    main()
