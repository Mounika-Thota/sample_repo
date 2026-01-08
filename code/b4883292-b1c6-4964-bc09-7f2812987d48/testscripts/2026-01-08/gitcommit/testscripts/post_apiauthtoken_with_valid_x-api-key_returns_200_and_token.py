import os
import pytest
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost")
VALID_API_KEY = os.getenv("VALID_API_KEY")

@pytest.fixture(scope="module")
def api_key():
    if not VALID_API_KEY:
        pytest.skip("VALID_API_KEY environment variable not set.")
    return VALID_API_KEY

@pytest.fixture(scope="module")
def api_url():
    return f"{API_BASE_URL}/api/auth/token"

class TestGetToken:
    def test_valid_api_key_returns_200_and_valid_json(self, api_key, api_url):
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        response = requests.post(api_url, headers=headers)
        # Assert status code is 200
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        # Assert response body is a valid JSON object
        try:
            json_body = response.json()
        except ValueError:
            pytest.fail("Response body is not valid JSON.")
        assert isinstance(json_body, dict), f"Expected JSON object (dict), got {type(json_body)}"
        # Optionally, further validation of token payload structure can be added here
