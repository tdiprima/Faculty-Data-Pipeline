"""
Grabs faculty data and creates Drupal nodes.
"""
import requests
import json

# Faculty 180 API settings (replace with real values)
FACULTY_API_URL = "https://api.faculty180.com/v1/faculty"  # Example endpoint
FACULTY_API_TOKEN = "your_faculty180_api_token"

# Drupal API settings
DRUPAL_URL = "http://yoursite.com/user/login?_format=json"
DRUPAL_NODE_URL = "http://yoursite.com/node?_format=json"
DRUPAL_USERNAME = "your_drupal_username"
DRUPAL_PASSWORD = "your_drupal_password"


# Step 1: Get data from Faculty 180
def get_faculty_data():
    headers = {"Authorization": f"Bearer {FACULTY_API_TOKEN}"}
    try:
        response = requests.get(FACULTY_API_URL, headers=headers)
        response.raise_for_status()  # Check for errors
        return response.json()  # Assuming JSON response
    except requests.exceptions.RequestException as e:
        print(f"Oops, Faculty 180 API error: {e}")
        return []


# Step 2: Log in to Drupal and get CSRF token
def login_to_drupal():
    login_data = {
        "name": DRUPAL_USERNAME,
        "pass": DRUPAL_PASSWORD
    }
    try:
        response = requests.post(DRUPAL_URL, json=login_data)
        response.raise_for_status()
        data = response.json()
        csrf_token = data["csrf_token"]
        cookies = response.cookies.get_dict()
        return csrf_token, cookies
    except requests.exceptions.RequestException as e:
        print(f"Drupal login failed: {e}")
        return None, None


# Step 3: Push data to Drupal as nodes
def create_drupal_node(faculty, csrf_token, cookies):
    node_data = {
        "type": [{"target_id": "faculty_profile"}],  # Your content type
        "title": [{"value": faculty.get("name", "Unknown")}],
        "body": [{"value": faculty.get("bio", "No bio")}]
        # Add more fields as needed
    }
    headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token
    }
    try:
        response = requests.post(DRUPAL_NODE_URL, json=node_data, headers=headers, cookies=cookies)
        if response.status_code == 201:
            print(f"Created node for {faculty.get('name')}")
        else:
            print(f"Failed to create node: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Node creation error: {e}")


# Main function to tie it all together
def main():
    # Get faculty data
    faculty_list = get_faculty_data()
    if not faculty_list:
        print("No data from Faculty 180. Exiting...")
        return

    # Log in to Drupal
    csrf_token, cookies = login_to_drupal()
    if not csrf_token:
        print("Drupal login failed. Exiting...")
        return

    # Push each faculty to Drupal
    for faculty in faculty_list:
        create_drupal_node(faculty, csrf_token, cookies)


if __name__ == "__main__":
    main()
