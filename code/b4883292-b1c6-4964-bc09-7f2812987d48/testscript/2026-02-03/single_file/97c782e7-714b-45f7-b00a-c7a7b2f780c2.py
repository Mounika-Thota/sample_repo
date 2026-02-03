import pytest
import requests

BASE_URL = "http://localhost"  # Replace with actual API base URL if different
LOGIN_ENDPOINT = "/api/auth/login"

@pytest.fixture(scope="module")
def api_base_url():
    # Setup: Ensure API is reachable
    url = BASE_URL + "/openapi.json"  # Or use a health endpoint if available
    try:
        resp = requests.get(url, timeout=5)
        assert resp.status_code < 500, f"API not reachable at {url}"
    except Exception as exc:
        pytest.skip(f"API not reachable: {exc}")
    return BASE_URL

def test_login_empty_username_and_password(api_base_url):
    """
    TC-POST-1c9c1b1b-004: Verify that providing empty strings for both username and password returns a 422 validation error.
    """
    url = api_base_url + LOGIN_ENDPOINT
    headers = {"Content-Type": "application/json"}
    payload = {"username": "", "password": ""}

    response = requests.post(url, json=payload, headers=headers)

    # Assert status code is 422
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}"

    # Assert response body contains 'detail' field with validation errors
    try:
        resp_json = response.json()
    except Exception as exc:
        pytest.fail(f"Response is not valid JSON: {exc}")

    assert "detail" in resp_json, "Response JSON does not contain 'detail' field"
    assert isinstance(resp_json["detail"], list), "'detail' field is not an array/list"
    assert len(resp_json["detail"]) > 0, "'detail' array should contain at least one validation error"

    # Optionally, check that errors mention 'username' and 'password' fields
    error_fields = [err.get('loc', [])[-1] for err in resp_json["detail"] if isinstance(err, dict) and 'loc' in err]
    assert "username" in error_fields, "Validation errors should include 'username'"
    assert "password" in error_fields, "Validation errors should include 'password'"
