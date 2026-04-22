import pytest
import requests
import os

def get_bearer_token():
    """Retrieve the bearer token from environment or secure config."""
    token = os.getenv('API_BEARER_TOKEN')
    if not token:
        raise RuntimeError('Bearer token must be set in API_BEARER_TOKEN env variable')
    return token

@pytest.fixture(scope="module")
def api_base_url():
    url = os.getenv('API_BASE_URL', 'https://api.example.com')
    return url if url.endswith('/') else (url + '/')

@pytest.fixture(scope="module")
def auth_header():
    return {
        'Authorization': f'Bearer {get_bearer_token()}',
        'Content-Type': 'application/json'
    }

def build_payload():
    """Construct the malicious payload for SQL injection testing."""
    return {
        "slug": "slug'; DROP TABLE users;--",
        "display_name": "Agent SQL Injection",
        "category": "usg"
    }

def is_valid_asvs_error(resp_json):
    """Ensure error response schema matches RFC 8259/OWASP ASVS expectation."""
    if not isinstance(resp_json, dict):
        return False
    # ASVS: Should not leak internal errors, only structured error response
    # RFC 8259: JSON object
    if "detail" not in resp_json:
        return False
    if not isinstance(resp_json["detail"], list):
        return False
    for detail_item in resp_json["detail"]:
        if not isinstance(detail_item, dict):
            return False
        if not all(key in detail_item for key in ("loc", "msg", "type")):
            return False
    return True

@pytest.mark.security
@pytest.mark.regression
@pytest.mark.owasp_asvs('V5', 'V10')
def test_post_agent_with_sql_injection_is_blocked(api_base_url, auth_header):
    """
    ID: TC-POST-7dead6b2-006
    Description: Validate POST /api/agents/ rejects or sanitizes SQL injection in 'slug'; no 500 or sensitive leakage.

    OWASP ASVS: V5 (Validation), V10 (Error Handling)
    ISO/IEC/IEEE 29148: Requirements traceable by test ID.
    """
    endpoint = api_base_url + 'api/agents/'
    payload = build_payload()

    # Step: Send POST request with SQL injection payload in 'slug'
    response = requests.post(endpoint, headers=auth_header, json=payload)
    # Validate status code
    assert response.status_code in (400, 422), (
        f"Expected 400/422 for invalid input (see ASVS V5), got {response.status_code}. Body: {response.text}")

    # Validate response schema
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response not valid JSON (RFC 8259 violation): {str(e)}\nBody: {response.text}")

    assert is_valid_asvs_error(resp_json), (
        f"Error schema does not conform to ASVS error response design. Got: {resp_json}")

    # Additional ISO/OWASP check: should not expose database internals or unhandled stack traces
    lower_text = response.text.lower()
    assert "sql" not in lower_text and "traceback" not in lower_text and "exception" not in lower_text, (
        f"API should NOT expose technical error details (ASVS V10). Leak detected in: {response.text}")

    # Must NOT return 500 or leak any internal error
    assert response.status_code != 500, (
        "Server must not raise unhandled exceptions (no 500 error; ASVS V10)")
