import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with the actual API base URL
LOGIN_ENDPOINT = "/login"
\****************(scope="module")
def credentials():
    # These should come from a secure source or test configuration
    # Replace with actual valid credentials for testing
    return {
        "valid": {"username": "testuser", "password": "TestPass123!"},
        "invalid": {"username": "testuser", "password": "WrongPass"}
    }

def test_login_success(credentials):
    payload = credentials["valid"]
    response = requests.post(
        f"{BASE_URL}{LOGIN_ENDPOINT}",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code} - {response.text}"
    # JWT token is typically in 'token' or 'access_token' key
    json_body = response.json()
    assert any(k in json_body for k in ("token", "access_token", "jwt")), "JWT token not found in response"
    token = json_body.get("token") or json_body.get("access_token") or json_body.get("jwt")
    assert token and isinstance(token, str) and len(token) > 0, "Invalid token format"

def test_login_invalid_credentials(credentials):
    payload = credentials["invalid"]
    response = requests.post(
        f"{BASE_URL}{LOGIN_ENDPOINT}",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 401, f"Expected 401, got {response.status_code} - {response.text}"