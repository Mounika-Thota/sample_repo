import os
import requests
import pytest

BASE_URL = os.environ.get('API_BASE_URL', 'https://api.example.com')
AGENT_ID = os.environ.get('AGENT_ID')
INVALID_TOKEN = 'INVALID_TOKEN'
\****************(scope='module', autouse=True)
def check_preconditions():
    # Preconditions: API is reachable and agent exists
    assert BASE_URL is not None, "BASE_URL must be set in environment variables."
    assert AGENT_ID is not None, "AGENT_ID must be set in environment variables."
    # Healthcheck endpoint, align to RFC 8259 and ISO 29148 for traceability
    health_endpoint = BASE_URL + "/health"  # Adjust as necessary
    try:
        resp = requests.get(health_endpoint, timeout=5)
        assert resp.status_code < 400, f"API is not reachable. Health endpoint failed with {resp.status_code}."
    except Exception as ex:
        pytest.skip(f"API is not reachable: {ex}")
    # Check agent existence
    # (Assume an authorized token exists in env for this purpose only; not used in test)
    AUTH_TOKEN = os.environ.get('VALID_BEARER_TOKEN', '')
    agent_url = f"{BASE_URL}/api/agents/{AGENT_ID}"
    check_resp = requests.get(agent_url, headers={'Authorization': f'Bearer {AUTH_TOKEN}'}, timeout=5)
    assert check_resp.status_code == 200, f"Agent with ID {AGENT_ID} must exist for the test, got {check_resp.status_code}."
    yield
    # No teardown needed for this read-only test

def test_get_agent_invalid_token_unauthorized():
    """
    Validate that a GET request to /api/agents/{agent_id} with an invalid Bearer token returns HTTP 401 Unauthorized.
    Requirements:
     - RFC 8259 (JSON syntax, even in errors)
     - OWASP ASVS V2: Authentication
     - OWASP ASVS V10: Error Handling & Logging
     - ISO/IEC/IEEE 29148: Requirements traceability
    """
    endpoint = f"{BASE_URL}/api/agents/{AGENT_ID}"
    headers = {'Authorization': f'Bearer {INVALID_TOKEN}', 'Accept': 'application/json'}

    response = requests.get(endpoint, headers=headers)

    # Validate HTTP status code aligns with test design (OWASP ASVS V2, V10)
    assert response.status_code == 401, (
        f"Expected 401, got {response.status_code}. Test ID: TC-GET-2e2e0c6c-003. Trace: OWASP ASVS V2/V10"
    )
    
    # Validate response body is JSON (RFC 8259)
    content_type = response.headers.get('Content-Type', '')
    assert 'application/json' in content_type, (
        f"Expected application/json response, got {content_type}. Test ID: TC-GET-2e2e0c6c-003"
    )
    
    # Validate error message structure (ISO/IEC/IEEE 29148: verifiable requirement)
    # Response should indicate invalid authentication
    resp_json = response.json()
    assert isinstance(resp_json, dict), "Response body must be a JSON object as per RFC 8259."
    
    # Example: { "error": "Unauthorized", "message": "Invalid authentication token." }
    assert 'error' in resp_json or 'message' in resp_json, (
        "Error response must contain at least 'error' or 'message' field to comply with ISO 29148 verifiability and ASVS V10."
    )
    unauthorized_indicators = ('unauthorized', 'invalid token', 'authentication', 'not authorized')
    summary = (resp_json.get('error', '') + ' ' + resp_json.get('message', '')).lower()
    assert any(sub in summary for sub in unauthorized_indicators), (
        f"Response message must indicate authentication failure. Got: '{summary}'. Trace: ASVS V2/V10"
    )
